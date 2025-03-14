import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
import io

class Command(BaseCommand):
    help = 'Optimizes images in the media directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='JPEG/WebP quality (1-100)',
        )
        parser.add_argument(
            '--convert',
            type=str,
            choices=['webp', 'jpeg', 'none'],
            default='webp',
            help='Convert images to this format',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Maximum width for images',
        )
        parser.add_argument(
            '--max-height',
            type=int,
            default=1080,
            help='Maximum height for images',
        )

    def handle(self, *args, **options):
        quality = options['quality']
        convert_to = options['convert']
        max_width = options['max_width']
        max_height = options['max_height']
        
        # Get all image files in media directory
        media_root = settings.MEDIA_ROOT
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(media_root, '**', ext), recursive=True))
        
        self.stdout.write(f"Found {len(image_files)} images to optimize")
        
        # Process each image
        for image_path in image_files:
            try:
                # Get relative path for output
                rel_path = os.path.relpath(image_path, media_root)
                
                # Open and optimize image
                with Image.open(image_path) as img:
                    # Resize if needed
                    if img.width > max_width or img.height > max_height:
                        img.thumbnail((max_width, max_height), Image.LANCZOS)
                    
                    # Convert if needed
                    if convert_to != 'none':
                        if convert_to == 'webp':
                            output_path = os.path.splitext(image_path)[0] + '.webp'
                            img.save(output_path, 'WEBP', quality=quality)
                            # Remove original if conversion successful
                            if os.path.exists(output_path):
                                os.remove(image_path)
                                self.stdout.write(f"Converted and optimized: {rel_path} -> {os.path.relpath(output_path, media_root)}")
                        elif convert_to == 'jpeg':
                            # Convert to RGB if needed (for PNG with transparency)
                            if img.mode in ('RGBA', 'LA'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                                img = background
                            
                            output_path = os.path.splitext(image_path)[0] + '.jpg'
                            img.save(output_path, 'JPEG', quality=quality, optimize=True)
                            # Remove original if conversion successful
                            if os.path.exists(output_path):
                                os.remove(image_path)
                                self.stdout.write(f"Converted and optimized: {rel_path} -> {os.path.relpath(output_path, media_root)}")
                    else:
                        # Just optimize in place
                        format_name = img.format
                        if format_name == 'JPEG':
                            img.save(image_path, 'JPEG', quality=quality, optimize=True)
                        elif format_name == 'PNG':
                            img.save(image_path, 'PNG', optimize=True)
                        elif format_name == 'GIF':
                            img.save(image_path, 'GIF', optimize=True)
                        self.stdout.write(f"Optimized: {rel_path}")
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {image_path}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('Image optimization completed')) 