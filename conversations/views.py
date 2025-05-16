from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, BooleanField, OuterRef

from accounts.models import User
from projects.models import Proposal
from .models import Conversation, Chat, Announcement
from .forms import ChatForm

@login_required(login_url="/login")
def create_conversation(request, proposal_id=None):
    referer = request.META.get("HTTP_REFERER", "project_list")
    selected_proposal = Proposal.objects.get(id=proposal_id)
    if not selected_proposal:
        messages.error(request, "Selected Proposal Not Found! try again later.")
        return redirect(referer)
    user = request.user
    seleced_recipient = selected_proposal.freelancer.user if user != selected_proposal.freelancer else selected_proposal.project.client.user
    if not seleced_recipient:
        messages.error(request, "Selected recipient Not Found! try again later.")
        return redirect(referer)

    if user == seleced_recipient:
        messages.info(request, "Can not send message to Self.")
        return redirect (referer)

    # check existance
    is_exists = Conversation.objects.filter(initiator=user, recipient=seleced_recipient, proposal=selected_proposal).exists()
    if not is_exists:
        Conversation.objects.create(initiator=user, recipient=seleced_recipient, proposal=selected_proposal)
    return redirect("conversations")

@login_required(login_url="/login")
def conversations(request):
    user = request.user

    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

    conversations = Conversation.objects.filter(
        Q(initiator=user) | Q(recipient=user)
    ).annotate(
        # Count of unread messages for the logged-in user
        unread_message_count=Count(
            'messages',
            filter=(~Q(messages__sender=user) & Q(messages__is_read=False))
        ),
        # Existence of unread messages
        has_unread_messages=Case(
            When(unread_message_count__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        # Highlight conversation if it is created within the last 1 hours or has zero messages
        is_recent=Case(
            When(Q(created_at__gte=twenty_four_hours_ago) & Q(initiator=user), then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by("-updated_at")

    return render(request, 'conversation_messages.html', {'conversations': conversations})

@login_required(login_url="/login")
def fetch_conversation_messages(request, conversation_id):
    """View to display and send messages in a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    msgs = Chat.objects.filter(conversation=conversation).order_by('created_at')

    # Mark all unread messages as read when the conversation is opened
    try:
        unread_messages = msgs.filter(conversation__recipient=request.user, is_read=False)
        unread_messages.update(is_read=True)
    except:
        print("Can not update read status")

    messages = [
        {
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.first_name,
            'recipient_id': msg.recipient.id,
            'recipient_name': msg.recipient.first_name,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in msgs
    ]
    context = {'messages': messages,
                'selected_conversation_id': conversation.id,
                'current_user_id': request.user.id,
                'project_id': conversation.proposal.project.id,
                'project_title': conversation.proposal.project.title,
                'project_status': conversation.proposal.project.status,
                'proposal_id': conversation.proposal.id,
                'proposal_status': conversation.proposal.status}
    return JsonResponse(context)

@login_required(login_url="/login")
def send_chat(request, conversation_id):
    if request.method == 'POST':
        conversation = Conversation.objects.get(id=conversation_id)
        if not conversation:
            return JsonResponse({'status': 'fail'})

        content = request.POST.get('content', '').strip()
        if content:
            # recipient = conversation.recipient if request.user == conversation.initiator else conversation.initiator
            Chat.objects.create(conversation=conversation, sender=request.user, content=content)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})
