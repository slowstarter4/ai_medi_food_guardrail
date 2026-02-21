import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router";
import { BottomNav } from "../components/BottomNav";
import { IngredientChip } from "../components/IngredientChip";
import { Camera, Maximize2, Search, Barcode, ChevronRight, RefreshCw } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { motion } from "motion/react";
import Webcam from "react-webcam";

const commonConditions = [
  { id: "elderly", label: "고령" },
  { id: "hypertension", label: "고혈압" },
  { id: "diabetes", label: "당뇨" },
  { id: "hyperlipidemia", label: "고지혈증" },
  { id: "arthritis", label: "관절염" },
  { id: "asthma", label: "천식" },
];

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
  const webcamRef = useRef<Webcam>(null);
  const [scanMode, setScanMode] = useState<"camera" | "manual">("camera");
  const [isScanning, setIsScanning] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(true);
  const [boundingBoxes, setBoundingBoxes] = useState<BoundingBox[]>([]);
  const [detectedIngredients, setDetectedIngredients] = useState<string[]>([]);
  const [manualSearch, setManualSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [lastAnalysisResult, setLastAnalysisResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const startScanning = () => {
    fileInputRef.current?.click();
  };

  // Helper: Base64 to File conversion
  const base64ToFile = (base64String: string, filename: string) => {
    const arr = base64String.split(",");
    const mime = arr[0].match(/:(.*?);/)?.[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCameraEnabled(false); // Stop camera after capture
      const file = base64ToFile(imageSrc, "scan.jpg");
      processFile(file);
    }
  }, [webcamRef]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  const processFile = async (file: File) => {
    setSelectedFile(file);
    setIsScanning(true);
    setBoundingBoxes([]);
    setDetectedIngredients([]);

    // Preparation for API Call
    const formData = new FormData();
    formData.append("file", file);

    const savedMeds = localStorage.getItem("medications");
    const savedConditions = localStorage.getItem("conditions");
    const conditionLabels = savedConditions
      ? JSON.parse(savedConditions).map((id: string) => {
        const found = commonConditions.find(c => c.id === id);
        return found ? found.label : id;
      })
      : [];

    if (savedMeds) {
      const medNames = JSON.parse(savedMeds).map((m: any) => m.name);
      formData.append("medications", JSON.stringify(medNames));
    }
    if (conditionLabels.length > 0) {
      formData.append("conditions", JSON.stringify(conditionLabels));
    }

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_URL}/api/analyze/image`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("분석 실패");

      const result = await response.json();
      if (result.error) throw new Error(result.error);

      // Parsing Results
      const entities = result.debug_info?.entities || {};
      const allIngredients = [
        ...(entities.drugs?.map((d: any) => d.raw) || []),
        ...(entities.foods?.map((f: any) => f.raw) || [])
      ];

      if (allIngredients.length === 0) {
        alert("인식된 성분이 없습니다. 다시 촬영하거나 수동으로 입력하세요.");
        setCameraEnabled(true);
        return;
      }

      // Mock Bounding Boxes for UI
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
    } catch (error: any) {
      console.error("Error analyzing image:", error);
      alert(error.message || "이미지 분석 실패");
      setCameraEnabled(true);
    } finally {
      setIsScanning(false);
    }
  };

  const analyzeIngredients = async () => {
    if (isLoading || (detectedIngredients.length === 0 && !manualSearch)) return;

    setIsLoading(true);
    let resultToPass = lastAnalysisResult;

    if (scanMode === "manual" && manualSearch && !resultToPass) {
      try {
        const savedMeds = localStorage.getItem("medications");
        const savedConditions = localStorage.getItem("conditions");
        const medNames = savedMeds ? JSON.parse(savedMeds).map((m: any) => m.name) : [];
        const conditionLabels = savedConditions
          ? JSON.parse(savedConditions).map((id: string) => {
            const found = commonConditions.find(c => c.id === id);
            return found ? found.label : id;
          })
          : [];

        const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_URL}/api/analyze/text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: manualSearch,
            medications: medNames,
            conditions: conditionLabels
          }),
        });
        if (response.ok) resultToPass = await response.json();
      } catch (error) {
        console.error("Manual analysis failed", error);
      }
    }

    const scanData = {
      id: Date.now().toString(),
      foodName: manualSearch || "스캔한 식품",
      ingredients: detectedIngredients,
      date: new Date().toLocaleString(),
      riskLevel: resultToPass?.risk_result?.risk_level?.toLowerCase() === "red" ? "danger" :
        resultToPass?.risk_result?.risk_level?.toLowerCase() === "yellow" ? "warning" : "safe",
      explanation: resultToPass?.explanation || resultToPass?.risk_result?.explanation
    };

    const scan_history = JSON.parse(localStorage.getItem("scan_history") || "[]");
    scan_history.unshift(scanData);
    localStorage.setItem("scan_history", JSON.stringify(scan_history.slice(0, 10)));

    setIsLoading(false);
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
            <div className="relative bg-gray-900 h-[320px] flex items-center justify-center overflow-hidden">
              {!isScanning && cameraEnabled ? (
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{
                    facingMode: "environment",
                    width: 720,
                    height: 1280,
                  }}
                  className="w-full h-full object-cover"
                />
              ) : isScanning ? (
                <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-10">
                  <div className="text-white text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-3"></div>
                    <p className="font-medium">분석 중...</p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-white p-6">
                  <Camera className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-base mb-1">카메라가 꺼져있습니다</p>
                  <Button
                    variant="link"
                    className="text-[#009688] p-0 h-auto"
                    onClick={() => setCameraEnabled(true)}
                  >
                    카메라 켜기
                  </Button>
                </div>
              )}

              {/* Overlay */}
              {!isScanning && cameraEnabled && (
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute inset-0 border-4 border-[#009688] opacity-30 rounded-lg m-10"></div>
                  <div className="absolute top-1/2 left-0 w-full h-0.5 bg-[#009688] opacity-50 animate-pulse shadow-[0_0_15px_#009688]"></div>
                </div>
              )}

              {/* Bounding Boxes on result */}
              {!isScanning && !cameraEnabled && boundingBoxes.length > 0 && (
                <>
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
                    </motion.div>
                  ))}
                </>
              )}
            </div>

            <div className="p-4 bg-gray-50 border-t">
              {!isScanning && cameraEnabled ? (
                <div className="space-y-3">
                  <Button
                    onClick={capture}
                    className="w-full bg-[#009688] hover:bg-[#00796B] text-white py-6"
                  >
                    인식하기
                  </Button>
                  <Button
                    variant="outline"
                    onClick={startScanning}
                    className="w-full"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    갤러리에서 불러오기
                  </Button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsScanning(false);
                      setCameraEnabled(true);
                      setBoundingBoxes([]);
                      setDetectedIngredients([]);
                    }}
                    className="flex-1"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    다시 촬영
                  </Button>
                  <Button
                    onClick={() => setScanMode("manual")}
                    className="flex-1 bg-[#009688] hover:bg-[#00796B] text-white"
                  >
                    수정하기
                  </Button>
                </div>
              )}
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
                  if (manualSearch.trim()) setDetectedIngredients([manualSearch]);
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
            </div>
          </div>
        )}

        {/* Action Button */}
        {detectedIngredients.length > 0 && (
          <Button
            onClick={analyzeIngredients}
            disabled={isLoading}
            className="w-full bg-[#009688] hover:bg-[#00796B] text-white py-4 text-lg shadow-lg mb-4"
          >
            {isLoading ? "분석 중..." : "위험도 분석하기"}
            {!isLoading && <ChevronRight className="w-5 h-5 ml-2" />}
          </Button>
        )}

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
