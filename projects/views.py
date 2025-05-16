from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Project, ProjectAttachment, MAX_FILE_COUNT, Proposal
from .forms import ProjectForm, ProjectAttachmentForm, ProposalForm, ProposalStatusForm, ProjectSubmissionStatusForm
from accounts.models import User

def get_user_by_username(request, username=None):
    # get user by username if provided or else get from request    
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
        except:            
            referer = request.META.get("HTTP_REFERER", "project_list")
            return redirect(referer)
    else:
        user = request.user
    return user

@login_required(login_url="/login")
def project_upload(request):
    if not request.user.is_client:
        messages.warning(request, "login with a client profile.")
        return redirect('login')
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        uploaded_files = request.FILES.getlist('files')
        
        if not uploaded_files and not form['description']:
            messages.warning(request, "You must provide a description or at least one file.")
            return redirect('project_upload')

        if len(uploaded_files) > MAX_FILE_COUNT:
            messages.error(request, f"You can only upload up to {MAX_FILE_COUNT} files.")
            return redirect('project_upload')

        if form.is_valid():
            try:
                with transaction.atomic():
                    project = form.save(commit=False)
                    project.client = request.user.client_profile
                    project.save()

                    for file in uploaded_files:
                        ProjectAttachment.objects.create(project=project, files=file)

                messages.success(request, "Project uploaded successfully!")
                return redirect('project_detail', project_id=project.id)

            except ValidationError as e:
                messages.error(request, f"File validation error: {str(e)}")
                return redirect('project_upload')
            except Exception as e:
                messages.error(request, "Project upload failed due to an error. Please try again.")
                return redirect('project_upload')

        else:
            messages.error(request, "Form submission failed. Please check the fields.")
            return redirect('project_upload')

    else:
        form = ProjectForm()

    return render(request, "project_upload.html", {"form": form})

# show all projects
def project_list(request):
    """View to list all projects"""
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

# view projects of a specific client user
@login_required(login_url="/login")
def project_list_user(request, username=None):
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return redirect('home')
    else:
        user = request.user
    projects = None
    if request.user.is_client:
        projects = Project.objects.filter(client=user.client_profile)
    else:
        messages.warning(request, "login with a client profile for your project list.")
        return redirect("project_list")
    return render(request, "project_list.html", {'projects': projects, 'is_self': True})

def project_detail(request, project_id):
    """View to display project details"""
    project = get_object_or_404(Project, id=project_id)
    self_proposal = None
    if request.user.is_authenticated and request.user.is_freelancer:
        try:
            self_proposal = Proposal.objects.get(project=project, freelancer=request.user.freelancer_profile)
        except:
            self_proposal = None
    return render(request, 'project_detail.html', {'project': project, 'self_proposal': self_proposal})

# Update project status
@login_required(login_url="/login")
def project_status_update(request, project_id):
    referer = request.META.get("HTTP_REFERER", "project_list")
    project = None
    try:
        project = Project.objects.get(id=project_id)
    except Exception as e:
        messages.error(request, f"Error: details not found")
        return redirect(referer)

    status_choices = [val for val, _ in project.STATUS_CHOICES]

    # Only the client who owns the project can update the status
    if request.user != project.client.user:
        messages.warning(request, "You do not have permissions!")
        return redirect(referer)

    if request.method == "POST":
        status = request.POST.get('status')
        if status:
            if status not in status_choices:
                messages.warning(request, "Invalid status value.")
            else:
                project.status = status
                project.save()
                messages.success(request, "project status updated successfully!")
            return redirect(referer)
        else:
            messages.error(request, "Failed to update project status.")
    
    return redirect(referer)

# ================= Proposals section ====================

# View all proposals for a project
# class ProposalListView(View):
@login_required(login_url="/login")
def ProposalListView(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    proposals = None
    proposals = Proposal.objects.filter(project=project)
    self_proposal = None
    if request.user.is_freelancer:
        try:
            self_proposal = Proposal.objects.get(project=project, freelancer=request.user.freelancer_profile)
        except:
            self_proposal = None
    return render(request, "proposal_list.html", {"project": project, "proposals": proposals, 'self_proposal': self_proposal})

# view proposals of a specific freelancer
@login_required(login_url="/login")
def proposal_list_user(request, username=None):
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return redirect('home')
    else:
        user = request.user
    proposals = None
    if request.user.is_freelancer:
        try:
            proposals = Proposal.objects.filter(freelancer=user.freelancer_profile)
        except:
            proposals = None
    else:
        messages.warning(request, "login with a freelancer profile for your proposal list.")
        return redirect("project_list")
    return render(request, "proposal_list_freelancer.html", {'proposals': proposals})

# Submit a proposal
@login_required(login_url="/login")
def proposal_submit_form(request, project_id):
    if not request.user.is_freelancer:
        messages.warning(request, "login with a freelancer profile.")
        return redirect('project_list')
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.freelancer = request.user.freelancer_profile
            proposal.project = project
            
            # Validate bid price
            if proposal.proposed_amount < 1.0 or proposal.proposed_amount > project.budget:
                messages.error(request, "Bid price must be within the project budget range.")
                return redirect("proposal_submit", project_id=project.id)
            
            proposal.save()
            messages.success(request, "Proposal submitted successfully!")
            return redirect("proposal_list", project_id=project.id)
    else:
        form = ProposalForm()
    
    return render(request, "proposal_submit.html", {"form": form, "project": project})

@login_required(login_url="/login")
def proposal_submit(request, project_id):
    if not request.user.is_freelancer:
        messages.warning(request, "login with a freelancer profile.")
        return redirect('project_list')
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        proposed_amount = request.POST.get("proposed_amount")
        cover_letter = request.POST.get("cover_letter", "")

        if not proposed_amount or float(proposed_amount) > project.budget:
            messages.warning(request, "Invalid amount.")
            return redirect("project_detail", project_id=project_id)
        try:
            proposal = Proposal.objects.get(project=project, freelancer=request.user.freelancer_profile)
            proposal.proposed_amount = proposed_amount
            proposal.cover_letter = cover_letter
            proposal.save()
            messages.success(request, "Bid proposal updated.")
        except Proposal.DoesNotExist:
            Proposal.objects.create(
                project=project,
                freelancer=request.user.freelancer_profile,
                proposed_amount=proposed_amount,
                cover_letter=cover_letter,
            )
            messages.success(request, "Bid proposal submitted.")
        except:
            messages.error(request, "Failed to submit! Try again later.")
        return redirect("project_detail", project_id=project_id)
    return redirect("project_detail", project_id=project_id)

# Update proposal status
@login_required(login_url="/login")
def proposal_status_update(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        if request.user.is_client:
            referer = reverse('proposal_list')
        else:
            referer = reverse('project_detail', proposal.project.id)

    # Only the freelancer who submitted or the client who owns the project can update the status
    if request.user != proposal.freelancer.user and request.user != proposal.project.client.user:
        messages.warning(request, "You do not have permissions!")
        return redirect(referer)

    if request.method == "POST":
        form = ProposalStatusForm(request.POST, instance=proposal)
        if form.is_valid():
            if request.user == proposal.freelancer.user and form.cleaned_data['status'] != 'rejected':
                messages.warning(request, "You can only set Rejected!")
                return redirect(referer)
            form.save()
            messages.success(request, "Proposal status updated successfully!")
        else:
            messages.error(request, "Failed to update proposal status.")
    
    return redirect(referer)

@csrf_exempt
@login_required(login_url="/login")
@require_POST
def accept_proposal(request, proposal_id):
    user = request.user

    # Check if user is a client
    if not hasattr(user, "client_profile"):
        return JsonResponse({'success': False, 'error': 'Only clients can accept proposals.'})

    # Try to get the proposal
    proposal = get_object_or_404(Proposal, id=proposal_id)

    # Check if this proposal belongs to the logged-in client's project
    if proposal.project.client != user.client_profile:
        return JsonResponse({'success': False, 'error': 'Unauthorized: This proposal is not for your project.'})

    try:
        # Accept this proposal
        proposal.status = 'accepted'
        proposal.save()

        # Reject all other proposals for the same project
        Proposal.objects.filter(project=proposal.project).exclude(id=proposal.id).update(status='rejected')

        return JsonResponse({'success': True, 'message': 'Proposal accepted successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})


# ================= Project submit section ====================

from .models import ProjectSubmission, ProjectSubmissionAttachment
from .forms import ProjectSubmissionForm

@login_required(login_url='/login')
def project_submission0(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        if request.user.is_client:
            referer = reverse('proposal_list')
        else:
            referer = reverse('project_detail', proposal.project.id)

    # Ensure the proposal is accepted and belongs to the freelancer
    if proposal.status != "accepted" or proposal.freelancer.user != request.user:
        messages.warning(request, "No persmission.")
        return redirect(referer)

    # Get or create the submission
    submission, _ = ProjectSubmission.objects.get_or_create(proposal=proposal)

    if request.method == "POST":
        form = ProjectSubmissionForm(request.POST, instance=submission)

        if form.is_valid():
            # submission = form.save()
            uploaded_files = request.FILES.getlist("files")
            try:
                with transaction.atomic():
                    submission = form.save(commit=False)
                    submission.request_revision()
                    submission.save()

                    for file in uploaded_files:
                        ProjectSubmissionAttachment.objects.create(submission=submission, files=file)

                messages.success(request, "submission uploaded successfully!")
                return redirect('submission_detail', submission_id=submission.id)

            except ValidationError as e:
                messages.error(request, f"File validation error: {str(e)}")
            except Exception as e:
                messages.error(request, "submission upload failed due to an error. Please try again.")

            # Handle file uploads
            # uploaded_files = request.FILES.getlist("files")
            # for file in files:
            #     ProjectSubmissionAttachment.objects.create(submission=submission, files=file)

            # messages.success(request, "Project submitted.")
            # return redirect(referer)
    else:
        form = ProjectSubmissionForm(instance=submission)

    messages.error(request, "Failed submission! Try again later.")
    return redirect(referer)

@login_required(login_url="/login")
def project_submission(request, proposal_id):
    """Handles creating or updating a project submission."""
    referer = request.META.get("HTTP_REFERER", "project_list")
    if not request.user.is_freelancer:
        messages.error(request, "only freelancer can submit!")
        return redirect(referer)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect(referer)

    proposal = Proposal.objects.filter(id=proposal_id, status="accepted").first()
    if not proposal:
        messages.error(request, "Proposal not found or not accepted.")
        return redirect(referer)
    
    if request.user != proposal.freelancer.user:
        messages.warning(request, "Page not found.")
        return redirect(referer)
    
    message = request.POST.get("message", "").strip()
    final_amount = request.POST.get("final_amount")
    files = request.FILES.getlist("files")
    # Ensure at least a message or file is provided
    if not files and not message:
        messages.warning(request, "You must provide a message or at least one file.")
        return redirect(referer)
    try:
        with transaction.atomic():
            # Create or update submission
            submission, created = ProjectSubmission.objects.get_or_create(
                proposal=proposal,
                defaults={
                    "message": message,
                    "final_amount": final_amount,
                    # "revision_count": 0 if created else None,
                },
            )
            msg = "Submission successful!"
            if not created:
                # Update submission if it already exists
                submission.message = message
                submission.final_amount = final_amount
                # submission.revision_count += 1
                submission.save()
                msg = "Submission updated."
            submission.request_revision()
            # Handle file uploads
            if files:
                # Delete old attachments if updating
                if not created:
                    submission.attachments.all().delete()

                for file in files:
                    # attachment = ProjectSubmissionAttachment(
                    #     submission=submission, files=file
                    # )
                    # attachment.full_clean()  # Validate before saving
                    # attachment.save()
                    ProjectSubmissionAttachment.objects.create(submission=submission, files=file)

        messages.success(request, msg)
    except ValidationError as e:
        messages.error(request, f"Validation error: {e}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    return redirect(referer)

@login_required(login_url="/login")
def project_submission_list(request, project_id):
    """Lists all project submissions for a specific project."""
    referer = request.META.get("HTTP_REFERER", "project_list")
    try:
        project = Project.objects.get(id=project_id)
    except Exception as e:
        messages.error(request, f"Error: details not found")
        return redirect(referer)

    # if request.user != project.client.user:
    #     messages.warning(request, "Page not found.")
    #     return redirect(referer)
    
    submissions = None
    # Check if the user is the project owner (client) or the freelancer involved
    if request.user.is_client:
        submissions = ProjectSubmission.objects.filter(proposal__project=project)
    elif request.user.is_freelancer:
        submissions = ProjectSubmission.objects.filter(
            proposal__project=project, proposal__freelancer=request.user.freelancer_profile
        )

    context = {
        "project": project,
        "submissions": submissions,
    }
    return render(request, "project_submission_list.html", context)

@login_required(login_url="/login")
def project_submission_list_user(request, username=None):
    """Lists all project submissions for the logged-in user."""
    user = get_user_by_username(request, username)
    submissions = None
    if user.is_freelancer:
        submissions = ProjectSubmission.objects.filter(proposal__freelancer=user.freelancer_profile)
    elif user.is_client:
        submissions = ProjectSubmission.objects.filter(proposal__project__client=user.client_profile)

    context = {
        "submissions": submissions,
        "is_self": True,
    }

    return render(request, "project_submission_list_user.html", context)

@login_required(login_url="/login")
def project_submission_detail(request, submission_id):
    referer = request.META.get("HTTP_REFERER", "project_list")
    submission = None
    attachments = None
    try:
        submission = ProjectSubmission.objects.get(id=submission_id)
        attachments = submission.attachments.all()
    except Exception as e:
        messages.error(request, f"Error: details not found")
        return redirect(referer)
    
    if request.user != submission.proposal.freelancer.user and request.user != submission.proposal.project.client.user:
        messages.warning(request, "Page not found.")
        return redirect(referer)
    # Handle instructor feedback and grade updates
    # if request.method == "POST":
    #     # form = FeedbackForm(request.POST, instance=submission)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, "Feedback and grade updated successfully.")
    #         # return HttpResponseRedirect(request.path_info)  # Refresh the page
    # else:
    #     form = FeedbackForm(instance=submission)

    context = {
        "submission": submission,
        "attachments": attachments,
    }
    return render(request, "project_submission_detail.html", context)

# Update submission status
@login_required(login_url="/login")
def submission_status_update(request, submission_id):
    referer = request.META.get("HTTP_REFERER", "project_list")
    submission = None
    try:
        submission = ProjectSubmission.objects.get(id=submission_id)
    except Exception as e:
        messages.error(request, f"Error: details not found")
        return redirect(referer)

    STATUS_CHOICES = [
        "submitted",
        "revision_requested",
        "approved",
        "completed",
        "canceled",
        "disputed",
    ]

    # Only the freelancer who submitted or the client who owns the project can update the status
    if request.user != submission.proposal.freelancer.user and request.user != submission.proposal.project.client.user:
        messages.warning(request, "You do not have permissions!")
        return redirect(referer)

    if request.method == "POST":
        form = ProjectSubmissionStatusForm(request.POST, instance=submission)
        if form.is_valid():
            if request.user == submission.proposal.freelancer.user and form.cleaned_data['status'] not in ['submitted', 'completed', 'disputed']:
                messages.warning(request, "You can not set this status value.")
                return redirect(referer)
            form.save()
            messages.success(request, "submission status updated successfully!")
        else:
            messages.error(request, "Failed to update submission status.")
    
    return redirect(referer)
