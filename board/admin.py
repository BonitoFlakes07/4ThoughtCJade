from django.contrib import admin
from .models import Board, Thread, Reply, Report, ModLog


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    fields = ('poster_id', 'parent', 'content', 'image', 'nsfw', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')
    search_fields = ('slug', 'title')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'board', 'poster_id', 'created_at', 'bumped_at', 'pinned', 'locked', 'nsfw')
    list_filter = ('board', 'pinned', 'locked', 'nsfw', 'created_at')
    search_fields = ('subject', 'content', 'poster_id')
    list_editable = ('pinned', 'locked', 'nsfw')
    readonly_fields = ('created_at', 'bumped_at')
    inlines = [ReplyInline]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'parent', 'poster_id', 'created_at', 'nsfw')
    list_filter = ('thread__board', 'nsfw', 'created_at')
    search_fields = ('content', 'poster_id')
    list_editable = ('nsfw',)
    readonly_fields = ('created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'thread', 'reply', 'reporter_id', 'created_at', 'resolved')
    list_filter = ('reason', 'resolved')


@admin.register(ModLog)
class ModLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'detail', 'performed_by', 'created_at')
    list_filter = ('action',)
