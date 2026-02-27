import json
import uuid
import time
import requests
import pandas as pd

class medi_ocr:
    
    def __init__(self, image_file:str, csv_path:str):
        self.image_file = image_file
        self.csv_path = csv_path

    def extract_text(self):

        api_url = 'https://d9vntg0cv1.apigw.ntruss.com/custom/v1/50260/ca3704aa0b06f5954c79ee837faa152d84d6b2d42838f0637a15eda8337dbdce/general'
        secret_key = 'TkhMRWtEZEpEYlNoeWRDZ1RLUldobEhjQU1XUkdhUks='

        request_json = {
            "images": [{"format": "jpeg",  "name": "demo"}], 
            "requestId": str(uuid.uuid4()),
            "version": "V2",
            "timestamp": int(time.time() * 1000),
        }

        payload = {"message": json.dumps(request_json)}  # encode() 굳이 X
        headers = {"X-OCR-SECRET": secret_key}

        with open(self.image_file, "rb") as f:
            files = {"file": f}
            response = requests.post(api_url, headers=headers, data=payload, files=files)

        response.raise_for_status()

        results = response.json()["images"][0].get("fields", [])
        return results, len(results) 


    def load_drug_db(self):

        df = pd.read_csv(self.csv_path)
        if "keyword" not in df.columns:
            raise ValueError("db file must have columns: keyword")
        
        drug_db = set(df["keyword"].astype(str))

        return drug_db

    @staticmethod
    def match_drugs(results, drug_db):

        texts = [r.get("inferText", "") for r in results if isinstance(r, dict)]
        matched = []

        for keyword in drug_db:

            if any(keyword in t for t in texts):
                matched.append({"drug_name": keyword})

        # 중복 제거
        uniq = {m["drug_name"]: m for m in matched}
        final_result = list(uniq.values())
        return final_result
    
    def json_output_save(self, final_result):    

        out = {
        "image_path": self.image_file,
        "matched_count": len(final_result),
        "matched_drugs": final_result,
         }


        with open("matched_output.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)


        return out

#%%
image_file1 = 'per1.jpeg'
csv_path1 = 'medi_info.csv'
output = medi_ocr(image_file1,csv_path1)

extracted_results, text_count = output.extract_text()
print(f"추출된 텍스트 덩어리 개수: {text_count}개")

drug_db = output.load_drug_db()
matched_drugs = medi_ocr.match_drugs(extracted_results, drug_db)

final_output = output.json_output_save(matched_drugs)

print("\n최종 결과")
print(final_output)
