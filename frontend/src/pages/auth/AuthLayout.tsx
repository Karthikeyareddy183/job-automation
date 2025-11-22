import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";

export default function AuthLayout() {
    return (
        <div className="min-h-screen w-full flex bg-background text-white overflow-hidden">
            {/* Left Side - Form Area */}
            <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-8 relative z-10">
                <div className="w-full max-w-md space-y-8">
                    <div className="text-center lg:text-left">
                        <h1 className="text-4xl font-bold font-heading bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
                            Job Agent
                        </h1>
                        <p className="text-muted-foreground">
                            Your autonomous career assistant.
                        </p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Outlet />
                    </motion.div>
                </div>
            </div>

            {/* Right Side - Visual Area */}
            <div className="hidden lg:flex w-1/2 bg-surface relative items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 backdrop-blur-3xl" />

                {/* Animated Circles */}
                <motion.div
                    className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/30 rounded-full blur-3xl"
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.5, 0.3],
                    }}
                    transition={{ duration: 8, repeat: Infinity }}
                />
                <motion.div
                    className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/30 rounded-full blur-3xl"
                    animate={{
                        scale: [1.2, 1, 1.2],
                        opacity: [0.3, 0.5, 0.3],
                    }}
                    transition={{ duration: 10, repeat: Infinity }}
                />

                <div className="relative z-10 p-12 text-center max-w-lg">
                    <h2 className="text-3xl font-bold font-heading mb-6">
                        Let AI Handle Your Job Search
                    </h2>
                    <p className="text-lg text-muted-foreground leading-relaxed">
                        "I stopped applying manually and let the agents take over.
                        They found better matches and tailored my resume perfectly."
                    </p>
                </div>
            </div>
        </div>
    );
}
