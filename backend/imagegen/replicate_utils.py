import os
import requests

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

def generate_image_from_prompt(prompt):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "version": "db21e45f7339e45f8c0f7d756f0de50f0cfbc810e97174b1d2a6d52bfb171e60",  # Stable Diffusion XL
        "input": {"prompt": prompt}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        raise Exception(f"Failed to create prediction: {response.json()}")

    prediction = response.json()
    return prediction["urls"]["get"]  # URL to poll for result
