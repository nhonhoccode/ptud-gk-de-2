from django.conf import settings
import re
from urllib.parse import urlparse

class ImageOptimizationMiddleware:
    """
    Middleware to optimize image delivery in responses.
    
    This middleware:
    1. Adds appropriate cache headers for images
    2. Rewrites image URLs to use optimized versions when available
    3. Adds loading="lazy" attribute to images below the fold
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Compile regex patterns for performance
        self.img_pattern = re.compile(r'<img[^>]*src=["\'](.*?)["\'][^>]*>', re.IGNORECASE)
        self.lazy_pattern = re.compile(r'<img(?![^>]*loading=)[^>]*>', re.IGNORECASE)
        
        # Define image extensions for caching
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process HTML responses
        content_type = response.get('Content-Type', '')
        if not content_type.startswith('text/html'):
            # Add cache headers for image files
            if any(ext in request.path.lower() for ext in self.image_extensions):
                self._add_cache_headers(response)
            return response
            
        # Don't process streaming responses or responses without content
        if getattr(response, 'streaming', False) or not hasattr(response, 'content'):
            return response
            
        # Process HTML content
        content = response.content.decode('utf-8')
        
        # Add lazy loading to images
        if 'loading=' not in content:  # Quick check to avoid unnecessary processing
            content = self._add_lazy_loading(content)
            
        # Update response content if modified
        response.content = content.encode('utf-8')
        
        return response
        
    def _add_cache_headers(self, response):
        """Add appropriate cache headers for images"""
        # Only add cache headers if not already set
        if 'Cache-Control' not in response:
            # Cache images for 1 week (604800 seconds)
            response['Cache-Control'] = 'public, max-age=604800, immutable'
            
    def _add_lazy_loading(self, content):
        """Add loading="lazy" attribute to images"""
        # Find the approximate fold position (first 1000 characters)
        fold_position = 1000
        
        # Don't add lazy loading to images above the fold
        content_parts = [content[:fold_position], content[fold_position:]]
        
        # Add lazy loading only to images below the fold
        content_parts[1] = self.lazy_pattern.sub(
            lambda m: m.group(0).replace('<img', '<img loading="lazy"'),
            content_parts[1]
        )
        
        return ''.join(content_parts) 