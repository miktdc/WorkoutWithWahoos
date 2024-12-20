# Generated by Django 4.2.16 on 2024-12-06 02:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('size_capacity', models.PositiveIntegerField()),
                ('duration_minutes', models.PositiveIntegerField()),
                ('topic', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, null=True, upload_to='session_files/')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_sessions', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='sessions_enrolled', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='session_files/')),
                ('file_title', models.CharField(blank=True, max_length=100, null=True)),
                ('file_description', models.TextField(blank=True, null=True)),
                ('file_keywords', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file_extension', models.CharField(blank=True, max_length=10, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_files', to='auth_app.session')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_name', models.CharField(default='name', help_text='Enter full name', max_length=255)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('google_account', models.EmailField(default='example@mail.com', help_text="User's Google account/email address", max_length=254)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_type', models.CharField(choices=[('common', 'Common User'), ('pma_admin', 'PMA Administrator')], default='common', max_length=20)),
                ('about_me', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')], max_length=20, null=True)),
                ('preferred_dates', models.CharField(blank=True, help_text='Enter preferred workout days (e.g., Weekdays, Weekends)', max_length=100, null=True)),
                ('preferred_times', models.CharField(blank=True, help_text='Enter preferred workout times (e.g., Mornings, Evenings)', max_length=100, null=True)),
                ('workout_likes', models.TextField(blank=True, help_text='Describe the types of workouts you enjoy', null=True)),
                ('workout_dislikes', models.TextField(blank=True, help_text='Describe the types of workouts you dislike', null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='auth_app.session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EnrollmentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollment_requests', to='auth_app.session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
