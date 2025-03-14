import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
from io import BytesIO
import concurrent.futures

class Command(BaseCommand):
    help = 'Downloads and caches avatar images for better performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=92,
            help='Number of avatars to download (default: 92)',
        )
        parser.add_argument(
            '--sizes',
            type=str,
            default='38,96,200',
            help='Comma-separated list of sizes to generate (default: 38,96,200)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['webp', 'jpeg', 'png'],
            default='webp',
            help='Image format to save as (default: webp)',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Image quality for JPEG/WebP (default: 85)',
        )

    def handle(self, *args, **options):
        count = options['count']
        sizes = [int(size) for size in options['sizes'].split(',')]
        img_format = options['format']
        quality = options['quality']
        
        # Create directory for cached avatars
        cache_dir = os.path.join(settings.STATIC_ROOT, 'img', 'avatars')
        os.makedirs(cache_dir, exist_ok=True)
        
        self.stdout.write(f"Downloading and caching {count} avatars in {len(sizes)} sizes...")
        
        # Use ThreadPoolExecutor for parallel downloads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for avatar_id in range(1, count + 1):
                for size in sizes:
                    futures.append(
                        executor.submit(
                            self._download_and_cache_avatar,
                            avatar_id,
                            size,
                            cache_dir,
                            img_format,
                            quality
                        )
                    )
            
            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    result = future.result()
                    self.stdout.write(f"Progress: {i+1}/{len(futures)} - {result}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully cached {count} avatars in {len(sizes)} sizes"))
    
    def _download_and_cache_avatar(self, avatar_id, size, cache_dir, img_format, quality):
        """Download and cache a single avatar image"""
        url = f"https://avatar.iran.liara.run/public/{avatar_id}?size={size}"
        
        # Define output filename
        ext = 'webp' if img_format == 'webp' else 'jpg' if img_format == 'jpeg' else 'png'
        output_path = os.path.join(cache_dir, f"avatar_{avatar_id}_{size}.{ext}")
        
        # Skip if file already exists
        if os.path.exists(output_path):
            return f"Skipped existing avatar_{avatar_id}_{size}.{ext}"
        
        # Download the image
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to download avatar {avatar_id} (size {size})")
        
        # Process and save the image
        img = Image.open(BytesIO(response.content))
        
        if img_format == 'webp':
            img.save(output_path, 'WEBP', quality=quality)
        elif img_format == 'jpeg':
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        else:  # png
            img.save(output_path, 'PNG', optimize=True)
        
        return f"Cached avatar_{avatar_id}_{size}.{ext}" 