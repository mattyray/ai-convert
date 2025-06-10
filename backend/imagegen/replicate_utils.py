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
        "version": "db21e45a0968b68a30f86cd1df30878e61d33c6b5519595c13bafd1b5c48c6b1",  # ✅ Valid SDXL v1.0
        "input": {
            "prompt": prompt
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}

    return response.json()
