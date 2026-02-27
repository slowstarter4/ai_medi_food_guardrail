import requests
import uuid
import time
import json
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_url = os.getenv("CLOVA_OCR_API_URL")
secret_key = os.getenv("CLOVA_OCR_SECRET")

# Create a valid minimal JPEG
img = Image.new('RGB', (100, 100), color = 'white')
img.save('sample_prescription.jpg')

image_path = "sample_prescription.jpg"
request_json = {
    "images": [{"format": "jpg", "name": "sample"}], 
    "requestId": str(uuid.uuid4()),
    "version": "V2",
    "timestamp": int(time.time() * 1000),
}

payload = {"message": json.dumps(request_json)}
headers = {"X-OCR-SECRET": secret_key}

try:
    with open(image_path, "rb") as f:
        # Standard way Requests expects files for multipart:
        files = [('file', ('sample_prescription.jpg', f, 'image/jpeg'))]
        response = requests.post(api_url, headers=headers, data=payload, files=files, timeout=30)
    print("Status:", response.status_code)
    print("Response:", response.text[:200])
except Exception as e:
    print(e)
