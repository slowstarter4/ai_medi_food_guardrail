import json
import uuid
import time
import requests
import pandas as pd



def extract_text(image_file):
    api_url = 'https://d9vntg0cv1.apigw.ntruss.com/custom/v1/50260/ca3704aa0b06f5954c79ee837faa152d84d6b2d42838f0637a15eda8337dbdce/general'
    secret_key = 'TkhMRWtEZEpEYlNoeWRDZ1RLUldobEhjQU1XUkdhUks='

    request_json = {
        "images": [{"format": "jpeg", "name": "demo"}], 
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(time.time() * 1000),
    }

    payload = {"message": json.dumps(request_json)}  # encode() 굳이 X
    headers = {"X-OCR-SECRET": secret_key}

    with open(image_file, "rb") as f:
        files = {"file": f}
        response = requests.post(api_url, headers=headers, data=payload, files=files)

    response.raise_for_status()

    results = response.json()["images"][0].get("fields", [])
    return results, len(results)


def load_drug_db(csv_path="medi_list.csv"):

    df = pd.read_csv(csv_path)
    if "keyword" not in df.columns or "code" not in df.columns:
        raise ValueError("medi_list.csv must have columns: keyword, code")
    return dict(zip(df["keyword"].astype(str), df["code"].astype(str)))


def match_drugs(results, drug_db):

    texts = [r.get("inferText", "") for r in results if isinstance(r, dict)]
    matched = []

    for keyword, code in drug_db.items():

        if any(keyword in t for t in texts):
            matched.append({"drug_name": keyword, "category": code})

    # 중복 제거
    uniq = {m["drug_name"]: m for m in matched}
    return list(uniq.values())


if __name__ == "__main__":
    image_file = "/Users/johongmin/Desktop/study_ai/OCR/per1.jpeg"


    results, re_len = extract_text(image_file)
    print("OCR lines:", re_len)

 
    drug_db = load_drug_db("medi_list.csv")

    final_result = match_drugs(results, drug_db)


    out = {
        "image_path": image_file,
        "matched_count": len(final_result),
        "matched_drugs": final_result,
    }

    print(json.dumps(out, ensure_ascii=False, indent=2))

    with open("matched_output.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Saved: matched_output.json")