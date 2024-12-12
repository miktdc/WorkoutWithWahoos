from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, Session, Message, EnrollmentRequest, SessionFile
from .forms import SessionForm, ProfileUpdateForm, MessageForm, SessionFileForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


@login_required
def pma_admin_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    sessions = Session.objects.all()
    return render(request, 'pma_admin_dashboard.html',  {'profile': profile, 'sessions': sessions})

@login_required
def common_user_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    created_sessions = Session.objects.filter(creator=request.user)
    joined_sessions = Session.objects.filter(participants=request.user)
    return render(request, 'common_user_dashboard.html', {
        'profile': profile,
        'created_sessions': created_sessions,
        'joined_sessions': joined_sessions
    })

def home(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            if profile.user_type == "pma_admin":
                return redirect("pma_admin_dashboard")
            elif profile.user_type == "common":
                return redirect("common_user_dashboard")
        except Profile.DoesNotExist:
            Profile.objects.create(user=request.user, user_type="common")
            return render(request, "index.html")
    return render(request, "index.html")

def logout_view(request):
    logout(request)
    return redirect("/")


def available_sessions(request):
    sessions = Session.objects.exclude(creator=request.user).order_by("time")
    now = timezone.now()

    enrollment_requests = EnrollmentRequest.objects.filter(user=request.user)
    enrollment_status = {req.session.id: req.status for req in enrollment_requests}

    for session in sessions:
        session_time = timezone.make_aware(datetime.combine(session.date, session.time))
        time_left = session_time - now

        if time_left > timedelta(0):
            session.time_left = time_left
            session.days_left = time_left.days
            session.hours_left = time_left.seconds // 3600
            session.minutes_left = (time_left.seconds // 60) % 60
        else:
            session.time_left = timedelta(0)
            session.days_left = 0
            session.hours_left = 0
            session.minutes_left = 0

    # Sort sessions by time_left (ascending order)
    sessions = sorted(sessions, key=lambda x: x.time_left)

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        session = get_object_or_404(Session, id=session_id)

        if request.user in session.participants.all():
            message = "You are already enrolled in this session."
        elif session.remaining_capacity() > 0:
            session.participants.add(request.user)
            message = "You are successfully enrolled."
        else:
            message = "Session is full."

    return render(
        request,
        "available_sessions.html",
        {
            "sessions": sessions,
            "enrollment_status": enrollment_status,  # Keep as a dictionary
        },
    )

def create_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            date = form.cleaned_data.get("date")
            time = form.cleaned_data.get("time")
            session_datetime = make_aware(datetime.combine(date, time))
            if session_datetime <= now():
                messages.error(request, "Workout session cannot be in the past.")
            else:
                session = form.save(commit=False)
                session.creator = request.user
                session.save()
                return redirect('common_user_dashboard')
        else:
            messages.error(request, "Please fix the error.")
    else:
        form = SessionForm()
    return render(request, "create_session.html", {"form": form})

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

def update_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to some profile detail page after saving
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form, 'profile': profile})

def anonymous_user(request):
    sessions = Session.objects.order_by('time')
    return render(request, "anonymous_user.html", {'sessions': sessions})

def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    creator = session.creator
    session_name = session.topic
    session.delete()
    messages.success(request, f"The session has been successfully deleted.")
    return redirect('pma_admin_dashboard')


def edit_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            form.save()
            return redirect("common_user_dashboard")
    else:
        form = SessionForm(instance=session)
    context = {
        'session': session,
        'form': form,
    }
    return render(request, "edit_session.html", context)


def drop_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    user = request.user

    if user in session.participants.all():
        session.participants.remove(user)

        # Remove *all* related enrollment requests for this user and session
        EnrollmentRequest.objects.filter(session=session, user=user).delete()

        messages.success(request, "You have successfully dropped the session.")
    else:
        messages.error(request, "You are not part of this session.")

    return redirect("common_user_dashboard")

def workout_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    session_messages = session.messages.order_by('-created_at')  # Use the related name
    form = MessageForm()
    remaining_capacity = session.size_capacity - session.participants.count()

    if request.method == 'POST':
        if 'message_submit' in request.POST:
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.user = request.user
                message.session = session
                message.save()
                return redirect('workout_detail', session_id=session.id)

    context = {
        'session': session,
        'session_messages': session_messages,  # Updated context key
        'form': form,
        'remaining_capacity': range(remaining_capacity),
    }
    return render(request, 'workout_detail.html', context)

@login_required
def request_enrollment(request):
    if request.method == "POST":
        session_id = request.POST.get("session_id")
        session = get_object_or_404(Session, id=session_id)

        # Prevent the creator from enrolling in their own session
        if request.user == session.creator:
            messages.error(request, "You cannot enroll in your own session.")
            return redirect("available_sessions")

        # Check if there’s an existing request
        existing_request = EnrollmentRequest.objects.filter(
            session=session, user=request.user
        ).first()
        if existing_request:
            if existing_request.status == "accepted":
                messages.success(
                    request,
                    f"You are already enrolled in the session '{session.topic}'.",
                )
                return redirect("available_sessions")
            elif existing_request.status == "denied":
                # Allow re-request after denial
                existing_request.status = "pending"
                existing_request.save()
                messages.success(
                    request,
                    "Your enrollment request has been re-sent to the session creator.",
                )
                return redirect("available_sessions")
            else:
                messages.warning(
                    request, "You have already requested to enroll in this session."
                )
                return redirect("available_sessions")

        # If no request exists, create a new one
        EnrollmentRequest.objects.create(session=session, user=request.user)
        messages.success(
            request, "Your enrollment request has been sent to the session creator."
        )
        return redirect("available_sessions")

    return redirect("available_sessions")

@login_required
def manage_requests(request, session_id):
    session = get_object_or_404(Session, id=session_id, creator=request.user)

    pending_requests = EnrollmentRequest.objects.filter(session=session, status='pending')

    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id, session=session)

        if action == 'approve':
            # Check if the session has remaining capacity
            if session.remaining_capacity() <= 0:
                messages.error(request, f"Cannot approve the request. The session '{session.topic}' is full.")
            else:
                enrollment_request.status = 'accepted'
                enrollment_request.save()
                session.participants.add(enrollment_request.user)
                messages.success(request, f"Request from {enrollment_request.user.profile.real_name} approved.")

        elif action == 'deny':
            enrollment_request.status = 'denied'
            enrollment_request.save()
            messages.success(request, f"Request from {enrollment_request.user.profile.real_name} denied.")

        return redirect('manage_requests', session_id=session.id)

    return render(request, 'manage_requests.html', {'pending_requests': pending_requests, 'session': session})


def creator_delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if session.creator != request.user:
        messages.error(request, "You are not authorized to delete this session.")
        return redirect('common_user_dashboard')

    session.delete()
    messages.success(request, "Session deleted successfully.")
    return redirect('common_user_dashboard')


def file_upload(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = SessionFileForm(request.POST, request.FILES)
        if form.is_valid():
            session_file = form.save(commit=False)
            session_file.session = session
            session_file.uploaded_by = request.user  # Set the uploader
            session_file.save()
            messages.success(request, "File uploaded successfully!")
            return redirect('workout_detail', session_id=session.id)
    else:
        form = SessionFileForm()
    return render(request, 'file_upload.html', {'form': form, 'session': session})


@login_required
def delete_file(request, file_id):
    file = get_object_or_404(SessionFile, id=file_id)
    if request.user == file.uploaded_by or request.user == file.session.creator:
        file.delete()
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this file.")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

