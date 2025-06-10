import face_recognition
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
input_dir = BASE_DIR / "imagegen" / "historical_faces"
output_file = BASE_DIR / "face_data" / "embeddings.json"

embeddings = []

for filename in os.listdir(input_dir):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        image_path = input_dir / filename
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            print(f"No face found in {filename}, skipping.")
            continue
        encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
        embeddings.append({
            "name": filename.rsplit(".", 1)[0],
            "embedding": encoding.tolist(),
        })

# Save to JSON
with open(output_file, "w") as f:
    json.dump(embeddings, f)

print(f"✅ Saved {len(embeddings)} embeddings to {output_file}")
