from django.db import models

from accounts.models import User
from projects.models import Proposal

class Conversation(models.Model):
    """Represents a conversation between two users tied to a proposal."""
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='initiated_conversations'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_conversations'
    )
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The proposal related to this conversation, if any.",
        related_name='conversations'
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional subject for the conversation."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('initiator', 'recipient', 'proposal')
    def __str__(self):
        return f"Conversation between {self.initiator.username} and {self.recipient.username} for Proposal {self.proposal.id}"

class Chat(models.Model):
    """Represents messages in a conversation."""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    file = models.FileField(
        upload_to='message_files/',
        blank=True,
        null=True,
        help_text="Optional file attachment for the message."
    )
    is_read = models.BooleanField(default=False, help_text="Indicates if the message has been read.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
    
    @property
    def recipient(self):
        return self.conversation.recipient if self.sender == self.conversation.initiator else self.conversation.initiator
        
    def __str__(self):
        return f"Message from {self.sender.username} in Conversation {self.conversation.id}"

class Announcement(models.Model):
    TARGET_GROUP_CHOICES = [
        ('all', 'All Users'),
        ('clients', 'Client Users'),
        ('freelancers', 'Freelancer Users'),
    ]
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional subject for the system message."
    )
    content = models.TextField()
    target_group = models.CharField(
        max_length=20,
        choices=TARGET_GROUP_CHOICES,
        default='all',
        help_text="Defines which group of users the announcement is targeted to."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
