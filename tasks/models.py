from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    
    def get_avatar(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        elif self.avatar_url:
            return self.avatar_url
        elif self.avatar_id:
            return f"https://avatar.iran.liara.run/public/{self.avatar_id}"
        else:
            # Default avatar from the service
            return "https://avatar.iran.liara.run/public/1"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new UserProfile for the user with a random avatar
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'avatar_id': random.randint(1, 92)}
        )

# Signal to save UserProfile when User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'avatar_id': random.randint(1, 92)}
        )

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def complete(self):
        self.status = 'completed'
        self.finished = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']
