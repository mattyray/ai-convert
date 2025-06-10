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
        # ✅ Use the public 'Latest' SDXL version ID
        "version": "7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        "input": {
            "prompt": prompt
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}
    return response.json()
