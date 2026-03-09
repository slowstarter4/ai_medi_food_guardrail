import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Calendar, MessageCircle, Phone, X } from "lucide-react";
import { Button } from "./ui/button";
import { consultationContacts } from "../utils/consultationData";

interface CounselingOverlayProps {
    riskLevel: "safe" | "warning" | "danger";
    isOpen: boolean;
    onClose: () => void;
}

export const CounselingOverlay: React.FC<CounselingOverlayProps> = ({
    riskLevel,
    isOpen,
    onClose,
}) => {
    if (riskLevel === "safe") return null;

    if (riskLevel === "danger") {
        return (
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Dark Overlay */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={onClose}
                            className="fixed inset-0 bg-black/60 z-[100]"
                        />

                        {/* Urgent Popup */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90%] max-w-sm bg-white rounded-3xl overflow-hidden z-[101] shadow-[0_0_50px_rgba(229,57,53,0.5)] border-4 border-[#E53935]"
                        >
                            <div className="bg-[#E53935] p-6 text-white text-center">
                                <motion.div
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ repeat: Infinity, duration: 1.5 }}
                                    className="bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                                >
                                    <AlertCircle className="w-10 h-10 text-white" />
                                </motion.div>
                                <div className="inline-block px-2 py-0.5 bg-white text-[#E53935] text-[10px] font-black rounded mb-2">🚨 EMERGENCY / 긴급 상황</div>
                                <h2 className="text-xl font-bold mb-2">즉시 섭취 중단 및 상담 권고</h2>
                                <p className="text-sm text-white/90 leading-relaxed font-bold">
                                    매우 위험한 상호작용이 감지되었습니다!
                                </p>
                            </div>

                            <div className="p-6 space-y-3">
                                <Button
                                    className="w-full h-14 bg-[#E53935] hover:bg-[#C62828] text-white font-bold rounded-xl flex items-center justify-center gap-3 text-lg shadow-lg border-2 border-white/20"
                                    onClick={() => window.open(consultationContacts.pharmacy.action)}
                                >
                                    <Phone className="w-6 h-6" />
                                    가장 가까운 약국에 문의하기
                                </Button>
                                <Button
                                    variant="outline"
                                    className="w-full h-14 border-2 border-[#E53935] text-[#E53935] hover:bg-[#E53935]/5 font-bold rounded-xl flex items-center justify-center gap-3 text-lg"
                                    onClick={() => window.open(consultationContacts.chat.action)}
                                >
                                    <MessageCircle className="w-6 h-6" />
                                    단골 약사와 채팅 상담
                                </Button>
                                <button
                                    onClick={onClose}
                                    className="w-full py-2 text-gray-400 text-sm font-medium hover:text-gray-600 transition"
                                >
                                    닫기
                                </button>
                            </div>
                        </motion.div>

                        {/* Floating Action Button (FAB) for ongoing awareness */}
                        {!isOpen && (
                            <motion.button
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                onClick={() => onClose()} // Re-open logic would be handled by parent
                                className="fixed bottom-24 right-6 w-14 h-14 bg-[#E53935] text-white rounded-full shadow-xl flex items-center justify-center z-[90]"
                            >
                                <Phone className="w-6 h-6" />
                            </motion.button>
                        )}
                    </>
                )}
            </AnimatePresence>
        );
    }

    if (riskLevel === "warning") {
        return (
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        className="fixed bottom-24 left-4 right-4 bg-white border border-[#FFB74D] rounded-xl px-4 py-3 shadow-md z-50 flex items-center justify-between gap-3"
                    >
                        <div className="flex items-center gap-3 flex-1">
                            <div className="bg-[#FFB74D]/10 p-1.5 rounded-lg text-[#F57C00]">
                                <Calendar className="w-4 h-4" />
                            </div>
                            <div className="flex-1">
                                <p className="text-xs font-bold text-[#E65100]">전문의 상담 권유</p>
                                <p className="text-[10px] text-gray-500 line-clamp-1">개인 상태에 따른 정밀 분석</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button
                                className="bg-[#FFB74D] hover:bg-[#F57C00] text-white text-[11px] h-8 px-3 font-bold rounded-lg shrink-0"
                                onClick={() => window.open(consultationContacts.chat.action)}
                            >
                                상담 예약
                            </Button>
                            <button onClick={onClose} className="p-1 text-gray-300 hover:text-gray-500">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        );
    }

    return null;
};
