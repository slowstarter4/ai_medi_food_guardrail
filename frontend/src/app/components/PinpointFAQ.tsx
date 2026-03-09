import React, { useState } from "react";
import { ChevronRight, HelpCircle } from "lucide-react";
import { FAQItem, contextFAQs, globalFAQs } from "../utils/consultationData";
import { motion, AnimatePresence } from "framer-motion";

interface PinpointFAQProps {
    userConditions: string[];
    detectedDrugs: string[];
    detectedIngredients: string[];
}

export const PinpointFAQ: React.FC<PinpointFAQProps> = ({
    userConditions,
    detectedDrugs,
    detectedIngredients,
}) => {
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

    // 현재 컨텍스트에 맞는 FAQ 필터링 (예: 고혈압-자몽)
    const getRelevantFAQs = (): FAQItem[] => {
        const relevant: FAQItem[] = [];

        // 단순 매핑 매칭 (임시 로직)
        const contextKeys = Object.keys(contextFAQs);

        contextKeys.forEach(key => {
            const [condition, ingredient] = key.split("-");
            const hasCondition = userConditions.some(c => c.includes(condition));
            const hasIngredient = detectedIngredients.some(i => i.includes(ingredient));

            if (hasCondition && hasIngredient) {
                relevant.push(...contextFAQs[key]);
            }
        });

        // 검색된 관련 FAQ가 없으면 일반 FAQ 중 일부 노출
        if (relevant.length === 0) {
            return globalFAQs.slice(0, 2);
        }

        return relevant;
    };

    const faqs = getRelevantFAQs();

    return (
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
            <h2 className="font-bold text-[#263238] mb-4 flex items-center gap-2 text-sm">
                <HelpCircle className="w-4 h-4 text-[#009688]" />
                궁금해하실 내용을 찾아봤어요
            </h2>

            <div className="space-y-3">
                {faqs.map((faq, index) => (
                    <div key={index} className="border border-gray-100 rounded-lg overflow-hidden">
                        <button
                            onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition text-left"
                        >
                            <span className="text-xs font-semibold text-[#263238] pr-2">
                                {faq.question}
                            </span>
                            <ChevronRight
                                className={`w-4 h-4 text-gray-400 flex-shrink-0 transition-transform ${expandedIndex === index ? "rotate-90" : ""
                                    }`}
                            />
                        </button>
                        <AnimatePresence>
                            {expandedIndex === index && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                >
                                    <div className="px-3 pb-3">
                                        <p className="text-[11px] text-gray-600 leading-relaxed bg-[#F5F5F5] p-2 rounded-md">
                                            {faq.answer}
                                        </p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                ))}
            </div>
        </div>
    );
};
