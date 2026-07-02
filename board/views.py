from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Board, Thread, Reply, Report, ModLog
from .forms import ThreadForm, ReplyForm, BoardForm, ReportForm
from .utils import get_client_ip, hash_ip


def get_all_boards():
    return Board.objects.all()


def get_page_range(paginator, current_page, on_each_side=2, on_ends=2):
    total = paginator.num_pages
    if total <= 10:
        return list(range(1, total + 1))
    pages = set()
    for i in range(1, on_ends + 1):
        pages.add(i)
    for i in range(total - on_ends + 1, total + 1):
        pages.add(i)
    for i in range(max(1, current_page - on_each_side), min(total, current_page + on_each_side) + 1):
        pages.add(i)
    sorted_pages = sorted(pages)
    result, prev = [], None
    for p in sorted_pages:
        if prev is not None and p - prev > 1:
            result.append(None)
        result.append(p)
        prev = p
    return result


def log_action(request, action, detail=''):
    ModLog.objects.create(
        action=action,
        detail=detail,
        performed_by=request.user.username if request.user.is_authenticated else 'system',
    )


# ── PUBLIC VIEWS ──

def home(request):
    boards = Board.objects.all()
    form = BoardForm()
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save()
            return redirect('board_detail', slug=board.slug)
    return render(request, 'board/home.html', {
        'boards': boards, 'all_boards': get_all_boards(), 'form': form,
    })


def board_detail(request, slug):
    board = get_object_or_404(Board, slug=slug)
    thread_list = board.threads.annotate(reply_total=Count('replies'))
    sort = request.GET.get('sort', 'recent')
    per_page = request.GET.get('per_page', '9')
    min_replies = request.GET.get('min_replies', '0')
    hide_nsfw = request.GET.get('hide_nsfw', '0')

    try:
        per_page_int = int(per_page)
    except (TypeError, ValueError):
        per_page_int = 9
    per_page_int = per_page_int if per_page_int in (9, 10, 20, 40) else 9

    try:
        min_replies_int = int(min_replies)
    except (TypeError, ValueError):
        min_replies_int = 0
    min_replies_int = max(0, min_replies_int)

    if hide_nsfw == '1':
        thread_list = thread_list.filter(nsfw=False)

    if min_replies_int:
        thread_list = thread_list.filter(reply_total__gte=min_replies_int)

    if sort == 'most_replies':
        thread_list = thread_list.order_by('-reply_total', '-bumped_at')
    elif sort == 'oldest':
        thread_list = thread_list.order_by('created_at')
    else:
        sort = 'recent'
        thread_list = thread_list.order_by('-pinned', '-bumped_at')

    paginator = Paginator(thread_list, per_page_int)
    threads = paginator.get_page(request.GET.get('page'))
    page_range = get_page_range(paginator, threads.number)

    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.board = board
            thread.poster_id = hash_ip(get_client_ip(request))
            thread.save()
            return redirect('thread_detail', slug=slug, thread_id=thread.id)
    else:
        form = ThreadForm()

    return render(request, 'board/board_detail.html', {
        'board': board, 'threads': threads, 'form': form,
        'all_boards': get_all_boards(), 'page_range': page_range,
        'sort': sort, 'per_page': per_page_int, 'min_replies': min_replies_int,
        'hide_nsfw': hide_nsfw == '1',
    })


def thread_detail(request, slug, thread_id):
    board = get_object_or_404(Board, slug=slug)
    thread = get_object_or_404(Thread, id=thread_id, board=board)
    all_replies = list(thread.replies.select_related('parent').all())
    replies_by_parent = {}
    for reply in all_replies:
        replies_by_parent.setdefault(reply.parent_id, []).append(reply)

    def build_reply_nodes(parent_id=None):
        return [
            {'reply': reply, 'children': build_reply_nodes(reply.id)}
            for reply in replies_by_parent.get(parent_id, [])
        ]

    nested_replies = build_reply_nodes()

    if request.method == 'POST':
        if thread.locked:
            return redirect('thread_detail', slug=slug, thread_id=thread.id)
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.poster_id = hash_ip(get_client_ip(request))
            parent_id = form.cleaned_data.get('parent_id')
            if parent_id:
                parent_reply = thread.replies.filter(id=parent_id).first()
                reply.parent = parent_reply
            reply.save()
            thread.bumped_at = timezone.now()
            thread.save()
            return redirect('thread_detail', slug=slug, thread_id=thread.id)
    else:
        form = ReplyForm()

    return render(request, 'board/thread_detail.html', {
        'board': board, 'thread': thread, 'replies': nested_replies,
        'reply_total': len(all_replies), 'form': form, 'all_boards': get_all_boards(),
        'report_form': ReportForm(),
    })


def report_thread(request, slug, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, board__slug=slug)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.thread = thread
            report.reporter_id = hash_ip(get_client_ip(request))
            report.save()
            messages.success(request, 'Report submitted. A moderator will review it.')
        else:
            messages.error(request, 'Could not submit report — please try again.')
    return redirect('thread_detail', slug=slug, thread_id=thread_id)


def report_reply(request, slug, thread_id, reply_id):
    reply = get_object_or_404(Reply, id=reply_id, thread_id=thread_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reply = reply
            report.reporter_id = hash_ip(get_client_ip(request))
            report.save()
            messages.success(request, 'Report submitted. A moderator will review it.')
        else:
            messages.error(request, 'Could not submit report — please try again.')
    return redirect('thread_detail', slug=slug, thread_id=thread_id)


def error_404(request, exception):
    return render(request, 'board/404.html', {'all_boards': get_all_boards()}, status=404)

def error_500(request):
    return render(request, 'board/500.html', {'all_boards': get_all_boards()}, status=500)


# ── MODERATION VIEWS ──

def mod_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('mod_dashboard')

    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username', ''), password=request.POST.get('password', ''))
        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('mod_dashboard')
        error = 'Invalid credentials, or this account does not have moderator access.'

    return render(request, 'board/mod_login.html', {'error': error, 'all_boards': get_all_boards()})


def mod_logout(request):
    auth_logout(request)
    return redirect('mod_login')


@staff_member_required(login_url='mod_login')
def mod_dashboard(request):
    boards = Board.objects.annotate(thread_count=Count('threads', distinct=True))
    threads = Thread.objects.select_related('board').annotate(
        reply_total=Count('replies', distinct=True)
    ).order_by('-created_at')

    selected_board = request.GET.get('board')
    if selected_board:
        threads = threads.filter(board__slug=selected_board)

    pending_reports = Report.objects.filter(resolved=False).select_related(
        'thread', 'thread__board', 'reply', 'reply__thread', 'reply__thread__board'
    )
    logs = ModLog.objects.all()[:50]

    stats = {
        'board_count': Board.objects.count(),
        'thread_count': Thread.objects.count(),
        'reply_count': Reply.objects.count(),
        'pending_reports': pending_reports.count(),
    }

    return render(request, 'board/mod_dashboard.html', {
        'boards': boards, 'threads': threads, 'stats': stats,
        'selected_board': selected_board, 'all_boards': get_all_boards(),
        'pending_reports': pending_reports, 'logs': logs,
    })


@staff_member_required(login_url='mod_login')
def mod_toggle_pin(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.pinned = not thread.pinned
    thread.save()
    log_action(request, 'Pinned thread' if thread.pinned else 'Unpinned thread', f'"{thread}" in /{thread.board.slug}/')
    return redirect(request.POST.get('redirect_to') or 'mod_dashboard')


@staff_member_required(login_url='mod_login')
def mod_toggle_lock(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.locked = not thread.locked
    thread.save()
    log_action(request, 'Locked thread' if thread.locked else 'Unlocked thread', f'"{thread}" in /{thread.board.slug}/')
    return redirect(request.POST.get('redirect_to') or 'mod_dashboard')


@staff_member_required(login_url='mod_login')
def mod_delete_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    log_action(request, 'Deleted thread', f'"{thread}" in /{thread.board.slug}/')
    thread.delete()
    return redirect(request.POST.get('redirect_to') or 'mod_dashboard')


@staff_member_required(login_url='mod_login')
def mod_delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    log_action(request, 'Deleted reply', f'Reply #{reply.id} on "{reply.thread}"')
    reply.delete()
    return redirect(request.POST.get('redirect_to') or 'mod_dashboard')


@staff_member_required(login_url='mod_login')
def mod_delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    log_action(request, 'Deleted board', f'/{board.slug}/ — {board.title}')
    board.delete()
    return redirect('mod_dashboard')


@staff_member_required(login_url='mod_login')
def mod_resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.resolved = True
    report.save()
    log_action(request, 'Dismissed report', f'Report #{report.id} ({report.get_reason_display()})')
    return redirect('mod_dashboard')