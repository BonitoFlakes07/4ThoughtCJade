from django.contrib import admin
from .models import Board, Thread, Reply

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')
    search_fields = ('slug', 'title')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'board', 'poster_id', 'created_at', 'pinned', 'locked')
    list_filter = ('board', 'pinned', 'locked')
    search_fields = ('subject', 'content', 'poster_id')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'poster_id', 'created_at')
    list_filter = ('thread__board',)
    search_fields = ('content', 'poster_id')