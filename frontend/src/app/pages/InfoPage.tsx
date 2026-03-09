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
              식품 내<br />핵심 성분
            </div>
            <span className="text-[#009688] text-lg font-bold">→</span>
            <div className="bg-[#009688] text-white text-xs px-3 py-2 rounded shadow-sm text-center font-bold">
              공식 룰 매칭<br />& 위험 판정
            </div>
          </div>
        </motion.div>


        {/* Section 5: 사용자 교육 콘텐츠 (신규) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-[#FF9800]/10 p-2 rounded-lg">
              <BookOpen className="w-6 h-6 text-[#FF9800]" />
            </div>
            <h2 className="text-lg font-bold text-[#263238]">사용자 교육 콘텐츠</h2>
          </div>

          <div className="space-y-6">
            {/* Video Education */}
            <div>
              <h3 className="text-sm font-bold text-[#263238] mb-3 flex items-center gap-2">
                <span className="w-1 h-4 bg-[#FF9800] rounded-full"></span>
                영상으로 배우는 안전한 식생활
              </h3>
              <div className="aspect-video bg-gray-100 rounded-xl flex items-center justify-center border-2 border-dashed border-gray-200 group cursor-pointer hover:bg-gray-50 transition">
                <div className="text-center">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-2 shadow-sm group-hover:scale-110 transition">
                    <Rocket className="w-6 h-6 text-[#FF9800] fill-[#FF9800]/20" />
                  </div>
                  <p className="text-xs text-gray-500 font-medium">교육 영상 시청하기 (3~5분)</p>
                </div>
              </div>
            </div>

            {/* Downloads */}
            <div>
              <h3 className="text-sm font-bold text-[#263238] mb-3 flex items-center gap-2">
                <span className="w-1 h-4 bg-[#FF9800] rounded-full"></span>
                가이드북 및 매뉴얼
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-[#FF9800]/30 transition cursor-pointer">
                  <p className="text-xs font-bold text-[#263238] mb-1">세이프잇 가이드</p>
                  <p className="text-[10px] text-gray-500">PDF 다운로드</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-[#FF9800]/30 transition cursor-pointer">
                  <p className="text-xs font-bold text-[#263238] mb-1">상담 준비 체크리스트</p>
                  <p className="text-[10px] text-gray-500">인쇄용 제공</p>
                </div>
              </div>
            </div>

            {/* Newsletter/News */}
            <div className="p-4 bg-[#FF9800]/5 border border-[#FF9800]/10 rounded-xl">
              <h3 className="text-xs font-bold text-[#F57C00] mb-2">📢 최신 건강 소식</h3>
              <ul className="space-y-2">
                <li className="text-[11px] text-[#A65B00] flex items-center justify-between border-b border-[#FF9800]/10 pb-2">
                  <span>환절기 고혈압 환자 주의해야 할 식품</span>
                  <ChevronRight className="w-3 h-3" />
                </li>
                <li className="text-[11px] text-[#A65B00] flex items-center justify-between">
                  <span>신규 당뇨병 임상 가이드라인 요약</span>
                  <ChevronRight className="w-3 h-3" />
                </li>
              </ul>
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
    </div >
  );
}

// Helper components if needed
function ChevronRight(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}
