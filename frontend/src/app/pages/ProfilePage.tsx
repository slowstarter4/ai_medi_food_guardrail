import { useState, useEffect } from "react";
import { BottomNav } from "../components/BottomNav";
import { MedicationTag } from "../components/MedicationTag";
import { Plus, Upload, Calendar } from "lucide-react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

interface Medication {
  id: string;
  name: string;
  dosage: string;
}

const commonConditions = [
  { id: "hypertension", label: "고혈압" },
  { id: "diabetes", label: "당뇨병" },
  { id: "hyperlipidemia", label: "고지혈증" },
  { id: "arthritis", label: "관절염" },
  { id: "asthma", label: "천식" },
];

export function ProfilePage() {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [newMedName, setNewMedName] = useState("");
  const [newMedDosage, setNewMedDosage] = useState("");
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);

  useEffect(() => {
    const savedMeds = localStorage.getItem("medications");
    if (savedMeds) {
      setMedications(JSON.parse(savedMeds));
    }

    const savedConditions = localStorage.getItem("conditions");
    if (savedConditions) {
      setSelectedConditions(JSON.parse(savedConditions));
    }
  }, []);

  const addMedication = () => {
    if (!newMedName.trim()) {
      toast.error("약물명을 입력해주세요");
      return;
    }

    const newMed: Medication = {
      id: Date.now().toString(),
      name: newMedName,
      dosage: newMedDosage || "용법 미입력",
    };

    const updated = [...medications, newMed];
    setMedications(updated);
    localStorage.setItem("medications", JSON.stringify(updated));

    setNewMedName("");
    setNewMedDosage("");
    toast.success("약물이 추가되었습니다");
  };

  const removeMedication = (id: string) => {
    const updated = medications.filter((m) => m.id !== id);
    setMedications(updated);
    localStorage.setItem("medications", JSON.stringify(updated));
    toast.success("약물이 삭제되었습니다");
  };

  const toggleCondition = (conditionId: string) => {
    const updated = selectedConditions.includes(conditionId)
      ? selectedConditions.filter((c) => c !== conditionId)
      : [...selectedConditions, conditionId];

    setSelectedConditions(updated);
    localStorage.setItem("conditions", JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-20">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8">
        <h1 className="text-2xl font-bold">프로필 관리</h1>
        <p className="text-white/90 mt-2">복약 정보 및 건강 상태 관리</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 -mt-4">
        {/* Medication Input */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4">복약 정보 입력</h2>

          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                약물명
              </label>
              <Input
                placeholder="예: 아스피린"
                value={newMedName}
                onChange={(e) => setNewMedName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addMedication()}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                용법 및 용량
              </label>
              <Input
                placeholder="예: 100mg, 1일 1회"
                value={newMedDosage}
                onChange={(e) => setNewMedDosage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addMedication()}
              />
            </div>
          </div>

          <Button
            onClick={addMedication}
            className="w-full bg-[#009688] hover:bg-[#00796B] text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            약물 추가
          </Button>

          <div className="flex gap-2 mt-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => toast.info("처방전 업로드 기능은 준비 중입니다")}
            >
              <Upload className="w-4 h-4 mr-2" />
              처방전 업로드
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => toast.info("복약 스케줄 설정 기능은 준비 중입니다")}
            >
              <Calendar className="w-4 h-4 mr-2" />
              스케줄 설정
            </Button>
          </div>
        </div>

        {/* Current Medications */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4">
            등록된 약물 ({medications.length})
          </h2>
          {medications.length === 0 ? (
            <p className="text-gray-500 text-sm">등록된 약물이 없습니다.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {medications.map((med) => (
                <MedicationTag
                  key={med.id}
                  name={med.name}
                  dosage={med.dosage}
                  onRemove={() => removeMedication(med.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Health Conditions */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-3">질환 프리셋 선택</h2>
          <p className="text-sm text-gray-600 mb-4">
            해당되는 질환을 선택하면 더 정확한 위험도 분석이 가능합니다.
          </p>

          <div className="space-y-2">
            {commonConditions.map((condition) => (
              <label
                key={condition.id}
                className="flex items-center gap-3 p-3 rounded-lg border-2 border-gray-200 hover:border-[#009688] cursor-pointer transition"
              >
                <input
                  type="checkbox"
                  checked={selectedConditions.includes(condition.id)}
                  onChange={() => toggleCondition(condition.id)}
                  className="w-5 h-5 text-[#009688] rounded focus:ring-[#009688]"
                />
                <span className="font-medium text-[#263238]">
                  {condition.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="bg-[#009688]/5 border border-[#009688]/20 rounded-xl p-4 mb-4">
          <p className="text-sm text-[#263238]">
            💊 정확한 복약 정보를 입력하면 더 안전한 식품 추천을 받을 수 있습니다.
          </p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
