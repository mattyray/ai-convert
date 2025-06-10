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
        "version": "e67e7f63c8a4160992fce841a55bde2d9ce5d6c799aa5f076eb23ba2275d56db",
        "input": {
            "prompt": prompt
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {response.json()}"}

    return response.json()


def get_prediction_status(prediction_id):
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()
