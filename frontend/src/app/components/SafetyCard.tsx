import { ShieldCheck, Info, FileText, ChevronRight, AlertCircle, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

export interface SecondaryRule {
  rule_id: string;
  drug_name?: string;
  food_keyword?: string;
  risk_level: string;
  risk_type?: string;
  description?: string;
  title?: string;
  message?: string;
  evidence?: string;
  evidence_source?: string;
}

interface SafetyCardProps {
  riskLevel: "safe" | "warning" | "danger";
  title: string;
  message: string;
  evidence?: string;
  evidenceSource?: string;
  evidenceStrength?: "HIGH" | "MODERATE" | "LOW" | "EXPERT_PENDING";
  secondaryRules?: SecondaryRule[];
}

export function SafetyCard({
  riskLevel,
  title,
  message,
  evidence,
  evidenceSource,
  evidenceStrength,
  secondaryRules
}: SafetyCardProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const [openSecondary, setOpenSecondary] = useState<string | null>(null);

  const getTheme = () => {
    switch (riskLevel) {
      case "danger":
        return {
          bg: "bg-[#E53935]",
          lightBg: "bg-red-50",
          border: "border-red-100",
          text: "text-white",
          accent: "text-red-600",
          icon: "text-white",
          strengthBg: "bg-red-100/20",
          strengthText: "text-white"
        };
      case "warning":
        return {
          bg: "bg-[#FFB74D]",
          lightBg: "bg-orange-50",
          border: "border-orange-100",
          text: "text-white",
          accent: "text-orange-700",
          icon: "text-white",
          strengthBg: "bg-orange-100/30",
          strengthText: "text-white"
        };
      case "safe":
      default:
        return {
          bg: "bg-[#009688]",
          lightBg: "bg-green-50",
          border: "border-green-100",
          text: "text-white",
          accent: "text-green-700",
          icon: "text-white",
          strengthBg: "bg-green-100/20",
          strengthText: "text-white"
        };
    }
  };

  const theme = getTheme();

  return (
    <div className="space-y-4">
      {/* Primary Safety Card */}
      <div className={`rounded-xl shadow-lg border-2 ${theme.bg} overflow-hidden transition-all duration-300`}>
        {/* Risk Header */}
        <div className="p-5 flex items-start gap-4">
          <div className={`p-2 rounded-lg bg-white/20 backdrop-blur-sm`}>
            {riskLevel === "danger" ? (
              <AlertCircle className="w-6 h-6 text-white" />
            ) : riskLevel === "warning" ? (
              <Info className="w-6 h-6 text-white" />
            ) : (
              <ShieldCheck className="w-6 h-6 text-white" />
            )}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-white mb-1.5 leading-tight">
              {title}
            </h3>
            <p className="text-sm font-medium text-white/95 leading-relaxed">
              {message}
            </p>
          </div>
        </div>

        {/* Action/Evidence Footer (Compact) */}
        <div className="bg-white/10 backdrop-blur-sm border-t border-white/10">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="w-full flex items-center justify-between p-3"
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-white/80" />
              <span className="text-xs font-bold text-white">분석 요약 및 의학적 근거</span>
            </div>
            <ChevronRight className={`w-4 h-4 text-white/60 transition-transform duration-300 ${showEvidence ? 'rotate-90' : ''}`} />
          </button>

          <AnimatePresence>
            {showEvidence && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden bg-white/5"
              >
                <div className="p-4 space-y-3.5 border-t border-white/10">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-white/50 uppercase tracking-wider">분석 요약</span>
                      {evidenceStrength && (
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${theme.strengthBg} ${theme.strengthText}`}>
                          신뢰도 {evidenceStrength}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-white/90 leading-relaxed font-medium">
                      {evidence}
                    </p>
                  </div>
                  {evidenceSource && (
                    <div className="flex items-center gap-1.5 pt-1.5 border-t border-white/5">
                      <div className="px-1 py-0.5 bg-white/10 rounded text-[9px] text-white/60 font-medium">SOURCE</div>
                      <span className="text-[10px] text-white/40 italic font-medium">
                        {evidenceSource}
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Secondary Rules Section */}
      {secondaryRules && secondaryRules.length > 0 && (
        <div className="space-y-2.5">
          <div className="flex items-center gap-2 px-1">
            <Sparkles className="w-4 h-4 text-[#009688]" />
            <span className="text-xs font-bold text-gray-700">추가 확인이 필요한 주의사항</span>
            <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full font-bold">{secondaryRules.length}</span>
          </div>

          <div className="space-y-2">
            {secondaryRules.map((rule, idx) => (
              <div
                key={rule.rule_id}
                className="bg-white border border-gray-100 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"
              >
                <button
                  onClick={() => setOpenSecondary(openSecondary === rule.rule_id ? null : rule.rule_id)}
                  className="w-full flex items-center justify-between p-4 text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${rule.risk_level === 'RED' ? 'bg-[#E53935]' : 'bg-[#FFB74D]'}`} />
                    <span className="text-[14px] font-bold text-gray-800 leading-tight">
                      {rule.title || rule.description}
                    </span>
                  </div>
                  {openSecondary === rule.rule_id ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </button>

                <AnimatePresence>
                  {openSecondary === rule.rule_id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden border-t border-gray-50 bg-gray-50/50"
                    >
                      <div className="p-4 pt-3.5 space-y-3">
                        <p className="text-[14px] text-gray-700 leading-relaxed font-medium">
                          {rule.message || rule.description}
                        </p>
                        {rule.evidence && (
                          <div className="p-3 bg-white/50 rounded-lg border border-gray-100">
                            <div className="flex items-center gap-1.5 mb-1.5">
                              <Info className="w-3.5 h-3.5 text-gray-400" />
                              <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">상세 근거</span>
                            </div>
                            <p className="text-[13px] text-gray-600 leading-relaxed italic">
                              {rule.evidence}
                            </p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
