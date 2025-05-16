
from django.urls import path
from .views import *

urlpatterns = [   
    path('conversations/create/<int:proposal_id>', create_conversation, name='create_conversation'),
    path('conversations/', conversations, name='conversations'),
    path('send_chat/<int:conversation_id>/', send_chat, name='send_chat'),
    path('api/conversations/<int:conversation_id>/messages/', fetch_conversation_messages, name='fetch_conversation_messages'),
]