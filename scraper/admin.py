from django.contrib import admin
from .models import Image, Like, Comment, SearchHistory

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'copyright_status', 'is_transparent', 'created_at')
    list_filter = ('copyright_status', 'is_transparent')
    search_fields = ('title',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query',)
