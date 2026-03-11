import React from 'react';
import { ShieldCheck, AlertCircle, Info, Pill, Utensils } from 'lucide-react';

interface ShareReportCardProps {
  foodName: string;
  riskLevel: "safe" | "warning" | "danger";
  summary: string;
  matchedEntities?: {
    drug: string;
    target: string;
  };
  date: string;
}

export const ShareReportCard = React.forwardRef<HTMLDivElement, ShareReportCardProps>(
  ({ foodName, riskLevel, summary, matchedEntities, date }, ref) => {
    const theme = {
      danger: { color: "#EF4444", bg: "bg-red-50", icon: AlertCircle, label: "섭취 중단 권고" },
      warning: { color: "#F59E0B", bg: "bg-amber-50", icon: Info, label: "주의하여 섭취" },
      safe: { color: "#10B981", bg: "bg-emerald-50", icon: ShieldCheck, label: "안전하게 섭취" },
    }[riskLevel];

    return (
      <div 
        ref={ref}
        className="w-[400px] bg-white p-8 rounded-2xl flex flex-col gap-6 shadow-2xl border border-gray-100"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        {/* Logo & Header */}
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#009688] rounded-lg flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-black text-[#009688]">SafeEat</span>
          </div>
          <span className="text-[10px] text-gray-400 font-medium">{date}</span>
        </div>

        {/* Food Name */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">{foodName}</h2>
          <p className="text-xs text-gray-500 mt-1">AI 맞춤 상호작용 분석 리포트</p>
        </div>

        {/* Risk Status */}
        <div className={`${theme.bg} p-6 rounded-xl flex flex-col items-center gap-3 border-2`} style={{ borderColor: theme.color }}>
          <theme.icon className="w-10 h-10" style={{ color: theme.color }} />
          <div className="text-center">
            <h3 className="text-lg font-bold" style={{ color: theme.color }}>{theme.label}</h3>
            <p className="text-sm text-gray-700 mt-2 leading-relaxed font-medium">
              {summary}
            </p>
          </div>
        </div>

        {/* Interaction Map Summary (Compact) */}
        {matchedEntities && riskLevel !== "safe" && (
          <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
             <div className="flex items-center justify-center gap-4">
                <div className="flex flex-col items-center">
                  <Pill className="w-5 h-5 text-blue-500 mb-1" />
                  <span className="text-[10px] font-bold text-gray-500">{matchedEntities.drug}</span>
                </div>
                <div className="w-8 h-0.5" style={{ backgroundColor: theme.color }} />
                <div className="flex flex-col items-center">
                  <Utensils className="w-5 h-5 text-green-500 mb-1" />
                  <span className="text-[10px] font-bold text-gray-500">{matchedEntities.target}</span>
                </div>
             </div>
             <p className="text-[9px] text-center text-gray-400 mt-2 italic">상호작용 위험이 감지되었습니다</p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-4 pt-4 border-t text-center">
          <p className="text-[10px] text-gray-400 leading-relaxed">
            본 리포트는 AI 보조 정보이며 의학적 확진이 아닙니다.<br />
            정확한 판단은 반드시 전문가와 상담하시기 바랍니다.
          </p>
          <div className="mt-3 text-[11px] font-bold text-[#009688]/60">
            Powered by SafeEat AI Guardrail
          </div>
        </div>
      </div>
    );
  }
);

ShareReportCard.displayName = "ShareReportCard";
