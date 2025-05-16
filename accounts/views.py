from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from django.utils import timezone
from PIL import Image
import re

from .models import User, FreelancerProfile, ClientProfile

special_char_list = r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
email_special_char_list = r"!\"#$%&'()*+,/:;<=>?@[\]^`{|}~"
def num_checker(string):
    string = str(string)
    return any(i.isdigit() for i in string)

def special_char_checker(string):
    for i in string:
        if i in special_char_list:
            return True
    return False

special_char_list_web = r"!#$%&'()*+,;<=>?@[\]^`{|}~"
def special_char_checker_web(string):
    for i in string:
        if i in special_char_list:
            return True
    return False

def email_special_char_checker(string):
    if "@" in string:
        email = re.split(r'@+', string)
        print(email)
        for i in email[0]:
            if i in special_char_list:
                return True
        return False
    else:
        return True
        
def validate_profile_picture(picture_file, max_size=5):
    """
    Check if the uploaded profile picture is an image file.
    """
    if picture_file:
        file_extension = picture_file.name.split('.')[-1]
        allowed_extensions = ['jpg', 'jpeg', 'png']
        if file_extension.lower() not in allowed_extensions:
            return f"FIle '{picture_file.name}': Only JPG, JPEG, and PNG files are allowed."

        max_size = max_size * 1024 * 1024
        if picture_file.size > max_size:
            return f"FIle '{picture_file.name}': size exceeds the limit of {max_size} MB."

    return None

def validate_confirm_password(pass1, pass2):
    if pass1 != pass2:
        return "Passwords do not match"
    return None

def home_view(request):
    context = {}
    return render(request, "index.html", context)


# base resigter organier or client
def signup_base(request, client=True):
    if request.method == 'POST':
        post_username = request.POST.get('username').strip()
        post_email = request.POST.get('email').strip()
        post_first_name = request.POST.get('first_name', '').strip()
        post_last_name = request.POST.get('last_name', '').strip()
        post_password = request.POST.get('password')
        post_confirm_password = request.POST.get('confirm_password')
        post_phone = request.POST.get('phone', '').strip()
        post_profile_picture = request.FILES.get('profile_picture')
        post_country = request.POST.get('country')
        post_city = request.POST.get('city')
        post_bio = request.POST.get('bio', '').strip()

        post_email = post_email.lower()

        check_username = User.objects.filter(username=post_username).exists()
        check_email = User.objects.filter(email=post_email).exists()
        check_phone = User.objects.filter(phone=post_phone).exists()

        result = {"status": "Failed", "message": "Failed! Try Again Later.", "content": ""}

        if check_phone:
            result["message"] = "Phone number already exists!"
            return result
        if check_username:
            result["message"] = "Username already exists!"
            return result
        if check_email:
            result["message"] = "Email already exists!"
            return result

        # Checking for special characters and existing database entries
        if special_char_checker(post_first_name):
            result["message"] = "First Name can't contain a special character."
            return result
        if special_char_checker(post_last_name):
            result["message"] = "Last Name can't contain a special character."
            return result
        if special_char_checker(post_username):
            result["message"] = "Username can't contain a special character."
            return result
        if email_special_char_checker(post_email):
            result["message"] = "Email can't contain a special character."
            return result

        msg1 = validate_confirm_password(post_password, post_confirm_password)
        if msg1 is not None:
            result["message"] = msg1
            return result

        msg2 = validate_profile_picture(post_profile_picture)
        if msg2 is not None:
            result["message"] = msg2
            return result
        try:
            user = User.objects.create_user(username=post_username, 
                                            email=post_email, 
                                            first_name=post_first_name, 
                                            last_name=post_last_name, 
                                            phone=post_phone,
                                            country=post_country,
                                            city=post_city,
                                            bio=post_bio,)
            user.set_password(post_password)
            user.profile_picture = post_profile_picture  # Save profile picture
            if client is True:
                user.user_type = "client"
            else:
                user.user_type = "freelancer"

            user.save()
            result["content"] = user
            result["status"] = "Success"
            result["message"] = "New account created. Login Now."
            return result
        except Exception as e:
            result["message"] = e
            return result
    return None
        
def freelancer_signup_view(request):
    template_name = 'signup_freelancer.html'
    if request.method == 'POST':
        template_url = 'signup_freelancer'
        result = signup_base(request, False)
        if result:
            if result["status"] == "Success" and result['content']:
                user = result['content']
            else:
                messages.error(request, result["message"])
                return redirect(template_url)
        else:
            messages.error(request, "Error Occured! Try again later.")
            return redirect(template_url)

        post_availability_status = request.POST.get('availability_status', '').strip()
        post_skills = request.POST.get('skills', '').strip()
        post_experience_level = request.POST.get('experience_level', '').strip()
        post_hourly_rate = request.POST.get('hourly_rate', '').strip()
        post_portfolio_link = request.POST.get('portfolio_link', '').strip()

        check_freelancer_user = FreelancerProfile.objects.filter(user=user).exists()
        check_experience_level = FreelancerProfile.objects.filter(experience_level=post_experience_level).exists()

        if check_freelancer_user:
            messages.error(request, "Organizer user already exists!")
            return redirect(template_url)
        if check_experience_level:
            messages.error(request, "Organization Name already exists!")
            return redirect(template_url)

        try:
            freelancer = FreelancerProfile.objects.create(user=user,
                                    availability_status=post_availability_status,
                                    skills=post_skills,
                                    experience_level=post_experience_level,
                                    hourly_rate=post_hourly_rate,
                                    portfolio_link=post_portfolio_link,
                                    )
            freelancer.save()
            messages.success(request, result["message"])
            return redirect('login')
        except Exception as e:
            user.delete()
            messages.error(request, str(e))
            return redirect(template_url)
    else:
        return render(request, template_name)

def client_signup_view(request):
    template_name = 'signup_client.html'
    if request.method == 'POST':
        post_hiring_status = request.POST.get('hiring_status', '').strip()
        template_url = 'signup_client'
        result = signup_base(request)
        if result:
            if result["status"] == "Success" and result['content']:
                user = result['content']
            else:
                messages.error(request, result["message"])
                return redirect(template_url)
        else:
            messages.error(request, "Error Occured! Try again later.")
            return redirect(template_url)

        try:
            client = ClientProfile.objects.create(user=user,
                                    hiring_status=post_hiring_status,
                                    )
            client.save()
            messages.success(request, result["message"])
            return redirect('login')
        except Exception as e:
            user.delete()
            messages.error(request, str(e))
            return redirect(template_url)
    else:
        return render(request, template_name)

def user_login_view(request):
    if request.method == 'POST':
        post_username = request.POST['username']
        post_password = request.POST['password']
        user = authenticate(username=post_username, password=post_password)
        if user is not None:
            login(request, user)
            
            # messages.success(request, "You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Incorrect Email or Password!")
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url="/login")
def user_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"You are logged out.")
        return redirect("login")
    else:
        messages.error(request,"You are not Logged in.")
        return redirect("login")

@login_required(login_url="/login")
def profile_view(request, username=None):
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return redirect('home')
    else:
        user = request.user
    skills_list = []
    if user.is_freelancer:
        skills_list = user.freelancer_profile.skills.split(",") if user.freelancer_profile.skills else []

    context = {'user': user, "skills": skills_list}
    return render(request, 'profile.html', context)
