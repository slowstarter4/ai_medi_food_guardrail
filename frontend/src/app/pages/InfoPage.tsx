import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { ArrowLeft, BookOpen, Shield, Target, Rocket } from "lucide-react";
import { motion } from "motion/react";

export function InfoPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-24">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 mb-4 hover:opacity-80"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>뒤로 가기</span>
        </button>
        <h1 className="text-2xl font-bold">서비스 소개 및 분석 기준</h1>
        <p className="text-white/90 mt-1">SafeEat의 신뢰할 수 있는 데이터 기준</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 -mt-4 space-y-6">
        
        {/* Section 1: 투명한 데이터 출처 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-[#3F51B5]/10 p-2 rounded-lg">
              <BookOpen className="w-6 h-6 text-[#3F51B5]" />
            </div>
            <h2 className="text-lg font-bold text-[#263238]">투명한 데이터 출처</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4 leading-relaxed">
            분석에 사용된 모든 데이터는 공신력 있는 기관의 검증된 자료를 바탕으로 구성되었습니다.
          </p>
          <ul className="space-y-3">
            <li className="flex gap-2">
              <span className="text-lg">💊</span>
              <div>
                <p className="font-semibold text-sm text-[#263238]">약물 및 상호작용 정보</p>
                <p className="text-xs text-gray-500">식약처 의약품안전나라(e약은요), FDA Drug Label (DailyMed), DUR 시스템</p>
              </div>
            </li>
            <li className="flex gap-2">
              <span className="text-lg">🥦</span>
              <div>
                <p className="font-semibold text-sm text-[#263238]">식품 영양성분 정보</p>
                <p className="text-xs text-gray-500">식품안전나라(식약처), 국가표준식품성분표(농진청), USDA FoodData Central</p>
              </div>
            </li>
            <li className="flex gap-2">
              <span className="text-lg">📋</span>
              <div>
                <p className="font-semibold text-sm text-[#263238]">임상 평가 기준</p>
                <p className="text-xs text-gray-500">주요 임상 가이드라인 (ADA 당뇨, ACCP 등) 및 약리학/임상 논문</p>
              </div>
            </li>
          </ul>
        </motion.div>

        {/* Section 2: 안전성 평가 기준 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-[#4CAF50]/10 p-2 rounded-lg">
              <Shield className="w-6 h-6 text-[#4CAF50]" />
            </div>
            <h2 className="text-lg font-bold text-[#263238]">안전성 평가 등급 기준</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4 leading-relaxed">
            개인의 질환 및 복용 약물에 맞춰, 허가사항 및 임상 가이드라인의 "경고 강도"를 기준으로 3단계 등급을 부여합니다.
          </p>
          
          <div className="space-y-3">
            <div className="p-3 bg-[#E53935]/5 border border-[#E53935]/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-3 h-3 rounded-full bg-[#E53935]"></span>
                <span className="font-bold text-[#E53935] text-sm">섭취 중단 권고 (RED)</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed">
                의약품 허가사항 내 "병용금기 / 피해야 함" 등 즉각적이고 중대한 부작용(출혈, 심혈관 이상 등) 위험이 공식 보고된 경우
              </p>
            </div>
            
            <div className="p-3 bg-[#FFB74D]/5 border border-[#FFB74D]/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-3 h-3 rounded-full bg-[#FFB74D]"></span>
                <span className="font-bold text-[#F57C00] text-sm">주의 요망 (YELLOW)</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed">
                허가사항에 "주의 / 모니터링 필요" 문구가 있으며, 부작용 가능성이 있으나 용량/시간 조절로 대처 가능한 경우
              </p>
            </div>

            <div className="p-3 bg-[#4CAF50]/5 border border-[#4CAF50]/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-3 h-3 rounded-full bg-[#4CAF50]"></span>
                <span className="font-bold text-[#4CAF50] text-sm">안전 (GREEN)</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed">
                해당 조직에 대한 공식적인 상호작용 위험 경고가 보고되지 않아, 일반적인 섭취가 가능한 경우
              </p>
            </div>
          </div>
        </motion.div>

        {/* Section 3: 개인 맞춤형 분석 원리 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-[#009688]/10 p-2 rounded-lg">
              <Target className="w-6 h-6 text-[#009688]" />
            </div>
            <h2 className="text-lg font-bold text-[#263238]">개인 맞춤형 분석 원리</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4 leading-relaxed">
            단순한 음식명 비교가 아닌, <b>"식품의 핵심 위험 성분"</b>과 개인의 <b>"질환/약물"</b>을 기반으로 상호작용을 파악합니다.
          </p>
          <div className="flex items-center justify-center p-4 bg-gray-50 rounded-xl my-4 gap-2">
            <div className="text-center">
              <div className="bg-white border text-xs px-2 py-1 rounded shadow-sm">개인 질환 이력</div>
              <div className="text-[10px] text-gray-400 mt-1">&</div>
              <div className="bg-white border text-xs px-2 py-1 rounded shadow-sm">복용 중인 약물</div>
            </div>
            <span className="text-gray-400 text-lg">+</span>
            <div className="bg-white border border-[#2196F3] text-[#2196F3] text-xs px-2 py-2 rounded shadow-sm text-center font-medium">
              식품 내<br/>핵심 성분
            </div>
            <span className="text-[#009688] text-lg font-bold">→</span>
            <div className="bg-[#009688] text-white text-xs px-3 py-2 rounded shadow-sm text-center font-bold">
              공식 룰 매칭<br/>& 위험 판정
            </div>
          </div>
        </motion.div>

        {/* Section 4: 서비스 발전 로드맵 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-[#263238] text-white rounded-2xl shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-white/10 p-2 rounded-lg">
              <Rocket className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-lg font-bold">서비스 향후 로드맵</h2>
          </div>
          <p className="text-sm text-white/80 mb-6 leading-relaxed">
            현재 SafeEat은 사용자 여러분께 빠르고 직관적인 초기 가이드를 제공하는 <b>"AI 보조 도구"</b>입니다. 
            더욱 완전한 헬스케어 서비스를 위해 다음과 같이 진화할 예정입니다.
          </p>
          
          <div className="relative border-l-2 border-[#009688] ml-3 pl-5 space-y-6">
            <div className="relative">
              <span className="absolute -left-[27px] bg-[#009688] w-4 h-4 rounded-full border-4 border-[#263238]"></span>
              <p className="font-bold text-sm text-[#009688]">Phase 1 (현재)</p>
              <p className="text-sm font-medium mt-1">공공 보건 데이터 기반 AI 1차 스크리닝</p>
            </div>
            <div className="relative">
              <span className="absolute -left-[27px] bg-gray-500 w-4 h-4 rounded-full border-4 border-[#263238]"></span>
              <p className="font-bold text-sm text-gray-400">Phase 2 (예정)</p>
              <p className="text-sm font-medium mt-1 text-white/70">전문가(의사/약사) 자문위원단 교차 검증 시스템 도입</p>
            </div>
            <div className="relative">
              <span className="absolute -left-[27px] bg-gray-500 w-4 h-4 rounded-full border-4 border-[#263238]"></span>
              <p className="font-bold text-sm text-gray-400">Phase 3 (예정)</p>
              <p className="text-sm font-medium mt-1 text-white/70">비대면 진료 서비스 연계 및 주치의 다이렉트 상담 기능</p>
            </div>
          </div>
        </motion.div>

        {/* Disclaimer Warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-sm text-yellow-800 leading-relaxed">
          <span className="font-bold">⚠️ 주의사항:</span> 본 서비스가 제공하는 결과는 참고용 보조 지표입니다. 
          질병의 진단, 치료, 예방 등 최종적인 의학적 결정은 반드시 의사 또는 약사와 같은 의료 전문가와 상담하시기 바랍니다.
        </div>
      </div>
      <BottomNav />
    </div>
  );
}
