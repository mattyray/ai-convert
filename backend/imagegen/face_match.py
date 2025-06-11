# imagegen/face_match.py

import face_recognition
import numpy as np
import json
from pathlib import Path

EMBEDDINGS_PATH = Path(__file__).resolve().parent.parent / "face_data" / "embeddings.json"

def match_face(uploaded_image_path):
    try:
        # Load the uploaded selfie
        image = face_recognition.load_image_file(uploaded_image_path)
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return {"error": "No face detected in uploaded image."}
        uploaded_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
    except Exception as e:
        return {"error": f"Failed to process uploaded image: {e}"}

    # Load historical figure embeddings
    try:
        with open(EMBEDDINGS_PATH, "r") as f:
            known_embeddings = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load historical embeddings: {e}"}

    # Compare using cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    best_match = None
    best_score = -1

    for entry in known_embeddings:
        try:
            known_vector = np.array(entry["embedding"])
            score = cosine_similarity(uploaded_encoding, known_vector)
            if score > best_score:
                best_score = score
                best_match = entry["name"]
        except Exception:
            continue

    if best_match:
        return {"match_name": best_match, "score": best_score}
    return {"error": "No match found"}
