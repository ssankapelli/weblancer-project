from django.db import models

from accounts.models import User
from projects.models import Project

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('reviewer', 'reviewed_user', 'project')

    def __str__(self):
        return f"{self.reviewer} - {self.reviewed_user} ({self.rating} Stars)"
