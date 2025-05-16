from django.db import models
from django.core.exceptions import ValidationError
import os

from accounts.models import ClientProfile, FreelancerProfile

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.zip', '.png', '.jpg', '.jpeg', '.webp'}
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB
MAX_FILE_COUNT = 5  # Maximum number of files allowed per submission

def validate_file_size(file, max_size_mb=MAX_FILE_SIZE_MB):
    """Validate file size (default: 10MB)"""
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file.size > max_size:
        raise ValidationError(f"File {file.name} exceeds the maximum size of {max_size_mb}MB.")

def validate_file_type(file):
    """Validate allowed file types"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type {ext} is not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

class Project(models.Model):
    """Represents a project posted by a client for freelancers"""

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    skills_required = models.TextField(help_text="Comma-separated skills required")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_completed(self):
        return self.status == "completed"

    def __str__(self):
        return self.title

class ProjectAttachment(models.Model):
    """Allows clients to upload multiple files for a project"""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attachments")
    files = models.FileField(upload_to="project_files/", validators=[validate_file_size, validate_file_type])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     # Count existing files for the project
    #     existing_files_count = ProjectAttachment.objects.filter(project=self.project).count()
    #     if existing_files_count >= MAX_FILE_COUNT:
    #         raise ValidationError(f"You can only upload up to {MAX_FILE_COUNT} files.")
        
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Attachment for {self.project.title}"

class Proposal(models.Model):
    """Represents a freelancer's proposal for a project"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_proposals")
    freelancer = models.ForeignKey(
        FreelancerProfile,
        on_delete=models.CASCADE,
        related_name="freelancer_proposals"
    )
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal by {self.freelancer} for {self.project.title}"

class ProjectSubmission(models.Model):
    """Represents the final submission of work by the freelancer"""

    proposal = models.OneToOneField(
        Proposal, on_delete=models.CASCADE, related_name="submitted_projects"
    )
    
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("revision_requested", "Revision Requested"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
        ("disputed", "Disputed"),
    ]
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # final_agreed_amount
    revision_count = models.PositiveIntegerField(default=0, help_text="Number of times resubmitted")
    
    message = models.TextField(blank=True, null=True)  # Optional message from freelancer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_completed(self):
        return self.status == "completed"
    
    def request_revision(self):
        """Increments revision count and changes status to 'revision_requested'."""
        self.revision_count += 1
        self.status = "revision_requested"
        self.save()

    def __str__(self):
        return f"Submission for {self.proposal.project.title} by {self.proposal.freelancer.user.username}"

class ProjectSubmissionAttachment(models.Model):
    submission = models.ForeignKey(
        ProjectSubmission, on_delete=models.CASCADE, related_name="attachments"
    )
    files = models.FileField(upload_to="submission_files/", validators=[validate_file_size, validate_file_type])
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment for Submission {self.submission.id}"
