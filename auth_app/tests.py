from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Profile, Session
from datetime import datetime, time, timedelta

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.profile = Profile.objects.create(user=self.user, user_type='common')

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.user_type, 'common')

class SessionModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='creator', password='12345')
        future_time = (datetime.now() + timedelta(hours=1)).time()
        self.session = Session.objects.create(
            creator=self.user,
            location="Gym",
            title="Title",
            description="Description",
            date=datetime.now().date(),
            time=future_time,
            size_capacity=5,
            duration_minutes=60,
            topic="Morning Workout",
        )

    def test_session_creation(self):
        self.assertEqual(self.session.creator.username, 'creator')
        self.assertEqual(self.session.location, "Gym")
        self.assertEqual(self.session.remaining_capacity(), 5)

class HomeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        Profile.objects.create(user=self.user, user_type='common')
    
    
    def test_home_redirect_authenticated_common_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('common_user_dashboard'))

    def test_home_anonymous_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue as Guest")

class CreateSessionViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='creator', password='12345')
        Profile.objects.create(user=self.user, user_type='common')

    def test_create_session(self):
        self.client.login(username='creator', password='12345')
        future_time = (datetime.now() + timedelta(hours=13)).time()
        response = self.client.post(
            reverse("create_session"),
            {
                "title": "Title",
                "location": "Gym",
                "description": "Description",
                "date": datetime.now().date(),
                "time": future_time,
                "size_capacity": 5,
                "duration_minutes": 60,
                "topic": "Yoga",
            },
        )
        self.assertRedirects(response, reverse('common_user_dashboard'))
        self.assertTrue(Session.objects.filter(topic='Yoga').exists())
