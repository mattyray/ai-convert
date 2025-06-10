import requests
import os

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

def generate_image_from_prompt(prompt):
    if not REPLICATE_API_TOKEN:
        raise ValueError("Missing Replicate API token.")

    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "version": "a9758cbf4e64239de7dbe7e1c3cfb6f25ad9a5825ebf27357c1f0c480ab0a261",  # ✅ Public SDXL v1.0
        "input": {
            "prompt": prompt
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}

    return response.json()
