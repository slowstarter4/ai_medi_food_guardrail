import { BottomNav } from "../components/BottomNav";
import { Bell, Shield, HelpCircle, Info, Trash2, ChevronRight } from "lucide-react";
import { Button } from "../components/ui/button";
import { useState } from "react";
import { toast } from "sonner";

export function SettingsPage() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const clearAllData = () => {
    if (
      window.confirm(
        "모든 데이터를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
      )
    ) {
      localStorage.clear();
      toast.success("모든 데이터가 삭제되었습니다");
      window.location.reload();
    }
  };

  const faqItems = [
    {
      q: "SafeEat은 어떤 서비스인가요?",
      a: "AI 기반 개인 맞춤형 식품·복약 안전 서비스로, 복용 중인 약물과 식품 성분 간의 상호작용을 실시간으로 분석하여 위험을 경고합니다.",
    },
    {
      q: "데이터는 안전하게 보호되나요?",
      a: "모든 개인정보는 암호화되어 저장되며, 제3자와 공유되지 않습니다. 현재 버전은 브라우저 로컬 스토리지를 사용합니다.",
    },
    {
      q: "처방전을 어떻게 등록하나요?",
      a: "프로필 페이지에서 '처방전 업로드' 버튼을 통해 사진을 업로드하거나, 약물명을 직접 입력할 수 있습니다.",
    },
    {
      q: "스캔 정확도는 얼마나 되나요?",
      a: "최신 OCR 기술과 식약처 데이터베이스를 기반으로 95% 이상의 정확도를 제공합니다. 부정확한 경우 수동 수정이 가능합니다.",
    },
  ];

  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-20">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8">
        <h1 className="text-2xl font-bold">설정</h1>
        <p className="text-white/90 mt-2">앱 설정 및 개인정보 관리</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 -mt-4">
        {/* Notification Settings */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-[#009688]" />
            알림 설정
          </h2>

          <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-[#009688] cursor-pointer transition">
            <div>
              <p className="font-medium text-[#263238]">복약 알림</p>
              <p className="text-sm text-gray-600">
                복용 시간이 되면 알림을 받습니다
              </p>
            </div>
            <input
              type="checkbox"
              checked={notificationsEnabled}
              onChange={(e) => {
                setNotificationsEnabled(e.target.checked);
                toast.success(
                  e.target.checked
                    ? "알림이 활성화되었습니다"
                    : "알림이 비활성화되었습니다"
                );
              }}
              className="w-5 h-5 text-[#009688] rounded focus:ring-[#009688]"
            />
          </label>
        </div>

        {/* Privacy */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#009688]" />
            개인정보 보호
          </h2>

          <div className="space-y-3">
            <button
              className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-[#009688] hover:bg-gray-50 transition text-left"
              onClick={() =>
                alert(
                  "개인정보 처리방침:\n\n1. 수집 항목: 복약 정보, 건강 상태\n2. 수집 목적: 맞춤형 식품 안전 분석\n3. 보유 기간: 서비스 이용 기간\n4. 제3자 제공: 없음\n5. 암호화 보관"
                )
              }
            >
              <div>
                <p className="font-medium text-[#263238]">개인정보 처리방침</p>
                <p className="text-sm text-gray-600">
                  데이터 수집 및 처리 정책 확인
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>

            <button
              className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-[#009688] hover:bg-gray-50 transition text-left"
              onClick={() =>
                alert(
                  "데이터 보안:\n\n• 모든 데이터는 암호화되어 저장됩니다\n• 제3자와 정보를 공유하지 않습니다\n• 익명화된 통계만 사용됩니다\n• 언제든지 데이터를 삭제할 수 있습니다"
                )
              }
            >
              <div>
                <p className="font-medium text-[#263238]">데이터 보안</p>
                <p className="text-sm text-gray-600">암호화 및 보안 정책</p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600 mb-3">
              SafeEat은 의료 정보를 안전하게 보호하며, PII(개인 식별 정보) 수집을
              최소화합니다.
            </p>
            <Button
              variant="destructive"
              className="w-full"
              onClick={clearAllData}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              모든 데이터 삭제
            </Button>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4 flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-[#009688]" />
            자주 묻는 질문
          </h2>

          <div className="space-y-2">
            {faqItems.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg">
                <button
                  onClick={() =>
                    setExpandedFaq(expandedFaq === index ? null : index)
                  }
                  className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition text-left"
                >
                  <span className="font-medium text-[#263238] pr-2">
                    {item.q}
                  </span>
                  <ChevronRight
                    className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${expandedFaq === index ? "rotate-90" : ""
                      }`}
                  />
                </button>
                {expandedFaq === index && (
                  <div className="px-3 pb-3">
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {item.a}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* About */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <h2 className="font-bold text-[#263238] mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-[#009688]" />
            앱 정보
          </h2>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">버전</span>
              <span className="font-medium">1.0.0</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">개발</span>
              <span className="font-medium">SafeEat Team</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">문의</span>
              <span className="font-medium text-[#009688]">
                support@safeeat.com
              </span>
            </div>

            <div className="pt-3 border-t">
              <Button
                variant="outline"
                className="w-full border-[#009688] text-[#009688] hover:bg-[#009688]/5"
                onClick={() => {
                  localStorage.removeItem("hasVisited");
                  window.location.href = "/";
                }}
              >
                서비스 안내(튜토리얼) 다시보기
              </Button>
            </div>
          </div>
        </div>

        {/* Slogan */}
        <div className="bg-[#009688]/5 border border-[#009688]/20 rounded-xl p-4 text-center">
          <p className="text-sm font-medium text-[#263238]">
            쉽고 똑똑한 건강한 한입
          </p>
          <p className="text-xs text-gray-600 mt-1">SafeEat - 안전한 식생활 파트너</p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
