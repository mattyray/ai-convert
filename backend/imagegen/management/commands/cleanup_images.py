from django.core.management.base import BaseCommand
from django.utils import timezone
from imagegen.models import GeneratedImage
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired images from Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup all images regardless of expiration',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--image-id',
            type=int,
            help='Clean up specific image by ID',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧹 Starting image cleanup...')
        )

        if options['image_id']:
            # Clean up specific image
            try:
                image = GeneratedImage.objects.get(id=options['image_id'])
                self.stdout.write(f"🎯 Cleaning up specific image: {image.id}")
                
                if options['test']:
                    self.stdout.write(f"TEST MODE: Would delete image {image.id}")
                    if image.selfie:
                        public_id = image.get_image_public_id(image.selfie)
                        self.stdout.write(f"  - Selfie public_id: {public_id}")
                    if image.output_image:
                        public_id = image.get_image_public_id(image.output_image)
                        self.stdout.write(f"  - Output public_id: {public_id}")
                else:
                    deleted_files = image.expire_and_cleanup()
                    self.stdout.write(f"✅ Deleted: {deleted_files}")
                
                return
                
            except GeneratedImage.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Image with ID {options["image_id"]} not found')
                )
                return

        # Regular cleanup
        now = timezone.now()
        
        if options['force']:
            # Force cleanup all images
            images_to_cleanup = GeneratedImage.objects.filter(
                cleanup_attempted=False
            )
            self.stdout.write(f"🔥 FORCE MODE: Cleaning up ALL {images_to_cleanup.count()} images")
        else:
            # Normal cleanup - only expired images
            images_to_cleanup = GeneratedImage.objects.filter(
                expires_at__lt=now,
                is_expired=False,
                cleanup_attempted=False
            )
            self.stdout.write(f"📅 Normal cleanup: {images_to_cleanup.count()} expired images")

        if not images_to_cleanup.exists():
            self.stdout.write(
                self.style.WARNING('📭 No images to clean up')
            )
            return

        # Show details of images to be cleaned
        self.stdout.write(f"\n📋 Images to clean up:")
        for img in images_to_cleanup[:10]:  # Show first 10
            age_hours = (now - img.created_at).total_seconds() / 3600
            self.stdout.write(f"  - ID {img.id}: {img.match_name} (age: {age_hours:.1f}h)")

        if images_to_cleanup.count() > 10:
            self.stdout.write(f"  ... and {images_to_cleanup.count() - 10} more")

        if options['test']:
            self.stdout.write(
                self.style.WARNING('\n🧪 TEST MODE: No actual deletion performed')
            )
            return

        # Confirm before proceeding
        if not options['force']:
            confirm = input(f"\n❓ Proceed with cleanup of {images_to_cleanup.count()} images? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write('❌ Cleanup cancelled')
                return

        # Perform cleanup
        deleted_count = 0
        failed_count = 0

        for img in images_to_cleanup:
            try:
                self.stdout.write(f"🧹 Cleaning up image {img.id}...")
                deleted_files = img.expire_and_cleanup()
                deleted_count += 1
                self.stdout.write(f"  ✅ Success: {deleted_files}")
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Failed: {e}")
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Cleanup complete!\n'
                f'  ✅ Deleted: {deleted_count}\n'
                f'  ❌ Failed: {failed_count}'
            )
        )

        # Show remaining images
        remaining = GeneratedImage.objects.filter(is_expired=False).count()
        self.stdout.write(f"📊 Remaining active images: {remaining}")