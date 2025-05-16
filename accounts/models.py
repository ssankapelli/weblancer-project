from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings

import os
import numpy as np

def validate_image_size(image):
    max_size_mb = 5 # max size limit 5MB
    max_size_bt = max_size_mb * 1024 * 1024
    if image.size > max_size_bt:
        raise ValidationError(f"Image size should not exceed {max_size_mb} MB")

def validate_image_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension.')
        
def validate_image_file_type(image):
    valid_mime_types = ['image/jpeg', 'image/png']
    valid_extensions = ['jpg', 'jpeg', 'png']
    file_extension = image.name.split('.')[-1].lower()
    if image.file.content_type not in valid_mime_types or file_extension not in valid_extensions:
        raise ValidationError(f"Unsupported file type: {file_extension}. Supported file types are: {', '.join(valid_extensions)}")

class User(AbstractUser):
    Freelancer = 'freelancer'
    CLIENT = 'client'
    ROLE_CHOICES = [
        (Freelancer, 'Freelancer'),
        (CLIENT, 'Client'),
    ]
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, validators=[validate_image_size, validate_image_file_type])
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENT)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # For email or profile verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'phone']

    @property
    def user_type_choices(self):
        return [choice for choice in self._meta.get_field('user_type').choices]

    @property
    def is_freelancer(self):
        return self.user_type == self.Freelancer

    @property
    def is_client(self):
        return self.user_type == self.CLIENT

    @property
    def profile_picture_url(self):
        """
        function returns profile picture or a default image URL.
        """
        if self.profile_picture:
            return self.profile_picture.url
        else:
            return f"{settings.STATIC_URL}images/default_profile_picture.png"
    
    @property
    def avg_rating(self):
        """Calculate the median rating (helps ignore outliers)."""
        reviews = self.received_reviews.values_list("rating", flat=True)
        if not reviews:
            return None
        return np.median(reviews)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - ({self.user_type})"

class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile', limit_choices_to={'user_type': 'client'})
    availability_status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('looking_for_work', 'Looking for Work'),
    ], null=True, blank=True)
    skills = models.TextField(help_text="Comma-separated skills", blank=True, null=True)
    experience_level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ], default='beginner')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Freelancer"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', limit_choices_to={'user_type': 'client'})
    hiring_status = models.CharField(max_length=20, choices=[
        ('actively_hiring', 'Actively Hiring'),
        ('reviewing_proposals', 'Reviewing Proposals'),
        ('not_hiring', 'Not Hiring'),
    ], null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Client"
