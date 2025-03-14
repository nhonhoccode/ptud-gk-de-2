from django.conf import settings

def image_optimization(request):
    """
    Context processor to provide image optimization functions to all templates.
    """
    return {
        'get_optimized_avatar': lambda user_profile, size=None: user_profile.get_avatar(size=size),
        'get_avatar_small': lambda user_profile: user_profile.get_avatar_small(),
        'get_avatar_medium': lambda user_profile: user_profile.get_avatar_medium(),
        'get_avatar_large': lambda user_profile: user_profile.get_avatar_large(),
        'MEDIA_URL': settings.MEDIA_URL,
    } 