"""
처방전 OCR 시스템
PaddleOCR을 사용하여 처방전에서 약명과 용량 정보를 추출
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
from paddleocr import PaddleOCR


BBox = Optional[Any]
NormLine = Tuple[BBox, str, Optional[float]] 

class PrescriptionOCR:
    def __init__(self, lang: str = "korean"):

        self.ocr = PaddleOCR(
            lang=lang,
            use_textline_orientation=True,
            device="cpu",
        )


    def extract_text(self, image_path: str) -> List[NormLine]:

        img = cv2.imread(image_path)
        if img is None:
            return []

    
        result = self.ocr.predict(img)
        if not result:
            return []

        if isinstance(result, dict):
            return self._normalize_from_dict(result)


        if isinstance(result, (list, tuple)):
            return self._normalize_from_list(result)
        
        print("RAW RESULT TYPE:", type(result))
        print("RAW RESULT:", result)


        return []

    def _normalize_from_dict(self, d: Dict) -> List[NormLine]:
        texts = d.get("rec_texts") or d.get("texts") or []
        scores = d.get("rec_scores") or d.get("scores") or [None] * len(texts)

        out: List[NormLine] = []
        for t, s in zip(texts, scores):
            if isinstance(t, str) and t.strip():
                conf = self._to_float_or_none(s)
                out.append((None, t.strip(), conf))
        return out

    def _normalize_from_list(self, result_list: Any) -> List[NormLine]:

        lines = result_list
        if len(result_list) == 1 and isinstance(result_list[0], (list, tuple)):
            lines = result_list[0]

        out: List[NormLine] = []
        if not isinstance(lines, (list, tuple)):
            return out

        for line in lines:
            norm = self._normalize_line(line)
            if norm:
                out.append(norm)
        return out

    def _normalize_line(self, line: Any) -> Optional[NormLine]:

        bbox: BBox = None
        text: Optional[str] = None
        conf: Optional[float] = None

        if isinstance(line, str):
            return (None, line.strip(), None) if line.strip() else None


        if isinstance(line, (list, tuple)) and len(line) >= 2:
            bbox = line[0]
            second = line[1]

            if isinstance(second, (list, tuple)) and len(second) >= 2 and isinstance(second[0], str):
                text = second[0]
                conf = self._to_float_or_none(second[1])
            elif isinstance(second, dict):

                text = second.get("text") or second.get("rec_text") or second.get("inferText")
                conf = self._to_float_or_none(
                    second.get("score") or second.get("rec_score") or second.get("confidence") or second.get("inferConfidence")
                )

  
        if text is None and isinstance(line, (list, tuple)) and len(line) >= 2 and isinstance(line[0], str):
            text = line[0]
            conf = self._to_float_or_none(line[1])
            bbox = None

        if isinstance(text, str) and text.strip():
            return (bbox, text.strip(), conf)

        return None

    @staticmethod
    def _to_float_or_none(x: Any) -> Optional[float]:
        try:
            return float(x) if x is not None else None
        except Exception:
            return None


    def parse_medication_info(self, ocr_results: List[NormLine]) -> List[Dict]:

        meds: List[Dict] = []
        for i, (_, text, conf) in enumerate(ocr_results):
            confidence = conf if conf is not None else 0.0

            med = self._extract_medication_from_line(text, confidence)
            if not med:
                continue

            # 근처 줄에서 복용정보 보조 추출
            med.update(self._find_dosage_info(ocr_results, i))
            meds.append(med)

        # 중복 제거
        uniq = {}
        for m in meds:
            key = (m.get("medication_name"), m.get("dosage_per_unit"))
            if key not in uniq:
                uniq[key] = m
        return list(uniq.values())

    def _extract_medication_from_line(self, text: str, confidence: float) -> Optional[Dict]:

        medication_keywords = [
            "정", "캡슐", "시럽", "액", "연고", "크림", "패치",
            "탭", "Tab", "Cap", "Inj", "Syr",
        ]

        has_form = any(k in text for k in medication_keywords)
        has_unit = re.search(r"\d+\.?\d*\s*(mg|mcg|μg|ug|g|ml|mL|㎎|㎖)", text, re.IGNORECASE) is not None

        if not (has_form or has_unit):
            return None

        med_name, dosage = self._split_name_and_dosage(text)

        # 너무 짧은 건 노이즈일 수 있어서 컷
        if len(med_name) < 2:
            return None

        return {
            "medication_name": med_name,
            "dosage_per_unit": dosage,
            "confidence": round(confidence, 3),
            "original_text": text,
        }

    def _split_name_and_dosage(self, text: str) -> Tuple[str, Optional[str]]:

        m = re.search(r"(\d+\.?\d*\s*(?:mg|mcg|μg|ug|g|ml|mL|㎎|㎖))", text, re.IGNORECASE)
        if m:
            dosage = m.group(1).strip()
            # 1번만 제거
            med_name = text.replace(dosage, "", 1).strip()
            return med_name, dosage
        return text.strip(), None

    def _find_dosage_info(self, ocr_results: List[NormLine], current_idx: int) -> Dict:

        info = {"frequency": None, "amount_per_dose": None, "duration": None}

        for j in range(current_idx, min(current_idx + 4, len(ocr_results))):
            _, t, _ = ocr_results[j]

            # 1일 n회
            m = re.search(r"1일\s*(\d+)\s*회", t)
            if m and not info["frequency"]:
                info["frequency"] = f"1일 {m.group(1)}회"

            # 1회 n정/캡슐/포/알
            m = re.search(r"1회\s*(\d+\.?\d*)\s*(정|캡슐|포|알|T)", t)
            if m and not info["amount_per_dose"]:
                info["amount_per_dose"] = f"1회 {m.group(1)}{m.group(2)}"

            # n일분
            m = re.search(r"(\d+)\s*일분?", t)
            if m and not info["duration"]:
                info["duration"] = f"{m.group(1)}일분"

        return info


    def process_prescription(self, image_path: str, output_json: Optional[str] = None) -> Dict:
        print(f"처방전 처리 중: {image_path}")

        ocr_results = self.extract_text(image_path)

        if not ocr_results:
            print("텍스트를 추출할 수 없습니다.")
            result = {
                "image_path": str(image_path),
                "total_medications": 0,
                "medications": [],
                "raw_text": [],
            }
            if output_json:
                self.save_to_json(result, output_json)
                print(f"결과 저장됨: {output_json}")
            return result

        print(f"총 {len(ocr_results)}개의 텍스트 라인 추출됨")
        print("샘플:", ocr_results[0])

        medications = self.parse_medication_info(ocr_results)

        raw_texts = [
            {
                "text": text,
                "confidence": None if conf is None else round(conf, 3),
            }
            for _, text, conf in ocr_results
        ]

        result = {
            "image_path": str(image_path),
            "total_medications": len(medications),
            "medications": medications,
            "raw_text": raw_texts,
        }

        if output_json:
            self.save_to_json(result, output_json)
            print(f"결과 저장됨: {output_json}")

        return result

    def save_to_json(self, data: Dict, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)



def main():
    ocr_processor = PrescriptionOCR(lang="korean")
    result = ocr_processor.process_prescription("per1.jpeg", "output.json")
    print("total_medications =", result.get("total_medications", 0))
    return result


if __name__ == "__main__":
    main()


