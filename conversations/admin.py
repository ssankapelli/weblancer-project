from django.contrib import admin
from .models import Conversation, Chat, Announcement

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiator', 'recipient', 'proposal', 'created_at', 'updated_at')
    search_fields = ('initiator__username', 'recipient__username', 'proposal__title')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content', 'file', 'created_at', 'updated_at')
    search_fields = ('sender__username', 'content')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'target_group', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('target_group', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
