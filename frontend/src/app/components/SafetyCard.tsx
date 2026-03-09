import { AlertTriangle, CheckCircle, XCircle, ShieldCheck, ShieldAlert, Shield, Info, Lightbulb } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export type RiskLevel = "safe" | "warning" | "danger";

interface SecondaryRule {
  rule_id: string;
  risk_level: string;
  description: string;
  risk_type: string;
}

interface SafetyCardProps {
  riskLevel: RiskLevel;
  title: string;
  message: string;
  evidence?: string;
  evidenceSource?: string;
  evidenceStrength?: "HIGH" | "MODERATE" | "LOW" | "EXPERT_PENDING";
  secondaryRules?: SecondaryRule[];
}

const riskConfig = {
  safe: {
    headerBg: "bg-[#E8F5E9]", // 부드러운 그린
    headerTextColor: "text-[#2E7D32]",
    subTitle: "Normal",
    icon: CheckCircle,
    label: "✅ 안전 상태",
  },
  warning: {
    headerBg: "bg-[#FFF9C4]", // 파스텔 옐로우
    headerTextColor: "text-[#F57F17]",
    subTitle: "Low/Caution",
    icon: AlertTriangle,
    label: "⚠️ 주의 권고",
  },
  danger: {
    headerBg: "bg-[#E53935]", // 강렬한 레드
    headerTextColor: "text-white",
    subTitle: "High/Danger",
    icon: XCircle,
    label: "🚨 긴급 위급",
  },
};

export function SafetyCard({
  riskLevel,
  title,
  message,
  evidence,
  evidenceSource,
  evidenceStrength,
  secondaryRules,
}: SafetyCardProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const config = riskConfig[riskLevel];
  const Icon = config.icon;

  return (
    <div className="flex flex-col gap-3 mb-6">
      {/* 1. Header Status Card */}
      <motion.div
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className={`${config.headerBg} rounded-[1.8rem] p-6 shadow-sm relative overflow-hidden`}
      >
        <div className="relative z-10">
          <p className={`${config.headerTextColor} font-bold text-xs mb-3 opacity-80 uppercase tracking-wide`}>
            {title}
          </p>
          <div className="flex items-baseline gap-2 mb-1">
            <span className={`${config.headerTextColor} text-4xl font-black tracking-tighter`}>
              {riskLevel === "danger" ? "High" : riskLevel === "warning" ? "Caution" : "Normal"}
            </span>
          </div>
          <p className={`${config.headerTextColor} text-base font-black opacity-90`}>
            {config.subTitle}
          </p>
        </div>

        {/* Background Accent Icon */}
        <Icon className={`absolute -right-3 -bottom-3 w-28 h-28 ${riskLevel === "danger" ? "text-white/10" : "text-black/5"}`} />
      </motion.div>

      {/* 2. Description Card (Main Analysis Message) */}
      <motion.div
        initial={{ y: 0, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-white/70 backdrop-blur-md rounded-[1.2rem] p-5 border border-white/50 shadow-sm"
      >
        <h4 className="text-[#4A148C] font-black text-[10px] mb-2 uppercase tracking-widest opacity-50">분석 요약</h4>
        <p className="text-[#263238] text-[14px] font-bold leading-[1.6]">
          {message}
        </p>
      </motion.div>

      {/* 3. Action/Evidence Card (Compacted) */}
      <motion.div
        initial={{ y: 0, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-[#EDE7F6]/40 rounded-[1.2rem] p-5 relative overflow-hidden border border-[#4A148C]/5"
      >
        <div className="flex items-start gap-3">
          <div className="bg-[#4A148C] p-2 rounded-xl shadow-md shrink-0">
            <Lightbulb className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="text-[#4A148C] font-black text-[11px] mb-1 uppercase tracking-wide">
              {riskLevel === "danger" ? "🚨 즉시 권고" : "✅ 다음 조치"}
            </h4>
            <div className="flex flex-col gap-2">
              <p className="text-[#263238] text-[13px] font-semibold leading-relaxed opacity-70">
                {riskLevel === "danger"
                  ? "섭취를 즉시 중단하고 전문가와 상담하세요."
                  : (evidence || "전문가와 상담해보시는 것을 추천드립니다.")}
              </p>

              {evidence && (
                <button
                  onClick={() => setShowEvidence(!showEvidence)}
                  className="text-[9px] font-black text-[#4A148C]/60 flex items-center gap-1 hover:text-[#4A148C] transition-colors"
                >
                  <Info className="w-3 h-3" />
                  {showEvidence ? "상세 근거 숨기기" : "의학적 근거 보기"}
                </button>
              )}
            </div>
          </div>
        </div>

        <AnimatePresence>
          {showEvidence && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-3 pt-3 border-t border-[#4A148C]/10"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-black tracking-widest ${evidenceStrength === "HIGH" ? "bg-blue-100 text-blue-700" : "bg-orange-100 text-orange-700"
                    }`}>
                    EVIDENCE: {evidenceStrength}
                  </span>
                </div>
                {evidenceSource && (
                  <p className="text-[8px] text-gray-400 font-bold uppercase tracking-widest">
                    Source: {evidenceSource}
                  </p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* 4. Secondary Alerts (Supplementary Precautions) */}
      {secondaryRules && secondaryRules.length > 0 && (
        <motion.div
          initial={{ y: 0, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col gap-2 mt-1"
        >
          <div className="flex items-center justify-between px-1">
            <h4 className="text-[#4A148C] font-black text-[10px] flex items-center gap-1.5 opacity-60">
              <ShieldAlert className="w-3 h-3 text-orange-500" />
              보조 주의사항
            </h4>
            <span className="text-[9px] font-bold text-[#4A148C]/50 bg-[#4A148C]/5 px-2 py-0.5 rounded-full">
              {secondaryRules.length}건 더 발견됨
            </span>
          </div>

          <div className="flex flex-col gap-2">
            {secondaryRules.map((rule) => (
              <motion.div
                key={rule.rule_id}
                whileHover={{ scale: 1.01 }}
                className="bg-white/80 rounded-[1rem] p-4 border border-white shadow-[0_2px_8px_rgba(0,0,0,0.02)] flex items-start gap-4 transition-all"
              >
                <div className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${rule.risk_level.toLowerCase() === "red" ? "bg-[#E53935]" : "bg-[#F57F17]"
                  }`} />
                <div className="flex-1">
                  <p className="text-[13px] font-bold text-[#263238] leading-[1.5]">
                    {rule.description}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-[9px] font-black text-[#4A148C]/30 uppercase tracking-tighter">
                      {rule.risk_type}
                    </span>
                    <span className="text-[9px] font-bold text-gray-200">
                      ID: {rule.rule_id}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
