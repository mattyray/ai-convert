import face_recognition
import os
import json
import requests
import tempfile
from pathlib import Path

# Django setup
import sys
import django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings.dev')
django.setup()

BASE_DIR = Path(__file__).resolve().parent.parent
output_file = BASE_DIR / "face_data" / "embeddings.json"

# Your Cloudinary URLs mapped to clean names
HISTORICAL_FIGURES = {
    "Princess Diana": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/princess_diana_ueb9ha.png",
    "Marilyn Monroe": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/marilyn_monroe_geys6v.png",
    "Pocahontas": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/Pocahontas_kp0obo.png",
    "Napoleon": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/napolean_ukozvo.png",
    "Marie Antoinette": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921363/Marie_Antoinette_fvjtgy.png",
    "Keith Haring": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/keith_k7b5xw.png",
    "Malcolm X": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/malcolm_x_a8sluo.png",
    "Jimi Hendrix": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/jimi_hendrix_u07bvu.png",
    "Joan of Arc": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/Joan_of_Arc_vvi28l.png",
    "Leonardo da Vinci": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/leonardo_davinci_lv7gy8.png",
    "Cleopatra": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921359/cleopatra_zcslcx.png",
    "Frida Kahlo": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/frida_khalo_wq6qyl.png",
    "JFK": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/jfk_rznzq0.png",
    "James Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/james_dean_wvmc5c.png",
    "Coco Chanel": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/Coco_Chanel_mnx6s9.png",
    "Elvis Presley": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921841/elvis_heazqa.png",
    "Che Guevara": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921355/Che_Guevara_n8nmln.png",
    "Alexander the Great": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921354/alexander_the_great_mcdwpy.png",
}

def download_and_encode_face(name, url):
    """Download image from URL and extract face encoding"""
    try:
        print(f"📥 Processing {name}...")
        
        # Download image to temporary file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            # Load and process with face_recognition
            image = face_recognition.load_image_file(tmp_path)
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print(f"❌ No face found in {name}, skipping.")
                return None
            
            if len(face_locations) > 1:
                print(f"⚠️  Multiple faces found in {name}, using the first one.")
            
            # Get face encoding
            encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
            
            print(f"✅ Successfully encoded {name}")
            return {
                "name": name,
                "embedding": encoding.tolist(),
                "url": url
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error processing {name}: {str(e)}")
        return None

def main():
    print("🚀 Starting face embedding generation from Cloudinary...")
    print(f"📁 Output file: {output_file}")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    embeddings = []
    
    for name, url in HISTORICAL_FIGURES.items():
        result = download_and_encode_face(name, url)
        if result:
            embeddings.append(result)
        print()  # Add blank line for readability
    
    # Save to JSON
    try:
        with open(output_file, "w") as f:
            json.dump(embeddings, f, indent=2)
        
        print(f"🎉 SUCCESS! Saved {len(embeddings)} embeddings to {output_file}")
        print(f"📊 Successfully processed: {len(embeddings)}/{len(HISTORICAL_FIGURES)} figures")
        
        # Print summary
        print("\n📋 Generated embeddings for:")
        for embedding in embeddings:
            print(f"  • {embedding['name']}")
            
    except Exception as e:
        print(f"❌ Error saving embeddings: {str(e)}")

if __name__ == "__main__":
    main()