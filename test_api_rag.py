import sys
from src.rag.retriever import retrieve_evidence
import json

def test_custom_drug_retrieval():
    # Windows 한글 출력 깨짐 방지
    sys.stdout.reconfigure(encoding='utf-8')

    print("Testing External API Retrieval for '암로디핀' (Not in Internal DB)...")
    
    # "타이레놀"은 evidence_db.json에 없는 키임 -> API 호출 유도
    evidence = retrieve_evidence(["암로디핀"])
    
    if evidence:
        print("\n[SUCCESS] Retrieved Evidence:")
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        
        if evidence[0].get("source") == "MFDS_API":
            print("\n✅ Source validation passed: MFDS_API")
        else:
            print(f"\n❌ Source validation failed. Expected MFDS_API, got {evidence[0].get('source')}")
    else:
        print("\n[FAIL] No evidence retrieved. Check API Key or Network.")

if __name__ == "__main__":
    test_custom_drug_retrieval()
