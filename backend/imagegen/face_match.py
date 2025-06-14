import face_recognition
import numpy as np
import json
from pathlib import Path

EMBEDDINGS_PATH = Path(__file__).resolve().parent.parent / "face_data" / "embeddings.json"

def match_face(uploaded_image_path):
    """
    Match an uploaded face image against historical figures
    Returns best match with confidence score
    """
    try:
        print(f"🔍 Processing uploaded image: {uploaded_image_path}")
        
        # Load the uploaded selfie
        image = face_recognition.load_image_file(uploaded_image_path)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return {"error": "No face detected in uploaded image."}
        
        if len(face_locations) > 1:
            print(f"⚠️  Multiple faces detected, using the largest one.")
        
        # Get encoding for the uploaded face
        uploaded_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
        print(f"✅ Successfully extracted face encoding from uploaded image")
        
    except Exception as e:
        print(f"❌ Error processing uploaded image: {str(e)}")
        return {"error": f"Failed to process uploaded image: {e}"}

    # Load historical figure embeddings
    try:
        if not EMBEDDINGS_PATH.exists():
            return {"error": f"Embeddings file not found at {EMBEDDINGS_PATH}. Run embed_cloudinary_faces.py first."}
            
        with open(EMBEDDINGS_PATH, "r") as f:
            known_embeddings = json.load(f)
            
        if not known_embeddings:
            return {"error": "No historical embeddings found. Run embed_cloudinary_faces.py first."}
            
        print(f"📚 Loaded {len(known_embeddings)} historical figure embeddings")
        
    except Exception as e:
        print(f"❌ Error loading embeddings: {str(e)}")
        return {"error": f"Failed to load historical embeddings: {e}"}

    # Compare using cosine similarity
    def cosine_similarity(a, b):
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    best_match = None
    best_score = -1
    all_scores = []

    print("🎯 Comparing against historical figures...")
    
    for entry in known_embeddings:
        try:
            name = entry["name"]
            known_vector = np.array(entry["embedding"])
            
            # Calculate similarity score
            score = cosine_similarity(uploaded_encoding, known_vector)
            all_scores.append((name, score))
            
            print(f"  • {name}: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_match = name
                
        except Exception as e:
            print(f"⚠️  Error processing {entry.get('name', 'unknown')}: {str(e)}")
            continue

    # Sort all scores for debugging
    all_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"\n🏆 Top 3 matches:")
    for i, (name, score) in enumerate(all_scores[:3]):
        print(f"  {i+1}. {name}: {score:.3f}")

    if best_match and best_score > 0.3:  # Minimum confidence threshold
        print(f"\n✅ Best match: {best_match} (confidence: {best_score:.3f})")
        return {
            "match_name": best_match, 
            "score": best_score,
            "all_matches": all_scores[:5]  # Return top 5 for debugging
        }
    else:
        print(f"\n❌ No confident match found (best score: {best_score:.3f})")
        return {
            "error": f"No confident match found. Best match was {best_match} with score {best_score:.3f}",
            "all_matches": all_scores[:5]
        }