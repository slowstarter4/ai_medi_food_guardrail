import os
import json
from services.eyak_api import fetch_drug_info_from_api

SERVICE_KEY = os.getenv("EYAK_SERVICE_KEY")

if __name__ == "__main__":
    result = fetch_drug_info("와파린", SERVICE_KEY)
    print(json.dumps(result, ensure_ascii_False, indent=2))