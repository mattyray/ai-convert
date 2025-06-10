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
        "version": "db21e45e5b0e5cc1c6e3ee1b3e2d592e25528884f056ecb2d6c04d6df4c3f4c3",  # SDXL v1.0
        "input": {
            "prompt": prompt
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}

    prediction = response.json()
    return prediction
