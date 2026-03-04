import { useLocation, useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { SafetyCard } from "../components/SafetyCard";
import { IngredientChip } from "../components/IngredientChip";
import { ArrowLeft, Share2, Heart, ExternalLink, ShieldCheck, Sparkles, AlertCircle, Info } from "lucide-react";
import { Button } from "../components/ui/button";
import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
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
      }
    });

    return Object.keys(sections).length > 0 ? sections : null;
  };

  const explanationSections = parseExplanation(backendResult?.explanation);
  const durAlerts = backendResult?.risk_result?.supplementary_info?.dur_alerts || [];
  const verifiedDrugs = backendResult?.risk_result?.supplementary_info?.api_verified_drugs || [];

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

  // Get matched rule's evidence info
  const matchedRule = backendResult?.risk_result?.matched_rule;
  const evidenceKey = matchedRule?.evidence_key;
  // Note: Backend might need to send evidence details, or we pull from a local map if needed.
  // Assuming backend already includes processed evidence in risk_result from evaluator/assessor.
  const evidenceInfo = backendResult?.risk_result?.evidence_details;

  const getRiskInfo = () => {
    if (explanationSections) {
      return {
        title: explanationSections.conclusion || (riskLevel === "danger" ? "섭취 중단 권고" : "주의 필요"),
        message: explanationSections.reason || "상세 이유를 불러오고 있습니다.",
        evidence: evidenceInfo?.evidence_summary_user || explanationSections.action || "권장 대처 방안을 확인하세요.",
        evidenceSource: evidenceInfo?.evidence_source_label || explanationSections.source || "SafeEat AI 분석 결과",
        evidenceStrength: evidenceInfo?.evidence_strength,
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
    <div className="min-h-screen bg-[#F5F5F5] pb-20 font-sans">
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
        {/* AI Analysis Label */}
        <div className="flex items-center gap-1.5 mb-2 px-1">
          <Sparkles className="w-4 h-4 text-[#009688]" />
          <span className="text-xs font-bold text-[#009688]">SafeEat AI 맞춤 분석 가이드</span>
        </div>

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
            evidenceStrength={riskInfo.evidenceStrength as any}
          />
        </motion.div>

        {/* Analysis Context (Personalized) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-4 mt-4">
          <h2 className="text-sm font-bold text-gray-800 mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Info className="w-4 h-4 text-[#009688]" />
              분석 기반 정보
            </span>
            <span className="text-[10px] text-gray-400 font-normal">사용자 맞춤형</span>
          </h2>
          <div className="space-y-3">
            <div>
              <span className="text-xs text-gray-500 block mb-1.5">활성화된 페르소나 (질환/상태)</span>
              <div className="flex flex-wrap gap-1.5">
                {(backendResult?.risk_result?.user_conditions?.length > 0) ? (
                  backendResult.risk_result.user_conditions.map((c: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-[#009688]/5 border border-[#009688]/20 rounded-md text-[11px] font-medium text-[#009688]">
                      {c}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-gray-400 italic">등록된 질환 정보 없음</span>
                )}
              </div>
            </div>
            <div>
              <span className="text-xs text-gray-500 block mb-1.5">분석에 포함된 약물</span>
              <div className="flex flex-wrap gap-1.5">
                {(backendResult?.risk_result?.entities_involved?.drugs?.filter((d: any) => d.entity_id !== "DRUG_UNKNOWN").length > 0) ? (
                  backendResult.risk_result.entities_involved.drugs
                    .filter((d: any) => d.entity_id !== "DRUG_UNKNOWN")
                    .map((d: any, i: number) => {
                      const isVerified = verifiedDrugs.includes(d.raw);
                      return (
                        <span key={i} className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium border ${isVerified ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600'}`}>
                          {d.raw}
                          {isVerified && <ShieldCheck className="w-3 h-3 text-blue-500" />}
                        </span>
                      );
                    })
                ) : (
                  <span className="text-[11px] text-gray-400 italic">감지된 약물 정보 없음</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Supplementary AI Analysis (DUR) */}
        {durAlerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-[#FFF9C4] border border-[#FBC02D] rounded-xl p-4 mb-4"
          >
            <h2 className="text-sm font-bold text-[#F57F17] mb-2 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4" />
              공공 API(e약은요) 보조 정보
            </h2>
            <div className="space-y-2">
              {durAlerts.map((alert: string, i: number) => (
                <div key={i} className="text-xs text-[#7B5E00] leading-relaxed flex gap-2">
                  <span className="shrink-0">•</span>
                  <span>{alert}</span>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-[#F57F17]/70 mt-3 italic">
              * 식약처 공공 데이터를 기반으로 AI가 추출한 보조 상호작용 정보입니다.
            </p>
          </motion.div>
        )}

        {/* Detected Ingredients */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-3 flex items-center gap-1.5 text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-[#009688]"></div>
            인식된 성분
          </h2>
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
                    toast.info(`${ingredient}에 대한 상세 정보는 상세 정보 탭을 이용해 주세요.`);
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
            className="flex flex-col h-auto py-3 gap-1 bg-white border-gray-200 text-gray-700 shadow-sm"
            onClick={() => setShowAlternatives(!showAlternatives)}
          >
            <Heart className={`w-5 h-5 ${showAlternatives ? 'fill-red-500 text-red-500' : ''}`} />
            <span className="text-[11px] font-bold">대체 식품</span>
          </Button>
          <Button
            variant="outline"
            className="flex flex-col h-auto py-3 gap-1 bg-white border-gray-200 text-gray-700 shadow-sm"
            onClick={() => toast("공유 기능은 준비 중입니다.")}
          >
            <Share2 className="w-5 h-5 text-gray-500" />
            <span className="text-[11px] font-bold">공유하기</span>
          </Button>
          <Button
            variant="outline"
            className="flex flex-col h-auto py-3 gap-1 bg-white border-gray-200 text-gray-700 shadow-sm"
            onClick={() =>
              window.open(
                "https://nedrug.mfds.go.kr/index",
                "_blank"
              )
            }
          >
            <ExternalLink className="w-5 h-5 text-gray-500" />
            <span className="text-[11px] font-bold">의약품백과</span>
          </Button>
        </div>

        {/* Alternative Foods */}
        <AnimatePresence>
          {showAlternatives && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-bold text-[#263238] flex items-center gap-1.5 text-sm">
                    <Sparkles className="w-4 h-4 text-[#009688]" />
                    AI 추천 대체 식품
                  </h2>
                </div>

                {explanationSections?.alternative ? (
                  <div className="p-4 bg-[#009688]/5 border border-[#009688]/20 rounded-lg">
                    <p className="text-sm text-[#263238] leading-relaxed">
                      {explanationSections.alternative}
                    </p>
                  </div>
                ) : (
                  <>
                    <p className="text-xs text-gray-500 mb-4 italic">
                      맞춤형 분석 결과 위험 성분이 없는 안전한 대체품을 추천합니다.
                    </p>

                    <div className="space-y-3">
                      {alternatives.map((alt, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg hover:border-[#009688]/30 transition cursor-pointer"
                        >
                          <img
                            src={alt.imageUrl}
                            alt={alt.name}
                            className="w-16 h-16 object-cover rounded-lg shrink-0"
                          />
                          <div className="flex-1">
                            <h3 className="font-bold text-sm text-[#263238] mb-1">
                              {alt.name}
                            </h3>
                            <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
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
        </AnimatePresence>

        {/* AI Disclaimer & Info */}
        <div className="mt-8 mb-6 bg-gray-100 rounded-xl p-5 border border-gray-200">
          <div className="flex gap-3 mb-4">
            <div className="shrink-0 w-8 h-8 rounded-full bg-white flex items-center justify-center border border-gray-200">
              <Sparkles className="w-4 h-4 text-[#009688]" />
            </div>
            <div className="space-y-1">
              <h3 className="text-xs font-bold text-gray-700">SafeEat 분석의 두 가지 위계</h3>
              <p className="text-[10px] text-gray-500 leading-relaxed">
                1. **자체 룰 가드레일 (Tier 1)**: 식약처 및 의학 전문가 가이드 기반의 확정적 위험 감지 시스템입니다.<br />
                2. **AI 보조 분석 (Tier 2)**: 공공 API 데이터와 LLM 추론을 결합하여 개인별 정황(오타, 상황)을 보조적으로 분석합니다.
              </p>
            </div>
          </div>
          <p className="text-[10px] text-gray-400 leading-relaxed border-t border-gray-200 pt-4 text-center">
            본 결과는 AI의 보조 정보이며 의학적 확진이 아닙니다.<br />
            기저질환자의 최종 판단은 반드시 담당 의사 및 약사와 상담하시기 바랍니다.
          </p>
        </div>

        <div className="flex gap-3 mb-4">
          <Button
            onClick={() => recordIntake()}
            className="flex-1 bg-white border-[#009688] text-[#009688] hover:bg-[#E0F2F1] border h-12 font-bold shadow-sm"
          >
            기록으로 남기기
          </Button>
          <Button
            onClick={() => navigate("/")}
            className="flex-1 bg-[#009688] hover:bg-[#00796B] text-white h-12 font-bold shadow-sm"
          >
            홈으로 돌아가기
          </Button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
