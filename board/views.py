from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Board, Thread
from .forms import ThreadForm, ReplyForm
from .utils import get_client_ip, hash_ip


def get_all_boards():
    return Board.objects.all()


def get_page_range(paginator, current_page, on_each_side=2, on_ends=2):
    """
    Returns a list of page numbers with None as ellipsis markers.
    e.g. [1, 2, None, 5, 6, 7, None, 19, 20]
    """
    total = paginator.num_pages

    if total <= 10:
        return list(range(1, total + 1))

    pages = set()

    # always show first and last few pages
    for i in range(1, on_ends + 1):
        pages.add(i)
    for i in range(total - on_ends + 1, total + 1):
        pages.add(i)

    # always show pages around current
    for i in range(
        max(1, current_page - on_each_side),
        min(total, current_page + on_each_side) + 1
    ):
        pages.add(i)

    sorted_pages = sorted(pages)

    # insert None where there are gaps (for ellipsis)
    result = []
    prev = None
    for p in sorted_pages:
        if prev is not None and p - prev > 1:
            result.append(None)  # None = ellipsis
        result.append(p)
        prev = p

    return result


def home(request):
    boards = Board.objects.all()
    return render(request, 'board/home.html', {
        'boards': boards,
        'all_boards': get_all_boards(),
    })


def board_detail(request, slug):
    board = get_object_or_404(Board, slug=slug)
    thread_list = board.threads.all()

    paginator = Paginator(thread_list, 9)
    page_number = request.GET.get('page')
    threads = paginator.get_page(page_number)

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
        'board': board,
        'threads': threads,
        'form': form,
        'all_boards': get_all_boards(),
        'page_range': page_range,
    })


def thread_detail(request, slug, thread_id):
    board = get_object_or_404(Board, slug=slug)
    thread = get_object_or_404(Thread, id=thread_id, board=board)
    replies = thread.replies.all()

    if request.method == 'POST':
        if thread.locked:
            return redirect('thread_detail', slug=slug, thread_id=thread.id)
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.poster_id = hash_ip(get_client_ip(request))
            reply.save()
            thread.bumped_at = timezone.now()
            thread.save()
            return redirect('thread_detail', slug=slug, thread_id=thread.id)
    else:
        form = ReplyForm()

    return render(request, 'board/thread_detail.html', {
        'board': board,
        'thread': thread,
        'replies': replies,
        'form': form,
        'all_boards': get_all_boards(),
    })


def error_404(request, exception):
    return render(request, 'board/404.html', {'all_boards': get_all_boards()}, status=404)

def error_500(request):
    return render(request, 'board/500.html', {'all_boards': get_all_boards()}, status=500)