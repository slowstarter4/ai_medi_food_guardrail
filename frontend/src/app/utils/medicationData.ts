// Mock medication interaction database
export interface MedicationInteraction {
  medication: string;
  ingredient: string;
  riskLevel: "safe" | "warning" | "danger";
  interaction: string;
  evidence: string;
  source: string;
}

export const medicationInteractions: MedicationInteraction[] = [
  {
    medication: "로사르탄",
    ingredient: "자몽",
    riskLevel: "danger",
    interaction: "약물 대사 저해로 인한 혈압 과도 저하 위험",
    evidence:
      "자몽은 약물 대사 효소(CYP3A4)를 억제하여 혈중 약물 농도를 상승시킵니다. 이로 인해 저혈압, 어지러움 등의 부작용이 심각하게 증가할 수 있습니다.",
    source: "식품의약품안전처 의약품안전나라",
  },
  {
    medication: "메트포르민",
    ingredient: "당류",
    riskLevel: "warning",
    interaction: "혈당 수치 급격한 상승 가능성",
    evidence:
      "당뇨 환자의 경우 당류 섭취 시 혈당 수치가 급격히 상승할 수 있습니다. 메트포르민 복용 중에도 과도한 당류 섭취는 혈당 조절을 어렵게 만듭니다.",
    source: "대한당뇨병학회 식이지침",
  },
  {
    medication: "아토르바스타틴",
    ingredient: "자몽",
    riskLevel: "danger",
    interaction: "근육 손상 위험 증가",
    evidence:
      "자몽은 스타틴계 약물의 혈중 농도를 크게 증가시켜 근육통, 근육 손상(횡문근융해증) 위험을 높입니다.",
    source: "식품의약품안전처 의약품안전나라",
  },
  {
    medication: "와파린",
    ingredient: "비타민K",
    riskLevel: "warning",
    interaction: "항응고 효과 감소",
    evidence:
      "비타민K는 와파린의 항응고 효과를 감소시킬 수 있습니다. 녹색 채소 섭취량을 일정하게 유지하는 것이 중요합니다.",
    source: "대한심장학회 항응고요법 가이드라인",
  },
];

export function checkInteraction(
  medications: string[],
  ingredients: string[]
): MedicationInteraction | null {
  for (const med of medications) {
    for (const ingredient of ingredients) {
      const interaction = medicationInteractions.find(
        (i) =>
          i.medication.toLowerCase().includes(med.toLowerCase()) &&
          ingredient.toLowerCase().includes(i.ingredient.toLowerCase())
      );
      if (interaction) {
        return interaction;
      }
    }
  }
  return null;
}

export function getRiskLevel(
  medications: string[],
  ingredients: string[]
): "safe" | "warning" | "danger" {
  const interaction = checkInteraction(medications, ingredients);
  return interaction?.riskLevel || "safe";
}
