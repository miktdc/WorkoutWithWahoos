from django import forms
from .models import Session, Profile, Message, SessionFile
from datetime import datetime

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            "title",
            "location",
            "description",
            "date",
            "time",
            "size_capacity",
            "duration_minutes",
            "topic",
        ]
        widgets = {
            "date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter session description"}),
            "size_capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "topic": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["date"] = datetime.now().date()

class SessionFileForm(forms.ModelForm):
    KEYWORD_CHOICES = [
        ("Workout Info", "Workout Info"),
        ("Schedule", "Schedule"),
        ("Location", "Location"),
        ("Other", "Other"),
    ]
    file = forms.FileField(
    required=True,  # Makes the file upload mandatory
    widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    file_keywords = forms.ChoiceField(
        choices=KEYWORD_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    file_keywords_other = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter custom keyword", "class": "form-control"}
        ),
    )

    class Meta:
        model = SessionFile
        fields = [
            "file",
            "file_title",
            "file_description",
            "file_keywords",
            "file_keywords_other",
        ]

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        file_keywords = cleaned_data.get("file_keywords")
        file_keywords_other = cleaned_data.get("file_keywords_other")
        if not file:
            self.add_error("file", "A file is required for upload.")
        if file_keywords == "Other" and not file_keywords_other:
            self.add_error(
                "file_keywords_other",
                "Custom keyword required when 'Other' is selected.",
            )
        elif file_keywords == "Other":
            cleaned_data["file_keywords"] = file_keywords_other
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "real_name",
            "profile_picture",
            "about_me",
            "gender",
            "preferred_dates",
            "preferred_times",
            "workout_likes",
            "workout_dislikes",
        ]
        widgets = {
            "about_me": forms.Textarea(attrs={"rows": 1, "cols": 40}),
            "workout_likes": forms.Textarea(attrs={"rows": 1, "cols": 40}),
            "workout_dislikes": forms.Textarea(attrs={"rows": 1, "cols": 40}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # Make `user_type` non-editable if needed
        if 'user_type' in self.fields:
            self.fields['user_type'].disabled = True

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a message...'}),
        }
