import requests
import os

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
MODEL_VERSION = "6f7a773af6fc3e8de9d5a3c00be77c17308914bf67772726aff83496ba1e3bbe"

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}


def generate_image_from_prompt(prompt):
    """Creates a prediction and returns its status URL."""
    if not REPLICATE_API_TOKEN:
        return {"error": "Missing Replicate API token."}

    url = "https://api.replicate.com/v1/predictions"
    response = requests.post(url, headers=HEADERS, json={
        "version": MODEL_VERSION,
        "input": {"prompt": prompt}
    })

    try:
        data = response.json()
    except Exception as e:
        return {"error": f"Failed to parse Replicate response: {e}"}

    print("🔁 Replicate create image response:", data)

    if response.status_code != 201:
        return {"error": f"Failed to create prediction: {data}"}

    return {
        "prediction_id": data["id"],
        "status": data["status"],
        "get_url": data["urls"]["get"]
    }


def get_prediction_status(prediction_id_or_url):
    """Polls prediction for completion and returns output URLs."""
    if not REPLICATE_API_TOKEN:
        return {"error": "Missing Replicate API token."}

    url = prediction_id_or_url if prediction_id_or_url.startswith("http") \
        else f"https://api.replicate.com/v1/predictions/{prediction_id_or_url}"

    response = requests.get(url, headers=HEADERS)

    try:
        data = response.json()
    except Exception as e:
        return {"error": f"Failed to parse Replicate status response: {e}"}

    if response.status_code != 200:
        return {"error": f"Status check failed: {data}"}

    if data["status"] == "succeeded":
        return {"output": data["output"]}
    elif data["status"] in ("failed", "canceled"):
        return {"error": f"Prediction {data['status']}: {data.get('error', '')}"}
    else:
        return {"status": data["status"]}
