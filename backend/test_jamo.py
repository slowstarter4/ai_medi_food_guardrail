import sys
import unicodedata
from rapidfuzz import fuzz

def to_jamo(text):
    return unicodedata.normalize('NFKD', text)

t1 = to_jamo("이부프로팬")
t2 = to_jamo("이부프로펜")
print("이부프로팬 vs 이부프로펜 (Jamo):", fuzz.WRatio(t1, t2))

t3 = to_jamo("타이레놀ㄹ")
t4 = to_jamo("타이레놀")
print("타이레놀ㄹ vs 타이레놀 (Jamo):", fuzz.WRatio(t3, t4))

t5 = to_jamo("타이레놀서방정")
print("타이레놀서방정 vs 타이레놀 (Jamo):", fuzz.WRatio(t5, t4))
