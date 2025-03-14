from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.core.cache import cache
import os
from django.conf import settings

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    avatar_id = models.IntegerField(blank=True, null=True)
    
    def get_avatar(self, size=None):
        """
        Get the user's avatar with optional size optimization.
        Caches the avatar URL to reduce database queries.
        Checks for locally cached avatar images first.
        """
        # Try to get from cache first
        cache_key = f'user_avatar_{self.user.id}_{size}'
        cached_avatar = cache.get(cache_key)
        if cached_avatar:
            return cached_avatar
        
        # If not in cache, generate the URL
        avatar_url = None
        
        # Check for custom uploaded avatar
        if self.avatar and hasattr(self.avatar, 'url'):
            avatar_url = self.avatar.url
        elif self.avatar_url:
            avatar_url = self.avatar_url
        elif self.avatar_id:
            # Check if we have a locally cached version of this avatar
            if size:
                # Try to use locally cached avatar first
                avatar_filename = f"avatar_{self.avatar_id}_{size}.webp"
                avatar_path = os.path.join('img', 'avatars', avatar_filename)
                if os.path.exists(os.path.join(settings.STATIC_ROOT, avatar_path)):
                    avatar_url = f"{settings.STATIC_URL}{avatar_path}"
                else:
                    # Fall back to remote avatar service
                    avatar_url = f"https://avatar.iran.liara.run/public/{self.avatar_id}?size={size}"
            else:
                # Default to medium size if no size specified
                avatar_filename = f"avatar_{self.avatar_id}_96.webp"
                avatar_path = os.path.join('img', 'avatars', avatar_filename)
                if os.path.exists(os.path.join(settings.STATIC_ROOT, avatar_path)):
                    avatar_url = f"{settings.STATIC_URL}{avatar_path}"
                else:
                    avatar_url = f"https://avatar.iran.liara.run/public/{self.avatar_id}"
        else:
            # Default avatar
            if size:
                # Try to use locally cached default avatar
                avatar_filename = f"avatar_1_{size}.webp"
                avatar_path = os.path.join('img', 'avatars', avatar_filename)
                if os.path.exists(os.path.join(settings.STATIC_ROOT, avatar_path)):
                    avatar_url = f"{settings.STATIC_URL}{avatar_path}"
                else:
                    avatar_url = f"https://avatar.iran.liara.run/public/1?size={size}"
            else:
                avatar_url = "https://avatar.iran.liara.run/public/1"
        
        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, avatar_url, 3600)
        return avatar_url
    
    def get_avatar_small(self):
        """Get a small version of the avatar for performance"""
        return self.get_avatar(size=38)
    
    def get_avatar_medium(self):
        """Get a medium version of the avatar"""
        return self.get_avatar(size=96)
    
    def get_avatar_large(self):
        """Get a large version of the avatar for profile page"""
        return self.get_avatar(size=200)
    
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

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='primary')  # Bootstrap color class
    icon = models.CharField(max_length=50, default='fas fa-tasks')  # Font Awesome icon class
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        unique_together = ['name', 'user']  # Prevent duplicate category names per user

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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def complete(self):
        self.status = 'completed'
        self.finished = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']
