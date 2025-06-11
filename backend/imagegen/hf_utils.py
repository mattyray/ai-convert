import requests

HF_API_URL = "https://mnraynor90-facefusion3-1.hf.space/run/predict"

def facefusion_via_hf(selfie_url, target_url):
    try:
        response = requests.post(HF_API_URL, json={
            "data": [selfie_url, target_url]
        }, timeout=300)

        if response.status_code != 200:
            return {"error": f"HF API returned {response.status_code}: {response.text}"}

        data = response.json()
        if "data" in data and data["data"]:
            return {"base64": data["data"][0]}
        return {"error": "Unexpected Hugging Face response format."}

    except Exception as e:
        return {"error": f"FaceFusion API error: {e}"}
