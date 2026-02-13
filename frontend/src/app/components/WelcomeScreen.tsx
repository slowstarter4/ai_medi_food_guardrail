import { motion } from "motion/react";
import { ShieldCheck, Camera, Heart, Bell } from "lucide-react";
import { Button } from "../components/ui/button";

interface WelcomeScreenProps {
  onComplete: () => void;
}

export function WelcomeScreen({ onComplete }: WelcomeScreenProps) {
  const features = [
    {
      icon: ShieldCheck,
      title: "안전한 먹거리 보호",
      description: "AI가 실시간으로 식품 위험도를 분석합니다",
    },
    {
      icon: Camera,
      title: "간편한 스캔",
      description: "카메라로 성분표를 비추면 즉시 인식",
    },
    {
      icon: Heart,
      title: "맞춤형 대체 식품",
      description: "안전한 대체 식품을 추천합니다",
    },
    {
      icon: Bell,
      title: "복약 알림",
      description: "복용 시간을 놓치지 않도록 알려드립니다",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#009688] to-[#00796B] text-white flex flex-col items-center justify-center p-6">
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-12"
      >
        <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
          <ShieldCheck className="w-12 h-12 text-[#009688]" />
        </div>
        <h1 className="text-4xl font-bold mb-3">SafeEat</h1>
        <p className="text-xl text-white/90">당신의 식탁 위, AI가 지키는 안전</p>
      </motion.div>

      <div className="max-w-md w-full space-y-6 mb-12">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 + index * 0.1 }}
            className="flex gap-4 items-start bg-white/10 backdrop-blur-sm rounded-xl p-4"
          >
            <div className="bg-white/20 rounded-lg p-3 flex-shrink-0">
              <feature.icon className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold mb-1">{feature.title}</h3>
              <p className="text-sm text-white/80">{feature.description}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="w-full max-w-md"
      >
        <Button
          onClick={onComplete}
          className="w-full bg-white text-[#009688] hover:bg-white/90 py-6 text-lg font-bold rounded-xl shadow-xl"
        >
          시작하기
        </Button>
        <p className="text-center text-sm text-white/70 mt-4">
          쉽고 똑똑한 건강한 한입
        </p>
      </motion.div>
    </div>
  );
}
