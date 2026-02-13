import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { IngredientChip } from "../components/IngredientChip";
import { Camera, Maximize2, Search, Barcode, ChevronRight } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { motion } from "motion/react";

interface BoundingBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  riskLevel?: "safe" | "warning" | "danger";
}

export function ScanPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [scanMode, setScanMode] = useState<"camera" | "manual">("camera");
  const [isScanning, setIsScanning] = useState(false);
  const [boundingBoxes, setBoundingBoxes] = useState<BoundingBox[]>([]);
  const [detectedIngredients, setDetectedIngredients] = useState<string[]>([]);
  const [manualSearch, setManualSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [lastAnalysisResult, setLastAnalysisResult] = useState<any>(null);

  const startScanning = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setIsScanning(true);
    setBoundingBoxes([]);
    setDetectedIngredients([]);

    // 백엔드 API 호출
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/analyze/image", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("분석 실패");

      const result = await response.json();

      // 결과 데이터 파싱 (백엔드 메인 파이프라인 결과 구조에 맞춤)
      const entities = result.debug_info?.entities || {};
      const allIngredients = [
        ...(entities.drugs?.map((d: any) => d.raw) || []),
        ...(entities.foods?.map((f: any) => f.raw) || [])
      ];

      // 바운딩 박스 시뮬레이션 (실제 OCR 좌표가 없는 경우 UI를 위해 목업 생성)
      const mockBoxes: BoundingBox[] = allIngredients.map((text, i) => ({
        id: i.toString(),
        x: 20 + (i * 10) % 50,
        y: 30 + (i * 15) % 40,
        width: 40,
        height: 10,
        text: text,
        riskLevel: result.risk_result?.risk_level?.toLowerCase() === "red" ? "danger" :
          result.risk_result?.risk_level?.toLowerCase() === "yellow" ? "warning" : "safe"
      }));

      setBoundingBoxes(mockBoxes);
      setDetectedIngredients(allIngredients);
      setLastAnalysisResult(result);
    } catch (error) {
      console.error("Error analyzing image:", error);
      alert("이미지 분석 중 오류가 발생했습니다.");
    } finally {
      setIsScanning(false);
    }
  };

  const analyzeIngredients = async () => {
    if (detectedIngredients.length === 0 && !manualSearch) {
      return;
    }

    let resultToPass = lastAnalysisResult;

    // 수동 검색이고 직전 이미지 분석 결과가 없는 경우 텍스트 분석 API 호출
    if (scanMode === "manual" && manualSearch && !resultToPass) {
      try {
        const response = await fetch("http://localhost:8000/api/analyze/text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: manualSearch }),
        });
        if (response.ok) {
          resultToPass = await response.json();
        }
      } catch (error) {
        console.error("Manual analysis failed", error);
      }
    }

    const scanData = {
      id: Date.now().toString(),
      foodName: manualSearch || "스캔한 식품",
      ingredients: detectedIngredients,
      timestamp: new Date(),
      riskLevel: resultToPass?.risk_result?.risk_level?.toLowerCase() === "red" ? "danger" :
        resultToPass?.risk_result?.risk_level?.toLowerCase() === "yellow" ? "warning" : "safe"
    };

    const recentScans = JSON.parse(localStorage.getItem("recentScans") || "[]");
    recentScans.unshift(scanData);
    localStorage.setItem("recentScans", JSON.stringify(recentScans.slice(0, 10)));

    navigate("/result", {
      state: {
        scanData,
        boundingBoxes,
        backendResult: resultToPass
      }
    });
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] pb-20">
      {/* Header */}
      <div className="bg-[#009688] text-white p-6 pb-8">
        <h1 className="text-2xl font-bold">식품 스캔</h1>
        <p className="text-white/90 mt-2">성분표를 촬영하거나 직접 입력하세요</p>
      </div>

      <div className="max-w-2xl mx-auto px-4 -mt-4">
        {/* Mode Selector */}
        <div className="bg-white rounded-xl shadow-sm p-2 mb-4 flex gap-2">
          <button
            onClick={() => setScanMode("camera")}
            className={`flex-1 py-2.5 rounded-lg font-medium transition ${scanMode === "camera"
              ? "bg-[#009688] text-white"
              : "text-gray-600 hover:bg-gray-50"
              }`}
          >
            <Camera className="w-4 h-4 inline mr-2" />
            카메라 스캔
          </button>
          <button
            onClick={() => setScanMode("manual")}
            className={`flex-1 py-2.5 rounded-lg font-medium transition ${scanMode === "manual"
              ? "bg-[#009688] text-white"
              : "text-gray-600 hover:bg-gray-50"
              }`}
          >
            <Search className="w-4 h-4 inline mr-2" />
            수동 입력
          </button>
        </div>

        {/* Camera Mode */}
        {scanMode === "camera" && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-4">
            {/* Camera Viewfinder Simulation */}
            <div className="relative bg-gray-900 aspect-[3/4] flex items-center justify-center">
              {!isScanning ? (
                <div className="text-center text-white p-8">
                  <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">성분표를 카메라에 비추세요</p>
                  <p className="text-sm opacity-75">
                    실시간으로 성분을 인식합니다
                  </p>
                </div>
              ) : (
                <>
                  {/* Scanning Grid Overlay */}
                  <div className="absolute inset-0">
                    <div className="absolute inset-0 border-4 border-[#009688] opacity-30 rounded-lg m-8"></div>
                    <div className="absolute top-1/2 left-0 w-full h-0.5 bg-[#009688] opacity-40 animate-pulse"></div>
                  </div>

                  {/* Real-time Bounding Boxes with Text Preview */}
                  {boundingBoxes.map((box) => (
                    <motion.div
                      key={box.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="absolute"
                      style={{
                        left: `${box.x}%`,
                        top: `${box.y}%`,
                        width: `${box.width}%`,
                        height: `${box.height}%`,
                      }}
                    >
                      <div
                        className={`w-full h-full border-2 rounded ${box.riskLevel === "danger"
                          ? "border-[#E53935] bg-[#E53935]/20"
                          : box.riskLevel === "warning"
                            ? "border-[#FFB74D] bg-[#FFB74D]/20"
                            : "border-[#4CAF50] bg-[#4CAF50]/20"
                          }`}
                      ></div>
                      {/* Text Preview next to box */}
                      <div
                        className={`absolute -right-2 top-0 translate-x-full px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${box.riskLevel === "danger"
                          ? "bg-[#E53935] text-white"
                          : box.riskLevel === "warning"
                            ? "bg-[#FFB74D] text-white"
                            : "bg-[#4CAF50] text-white"
                          }`}
                      >
                        {box.text}
                      </div>
                    </motion.div>
                  ))}

                  {boundingBoxes.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-white text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-3"></div>
                        <p>성분 분석 중...</p>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Camera Controls */}
            <div className="p-4 bg-gray-50 border-t">
              {!isScanning ? (
                <Button
                  onClick={startScanning}
                  className="w-full bg-[#009688] hover:bg-[#00796B] text-white"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  스캔 시작
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsScanning(false);
                      setBoundingBoxes([]);
                      setDetectedIngredients([]);
                    }}
                    className="flex-1"
                  >
                    다시 촬영
                  </Button>
                  <Button
                    onClick={() => setScanMode("manual")}
                    className="flex-1 bg-[#009688] hover:bg-[#00796B] text-white"
                  >
                    <Maximize2 className="w-4 h-4 mr-2" />
                    수정하기
                  </Button>
                </div>
              )}

              <button
                className="w-full mt-3 text-sm text-gray-600 hover:text-[#009688] flex items-center justify-center gap-1"
                onClick={() => alert("바코드 스캔 기능은 준비 중입니다")}
              >
                <Barcode className="w-4 h-4" />
                바코드로 스캔하기
              </button>
            </div>
          </div>
        )}

        {/* Manual Mode */}
        {scanMode === "manual" && (
          <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
            <h3 className="font-bold text-[#263238] mb-3">제품명 검색</h3>
            <div className="flex gap-2 mb-4">
              <Input
                placeholder="예: 자몽 주스"
                value={manualSearch}
                onChange={(e) => setManualSearch(e.target.value)}
              />
              <Button
                onClick={() => {
                  if (manualSearch.trim()) {
                    setDetectedIngredients([manualSearch]);
                  }
                }}
                className="bg-[#009688] hover:bg-[#00796B]"
              >
                검색
              </Button>
            </div>

            <div className="border-t pt-4">
              <h3 className="font-bold text-[#263238] mb-3">
                인식된 성분 ({detectedIngredients.length})
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                성분을 클릭하여 수정하거나 삭제할 수 있습니다.
              </p>
              {detectedIngredients.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">
                  인식된 성분이 없습니다
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {detectedIngredients.map((ingredient, index) => {
                    const box = boundingBoxes.find((b) => b.text === ingredient);
                    return (
                      <IngredientChip
                        key={index}
                        label={ingredient}
                        riskLevel={box?.riskLevel}
                        onRemove={() => {
                          setDetectedIngredients(
                            detectedIngredients.filter((_, i) => i !== index)
                          );
                        }}
                      />
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analyze Button */}
        {detectedIngredients.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Button
              onClick={analyzeIngredients}
              className="w-full bg-[#009688] hover:bg-[#00796B] text-white py-4 text-lg shadow-lg mb-4"
            >
              위험도 분석하기
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        )}

        {/* Help Guide */}
        <div className="bg-[#009688]/5 border border-[#009688]/20 rounded-xl p-4">
          <h4 className="font-bold text-[#263238] mb-2">촬영 가이드</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• 성분표가 화면 중앙에 오도록 배치하세요</li>
            <li>• 밝은 곳에서 촬영하면 더 정확합니다</li>
            <li>• 흔들림 없이 안정적으로 촬영하세요</li>
          </ul>
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*"
        style={{ display: "none" }}
      />

      <BottomNav />
    </div>
  );
}
