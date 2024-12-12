import os
import boto3
from django.core.files.storage import default_storage
from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('common', 'Common User'),
        ('pma_admin', 'PMA Administrator'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=255, help_text="Enter full name", default="name")
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    google_account = models.EmailField(help_text="User's Google account/email address", default="example@mail.com")
    date_joined = models.DateTimeField(default=now)

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='common')
    about_me = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    preferred_dates = models.CharField(max_length=100, blank=True, null=True, help_text="Enter preferred workout days (e.g., Weekdays, Weekends)")
    preferred_times = models.CharField(max_length=100, blank=True, null=True, help_text="Enter preferred workout times (e.g., Mornings, Evenings)")
    workout_likes = models.TextField(blank=True, null=True, help_text="Describe the types of workouts you enjoy")
    workout_dislikes = models.TextField(blank=True, null=True, help_text="Describe the types of workouts you dislike")

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

    def get_file_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None


class Session(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_sessions')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='sessions_enrolled')
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=False, null=False)
    date = models.DateField()
    time = models.TimeField()
    size_capacity = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    file = models.FileField(upload_to="session_files/", null=True, blank=True)

    def __str__(self):
        return f"{self.topic} on {self.date} at {self.time}, Location: {self.location}"

    def remaining_capacity(self):
        return self.size_capacity - self.participants.count()

    def get_file_url(self):
        if self.file:
            return self.file.url
        return None

    def delete(self, *args, **kwargs):
        # Delete all related session files from S3
        for session_file in self.session_files.all():
            session_file.delete()

        super().delete(*args, **kwargs)


class SessionFile(models.Model):        #relate files to session class above
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='session_files')
    file = models.FileField(upload_to="session_files/", null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # metadata fields
    file_title = models.CharField(max_length=100, blank=True, null=True)
    file_description = models.TextField(blank=True, null=True)
    file_keywords = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_extension = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.file_title or f"File for {self.session.topic}"

    def save(self, *args, **kwargs):
        if self.file:
            _, file_extension = os.path.splitext(self.file.name)
            self.file_extension = file_extension.lower().replace('.', '')
        super().save(*args, **kwargs)

    def get_text_file_contents(self):
        if self.file and self.file_extension == 'txt':
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            # Extract the bucket and file name from the file URL
            file_name = self.file.name
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            return obj['Body'].read().decode('utf-8')
        return None

    def delete(self, *args, **kwargs):
        if self.file:
            file_path = self.file.name
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
        super().delete(*args, **kwargs)


class EnrollmentRequest(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='enrollment_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.session.topic} ({self.status})"\


class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} on {self.created_at}"
