import { motion } from "motion/react";
import { ShieldCheck } from "lucide-react";

export function SplashScreen() {
    return (
        <div className="fixed inset-0 bg-[#009688] flex flex-col items-center justify-center z-50">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                    duration: 0.8,
                    ease: "easeOut",
                }}
                className="flex flex-col items-center"
            >
                <div className="w-24 h-24 bg-white rounded-3xl flex items-center justify-center shadow-2xl mb-6">
                    <ShieldCheck className="w-14 h-14 text-[#009688]" />
                </div>
                <motion.h1
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.4, duration: 0.5 }}
                    className="text-4xl font-bold text-white tracking-widest"
                >
                    SafeEat
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8, duration: 0.5 }}
                    className="text-white/80 mt-2 text-sm"
                >
                    식탁 위의 스마트 안전 가이드
                </motion.p>
            </motion.div>

            <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: 0.2, duration: 1.5, ease: "easeInOut" }}
                className="absolute bottom-16 w-32 h-1 bg-white/30 rounded-full overflow-hidden"
            >
                <motion.div
                    animate={{ x: ["-100%", "100%"] }}
                    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                    className="w-1/2 h-full bg-white"
                />
            </motion.div>
        </div>
    );
}
