import { useState, useEffect, useRef, useCallback } from "react";
import { BottomNav } from "../components/BottomNav";
import { MedicationTag } from "../components/MedicationTag";
import { Plus, Upload, CheckCircle, Camera, X, AlertTriangle, FileText } from "lucide-react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import Webcam from "react-webcam";

interface Medication {
  id: string;
  name: string;
  dosage: string;
}

interface ParsedPrescriptionItem {
  raw_name: string;
  drug_name: string;
  entity_id: string | null;
  dose: string | null;
  frequency: string | null;
  amount_per_dose: string | null;
  total_days: string | null;
  timing: string | null;
  is_unknown: boolean;
}

const commonConditions = [
  { id: "elderly", label: "고령" },
  { id: "hypertension", label: "고혈압" },
  { id: "diabetes", label: "당뇨" },
  { id: "hyperlipidemia", label: "고지혈증" },
  { id: "arthritis", label: "관절염" },
  { id: "asthma", label: "천식" },
];

function buildDosageString(p: ParsedPrescriptionItem): string {
  const parts = [p.dose, p.frequency, p.amount_per_dose, p.timing].filter(Boolean);
  if (parts.length > 0) return parts.join(" · ");
  if (p.total_days) return p.total_days;
  return "용법 미확인";
}

export function ProfilePage() {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [newMedName, setNewMedName] = useState("");
  const [newMedDosage, setNewMedDosage] = useState("");
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [showCamera, setShowCamera] = useState(false);
  const [prescriptionPreview, setPrescriptionPreview] = useState<ParsedPrescriptionItem[] | null>(null);
  const webcamRef = useRef<Webcam>(null);

  useEffect(() => {
    const savedMeds = localStorage.getItem("medications");
    if (savedMeds) {
      setMedications(JSON.parse(savedMeds));
    }

    const savedConditions = localStorage.getItem("conditions");
    if (savedConditions) {
      try {
        const parsed = JSON.parse(savedConditions);
        const validIds = parsed.filter((id: string) =>
          commonConditions.some(c => c.id === id)
        );
        setSelectedConditions(validIds);
        if (validIds.length !== parsed.length) {
          localStorage.setItem("conditions", JSON.stringify(validIds));
        }
      } catch (e) {
        console.error("Failed to parse conditions", e);
      }
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

  const base64ToFile = (base64String: string, filename: string) => {
    const arr = base64String.split(",");
    const mime = arr[0].match(/:(.*?);/)?.[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const processPrescriptionFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    toast.promise(
      fetch(`${API_URL}/api/ocr/prescription`, {
        method: "POST",
        body: formData,
      }).then(async (res) => {
        if (!res.ok) throw new Error("분석 실패");
        const result = await res.json();

        const prescriptions: ParsedPrescriptionItem[] = result.prescriptions || [];

        if (prescriptions.length > 0) {
          setPrescriptionPreview(prescriptions);
          setShowCamera(false);
          return `${prescriptions.length}개의 약물이 인식되었습니다. 결과를 확인해주세요.`;
        }
        throw new Error("인식된 약물이 없습니다.");
      }),
      {
        loading: "처방전을 분석 중입니다...",
        success: (msg) => msg as string,
        error: (err) => err.message,
      }
    );
  };

  // 처방전 미리보기에서 전체 추가
  const addAllFromPrescription = () => {
    if (!prescriptionPreview) return;

    const currentMeds = [...medications];
    let addedCount = 0;

    prescriptionPreview.forEach((p) => {
      const name = p.drug_name || p.raw_name;
      if (!currentMeds.find((m) => m.name === name)) {
        currentMeds.push({
          id: Date.now().toString() + Math.random(),
          name,
          dosage: buildDosageString(p),
        });
        addedCount++;
      }
    });

    setMedications(currentMeds);
    localStorage.setItem("medications", JSON.stringify(currentMeds));
    setPrescriptionPreview(null);
    toast.success(`${addedCount}개의 약물이 등록되었습니다`);
  };

  // 처방전 미리보기에서 개별 추가
  const addSingleFromPrescription = (p: ParsedPrescriptionItem) => {
    const name = p.drug_name || p.raw_name;
    if (medications.find((m) => m.name === name)) {
      toast.info(`${name}은 이미 등록된 약물입니다`);
      return;
    }
    const newMed: Medication = {
      id: Date.now().toString() + Math.random(),
      name,
      dosage: buildDosageString(p),
    };
    const updated = [...medications, newMed];
    setMedications(updated);
    localStorage.setItem("medications", JSON.stringify(updated));
    toast.success(`${name} 추가됨`);
  };

  const capturePrescription = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      const file = base64ToFile(imageSrc, "prescription.jpg");
      processPrescriptionFile(file);
    }
  }, [webcamRef, medications]);

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
            <input
              type="file"
              id="prescription-upload"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) processPrescriptionFile(file);
              }}
            />
            <Button
              variant="outline"
              className="flex-1 bg-[#009688]/5 border-[#009688]/30 text-[#009688] hover:bg-[#009688]/10"
              onClick={() => setShowCamera(true)}
            >
              <Camera className="w-4 h-4 mr-2" />
              처방전 촬영
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => document.getElementById("prescription-upload")?.click()}
            >
              <Upload className="w-4 h-4 mr-2" />
              사진 불러오기
            </Button>
          </div>
        </div>

        {/* Prescription Preview Card */}
        {prescriptionPreview && prescriptionPreview.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border-2 border-[#009688]/30">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#009688]" />
                <h3 className="font-bold text-[#263238]">
                  처방전 인식 결과 ({prescriptionPreview.length}개)
                </h3>
              </div>
              <button
                onClick={() => setPrescriptionPreview(null)}
                className="p-1 hover:bg-gray-100 rounded-full"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            </div>

            <div className="space-y-2 mb-4">
              {prescriptionPreview.map((p, idx) => {
                const name = p.drug_name || p.raw_name;
                const dosageStr = buildDosageString(p);
                const alreadyAdded = medications.some((m) => m.name === name);

                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-3 rounded-lg border ${alreadyAdded
                      ? "bg-gray-50 border-gray-200 opacity-60"
                      : p.is_unknown
                        ? "bg-amber-50 border-amber-200"
                        : "bg-[#009688]/5 border-[#009688]/20"
                      }`}
                  >
                    <div className="flex items-start gap-2 flex-1 min-w-0">
                      {p.is_unknown ? (
                        <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-[#009688] mt-0.5 shrink-0" />
                      )}
                      <div className="min-w-0">
                        <p className="font-medium text-[#263238] text-sm truncate">{name}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{dosageStr}</p>
                        {p.is_unknown && (
                          <p className="text-xs text-amber-600 mt-0.5">⚠ 미등록 약물</p>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => addSingleFromPrescription(p)}
                      disabled={alreadyAdded}
                      className={`ml-3 text-xs px-3 py-1.5 rounded-full font-medium shrink-0 transition ${alreadyAdded
                        ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                        : "bg-[#009688] text-white hover:bg-[#00796B]"
                        }`}
                    >
                      {alreadyAdded ? "등록됨" : "추가"}
                    </button>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-2">
              <Button
                onClick={addAllFromPrescription}
                className="flex-1 bg-[#009688] hover:bg-[#00796B] text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                전체 추가
              </Button>
              <Button
                variant="outline"
                onClick={() => setPrescriptionPreview(null)}
                className="flex-1"
              >
                취소
              </Button>
            </div>
          </div>
        )}

        {/* Camera Overlay */}
        {showCamera && (
          <div className="fixed inset-0 z-50 bg-black flex flex-col">
            <div className="p-4 flex justify-between items-center text-white">
              <h3 className="font-bold">처방전 촬영</h3>
              <button
                onClick={() => setShowCamera(false)}
                className="p-2 hover:bg-white/10 rounded-full"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 relative overflow-hidden bg-gray-900 flex items-center justify-center">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  facingMode: "environment",
                  width: 1280,
                  height: 720
                }}
                className="w-full h-full object-cover"
              />

              {/* Scan Guide Overlay */}
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-x-8 top-1/4 bottom-1/4 border-2 border-[#009688] rounded-xl opacity-50 shadow-[0_0_20px_rgba(0,150,136,0.3)]"></div>
                <div className="absolute top-1/2 left-0 w-full h-0.5 bg-[#009688] opacity-30 animate-pulse"></div>
              </div>

              <div className="absolute bottom-8 inset-x-0 px-8">
                <p className="text-white/80 text-center text-sm mb-6 bg-black/40 py-2 rounded-full backdrop-blur-sm">
                  처방전의 약물 목록이 잘 보이도록 사각형 안에 맞춰주세요
                </p>
                <div className="flex justify-center gap-6">
                  <Button
                    onClick={capturePrescription}
                    className="w-20 h-20 rounded-full bg-white hover:bg-gray-100 p-0 shadow-xl border-4 border-gray-300"
                  >
                    <div className="w-14 h-14 rounded-full border-2 border-gray-200"></div>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

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
          <p className="text-sm text-gray-500 mb-4">
            해당되는 질환을 선택하면 더 정확한 위험도 분석이 가능합니다.
          </p>

          <div className="grid grid-cols-2 gap-3">
            {commonConditions.map((condition) => {
              const isSelected = selectedConditions.includes(condition.id);
              return (
                <button
                  key={condition.id}
                  onClick={() => toggleCondition(condition.id)}
                  className={`flex flex-col items-center justify-center py-4 px-2 rounded-xl border-2 transition-all ${isSelected
                      ? "border-[#009688] bg-[#009688]/10 text-[#009688]"
                      : "border-gray-200 bg-gray-50 text-gray-600 hover:border-[#009688]/40 hover:bg-gray-100"
                    }`}
                >
                  <div className="flex items-center gap-2">
                    {isSelected ? (
                      <CheckCircle className="w-4 h-4 text-[#009688]" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                    )}
                    <span className="font-semibold">{condition.label}</span>
                  </div>
                </button>
              );
            })}
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
