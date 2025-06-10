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
        "version": "ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969",  # OpenJourney v4
        "input": {
            "prompt": prompt,
            "width": 512,
            "height": 512,
            "num_outputs": 1
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}

    prediction = response.json()
    return prediction
