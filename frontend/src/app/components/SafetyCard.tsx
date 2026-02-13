import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { useState } from "react";

export type RiskLevel = "safe" | "warning" | "danger";

interface SafetyCardProps {
  riskLevel: RiskLevel;
  title: string;
  message: string;
  evidence?: string;
  evidenceSource?: string;
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
          <h3 className={`font-bold text-lg ${config.textColor} mb-2`}>
            {title}
          </h3>
          <p className="text-[#263238]">{message}</p>
        </div>
      </div>

      {evidence && (
        <div className="mt-4">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="text-sm text-gray-600 hover:text-[#009688] underline"
          >
            {showEvidence ? "근거 접기" : "근거 상세 보기"}
          </button>
          {showEvidence && (
            <div className="mt-3 p-3 bg-white/70 rounded-lg">
              <p className="text-sm text-gray-700 leading-relaxed">
                {evidence}
              </p>
              {evidenceSource && (
                <p className="text-xs text-gray-500 mt-2">
                  출처: {evidenceSource}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
