
from django.urls import path
from .views import *

urlpatterns = [
    path('all-projects/', project_list, name='project_list'),
    path('u/<str:username>/projects/', project_list_user, name='user_project_list'),
    path('projects/', project_list_user, name='user_project_list_request'),
    path('projects/new', project_upload, name='project_upload'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path("projects/<int:project_id>/update-status/", project_status_update, name="project_status_update"),

    path("project/<int:project_id>/proposals/", ProposalListView, name="proposal_list"),
    path("u/<str:username>/proposals/", proposal_list_user, name="user_proposal_list"),
    path("proposals/", proposal_list_user, name="user_proposal_list_request"),
    path("projects/<int:project_id>/submit-proposal/", proposal_submit, name="proposal_submit"),
    path("proposals/<int:proposal_id>/update-status/", proposal_status_update, name="proposal_status_update"),
    
    path('projects/<int:project_id>/submissions/', project_submission_list, name='submission_list'),
    path('u/<str:username>/submissions/', project_submission_list_user, name='user_submission_list'),
    path('submissions/', project_submission_list_user, name='user_submission_list_request'),
    path("proposal/<int:proposal_id>/submit/", project_submission, name="project_submission"),
    path("projects/submissions/<int:submission_id>/", project_submission_detail, name="project_submission_detail"),
    path("submissions/<int:submission_id>/update-status/", submission_status_update, name="submission_status_update"),
    path('proposals/accept/<int:proposal_id>/', accept_proposal, name='accept_proposal'),
]
