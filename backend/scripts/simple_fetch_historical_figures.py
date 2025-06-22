# simple_fetch_historical_figures.py - No Django dependencies!

import cv2
import os
import json
import requests
import re
import numpy as np
from pathlib import Path

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

# Get the current directory and create output folder
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "face_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
        'Abraham Lincoln': 'Abraham Lincoln',
        'Benjamin Franklin': 'Benjamin Franklin',
        'Thomas Jefferson': 'Thomas Jefferson',
        'John Adams': 'John Adams',
        'Theodore Roosevelt': 'Theodore Roosevelt',
        'Franklin Roosevelt': 'Franklin D. Roosevelt',
        'Ronald Reagan': 'Ronald Reagan',
        'John Kennedy': 'John F. Kennedy',
        'Lyndon Johnson': 'Lyndon B. Johnson',
        'Richard Nixon': 'Richard Nixon',
        'Jimmy Carter': 'Jimmy Carter',
        'Bill Clinton': 'Bill Clinton',
        'George Bush': 'George Bush',
        'Barack Obama': 'Barack Obama',
        'Donald Trump': 'Donald Trump',
        'Joe Biden': 'Joe Biden'
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
            "face_coordinates": faces.tolist()
        }
        
    except Exception as e:
        print(f"❌ Error processing {name}: {str(e)}")
        return None

def save_results(historical_figures, face_data):
    """Save the URLs and face detection results"""
    try:
        # Save URLs for Django app
        urls_file = OUTPUT_DIR / "historical_figures_urls.json"
        with open(urls_file, "w") as f:
            json.dump(historical_figures, f, indent=2)
        
        # Save face detection results
        face_detection_file = OUTPUT_DIR / "face_detection_results.json"
        with open(face_detection_file, "w") as f:
            json.dump(face_data, f, indent=2)
        
        # Save as Python dict for easy copying to Django
        python_file = OUTPUT_DIR / "historical_figures_dict.py"
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
        
        validated_file = OUTPUT_DIR / "validated_historical_figures.py"
        with open(validated_file, "w") as f:
            f.write("# Historical figures with confirmed face detection\n")
            f.write("# These are ready to use in your Django app\n\n")
            f.write("VALIDATED_HISTORICAL_FIGURES = {\n")
            for name, url in sorted(validated_figures.items()):
                f.write(f'    "{name}": "{url}",\n')
            f.write("}\n")
        
        print(f"\n💾 Files saved in {OUTPUT_DIR}:")
        print(f"  • All URLs: historical_figures_urls.json")
        print(f"  • Face detection results: face_detection_results.json")
        print(f"  • Python dict (all): historical_figures_dict.py")
        print(f"  • Validated figures only: validated_historical_figures.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving files: {e}")
        return False

def main():
    print("🚀 Simple Cloudinary Historical Figures Fetcher")
    print("=" * 55)
    print(f"📁 Target: /historical_figures folder")
    print(f"🔍 Using: OpenCV for face detection")
    print(f"📂 Output: {OUTPUT_DIR}")
    
    # Step 1: Fetch URLs from Cloudinary
    historical_figures = fetch_historical_figures_folder()
    
    if not historical_figures:
        print("❌ No historical figures found!")
        return
    
    print(f"\n📊 Found {len(historical_figures)} figures to process")
    
    # Ask user if they want face validation or just URLs
    print(f"\n🤔 Options:")
    print(f"  1. Just get URLs (fast)")
    print(f"  2. Get URLs + validate faces (slower)")
    
    choice = input("\nChoose option [1]: ").strip()
    
    if choice == "2":
        print(f"\n🔍 Starting face validation...")
        
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
        
        # Save everything
        save_results(historical_figures, [r for r in face_data if r])
        
        print(f"\n🎉 PROCESSING COMPLETE!")
        print(f"📊 Results:")
        print(f"  • Total figures found: {len(historical_figures)}")
        print(f"  • Faces successfully detected: {successful}")
        print(f"  • No face detected: {failed}")
        print(f"  • Success rate: {(successful/len(historical_figures)*100):.1f}%")
        
    else:
        # Just save URLs without face validation
        save_results(historical_figures, [])
        
        print(f"\n🎉 URLS EXTRACTED!")
        print(f"📊 Results:")
        print(f"  • Total figures found: {len(historical_figures)}")
        print(f"  • All URLs saved successfully")
    
    print(f"\n🔄 Next Steps:")
    print(f"  1. Check the generated files in: {OUTPUT_DIR}")
    print(f"  2. Copy HISTORICAL_FIGURES dict to your Django views.py")
    print(f"  3. Replace your old 18-figure dict with the new {len(historical_figures)}-figure dict!")

if __name__ == "__main__":
    main()