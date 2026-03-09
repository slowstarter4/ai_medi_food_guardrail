export interface FAQItem {
    question: string;
    answer: string;
    category?: string;
    tags?: string[];
}

export const globalFAQs: FAQItem[] = [
    {
        question: "RED와 YELLOW 등급은 어떻게 다르나요?",
        answer: "RED는 즉시 섭취 중단 및 상담이 필수적인 긴급 위험 상태를 의미하며, YELLOW는 주의 섭취 및 전문가 상담을 권장하는 주의 상태를 의미합니다.",
        category: "등급 안내"
    },
    {
        question: "경고 메시지를 받으면 반드시 상담해야 하나요?",
        answer: "세이프잇 AI 분석은 참고용입니다. 실제 치료 및 복약 결정은 반드시 의사나 약사와 같은 전문가의 상담을 통해 확정해야 합니다.",
        category: "상담 안내"
    },
    {
        question: "OCR 인식 오류가 있을 경우 어떻게 수정하나요?",
        answer: "스캔 결과 화면에서 성분명을 직접 클릭하거나 편집 버튼을 통해 수동으로 수정할 수 있습니다. 결과가 의심스러운 경우 전문가와 상담하세요.",
        category: "기능 문의"
    },
    {
        question: "DB에 없는 신규 식품은 어떻게 처리하나요?",
        answer: "데이터베이스에 없는 성분은 기본적으로 '주의' 등급으로 분류되며, 전문가 검토 프로세스를 통해 지속적으로 업데이트됩니다.",
        category: "기능 문의"
    },
    {
        question: "데이터는 얼마나 신뢰할 수 있나요?",
        answer: "식약처, FDA 등 공신력 있는 기관의 데이터와 임상 가이드라인을 기반으로 엄격한 검증 원칙에 따라 분석을 수행합니다.",
        category: "신뢰성"
    }
];

export const contextFAQs: Record<string, FAQItem[]> = {
    "고혈압-자몽": [
        {
            question: "자몽을 아주 조금만 먹는 것도 위험한가요?",
            answer: "자몽의 특정 성분은 소량으로도 혈압약의 농도를 크게 높일 수 있어, RED 등급인 경우 섭취하지 않는 것이 안전합니다."
        }
    ],
    "당뇨-설탕": [
        {
            question: "설탕을 조금만 먹는 것도 안 되나요?",
            answer: "당뇨 환자의 경우 소량의 설탕도 혈당 스파이크를 일으킬 수 있습니다. 가급적 대체 감미료를 사용하시거나 전문가와 상의하세요."
        }
    ]
};

export const consultationContacts = {
    pharmacy: {
        label: "가장 가까운 약국 문의",
        action: "tel:02-123-4567" // Mock phone
    },
    chat: {
        label: "단골 약사 채팅 상담",
        action: "https://pf.kakao.com/_xxxx" // Mock chat link
    }
};
