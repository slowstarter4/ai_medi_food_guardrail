import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { ArrowLeft, Search, Calendar, CheckCircle, AlertTriangle, ChevronRight, Trash2 } from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { toast } from "sonner";

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

export function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<ScanResult[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const savedHistory = localStorage.getItem("scan_history");
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory).sort((a: any, b: any) => b.id - a.id));
    }
  }, []);

  const clearHistory = () => {
    if (confirm("모든 히스토리를 삭제하시겠습니까?")) {
      localStorage.removeItem("scan_history");
      setHistory([]);
      toast.success("히스토리가 삭제되었습니다.");
    }
  };

  const deleteItem = (id: string) => {
    const newHistory = history.filter(item => item.id !== id);
    setHistory(newHistory);
    localStorage.setItem("scan_history", JSON.stringify(newHistory));
    toast.success("항목이 삭제되었습니다.");
  };

  const filteredHistory = history.filter(item => 
    item.foodName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRiskStyles = (level: string) => {
    if (level === "safe") return { bg: "bg-emerald-50", text: "text-emerald-600", border: "border-emerald-100", label: "안전" };
    if (level === "warning") return { bg: "bg-amber-50", text: "text-amber-600", border: "border-amber-100", label: "주의" };
    return { bg: "bg-red-50", text: "text-red-600", border: "border-red-100", label: "위험" };
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-24">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8 sticky top-0 z-10">
        <div className="flex justify-between items-center mb-4">
            <button onClick={() => navigate("/")} className="hover:opacity-80">
                <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-xl font-bold">분석 히스토리</h1>
            <button onClick={clearHistory} className="p-2 hover:bg-white/10 rounded-full transition">
                <Trash2 className="w-5 h-5" />
            </button>
        </div>
        
        <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
            <input 
                type="text"
                placeholder="제품명 검색..."
                className="w-full bg-white/10 border border-white/20 rounded-lg py-2 pl-10 pr-4 text-white placeholder:text-white/60 focus:outline-none focus:bg-white/20"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 mt-6">
        {filteredHistory.length === 0 ? (
            <div className="text-center py-20">
                <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">분석 기록이 없습니다.</p>
            </div>
        ) : (
            <div className="space-y-4">
                <AnimatePresence>
                    {filteredHistory.map((item) => {
                        const style = getRiskStyles(item.riskLevel);
                        return (
                            <motion.div
                                key={item.id}
                                layout
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
                            >
                                <div 
                                    className="p-4 flex items-center justify-between cursor-pointer active:bg-gray-50"
                                    onClick={() => navigate("/result", { 
                                        state: { 
                                            scanData: item,
                                            boundingBoxes: item.boundingBoxes,
                                            backendResult: item.backendResult
                                        } 
                                    })}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-12 h-12 rounded-full ${style.bg} flex items-center justify-center`}>
                                            {item.riskLevel === "safe" ? (
                                                <CheckCircle className={`w-6 h-6 ${style.text}`} />
                                            ) : (
                                                <AlertTriangle className={`w-6 h-6 ${style.text}`} />
                                            )}
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-800">{item.foodName}</h3>
                                            <div className="flex items-center gap-2 mt-0.5">
                                                <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-bold ${style.bg} ${style.text} border ${style.border}`}>
                                                    {style.label}
                                                </span>
                                                <span className="text-[11px] text-gray-400">{item.date.split(",")[0]}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <ChevronRight className="w-5 h-5 text-gray-300" />
                                </div>
                                
                                <button 
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        deleteItem(item.id);
                                    }}
                                    className="w-full py-2 bg-gray-50 text-[10px] text-gray-400 flex items-center justify-center gap-1 hover:bg-red-50 hover:text-red-400 transition"
                                >
                                    <Trash2 className="w-3 h-3" /> 항목 삭제
                                </button>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
