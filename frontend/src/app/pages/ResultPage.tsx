import { useLocation, useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { SafetyCard } from "../components/SafetyCard";
import { IngredientChip } from "../components/IngredientChip";
import { ArrowLeft, Share2, Heart, ExternalLink } from "lucide-react";
import { Button } from "../components/ui/button";
import { useState } from "react";
import { motion } from "motion/react";
import { toast } from "sonner";

interface AlternativeFood {
  name: string;
  reason: string;
  imageUrl: string;
}

export function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { scanData, boundingBoxes, backendResult } = location.state || {};
  const [showAlternatives, setShowAlternatives] = useState(false);

  // Helper for Object.entries-like mapping in TS if needed, or just use plain objects
  function items<T>(obj: T): [keyof T, T[keyof T]][] {
    return Object.entries(obj as any) as any;
  }

  // 백엔드 설명을 섹션별로 파싱하는 함수
  const parseExplanation = (text: string) => {
    if (!text) return null;
    console.log("Parsing explanation text:", text);
    const sections: Record<string, string> = {};
    const patterns = {
      conclusion: /■\s*\*?\*?\[결론\]\*?\*?:\s*(.*?)(?=\s*■|$)/s,
      reason: /■\s*\*?\*?\[이유\]\*?\*?:\s*(.*?)(?=\s*■|$)/s,
      action: /■\s*\*?\*?\[대처\]\*?\*?:\s*(.*?)(?=\s*■|$)/s,
      alternative: /■\s*\*?\*?\[대안\]\*?\*?:\s*(.*?)(?=\s*■|$)/s,
      source: /■\s*\*?\*?\[출처\]\*?\*?:\s*(.*?)(?=\s*■|$)/s,
    };

    items(patterns).forEach(([key, pattern]) => {
      const match = text.match(pattern);
      if (match) {
        sections[key] = match[1].trim();
        console.log(`Matched ${key}:`, sections[key]);
      }
    });

    // 하나라도 매칭되면 객체 반환, 아니면 null (fallback 유도)
    return Object.keys(sections).length > 0 ? sections : null;
  };

  const explanationSections = parseExplanation(backendResult?.explanation);

  // Mock data if no scan data provided
  const mockData = {
    foodName: "분석된 식품",
    riskLevel: "danger" as const,
    ingredients: ["알 수 없음"],
    mainRisk: {
      ingredient: "분석 중",
      medication: "복용 중인 약물",
      interaction: "상호작용 확인 중",
    },
  };

  // 위험도 매핑 (Backend RED/YELLOW/GREEN -> Frontend danger/warning/safe)
  const riskLevelMap: Record<string, "safe" | "warning" | "danger"> = {
    red: "danger",
    yellow: "warning",
    green: "safe",
  };

  const data = scanData || mockData;

  // Generate alternatives based on risk (기본 대체 식품 데이터)
  const alternatives: any[] = [
    {
      name: "오렌지 주스",
      reason: "자몽 성분이 없어 안전하게 섭취 가능",
      imageUrl: "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400",
    },
    {
      name: "사과 주스",
      reason: "약물 상호작용이 없는 안전한 대체품",
      imageUrl: "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=400",
    },
    {
      name: "포도 주스",
      reason: "고혈압 환자에게 권장되는 건강 음료",
      imageUrl: "https://images.unsplash.com/photo-1596363505729-4190a9506133?w=400",
    },
  ];

  const rawRisk = backendResult?.risk_result?.risk_level?.toLowerCase() || data.riskLevel || "safe";
  const riskLevel = riskLevelMap[rawRisk] || (rawRisk as any);

  const getRiskInfo = () => {
    if (explanationSections) {
      return {
        title: explanationSections.conclusion || (riskLevel === "danger" ? "섭취 중단 권고" : "주의 필요"),
        message: explanationSections.reason || "상세 이유를 불러오고 있습니다.",
        evidence: explanationSections.action || "권장 대처 방안을 확인하세요.",
        evidenceSource: explanationSections.source || "SafeEat AI 분석 결과",
      };
    }

    // 기본값 (백엔드 결과가 없을 때)
    if (riskLevel === "danger") {
      return {
        title: "섭취 중단 권고",
        message: `복용 중인 약물과 식품 성분이 충돌할 가능성이 높습니다.`,
        evidence: `성분 분석 결과 약물 상호작용 위험이 감지되었습니다. 섭취 전 반드시 전문가와 상담하세요.`,
        evidenceSource: "세이프잇 내부 정책",
      };
    } else if (riskLevel === "warning") {
      return {
        title: "주의하여 섭취",
        message: "주의가 필요한 성분이 포함되어 있습니다.",
        evidence: "상태에 따라 부작용이 나타날 수 있으니 소량 섭취를 권장합니다.",
        evidenceSource: "세이프잇 내부 정책",
      };
    } else {
      return {
        title: "안전하게 섭취 가능",
        message: "알려진 상호작용 위험이 없습니다.",
        evidence: "등록하신 복약 정보를 기반으로 분석한 결과, 안전하게 섭취하실 수 있습니다.",
        evidenceSource: "SafeEat AI 분석 결과",
      };
    }
  };

  const riskInfo = getRiskInfo();

  const recordIntake = () => {
    const history = JSON.parse(localStorage.getItem("scan_history") || "[]");
    const newEntry = {
      id: Date.now().toString(),
      date: new Date().toLocaleString(),
      foodName: data.foodName,
      riskLevel: riskLevel,
      explanation: backendResult?.explanation
    };
    localStorage.setItem("scan_history", JSON.stringify([newEntry, ...history]));
    toast.success("섭취 정보가 기록되었습니다.");
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-20">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 mb-4 hover:opacity-80"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>뒤로 가기</span>
        </button>
        <h1 className="text-2xl font-bold">{data.foodName}</h1>
        <p className="text-white/90 mt-1">위험도 분석 결과</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 mt-4">
        {/* Main Safety Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <SafetyCard
            riskLevel={riskLevel}
            title={riskInfo.title}
            message={riskInfo.message}
            evidence={riskInfo.evidence}
            evidenceSource={riskInfo.evidenceSource}
          />
        </motion.div>

        {/* Analysis Context (Personalized) */}
        <div className="bg-[#009688]/5 border border-[#009688]/20 rounded-xl p-4 mb-4">
          <h2 className="text-sm font-bold text-[#009688] mb-2 flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#009688]"></div>
            맞춤 분석 정보
          </h2>
          <div className="space-y-2">
            <div>
              <span className="text-xs text-gray-500 block mb-1">등록된 질환/상태</span>
              <div className="flex flex-wrap gap-1.5">
                {(backendResult?.risk_result?.user_conditions?.length > 0) ? (
                  backendResult.risk_result.user_conditions.map((c: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-white border border-[#009688]/30 rounded text-[11px] text-[#009688]">
                      {c}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-gray-400">등록된 질환 정보 없음</span>
                )}
              </div>
            </div>
            <div>
              <span className="text-xs text-gray-500 block mb-1">복용 중인 약물</span>
              <div className="flex flex-wrap gap-1.5">
                {(backendResult?.risk_result?.entities_involved?.drugs?.filter((d: any) => d.entity_id !== "DRUG_UNKNOWN").length > 0) ? (
                  backendResult.risk_result.entities_involved.drugs
                    .filter((d: any) => d.entity_id !== "DRUG_UNKNOWN")
                    .map((d: any, i: number) => (
                      <span key={i} className="px-2 py-0.5 bg-white border border-[#009688]/30 rounded text-[11px] text-[#009688]">
                        {d.raw}
                      </span>
                    ))
                ) : (
                  <span className="text-[11px] text-gray-400">등록된 약물 정보 없음</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Detected Ingredients */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-3">인식된 성분</h2>
          <div className="flex flex-wrap gap-2">
            {data.ingredients?.map((ingredient: string, index: number) => {
              const box = boundingBoxes?.find(
                (b: any) => b.text === ingredient
              );
              return (
                <IngredientChip
                  key={index}
                  label={ingredient}
                  riskLevel={box?.riskLevel}
                  onClick={() => {
                    alert(`${ingredient}에 대한 상세 정보`);
                  }}
                />
              );
            })}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <Button
            variant="outline"
            className="flex flex-col h-auto py-3 gap-1"
            onClick={() => setShowAlternatives(!showAlternatives)}
          >
            <Heart className="w-5 h-5" />
            <span className="text-xs">대체 식품</span>
          </Button>
          <Button
            variant="outline"
            className="flex flex-col h-auto py-3 gap-1"
            onClick={() => alert("가족과 공유 기능은 준비 중입니다")}
          >
            <Share2 className="w-5 h-5" />
            <span className="text-xs">공유하기</span>
          </Button>
          <Button
            variant="outline"
            className="flex flex-col h-auto py-3 gap-1"
            onClick={() =>
              window.open(
                "https://nedrug.mfds.go.kr/index",
                "_blank"
              )
            }
          >
            <ExternalLink className="w-5 h-5" />
            <span className="text-xs">상세 정보</span>
          </Button>
        </div>

        {/* Alternative Foods */}
        {showAlternatives && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-[#263238]">추천 대체 식품</h2>
                <span className="text-xs text-gray-500">
                  SafeEat 맞춤 추천
                </span>
              </div>

              {explanationSections?.alternative ? (
                <div className="p-4 bg-[#009688]/5 border border-[#009688]/20 rounded-lg">
                  <p className="text-[#263238] leading-relaxed">
                    {explanationSections.alternative}
                  </p>
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-600 mb-4">
                    {data.mainRisk?.ingredient || "위험 성분"}이 없는 안전한 대체품을
                    추천합니다
                  </p>

                  <div className="space-y-3">
                    {alternatives.map((alt, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex gap-3 p-3 bg-[#4CAF50]/5 border border-[#4CAF50]/20 rounded-lg hover:bg-[#4CAF50]/10 transition cursor-pointer"
                        onClick={() => {
                          alert(`${alt.name}에 대한 상세 정보`);
                        }}
                      >
                        <img
                          src={alt.imageUrl}
                          alt={alt.name}
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h3 className="font-bold text-[#263238] mb-1">
                            {alt.name}
                          </h3>
                          <p className="text-sm text-gray-600 leading-relaxed">
                            {alt.reason}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </motion.div>
        )}

        {/* Recommended Actions */}
        {riskLevel === "danger" && (
          <div className="bg-[#E53935]/5 border-2 border-[#E53935]/20 rounded-xl p-4 mb-4">
            <h3 className="font-bold text-[#E53935] mb-2">권장 조치</h3>
            <ul className="text-sm text-[#263238] space-y-1.5">
              <li>• 즉시 섭취를 중단하세요</li>
              <li>• 이미 섭취한 경우 의사와 상담하세요</li>
              <li>• 약물 복용 전후 최소 2시간 간격을 두세요</li>
              <li>• 대체 식품 목록을 참고하세요</li>
            </ul>
          </div>
        )}

        <div className="flex gap-3 mb-4">
          <Button
            onClick={() => recordIntake()}
            className="flex-1 bg-white border-[#009688] text-[#009688] hover:bg-[#E0F2F1] border"
          >
            기록으로 남기기
          </Button>
          <Button
            onClick={() => navigate("/")}
            className="flex-1 bg-[#009688] hover:bg-[#00796B] text-white"
          >
            홈으로 돌아가기
          </Button>
        </div>

        {/* AI Disclaimer & Roadmap Link */}
        <div className="mt-8 mb-4 border-t border-gray-200 pt-6">
          <p className="text-xs text-gray-400 leading-relaxed mb-3">
            본 결과는 공신력 있는 기준(식약처, FDA 등)을 바탕으로 한 AI의 보조 정보입니다. 기저질환자의 최종적인 판단 및 대처는 반드시 담당 의사 및 약사와 상담하시기 바랍니다.
          </p>
          <button
            onClick={() => navigate("/info")}
            className="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-xl text-sm font-medium transition flex justify-between items-center"
          >
            <span>SafeEat 분석 기준 및 서비스 로드맵 보기</span>
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
