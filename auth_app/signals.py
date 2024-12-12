from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import Profile
from django.utils.timezone import now

@receiver(post_save, sender=SocialAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance.user, 
                               user_type='common', 
                               real_name=f"{instance.user.first_name} {instance.user.last_name}".strip(), 
                               google_account=instance.user.email,
                               date_joined=now(),)