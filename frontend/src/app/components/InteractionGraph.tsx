import { motion } from "motion/react";
import { Pill, Utensils, AlertTriangle } from "lucide-react";

interface InteractionGraphProps {
  drugs: string[];
  foods: string[];
  riskLevel: "safe" | "warning" | "danger";
  matchedEntities?: {
    drug: string;
    target: string;
  };
}

export function InteractionGraph({ drugs, foods, riskLevel, matchedEntities }: InteractionGraphProps) {
  const colorMap = {
    danger: "#EF4444",
    warning: "#F59E0B",
    safe: "#10B981",
  };

  const color = colorMap[riskLevel];

  return (
    <div className="py-6 flex flex-col items-center">
      <div className="flex items-center justify-between w-full max-w-[280px] relative">
        {/* Connection Line */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gray-100 -z-10">
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            className="h-full origin-left"
            style={{ backgroundColor: color }}
            transition={{ duration: 1, delay: 0.5 }}
          />
        </div>

        {/* Drug Node */}
        <div className="flex flex-col items-center gap-2">
          <motion.div
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="w-14 h-14 rounded-full bg-white shadow-md border-2 border-gray-100 flex items-center justify-center relative"
          >
            <Pill className="w-7 h-7 text-blue-500" />
            <motion.div 
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-blue-500 border-2 border-white" 
            />
          </motion.div>
          <span className="text-[10px] font-bold text-gray-500 max-w-[80px] text-center truncate">
            {matchedEntities?.drug || drugs[0] || "복용 약물"}
          </span>
        </div>

        {/* Center Alert Icon */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", delay: 1 }}
          className="bg-white p-2 rounded-full shadow-lg border-2 z-10"
          style={{ borderColor: color }}
        >
          <AlertTriangle className="w-6 h-6" style={{ color }} />
        </motion.div>

        {/* Food Node */}
        <div className="flex flex-col items-center gap-2">
          <motion.div
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-14 h-14 rounded-full bg-white shadow-md border-2 border-gray-100 flex items-center justify-center relative"
          >
            <Utensils className="w-7 h-7 text-green-500" />
            <motion.div 
               animate={{ scale: [1, 1.1, 1] }}
               transition={{ repeat: Infinity, duration: 2, delay: 1 }}
               className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-green-500 border-2 border-white" 
            />
          </motion.div>
          <span className="text-[10px] font-bold text-gray-500 max-w-[80px] text-center truncate">
            {matchedEntities?.target || foods[0] || "대상 식품"}
          </span>
        </div>
      </div>
      
      {riskLevel !== "safe" && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="mt-4 text-[11px] font-bold"
          style={{ color }}
        >
          주의: 두 성분 간의 상호작용이 감지되었습니다
        </motion.p>
      )}
    </div>
  );
}
