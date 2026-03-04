import { AlertTriangle, CheckCircle, XCircle, ShieldCheck, ShieldAlert, Shield } from "lucide-react";
import { useState } from "react";

export type RiskLevel = "safe" | "warning" | "danger";

interface SafetyCardProps {
  riskLevel: RiskLevel;
  title: string;
  message: string;
  evidence?: string;
  evidenceSource?: string;
  evidenceStrength?: "HIGH" | "MODERATE" | "LOW" | "EXPERT_PENDING";
}

const riskConfig = {
  safe: {
    bgColor: "bg-[#4CAF50]/10",
    borderColor: "border-[#4CAF50]",
    textColor: "text-[#4CAF50]",
    icon: CheckCircle,
  },
  warning: {
    bgColor: "bg-[#FFB74D]/10",
    borderColor: "border-[#FFB74D]",
    textColor: "text-[#FFB74D]",
    icon: AlertTriangle,
  },
  danger: {
    bgColor: "bg-[#E53935]/10",
    borderColor: "border-[#E53935]",
    textColor: "text-[#E53935]",
    icon: XCircle,
  },
};

export function SafetyCard({
  riskLevel,
  title,
  message,
  evidence,
  evidenceSource,
}: SafetyCardProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const config = riskConfig[riskLevel];
  const Icon = config.icon;

  return (
    <div
      className={`${config.bgColor} ${config.borderColor} border-2 rounded-xl p-4 mb-4`}
    >
      <div className="flex items-start gap-3 mb-3">
        <Icon className={`w-6 h-6 ${config.textColor} flex-shrink-0 mt-1`} />
        <div className="flex-1">
          <h3 className={`font-bold text-lg ${config.textColor} mb-2 uppercase tracking-tight`}>
            {title}
          </h3>
          <p className="text-[#263238] font-medium leading-relaxed">{message}</p>
        </div>
      </div>

      {evidence && (
        <div className="mt-4 pt-4 border-t border-black/5">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="flex items-center gap-1.5 text-xs font-bold text-gray-500 hover:text-[#009688] transition-colors"
          >
            {showEvidence ? "근거 지표 접기" : "의학적 근거 지표 보기"}
            <span className={`transform transition-transform ${showEvidence ? 'rotate-180' : ''}`}>▼</span>
          </button>

          {showEvidence && (
            <div className="mt-3 p-3 bg-white/80 rounded-lg shadow-inner">
              <div className="flex items-center gap-2 mb-2.5">
                {evidenceStrength === "HIGH" && (
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-bold rounded-full">
                    <ShieldCheck className="w-3 h-3" />
                    검증된 권고 (HIGH)
                  </span>
                )}
                {evidenceStrength === "MODERATE" && (
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-orange-100 text-orange-700 text-[10px] font-bold rounded-full">
                    <ShieldAlert className="w-3 h-3" />
                    주의 권고 (MODERATE)
                  </span>
                )}
                {evidenceStrength === "EXPERT_PENDING" && (
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-600 text-[10px] font-bold rounded-full">
                    <Shield className="w-3 h-3" />
                    전문가 검토 중
                  </span>
                )}
              </div>

              <p className="text-sm text-gray-700 leading-relaxed mb-3">
                {evidence}
              </p>

              {evidenceSource && (
                <div className="flex items-center gap-1.5 pt-2 border-t border-gray-100 uppercase tracking-tighter">
                  <CheckCircle className="w-3 h-3 text-[#009688]" />
                  <p className="text-[10px] text-[#009688] font-bold">
                    REFERENCE: {evidenceSource}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
