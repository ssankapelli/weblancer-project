from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .forms import ReviewForm
from accounts.models import User
from .models import Review
from projects.models import Project, Proposal

@login_required(login_url="/login")
def review_submit(request, project_id):
    pass

@login_required(login_url="/login")
def review_submit(request, proposal_id):
    referer = request.META.get("HTTP_REFERER", "project_list")
    try:
        proposal = Proposal.objects.get(id=proposal_id)
        project = Project.objects.get(id=proposal.project.id)
    except Exception as e:
        messages.error(request, f"Error: details not found {e}")
        return redirect(referer)

    # Check if the user is allowed to review (e.g., client reviewing freelancer)
    if not project.is_completed or request.user not in [project.client.user, proposal.freelancer.user]:
        messages.error(request, f"You are not allowed to review this project.")
        return redirect(referer)

    existing_review = Review.objects.filter(project=project, reviewer=request.user).first()
    
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = project
            review.reviewer = request.user
            review.reviewed_user = proposal.freelancer.user if request.user == project.client.user else project.client.user
            review.save()
            if existing_review:
                messages.success(request, "Review updated successfully.")
            else:
                messages.success(request, "Review submitted successfully.")
            return redirect(referer)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, "review_form_modal.html", {"form": form, "project": project})
    # return redirect(referer)

@login_required(login_url="/login")
def review_list(request, project_id):
    referer = request.META.get("HTTP_REFERER", "project_list")
    try:
        project = Project.objects.get(id=project_id)
    except Exception as e:
        messages.error(request, f"Error: details not found {e}")
        return redirect(referer)
    
    reviews = Review.objects.filter(project=project).order_by("-created_at")
    context = {"project": project, "reviews": reviews}
    return render(request, "review_list.html", context)

@login_required(login_url="/login")
def review_list_user(request, username):
    reviews = Review.objects.filter(reviewed_user__username=username).order_by("-created_at")
    return render(request, "review_list.html", {"reviews": reviews, "reviewed_user": username})
