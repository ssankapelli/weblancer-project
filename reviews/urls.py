from django.urls import path
from .views import *

urlpatterns = [
    path("projects/<int:proposal_id>/review/", review_submit, name="review_submit"),
    path("projects/reviews/<str:username>/", review_list, name="review_list"),
    path("reviews/<str:username>/", review_list_user, name="review_list"),
]