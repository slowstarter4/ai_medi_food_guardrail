import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Sparkles, Brain, Search, Database, CheckCircle2 } from "lucide-react";

const steps = [
  { icon: Search, text: "이미지에서 성분 정보를 추출하고 있습니다...", duration: 2000 },
  { icon: Brain, text: "사용자 복약 정보와 상호작용을 분석 중입니다...", duration: 2500 },
  { icon: Database, text: "의학적 근거 및 식품 데이터를 검토하고 있습니다...", duration: 2000 },
  { icon: Sparkles, text: "맞춤형 안전 가이드를 생성하는 중입니다...", duration: 2000 },
];

export function AILoadingSequence() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1);
      }
    }, steps[currentStep].duration);

    return () => clearTimeout(timer);
  }, [currentStep]);

  const Icon = steps[currentStep].icon;

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="relative mb-8">
        {/* Outer Glow Effect */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute inset-0 bg-[#009688] blur-2xl rounded-full"
        />
        
        {/* Icon Container */}
        <motion.div
          key={currentStep}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 1.2, opacity: 0 }}
          className="relative z-10 w-20 h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center border-2 border-[#009688]/20"
        >
          <Icon className="w-10 h-10 text-[#009688]" />
        </motion.div>

        {/* Floating Particles */}
        {[...Array(4)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              y: [-10, 10, -10],
              x: [-10, 10, -10],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + i,
              repeat: Infinity,
              delay: i * 0.5,
            }}
            className="absolute w-2 h-2 bg-[#009688] rounded-full"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Progress Text */}
      <div className="space-y-4">
        <AnimatePresence mode="wait">
          <motion.p
            key={currentStep}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            className="text-lg font-bold text-gray-800 h-14"
          >
            {steps[currentStep].text}
          </motion.p>
        </AnimatePresence>

        {/* Step Indicator Tags */}
        <div className="flex gap-1.5 justify-center">
          {steps.map((_, i) => (
            <motion.div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-500 ${
                i <= currentStep ? "w-8 bg-[#009688]" : "w-2 bg-gray-200"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Subtle Hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-12 text-xs text-gray-400 font-medium tracking-tight"
      >
        AI가 정밀 분석을 수행하는 동안 잠시만 기다려 주세요
      </motion.p>
    </div>
  );
}
