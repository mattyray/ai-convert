# test_cloudinary_cleanup.py
# Run this script to test if Celery cleanup task properly deletes files from Cloudinary

import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings.dev')
django.setup()

from imagegen.models import GeneratedImage
from imagegen.tasks import cleanup_expired_images_task, manual_cleanup_task
import cloudinary.uploader
import cloudinary.api

def test_cloudinary_connection():
    """Test if Cloudinary is properly configured and accessible"""
    print("🔍 Testing Cloudinary Connection...")
    try:
        # Try to get account details
        result = cloudinary.api.ping()
        print(f"✅ Cloudinary connected successfully!")
        print(f"   - Status: {result.get('status')}")
        
        # Get usage info
        usage = cloudinary.api.usage()
        print(f"   - Images: {usage.get('resources', 0)}")
        print(f"   - Storage used: {usage.get('storage', {}).get('usage', 0)} bytes")
        return True
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False

def list_expired_images():
    """Show current expired images in database"""
    print("\n🔍 Checking for Expired Images in Database...")
    
    now = timezone.now()
    
    # All images
    all_images = GeneratedImage.objects.all()
    print(f"📊 Total images in database: {all_images.count()}")
    
    # Expired images
    expired_images = GeneratedImage.objects.filter(
        expires_at__lt=now,
        is_expired=False,
        cleanup_attempted=False
    )
    print(f"🗑️  Images ready for cleanup: {expired_images.count()}")
    
    # Already cleaned images
    cleaned_images = GeneratedImage.objects.filter(is_expired=True)
    print(f"✅ Already cleaned images: {cleaned_images.count()}")
    
    # Show details of images ready for cleanup
    if expired_images.exists():
        print(f"\n📋 Images ready for cleanup:")
        for img in expired_images[:5]:  # Show first 5
            print(f"   - ID {img.id}: {img.match_name} (created {img.created_at})")
            print(f"     Selfie: {img.selfie.url if img.selfie else 'None'}")
            print(f"     Output: {img.output_image.url if img.output_image else 'None'}")
    
    return expired_images.count()

def force_expire_recent_image():
    """Force expire a recent image for testing (if no expired images exist)"""
    print("\n🔧 Creating Test Data...")
    
    # Find a recent image that's not expired
    recent_image = GeneratedImage.objects.filter(
        is_expired=False,
        cleanup_attempted=False
    ).first()
    
    if recent_image:
        print(f"📸 Found recent image to expire: ID {recent_image.id} - {recent_image.match_name}")
        
        # Force expire it by setting expires_at to past
        recent_image.expires_at = timezone.now() - timedelta(hours=1)
        recent_image.save()
        
        print(f"⏰ Forced expiration of image {recent_image.id}")
        return recent_image
    else:
        print("❌ No recent images found to expire")
        return None

def test_manual_cleanup():
    """Test the manual cleanup task"""
    print("\n🧹 Testing Manual Cleanup Task...")
    
    try:
        # Run the manual cleanup task synchronously
        result = manual_cleanup_task(force=False)
        print(f"✅ Manual cleanup task completed: {result}")
        return True
    except Exception as e:
        print(f"❌ Manual cleanup task failed: {e}")
        return False

def test_celery_cleanup():
    """Test the Celery cleanup task"""
    print("\n🔄 Testing Celery Cleanup Task...")
    
    try:
        # Submit the cleanup task to Celery
        task = cleanup_expired_images_task.delay()
        print(f"✅ Cleanup task submitted to Celery with ID: {task.id}")
        
        # Wait for result
        try:
            result = task.get(timeout=30)  # 30 second timeout
            print(f"✅ Celery task completed: {result}")
            return True
        except Exception as e:
            print(f"⚠️  Task submitted but result timeout: {e}")
            print(f"   Task ID: {task.id}")
            print(f"   Task State: {task.state}")
            return False
            
    except Exception as e:
        print(f"❌ Celery cleanup task failed: {e}")
        return False

def verify_cloudinary_deletion(public_ids):
    """Verify that files were actually deleted from Cloudinary"""
    print(f"\n🔍 Verifying Cloudinary Deletion for {len(public_ids)} files...")
    
    if not public_ids:
        print("📝 No public IDs to verify")
        return True
    
    deleted_count = 0
    still_exists_count = 0
    
    for public_id in public_ids:
        try:
            # Try to get the resource info
            resource = cloudinary.api.resource(public_id)
            print(f"⚠️  File still exists on Cloudinary: {public_id}")
            still_exists_count += 1
        except cloudinary.api.NotFound:
            print(f"✅ File successfully deleted from Cloudinary: {public_id}")
            deleted_count += 1
        except Exception as e:
            print(f"❓ Error checking file {public_id}: {e}")
    
    print(f"\n📊 Verification Results:")
    print(f"   - Successfully deleted: {deleted_count}")
    print(f"   - Still exists: {still_exists_count}")
    
    return still_exists_count == 0

def main():
    """Main test function"""
    print("🚀 Starting Cloudinary Cleanup Test")
    print("=" * 50)
    
    # Test 1: Cloudinary connection
    if not test_cloudinary_connection():
        print("❌ Cannot proceed without Cloudinary connection")
        return
    
    # Test 2: Check current state
    expired_count = list_expired_images()
    
    # Test 3: Create test data if needed
    if expired_count == 0:
        print("\n💡 No expired images found. Creating test data...")
        test_image = force_expire_recent_image()
        if not test_image:
            print("❌ Cannot create test data. Please add some images first.")
            return
    
    # Test 4: Get public IDs before cleanup (for verification)
    expired_images = GeneratedImage.objects.filter(
        expires_at__lt=timezone.now(),
        is_expired=False,
        cleanup_attempted=False
    )
    
    public_ids_to_check = []
    for img in expired_images:
        try:
            if img.selfie and hasattr(img.selfie, 'public_id'):
                public_ids_to_check.append(img.selfie.public_id)
            if img.output_image and hasattr(img.output_image, 'public_id'):
                public_ids_to_check.append(img.output_image.public_id)
        except:
            pass
    
    print(f"\n📝 Will verify deletion of {len(public_ids_to_check)} files")
    
    # Test 5: Run cleanup task
    print("\n" + "=" * 50)
    print("🧹 Running Cleanup Tests")
    
    # Choose test method
    print("\nWhich cleanup method would you like to test?")
    print("1. Manual cleanup (direct function call)")
    print("2. Celery cleanup (async task)")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    success = False
    if choice in ['1', '3']:
        success = test_manual_cleanup() or success
    
    if choice in ['2', '3']:
        success = test_celery_cleanup() or success
    
    if not success:
        print("❌ Cleanup tests failed")
        return
    
    # Test 6: Verify deletion from Cloudinary
    print("\n" + "=" * 50)
    input("⏳ Press Enter after cleanup completes to verify Cloudinary deletion...")
    
    verify_cloudinary_deletion(public_ids_to_check)
    
    # Test 7: Final state check
    print("\n" + "=" * 50)
    print("📊 Final State Check")
    list_expired_images()
    
    print("\n🎉 Cleanup test completed!")

if __name__ == "__main__":
    main()