import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { ArrowLeft, BarChart3, ShieldCheck, MessageCircleHeart, Users, AlertCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { motion } from "motion/react";

interface ReportData {
    period: string;
    stats: {
        total_count: number;
        risk_distribution: { RED: number; YELLOW: number; GREEN: number };
        top_ingredients: string[];
        safety_score: number;
    };
    messages: {
        senior: string;
        guardian: string;
    };
}

export function ReportPage() {
    const navigate = useNavigate();
    const [reportData, setReportData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<"senior" | "guardian">("senior");

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const API_URL = (import.meta as any).env.VITE_API_URL || "http://localhost:8000";
                const response = await fetch(`${API_URL}/api/report/weekly`);
                if (response.ok) {
                    const data = await response.json();
                    setReportData(data);
                }
            } catch (error) {
                console.error("Failed to fetch report", error);
            } finally {
                setLoading(false);
            }
        };

        fetchReport();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#009688] mx-auto mb-4"></div>
                    <p className="text-gray-600">주간 리포트를 작성 중입니다...</p>
                </div>
            </div>
        );
    }

    const stats = reportData?.stats;

    return (
        <div className="min-h-screen bg-[#F5F5F5] pb-24">
            {/* Header */}
            <div className="bg-[#009688] text-white p-6 pb-8">
                <button
                    onClick={() => navigate("/")}
                    className="flex items-center gap-2 mb-4 hover:opacity-80"
                >
                    <ArrowLeft className="w-5 h-5" />
                    <span>홈으로</span>
                </button>
                <h1 className="text-2xl font-bold">주간 안심 리포트</h1>
                <p className="text-white/90 mt-1">{reportData?.period}</p>
            </div>

            <div className="max-w-2xl mx-auto px-4 -mt-4">
                {/* Mode Selector */}
                <div className="bg-white rounded-xl shadow-sm p-1 mb-4 flex">
                    <button
                        onClick={() => setViewMode("senior")}
                        className={`flex-1 py-2 rounded-lg font-medium text-sm transition ${viewMode === "senior" ? "bg-[#009688] text-white shadow-sm" : "text-gray-500"}`}
                    >
                        김영순 여사님용
                    </button>
                    <button
                        onClick={() => setViewMode("guardian")}
                        className={`flex-1 py-2 rounded-lg font-medium text-sm transition ${viewMode === "guardian" ? "bg-[#009688] text-white shadow-sm" : "text-gray-500"}`}
                    >
                        보호자(최지연 팀장)용
                    </button>
                </div>

                {/* Persona Message Card */}
                <motion.div
                    key={viewMode}
                    initial={{ opacity: 0, x: viewMode === "senior" ? -20 : 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-2xl shadow-sm p-6 mb-6 border-t-4 border-[#009688]"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="bg-[#009688]/10 p-2.5 rounded-full">
                            {viewMode === "senior" ? <MessageCircleHeart className="w-6 h-6 text-[#009688]" /> : <Users className="w-6 h-6 text-[#009688]" />}
                        </div>
                        <h2 className="font-bold text-lg text-[#263238]">
                            {viewMode === "senior" ? "영순 여사님을 위한 응원" : "어머니 건강 분석 요약"}
                        </h2>
                    </div>
                    <p className="text-[#37474F] leading-relaxed italic text-lg whitespace-pre-line">
                        "{viewMode === "senior" ? reportData?.messages.senior : reportData?.messages.guardian}"
                    </p>
                </motion.div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white rounded-xl shadow-sm p-5">
                        <div className="text-gray-500 text-xs mb-1 flex items-center gap-1">
                            <BarChart3 className="w-3.5 h-3.5" /> 총 분석 횟수
                        </div>
                        <div className="text-2xl font-bold text-[#263238]">{stats?.total_count}회</div>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm p-5">
                        <div className="text-gray-500 text-xs mb-1 flex items-center gap-1">
                            <ShieldCheck className="w-3.5 h-3.5" /> 안전 지수
                        </div>
                        <div className="text-2xl font-bold text-[#009688]">{stats?.safety_score}점</div>
                    </div>
                </div>

                {/* Risk Distribution */}
                <div className="bg-white rounded-xl shadow-sm p-5 mb-6">
                    <h3 className="font-bold text-[#263238] mb-4 text-sm uppercase tracking-wider">위험도 분포</h3>
                    <div className="space-y-4">
                        {[
                            { label: "매우 위험 (RED)", count: stats?.risk_distribution.RED, color: "#E53935" },
                            { label: "주의 요망 (YELLOW)", count: stats?.risk_distribution.YELLOW, color: "#FFB74D" },
                            { label: "안전 (GREEN)", count: stats?.risk_distribution.GREEN, color: "#4CAF50" },
                        ].map((item) => (
                            <div key={item.label}>
                                <div className="flex justify-between text-xs mb-1.5">
                                    <span className="text-gray-600">{item.label}</span>
                                    <span className="font-bold">{item.count}건</span>
                                </div>
                                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${stats?.total_count ? ((item.count || 0) / stats.total_count) * 100 : 0}%` }}
                                        className="h-full rounded-full"
                                        style={{ backgroundColor: item.color }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Management Ingredients */}
                {stats?.top_ingredients && stats.top_ingredients.length > 0 && (
                    <div className="bg-[#263238] text-white rounded-xl shadow-sm p-5">
                        <h3 className="font-bold mb-4 text-sm flex items-center gap-2">
                            <AlertCircle className="w-4 h-4 text-[#FFB74D]" /> 집중 관리 성분 TOP 3
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {stats.top_ingredients.map((name, i) => (
                                <span key={i} className="px-3 py-1 bg-white/10 rounded-full text-sm border border-white/20">
                                    {name}
                                </span>
                            ))}
                        </div>
                        <p className="text-white/60 text-[11px] mt-4 leading-normal">
                            * 위 성분들은 이번 주에 가장 자주 분석된 성분들입니다. 섭취 시 평소보다 더 주의를 기울여주세요.
                        </p>
                    </div>
                )}
            </div>

            <BottomNav />
        </div>
    );
}
