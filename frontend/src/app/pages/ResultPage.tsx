import { useLocation, useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { SafetyCard } from "../components/SafetyCard";
import { IngredientChip } from "../components/IngredientChip";
import { ArrowLeft, Share2, Heart, ExternalLink, ShieldCheck, Sparkles, AlertCircle, Info, Maximize2, ShieldCheck as ShieldCheckIcon } from "lucide-react";
import { Button } from "../components/ui/button";
import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { toast } from "sonner";
import { CounselingOverlay } from "../components/CounselingOverlay";
import { PinpointFAQ } from "../components/PinpointFAQ";
import { InteractionGraph } from "../components/InteractionGraph";
import { ShareReportCard } from "../components/ShareReportCard";
import { useRef } from "react";
import html2canvas from "html2canvas";

interface AlternativeFood {
  name: string;
  reason: string;
  imageUrl: string;
}

export function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { scanData, boundingBoxes, backendResult, scanImageUrl } = location.state || {};
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [showOCR, setShowOCR] = useState(true);
  const [isCounselingOpen, setIsCounselingOpen] = useState(true);
  const reportRef = useRef<HTMLDivElement>(null);

  const handleShare = async () => {
    if (!reportRef.current) return;

    try {
      toast.loading("안심 리포트 생성 중...");
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        backgroundColor: "#ffffff",
        logging: false,
        useCORS: true,
      });

      const image = canvas.toDataURL("image/png");
      const link = document.createElement("a");
      link.href = image;
      link.download = `SafeEat_Report_${data.foodName}_${new Date().getTime()}.png`;
      link.click();
      
      toast.dismiss();
      toast.success("리포트가 이미지로 저장되었습니다.");
    } catch (error) {
      console.error("Share failed:", error);
      toast.dismiss();
      toast.error("리포트 생성에 실패했습니다.");
    }
  };

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
  const evidenceInfo = backendResult?.risk_result?.evidence_details;

  const getRiskInfo = () => {
    if (explanationSections) {
      return {
        title: explanationSections.conclusion || (riskLevel === "danger" ? "섭취 중단 권고" : "주의 필요"),
        message: explanationSections.reason || "상세 이유를 불러오고 있습니다.",
        evidence: explanationSections.action || "권장 대처 방안을 확인하세요.",
        evidenceSource: explanationSections.source || "SafeEat AI 분석 결과",
        evidenceStrength: evidenceInfo?.evidence_strength,
      };
    }

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

  const [isSaved, setIsSaved] = useState(false);

  const recordIntake = () => {
    if (isSaved) {
      toast.info("이미 기록된 정보입니다.");
      return;
    }

    const history = JSON.parse(localStorage.getItem("scan_history") || "[]");
    const newEntry = {
      id: Date.now().toString(),
      date: new Date().toLocaleString(),
      foodName: data.foodName,
      riskLevel: riskLevel,
      explanation: backendResult?.explanation,
      ingredients: data.ingredients,
      backendResult: backendResult,
      boundingBoxes: boundingBoxes,
    };

    const updatedHistory = [newEntry, ...history].slice(0, 10);
    localStorage.setItem("scan_history", JSON.stringify(updatedHistory));
    setIsSaved(true);
    toast.success("섭취 정보가 기록되었습니다.");
  };

  return (
    <div className="min-h-screen bg-[#FDF7FF] pb-24">
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
        {/* AI Analysis Label & Confidence Score */}
        <div className="flex items-center justify-between mb-2 px-1">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-[#009688]" />
            <span className="text-xs font-bold text-[#009688]">SafeEat AI 맞춤 분석 가이드</span>
          </div>
          {backendResult?.risk_result?.confidence_score && (
            <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
              backendResult.risk_result.confidence_score >= 95 
                ? "bg-green-50 text-green-700 border-green-200" 
                : "bg-amber-50 text-amber-700 border-amber-200"
            }`}>
              <ShieldCheck className="w-3 h-3" />
              신뢰도 {backendResult.risk_result.confidence_score}%
            </div>
          )}
        </div>
        {backendResult?.risk_result?.confidence_score && backendResult.risk_result.confidence_score < 95 && (
          <div className="mx-1 mb-3 p-2 bg-amber-50 border border-amber-100 rounded-lg flex gap-2 items-start">
            <Info className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
            <p className="text-[10px] text-amber-700 leading-tight">
              성분명 오타가 보정되었거나 유사 성분으로 매칭되었습니다. 인식된 약물/식품명이 정확한지 한 번 더 확인해 주세요.
            </p>
          </div>
        )}

        {/* Interaction Graph Section */}
        {(backendResult?.risk_result?.entities_involved?.drugs?.length > 0 || data.ingredients?.length > 0) && (
          <InteractionGraph 
            drugs={backendResult?.risk_result?.entities_involved?.drugs?.map((d: any) => d.raw) || []}
            foods={data.ingredients || []}
            riskLevel={riskLevel}
            matchedEntities={backendResult?.risk_result?.matched_entities}
          />
        )}

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
            secondaryRules={backendResult?.risk_result?.secondary_rules}
          />
        </motion.div>

        {/* OCR Visual Overlay Section */}
        {scanImageUrl && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-4 mt-4 overflow-hidden">
            <h2 className="text-sm font-bold text-gray-800 mb-3 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Maximize2 className="w-4 h-4 text-[#009688]" />
                분석 원본 시각화
              </span>
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-[10px] h-6 px-2 text-[#009688]"
                onClick={() => setShowOCR(!showOCR)}
              >
                {showOCR ? "오버레이 숨기기" : "오버레이 표시"}
              </Button>
            </h2>
            
            <div className="relative rounded-lg overflow-hidden bg-gray-900 aspect-video">
              <img 
                src={scanImageUrl} 
                alt="Scanned product" 
                className="w-full h-full object-contain"
              />
              
              <AnimatePresence>
                {showOCR && boundingBoxes?.map((box: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute pointer-events-none"
                    style={{
                      left: `${box.x}%`,
                      top: `${box.y}%`,
                      width: `${box.width}%`,
                      height: `${box.height}%`,
                    }}
                  >
                    <div className={`w-full h-full border-2 rounded ${
                      box.riskLevel === "danger" 
                        ? "border-red-500 bg-red-500/20" 
                        : box.riskLevel === "warning" 
                          ? "border-amber-500 bg-amber-500/20" 
                          : "border-green-500 bg-green-500/20"
                    }`} />
                    <div className="absolute top-0 left-0 -translate-y-full bg-black/60 text-[8px] text-white px-1 rounded whitespace-nowrap">
                      {box.text}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            <p className="text-[10px] text-gray-400 mt-2 italic text-center">
              * AI가 이미지에서 직접 추출하여 분석한 영역입니다.
            </p>
          </div>
        )}

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
                          {isVerified && <ShieldCheckIcon className="w-3 h-3 text-blue-500" />}
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
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
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

        {/* Pinpoint FAQ */}
        <PinpointFAQ
          userConditions={backendResult?.risk_result?.user_conditions || []}
          detectedDrugs={backendResult?.risk_result?.entities_involved?.drugs?.map((d: any) => d.raw) || []}
          detectedIngredients={data.ingredients || []}
        />

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
            onClick={handleShare}
          >
            <Share2 className="w-5 h-5 text-[#009688]" />
            <span className="text-[11px] font-bold">리포트 공유</span>
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

        {/* Footnote */}
        <div className="mt-8 mb-6 py-6 border-t border-gray-200 text-center">
          <p className="text-[10px] text-gray-400 leading-relaxed">
            본 결과는 AI의 보조 정보이며 의학적 확진이 아닙니다.<br />
            기저질환자의 최종 판단은 전문가와 상담하시기 바랍니다.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 mb-4">
          <Button
            onClick={() => recordIntake()}
            disabled={isSaved || !!(location.state?.scanData?.id && !location.state?.fromScan)}
            className={`flex-1 h-12 font-bold shadow-sm border ${isSaved || !!(location.state?.scanData?.id && !location.state?.fromScan)
              ? "bg-gray-100 border-gray-200 text-gray-400"
              : "bg-white border-[#009688] text-[#009688] hover:bg-[#E0F2F1]"
              }`}
          >
            {isSaved || !!(location.state?.scanData?.id && !location.state?.fromScan) ? "기록 완료" : "기록으로 남기기"}
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

      {/* Counseling Overlay */}
      <CounselingOverlay
        riskLevel={riskLevel}
        isOpen={isCounselingOpen}
        onClose={() => setIsCounselingOpen(false)}
      />

      {/* Hidden Report Card for Capturing */}
      <div className="fixed -left-[9999px] top-0">
        <ShareReportCard
          ref={reportRef}
          foodName={data.foodName}
          riskLevel={riskLevel}
          summary={riskInfo.message}
          matchedEntities={backendResult?.risk_result?.matched_entities}
          date={new Date().toLocaleDateString()}
        />
      </div>
    </div>
  );
}
