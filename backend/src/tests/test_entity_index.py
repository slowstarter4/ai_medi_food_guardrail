# src/tests/test_entity_index.py
from service.entity_normalizer import load_entity_index

index = load_entity_index()

print(index["drugs"]["로사르탄"])
print(index["foods"]["자몽"])
print(index["situations"]["공복 복용"])
