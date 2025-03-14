from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import UserProfile
import random

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users that do not have one'

    def handle(self, *args, **options):
        users_without_profile = []
        created_count = 0
        
        # Find users without profiles and create them
        for user in User.objects.all():
            try:
                # Try to access the profile
                user.userprofile
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'avatar_id': random.randint(1, 92)}
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
        
        if created_count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} user profiles')) 