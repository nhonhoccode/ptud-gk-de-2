from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def optimized_img(src, alt="", width=None, height=None, css_class="", loading="lazy"):
    """
    Render an optimized image tag with lazy loading and placeholder.
    
    Usage:
    {% load image_tags %}
    {% optimized_img src="image.jpg" alt="Description" width=200 height=150 css_class="img-fluid" %}
    """
    width_attr = f'width="{width}"' if width else ''
    height_attr = f'height="{height}"' if height else ''
    class_attr = f'class="{css_class}"' if css_class else ''
    loading_attr = f'loading="{loading}"' if loading else ''
    
    # Create placeholder div
    placeholder = f'<div class="img-placeholder" style="width: {width}px; height: {height}px; border-radius: 8px;"></div>' if width and height else ''
    
    # Create image tag with onload event to hide placeholder
    img_tag = f'<img src="{src}" alt="{alt}" {width_attr} {height_attr} {class_attr} {loading_attr} onload="this.previousElementSibling && (this.previousElementSibling.style.display=\'none\')">'
    
    return mark_safe(f'{placeholder}{img_tag}')

@register.simple_tag
def avatar_img(user_profile, size=None, css_class="avatar-sm", alt="Avatar"):
    """
    Render an optimized avatar image with the appropriate size.
    
    Usage:
    {% load image_tags %}
    {% avatar_img user_profile size=38 css_class="avatar-sm" alt="User Avatar" %}
    """
    if size == 'small' or size == 38:
        src = user_profile.get_avatar_small()
        width = height = 38
    elif size == 'medium' or size == 96:
        src = user_profile.get_avatar_medium()
        width = height = 96
    elif size == 'large' or size == 200:
        src = user_profile.get_avatar_large()
        width = height = 200
    else:
        src = user_profile.get_avatar(size=size)
        width = height = size if size else 38
    
    return optimized_img(src=src, alt=alt, width=width, height=height, css_class=css_class) 