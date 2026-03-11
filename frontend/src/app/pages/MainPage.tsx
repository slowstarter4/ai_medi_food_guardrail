import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { MedicationTag } from "../components/MedicationTag";
import { WelcomeScreen } from "../components/WelcomeScreen";
import { SplashScreen } from "../components/SplashScreen";
import { Bell, Camera, Clock, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "../components/ui/button";
import { useEffect, useState } from "react";

interface Medication {
  id: string;
  name: string;
  dosage: string;
}

interface ScanResult {
  id: string;
  foodName: string;
  riskLevel: "safe" | "warning" | "danger";
  date: string;
  explanation?: string;
  ingredients?: string[];
  backendResult?: any;
  boundingBoxes?: any;
}

export function MainPage() {
  const navigate = useNavigate();
  const [medications, setMedications] = useState<Medication[]>([]);
  const [recentScans, setRecentScans] = useState<ScanResult[]>([]);
  const [nextDoseTime, setNextDoseTime] = useState<string>("오후 9:00");
  const [showWelcome, setShowWelcome] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Splash screen timer removed per user request

    // Check if first visit
    const hasVisited = localStorage.getItem("hasVisited");
    if (!hasVisited) {
      setShowWelcome(true);
    }

    // Load medications from localStorage
    const savedMeds = localStorage.getItem("medications");
    if (savedMeds) {
      setMedications(JSON.parse(savedMeds));
    } else {
      setMedications([]);
    }

    // Load recent scans from scan_history (consistent with ResultPage)
    const savedHistory = localStorage.getItem("scan_history");
    if (savedHistory) {
      const history = JSON.parse(savedHistory);
      setRecentScans(history);
    } else {
      setRecentScans([]);
    }
  }, []);

  const getRiskIcon = (level: string) => {
    if (level === "safe") return <CheckCircle className="w-5 h-5 text-[#4CAF50]" />;
    if (level === "warning") return <AlertTriangle className="w-5 h-5 text-[#FFB74D]" />;
    return <AlertTriangle className="w-5 h-5 text-[#E53935]" />;
  };

  const getRiskColor = (level: string) => {
    if (level === "safe") return "text-[#4CAF50]";
    if (level === "warning") return "text-[#FFB74D]";
    return "text-[#E53935]";
  };

  const handleWelcomeComplete = () => {
    localStorage.setItem("hasVisited", "true");
    setShowWelcome(false);
  };

  if (isLoading) {
    return <SplashScreen />;
  }

  if (showWelcome) {
    return <WelcomeScreen onComplete={handleWelcomeComplete} />;
  }

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-20">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">SafeEat</h1>
          <button className="p-2 hover:bg-white/10 rounded-full transition">
            <Bell className="w-6 h-6" />
          </button>
        </div>
        <p className="text-white/90">당신의 식탁 위, AI가 지키는 안전</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 -mt-4">
        {/* Next Medication Card */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-4 border-l-4 border-[#009688]">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-[#009688]" />
            <h3 className="font-bold text-[#263238]">다음 복용 시간</h3>
          </div>
          <p className="text-2xl font-bold text-[#009688] ml-8">{nextDoseTime}</p>
        </div>

        {/* Current Medications */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold text-[#263238]">복용 중인 약물</h2>
            <button
              onClick={() => navigate("/profile")}
              className="text-sm text-[#009688] hover:underline"
            >
              관리
            </button>
          </div>
          {medications.length === 0 ? (
            <p className="text-gray-500 text-sm">등록된 약물이 없습니다.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {medications.map((med) => (
                <MedicationTag key={med.id} name={med.name} dosage={med.dosage} />
              ))}
            </div>
          )}
        </div>

        {/* Recent Scans */}
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold text-[#263238]">최근 스캔 결과</h2>
            <button
              onClick={() => navigate("/history")}
              className="text-sm text-[#009688] hover:underline"
            >
              모두 보기
            </button>
          </div>
          {recentScans.length === 0 ? (
            <p className="text-gray-500 text-sm">스캔 기록이 없습니다.</p>
          ) : (
            <div className="space-y-3">
              {recentScans.slice(0, 3).map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition"
                  onClick={() => navigate("/result", {
                    state: {
                      scanData: scan,
                      boundingBoxes: scan.boundingBoxes,
                      backendResult: scan.backendResult
                    }
                  })}
                >
                  <div className="flex items-center gap-3">
                    {getRiskIcon(scan.riskLevel)}
                    <div>
                      <p className="font-medium text-[#263238]">{scan.foodName}</p>
                      <p className={`text-sm ${getRiskColor(scan.riskLevel)}`}>
                        {scan.riskLevel === "safe" ? "안전하게 섭취 가능" :
                          scan.riskLevel === "warning" ? "주의하여 섭취" : "섭취 중단 권고"}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">
                    {scan.date.split(",")[0]}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Weekly Report Button */}
        <div className="bg-[#009688]/10 border border-[#009688]/20 rounded-xl p-5 mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-[#009688]">주간 안심 리포트</h3>
            <p className="text-xs text-[#009688]/80 mt-1">이번 주 나의 식탁 안전도를 확인하세요</p>
          </div>
          <Button
            onClick={() => navigate("/report")}
            className="bg-[#009688] hover:bg-[#00796B] text-white text-xs h-9 px-4"
          >
            보기
          </Button>
        </div>

        {/* Scan Button */}
        <button
          onClick={() => navigate("/scan")}
          className="w-full bg-[#009688] hover:bg-[#00796B] text-white py-4 rounded-xl font-bold flex items-center justify-center gap-3 shadow-lg transition mb-4"
        >
          <Camera className="w-6 h-6" />
          새로운 식품 스캔하기
        </button>

        {/* Info Banner */}
        <div className="bg-[#009688]/5 border border-[#009688]/20 rounded-xl p-4 mb-4">
          <p className="text-sm text-[#263238] text-center">
            💡 내 몸에 딱 맞는 안전 먹거리를 챙기세요
          </p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
