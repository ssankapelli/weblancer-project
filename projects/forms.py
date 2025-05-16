from django import forms
from .models import Project, ProjectAttachment, Proposal, ProjectSubmission

class ProjectForm(forms.ModelForm):
    """Form for creating a new project"""
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'deadline', 'skills_required']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class ProjectAttachmentForm(forms.ModelForm):
    """Form for uploading attachments"""
    class Meta:
        model = ProjectAttachment
        fields = ['files']

    def clean_files(self):
        """Validate file size and type (already handled in model but added here for early feedback)"""
        file = self.cleaned_data.get("files")
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be less than 5MB.")
            if not file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.docx', '.zip')):
                raise forms.ValidationError("Invalid file type. Allowed: PNG, JPG, PDF, DOCX, ZIP.")
        return file

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["proposed_amount", "cover_letter"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proposed_amount"].widget.attrs.update({"class": "form-control", "placeholder": "Enter your bid amount"})
        self.fields["cover_letter"].widget.attrs.update({"class": "form-control", "placeholder": "Optional message"})

    def clean_proposed_amount(self):
        proposed_amount = self.cleaned_data["proposed_amount"]
        project_budget = self.instance.project.budget

        # Validate bid price within budget constraints
        if proposed_amount > project_budget:
            raise forms.ValidationError("Bid price cannot exceed the project budget.")
        if proposed_amount < project_budget * 0.5:  # Example of minimum bid constraint
            raise forms.ValidationError("Bid price is too low.")
        return proposed_amount

class ProposalStatusForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["status"]

class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ["message", "final_amount"]

    # attachments = forms.FileField(
    #     widget=forms.ClearableFileInput(attrs={"multiple": True}), 
    #     required=False
    # )


class ProjectSubmissionStatusForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ["status"]