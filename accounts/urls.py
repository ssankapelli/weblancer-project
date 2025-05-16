from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.freelancer_signup_view, name='signup_freelancer'),
    path('signup/client', views.client_signup_view, name='signup_client'),
    path('login/', views.user_login_view, name='login'),
    path('logout', views.user_logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
]
