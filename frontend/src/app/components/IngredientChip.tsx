import { X } from "lucide-react";
import type { RiskLevel } from "./SafetyCard";

interface IngredientChipProps {
  label: string;
  riskLevel?: RiskLevel;
  onRemove?: () => void;
  onClick?: () => void;
}

const riskColors = {
  safe: "border-[#4CAF50] bg-[#4CAF50]/10 text-[#4CAF50]",
  warning: "border-[#FFB74D] bg-[#FFB74D]/10 text-[#FFB74D]",
  danger: "border-[#E53935] bg-[#E53935]/10 text-[#E53935]",
};

export function IngredientChip({
  label,
  riskLevel,
  onRemove,
  onClick,
}: IngredientChipProps) {
  const colorClass = riskLevel
    ? riskColors[riskLevel]
    : "border-gray-300 bg-gray-50 text-gray-700";

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border-2 ${colorClass} ${
        onClick ? "cursor-pointer hover:opacity-80" : ""
      }`}
      onClick={onClick}
    >
      <span className="text-sm font-medium">{label}</span>
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="hover:opacity-70"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
