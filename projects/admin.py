from django.contrib import admin
from .models import Project, Proposal, ProjectSubmission, ProjectSubmissionAttachment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "budget", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "client__user__username")

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("project", "freelancer", "proposed_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("project__title", "freelancer__user__username")

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ("proposal", "status", "final_amount", "revision_count", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("proposal__project__title", "proposal__freelancer__user__username")

@admin.register(ProjectSubmissionAttachment)
class ProjectSubmissionAttachmentAdmin(admin.ModelAdmin):
    list_display = ("submission", "files", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("submission__proposal__project__title",)
