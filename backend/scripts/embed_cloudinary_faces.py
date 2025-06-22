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
# Generated from Cloudinary root level
# Copy this dict to your Django views.py

HISTORICAL_FIGURES = {
    "Abraham Lincoln": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608917/Abraham_Lincoln_o5kbjh.png",
    "Alexander the Great": "https://res.cloudinary.com/dddye9wli/image/upload/v1749854959/alexander_the_great_j5icxu.png",
    "Andy Warhol": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608920/Andy_Warhol_p6lq5q.png",
    "Anne Frank": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608918/Anne_Frank_flivyh.png",
    "Audrey Hepburn": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608919/Audrey_Hepburn_rtw37d.png",
    "Benjamin Franklin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608919/Benjamin_Franklin_lh9vdd.png",
    "Beyonce": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Beyonce_ry9nep.png",
    "Bill Clinton": "https://res.cloudinary.com/dddye9wli/image/upload/v1750374687/Bill_Clinton_za0jbh.png",
    "Billie Holiday": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Billie_Holiday_zpq9ks.png",
    "Bob Dylan": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608922/Bob_Dylan_soy4se.png",
    "Brittany Spears": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608923/Brittany_Spears_kdhdh3.png",
    "Che Guevara": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921229/Che_Guevara_kkrtcr.png",
    "Cher": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/cher_hhhcbg.png",
    "Christopher Columbus": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Christopher_columbus_oewf7p.png",
    "Cleopatra": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921359/cleopatra_zcslcx.png",
    "Coco Chanel": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/Coco_Chanel_dw4bcq.png",
    "Danny Devito": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Danny_Devito_ajkoal.png",
    "Donald Trump": "https://res.cloudinary.com/dddye9wli/image/upload/v1750550608/Donald_Trump_yqggmn.png",
    "Elon Musk": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608926/Elon_Musk_c3ii8i.png",
    "Elvis": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921841/elvis_heazqa.png",
    "Elvisnotsinging": "https://res.cloudinary.com/dddye9wli/image/upload/v1749857225/elvisnotsinging_twnnta.png",
    "Frida Khalo": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/frida_khalo_gzibma.png",
    "Genghis Khan": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608927/Genghis_Khan_ewsfvk.png",
    "Hernan Cortes": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Hernan_Cortes_lfonsp.png",
    "JFK": "https://res.cloudinary.com/dddye9wli/image/upload/v1749856600/jfk_npw3lg.png",
    "James Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921232/james_dean_bhaaum.png",
    "Janis Joplin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Janis_Joplin_cl5pi8.png",
    "Jimi Hendrix": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921237/jimi_hendrix_fm56df.png",
    "Joan of Arc": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921237/Joan_of_Arc_bysrio.png",
    "John Lennon": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/John_Lennon_lod1zc.png",
    "Josephine Baker": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608930/Josephine_Baker_spiswe.png",
    "Judy Garland": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608931/Judy_Garland_bfbss2.png",
    "Julius Cesear": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608931/Julius_Cesear_wampoh.png",
    "Karl Marx": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608934/Karl_Marx_hlmk0s.png",
    "Keith": "https://res.cloudinary.com/dddye9wli/image/upload/v1749856455/keith_o6fgff.png",
    "King Henry Vii": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/King_Henry_VII_wpclza.png",
    "Kylie Jenner": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Kylie_Jenner_vwasob.png",
    "Leonardo da Vinci": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921238/leonardo_davinci_wpggcn.png",
    "Lucille Ball": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Lucille_Ball_a5zjih.png",
    "Madonna": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Madonna_qlszs5.png",
    "Malcolm X": "https://res.cloudinary.com/dddye9wli/image/upload/v1749854991/malcolm_x_kwlnil.png",
    "Mao Zedong": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608935/Mao_zedong_lpvr7v.png",
    "Marco Polo": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608937/Marco_Polo_mah3wb.png",
    "Marie Antoinette": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921242/Marie_Antoinette_f6ndp6.png",
    "Marilyn Manson": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608936/Marilyn_Manson_zwe6f7.png",
    "Marilyn Monroe": "https://res.cloudinary.com/dddye9wli/image/upload/v1749858269/marilyn_monroe_zhaxku.png",
    "Mark Zuckerberg": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608936/Mark_Zuckerberg_tvctxl.png",
    "Mona Lisa": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608976/Mona_Lisa_cwnwdk.png",
    "Napolean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749742732/napolean_azenei.png",
    "Oprah Winfrey": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608983/oprah_winfrey_c24nib.png",
    "Paula Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608987/Paula_Dean_lmyabz.png",
    "Pocahontas": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921243/Pocahontas_ys39zg.png",
    "Princess Diana": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921243/princess_diana_xcvc2a.png",
    "Queen Elizabeth I": "https://res.cloudinary.com/dddye9wli/image/upload/v1750608993/Queen_Elizabeth_I_ct6ku4.png",
    "Queen Victoria": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609003/Queen_Victoria_jq4b9h.png",
    "Ragnar Lothbrok": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609005/Ragnar_Lothbrok_mwwutr.png",
    "Rasputin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Rasputin_kcpdi4.png",
    "Richard Nixon": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Richard_Nixon_qfgsnz.png",
    "Sigourney Weaver": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609007/Sigourney_Weaver_vn70qg.png",
    "Steve Jobs": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609007/Steve_Jobs_gluiyu.png",
    "Susan B Anthony": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609008/Susan_B_Anthony_pgeomw.png",
    "Vladimir Putin": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609009/Vladimir_Putin_u3k1st.png",
    "Xi Jinping": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609010/Xi_Jinping_tiyqx2.png",
    "Yoko Ono": "https://res.cloudinary.com/dddye9wli/image/upload/v1750609010/Yoco_ono_ttzyo1.png",
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
    print(f"📊 Total figures to process: {len(HISTORICAL_FIGURES)}")
    
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