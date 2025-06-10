import requests
import os
import time

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
MODEL_VERSION = "bytedance/sdxl-lightning-4step:latest"

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}

def generate_image_from_prompt(prompt):
    """Creates a prediction and returns its status URL."""
    if not REPLICATE_API_TOKEN:
        raise ValueError("Missing Replicate API token.")
    url = "https://api.replicate.com/v1/predictions"
    response = requests.post(url, headers=HEADERS, json={
        "version": MODEL_VERSION,
        "input": {"prompt": prompt}
    })
    data = response.json()
    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {data}"}
    return {"prediction_id": data["id"], "status": data["status"], "get_url": data["urls"]["get"]}

def get_prediction_status(prediction_id_or_url):
    """Polls prediction for completion and returns output URLs."""
    url = prediction_id_or_url if prediction_id_or_url.startswith("http") else f"https://api.replicate.com/v1/predictions/{prediction_id_or_url}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if response.status_code != 200:
        return {"error": f"Status check failed: {data}"}
    if data["status"] == "succeeded":
        return {"output": data["output"]}
    elif data["status"] in ("failed", "canceled"):
        return {"error": f"Prediction {data['status']}: {data.get('error', '')}"}
    else:
        return {"status": data["status"]}
