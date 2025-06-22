# root_level_fetch_historical_figures.py - Images are at root level, not in subfolders!

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
        'Yoco Ono': 'Yoko Ono',  # Fix the typo in the filename
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
        'Xi Jinping': 'Xi Jinping',
        'Vladimir Putin': 'Vladimir Putin',
        'Donald Trump': 'Donald Trump',
        'Joe Biden': 'Joe Biden',
        'Barack Obama': 'Barack Obama',
        'John Lennon': 'John Lennon',
        'Paul Mccartney': 'Paul McCartney',
        'George Harrison': 'George Harrison',
        'Ringo Starr': 'Ringo Starr',
        'Mao Zedong': 'Mao Zedong',
        'Joseph Stalin': 'Joseph Stalin',
        'Adolf Hitler': 'Adolf Hitler',
        'Benito Mussolini': 'Benito Mussolini',
        'Franklin Roosevelt': 'Franklin D. Roosevelt',
        'Theodore Roosevelt': 'Theodore Roosevelt',
        'Ronald Reagan': 'Ronald Reagan',
        'Bill Clinton': 'Bill Clinton',
        'George Bush': 'George Bush',
        'Jimmy Carter': 'Jimmy Carter',
        'Lyndon Johnson': 'Lyndon B. Johnson',
        'Richard Nixon': 'Richard Nixon'
    }
    
    return name_corrections.get(name, name)

def is_historical_figure(public_id):
    """
    Determine if a public_id looks like a historical figure
    Based on common patterns and names
    """
    filename = public_id.lower()
    
    # Skip obviously non-historical files
    skip_patterns = [
        'selfie', 'fused', 'result', 'generated', 'temp', 'test',
        'upload', 'sample', 'demo', 'placeholder', 'avatar',
        'profile', 'user', 'photo', 'pic', 'img'
    ]
    
    if any(pattern in filename for pattern in skip_patterns):
        return False
    
    # Look for historical figure patterns
    historical_patterns = [
        # World Leaders & Politicians
        'lincoln', 'washington', 'jefferson', 'franklin', 'roosevelt', 'kennedy', 'jfk',
        'reagan', 'clinton', 'obama', 'trump', 'biden', 'carter', 'nixon', 'johnson',
        'churchill', 'gandhi', 'mandela', 'putin', 'xi_jinping', 'mao', 'stalin',
        'hitler', 'mussolini', 'napoleon', 'caesar', 'alexander', 'cleopatra',
        
        # Scientists & Inventors
        'einstein', 'newton', 'tesla', 'edison', 'darwin', 'galileo', 'curie',
        'hawking', 'jobs', 'gates', 'musk', 'zuckerberg', 'bezos',
        
        # Artists & Musicians
        'picasso', 'davinci', 'van_gogh', 'monet', 'warhol', 'kahlo', 'haring',
        'mozart', 'beethoven', 'bach', 'elvis', 'lennon', 'mccartney', 'hendrix',
        'dylan', 'cash', 'presley', 'monroe', 'dean', 'yoko', 'ono',
        
        # Writers & Philosophers
        'shakespeare', 'dickens', 'twain', 'hemingway', 'orwell', 'tolkien',
        'plato', 'aristotle', 'socrates', 'nietzsche', 'kant',
        
        # Religious & Cultural Figures
        'jesus', 'buddha', 'muhammad', 'confucius', 'dalai_lama',
        'mother_teresa', 'joan', 'arc', 'marie_antoinette',
        
        # Civil Rights & Social Leaders
        'mlk', 'malcolm', 'che', 'guevara', 'king', 'luther', 'parks',
        'douglass', 'tubman', 'anthony'
    ]
    
    # Check if any historical pattern matches
    for pattern in historical_patterns:
        if pattern in filename:
            return True
    
    # Also check for single names that might be historical
    # If it's a simple name pattern (no numbers, no technical terms)
    if re.match(r'^[a-z_]+_[a-z0-9]{6}$', filename):  # name_cloudinaryid pattern
        name_part = filename.split('_')[0]
        if len(name_part) > 3:  # Reasonable name length
            return True
    
    return False

def fetch_all_images_and_filter():
    """Get all images and filter for historical figures"""
    
    print("🌤️ Fetching ALL images from Cloudinary root...")
    
    try:
        all_resources = []
        next_cursor = None
        
        while True:
            params = {
                "resource_type": "image",
                "type": "upload",
                "max_results": 500
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            
            response = cloudinary.api.resources(**params)
            batch = response.get('resources', [])
            all_resources.extend(batch)
            
            print(f"📄 Fetched {len(all_resources)} total images...")
            
            if 'next_cursor' in response:
                next_cursor = response['next_cursor']
            else:
                break
        
        print(f"✅ Found {len(all_resources)} total images in account")
        
        # Filter for historical figures
        historical_resources = []
        
        print(f"\n🎭 Filtering for historical figures...")
        for resource in all_resources:
            public_id = resource['public_id']
            
            if is_historical_figure(public_id):
                historical_resources.append(resource)
                print(f"✅ Historical figure: {public_id}")
        
        print(f"\n🎯 Found {len(historical_resources)} historical figures!")
        return historical_resources
        
    except Exception as e:
        print(f"❌ Error fetching images: {e}")
        return []

def organize_historical_figures(resources):
    """Process the resources and create clean name mappings"""
    historical_figures = {}
    
    print(f"\n🎭 Processing {len(resources)} historical figures...")
    
    for resource in resources:
        try:
            public_id = resource['public_id']
            
            # Clean up the name
            clean_name = clean_filename_to_name(public_id)
            url = resource['secure_url']
            
            historical_figures[clean_name] = url
            print(f"📸 {public_id} → {clean_name}")
            
        except Exception as e:
            print(f"⚠️ Error processing {resource.get('public_id', 'unknown')}: {e}")
            continue
    
    return historical_figures

def save_results(historical_figures):
    """Save the URLs in multiple formats"""
    try:
        # Save URLs as JSON
        urls_file = OUTPUT_DIR / "historical_figures_urls.json"
        with open(urls_file, "w") as f:
            json.dump(historical_figures, f, indent=2)
        
        # Save as Python dict for Django
        python_file = OUTPUT_DIR / "historical_figures_dict.py"
        with open(python_file, "w") as f:
            f.write("# Generated from Cloudinary root level\n")
            f.write("# Copy this dict to your Django views.py\n")
            f.write("# Replace your old HISTORICAL_FIGURES dictionary with this:\n\n")
            f.write("HISTORICAL_FIGURES = {\n")
            for name, url in sorted(historical_figures.items()):
                f.write(f'    "{name}": "{url}",\n')
            f.write("}\n")
        
        print(f"\n💾 Files saved in {OUTPUT_DIR}:")
        print(f"  • JSON format: historical_figures_urls.json")
        print(f"  • Python dict: historical_figures_dict.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving files: {e}")
        return False

def main():
    print("🚀 Root Level Historical Figures Fetcher")
    print("=" * 50)
    print(f"📁 Target: Root level images (not in subfolders)")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"🔍 Strategy: Get all images, filter for historical figures")
    
    # Step 1: Fetch all images and filter
    resources = fetch_all_images_and_filter()
    
    if not resources:
        print("❌ No historical figures found!")
        print("💡 The images might have different naming patterns")
        return
    
    # Step 2: Process and organize the figures
    historical_figures = organize_historical_figures(resources)
    
    if not historical_figures:
        print("❌ No historical figures could be processed!")
        return
    
    # Step 3: Save the results
    save_results(historical_figures)
    
    print(f"\n🎉 SUCCESS!")
    print(f"📊 Results:")
    print(f"  • Historical figures found: {len(historical_figures)}")
    print(f"  • All URLs extracted and organized")
    
    print(f"\n🔄 Next Steps:")
    print(f"  1. Open: {OUTPUT_DIR}/historical_figures_dict.py")
    print(f"  2. Copy the HISTORICAL_FIGURES dictionary")
    print(f"  3. Replace your old 18-figure dict in Django views.py")
    print(f"  4. Deploy with {len(historical_figures)} historical figures! 🚀")
    
    # Show a preview
    print(f"\n📋 Preview of figures found:")
    for i, name in enumerate(sorted(historical_figures.keys())[:15]):
        print(f"  {i+1}. {name}")
    if len(historical_figures) > 15:
        print(f"  ... and {len(historical_figures) - 15} more!")

if __name__ == "__main__":
    main()