from django.contrib import admin

from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("reviewer", "reviewed_user", "project", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("reviewer__username", "reviewed_user__username", "project__title")
    ordering = ("-created_at",)
