# fetch_historical_figures_opencv.py - OpenCV version (much simpler!)

import cv2
import os
import json
import requests
import tempfile
from pathlib import Path
import re
import numpy as np

# Django setup
import sys
import django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings.dev')
django.setup()

# Cloudinary setup
try:
    import cloudinary
    import cloudinary.api
    
    # Configure Cloudinary with your credentials
    cloudinary.config(
        cloud_name="dddye9wli",
        api_key="681124125678741",
        api_secret="sWHFXOtMDFWIdrSilA-kwNkTBn4",
        secure=True
    )
except ImportError:
    print("❌ Cloudinary not installed. Run: pip install cloudinary")
    exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent

def clean_filename_to_name(filename):
    """Convert filename to clean display name"""
    # Remove cloudinary suffix (random characters at the end)
    name = re.sub(r'_[a-z0-9]{6}$', '', filename)
    
    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').title()
    
    # Handle special cases and common corrections
    name_corrections = {
        'Jfk': 'JFK',
        'Mlk': 'Martin Luther King Jr.',
        'Fdr': 'Franklin D. Roosevelt',
        'Jrr Tolkien': 'J.R.R. Tolkien',
        'Leonardo Davinci': 'Leonardo da Vinci',
        'Da Vinci': 'Leonardo da Vinci',
        'Van Gogh': 'Vincent van Gogh',
        'Vincent Van Gogh': 'Vincent van Gogh',
        'Marie Antoinette': 'Marie Antoinette',
        'Napoleon Bonaparte': 'Napoleon',
        'Alexander Great': 'Alexander the Great',
        'Alexander The Great': 'Alexander the Great',
        'Joan Arc': 'Joan of Arc',
        'Joan Of Arc': 'Joan of Arc',
        'Keith Haring': 'Keith Haring',
        'Andy Warhol': 'Andy Warhol',
        'Pablo Picasso': 'Pablo Picasso',
        'Albert Einstein': 'Albert Einstein',
        'Isaac Newton': 'Isaac Newton',
        'Nikola Tesla': 'Nikola Tesla',
        'Thomas Edison': 'Thomas Edison',
        'Steve Jobs': 'Steve Jobs',
        'Bill Gates': 'Bill Gates',
        'Elon Musk': 'Elon Musk',
        'Mark Zuckerberg': 'Mark Zuckerberg',
        'Mahatma Gandhi': 'Mahatma Gandhi',
        'Martin Luther King': 'Martin Luther King Jr.',
        'Winston Churchill': 'Winston Churchill',
        'Theodore Roosevelt': 'Theodore Roosevelt',
        'George Washington': 'George Washington',
        'Abraham Lincoln': 'Abraham Lincoln'
    }
    
    return name_corrections.get(name, name)

def fetch_historical_figures_folder():
    """Fetch all images from the /historical_figures folder"""
    try:
        print("🌤️ Fetching from /historical_figures folder...")
        
        # Search for resources in the specific folder
        response = cloudinary.api.resources(
            resource_type="image",
            type="upload",
            prefix="historical_figures/",
            max_results=500
        )
        
        resources = response['resources']
        print(f"✅ Found {len(resources)} images in /historical_figures folder")
        
        historical_figures = {}
        
        for resource in resources:
            try:
                public_id = resource['public_id']
                
                # Remove the folder prefix: "historical_figures/einstein" -> "einstein"
                filename = public_id.replace('historical_figures/', '')
                
                if not filename:
                    continue
                
                # Clean up the name
                clean_name = clean_filename_to_name(filename)
                url = resource['secure_url']
                
                historical_figures[clean_name] = url
                print(f"📸 {clean_name}")
                
            except Exception as e:
                print(f"⚠️ Error processing {resource.get('public_id', 'unknown')}: {e}")
                continue
        
        print(f"\n🎭 Successfully mapped {len(historical_figures)} historical figures")
        return historical_figures
        
    except Exception as e:
        print(f"❌ Error fetching from Cloudinary folder: {e}")
        return {}

def detect_face_opencv(name, url):
    """Download image and detect faces using OpenCV"""
    try:
        print(f"📥 Processing {name}...")
        
        # Download image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"❌ Could not decode image for {name}")
            return None
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load the face detection classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            print(f"❌ No face detected in {name}")
            return None
        
        if len(faces) > 1:
            print(f"⚠️  Multiple faces detected in {name} ({len(faces)} faces)")
        
        print(f"✅ Face detected in {name}")
        return {
            "name": name,
            "url": url,
            "faces_detected": len(faces),
            "face_coordinates": faces.tolist()  # Store face locations for future use
        }
        
    except Exception as e:
        print(f"❌ Error processing {name}: {str(e)}")
        return None

def save_results(historical_figures, face_data):
    """Save the URLs and face detection results"""
    try:
        # Create output directory
        face_data_dir = BASE_DIR / "face_data"
        face_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save URLs for Django app
        urls_file = face_data_dir / "historical_figures_urls.json"
        with open(urls_file, "w") as f:
            json.dump(historical_figures, f, indent=2)
        
        # Save face detection results
        face_detection_file = face_data_dir / "face_detection_results.json"
        with open(face_detection_file, "w") as f:
            json.dump(face_data, f, indent=2)
        
        # Save as Python dict for easy copying to Django
        python_file = face_data_dir / "historical_figures_dict.py"
        with open(python_file, "w") as f:
            f.write("# Generated from /historical_figures folder using OpenCV\n")
            f.write("# Copy this dict to your Django views.py\n\n")
            f.write("HISTORICAL_FIGURES = {\n")
            for name, url in sorted(historical_figures.items()):
                f.write(f'    "{name}": "{url}",\n')
            f.write("}\n")
        
        # Save only the successfully detected faces for immediate use
        validated_figures = {}
        for result in face_data:
            if result:  # Only include figures where faces were detected
                validated_figures[result['name']] = historical_figures[result['name']]
        
        validated_file = face_data_dir / "validated_historical_figures.py"
        with open(validated_file, "w") as f:
            f.write("# Historical figures with confirmed face detection\n")
            f.write("# These are ready to use in your Django app\n\n")
            f.write("VALIDATED_HISTORICAL_FIGURES = {\n")
            for name, url in sorted(validated_figures.items()):
                f.write(f'    "{name}": "{url}",\n')
            f.write("}\n")
        
        print(f"\n💾 Files saved:")
        print(f"  • All URLs: {urls_file}")
        print(f"  • Face detection results: {face_detection_file}")
        print(f"  • Python dict (all): {python_file}")
        print(f"  • Validated figures only: {validated_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving files: {e}")
        return False

def main():
    print("🚀 OpenCV Version - Cloudinary Historical Figures Fetcher")
    print("=" * 65)
    print(f"📁 Target: /historical_figures folder")
    print(f"🔍 Using: OpenCV for face detection")
    
    # Step 1: Fetch URLs from Cloudinary
    historical_figures = fetch_historical_figures_folder()
    
    if not historical_figures:
        print("❌ No historical figures found!")
        return
    
    print(f"\n📊 Found {len(historical_figures)} figures to process")
    
    # Step 2: Validate faces using OpenCV
    face_data = []
    successful = 0
    failed = 0
    
    for i, (name, url) in enumerate(historical_figures.items(), 1):
        print(f"\n[{i}/{len(historical_figures)}]", end=" ")
        result = detect_face_opencv(name, url)
        face_data.append(result)
        
        if result:
            successful += 1
        else:
            failed += 1
    
    # Step 3: Save everything
    save_results(historical_figures, [r for r in face_data if r])  # Only save successful detections
    
    print(f"\n🎉 PROCESSING COMPLETE!")
    print(f"📊 Results:")
    print(f"  • Total figures found: {len(historical_figures)}")
    print(f"  • Faces successfully detected: {successful}")
    print(f"  • No face detected: {failed}")
    print(f"  • Success rate: {(successful/len(historical_figures)*100):.1f}%")
    
    # Show successful detections
    print(f"\n✅ Figures with faces detected:")
    for result in face_data:
        if result:
            faces_text = f"({result['faces_detected']} face{'s' if result['faces_detected'] > 1 else ''})"
            print(f"  ✅ {result['name']} {faces_text}")
    
    # Show failed detections
    if failed > 0:
        print(f"\n❌ Figures where no face was detected:")
        successful_names = {r['name'] for r in face_data if r}
        for name in historical_figures:
            if name not in successful_names:
                print(f"  ❌ {name}")
    
    print(f"\n🔄 Next Steps:")
    print(f"  1. Use face_data/validated_historical_figures.py for immediate deployment")
    print(f"  2. Copy the VALIDATED_HISTORICAL_FIGURES dict to your Django views.py")
    print(f"  3. This gives you {successful} confirmed face-detectable figures!")
    print(f"  4. For full face matching, you can install face_recognition later")
    
    print(f"\n💡 Note: This version detects faces but doesn't create embeddings.")
    print(f"   For face matching, you'll still need the face_recognition library eventually.")

if __name__ == "__main__":
    main()