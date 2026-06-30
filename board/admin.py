from django.contrib import admin
from .models import Board, Thread, Reply, Report, ModLog

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')
    search_fields = ('slug', 'title')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'board', 'poster_id', 'created_at', 'pinned', 'locked')
    list_filter = ('board', 'pinned', 'locked')
    search_fields = ('subject', 'content', 'poster_id')
    list_editable = ('pinned', 'locked')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'poster_id', 'created_at')
    list_filter = ('thread__board',)
    search_fields = ('content', 'poster_id')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'thread', 'reply', 'reporter_id', 'created_at', 'resolved')
    list_filter = ('reason', 'resolved')

@admin.register(ModLog)
class ModLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'detail', 'performed_by', 'created_at')
    list_filter = ('action',)