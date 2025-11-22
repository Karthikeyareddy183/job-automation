import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
    LayoutDashboard,
    Briefcase,
    FileText,
    Settings,
    LogOut,
    Menu,
    X,
    Sparkles
} from "lucide-react";
import { Button } from "../components/ui/Button";
import { supabase } from "../lib/supabase";
import toast from "react-hot-toast";

export default function DashboardLayout() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const location = useLocation();

    const handleLogout = async () => {
        await supabase.auth.signOut();
        toast.success("Logged out successfully");
        // Redirect handled by App.tsx auth listener (to be implemented)
        window.location.href = '/auth/login';
    };

    const navItems = [
        { icon: LayoutDashboard, label: "Overview", path: "/dashboard" },
        { icon: Briefcase, label: "Jobs", path: "/dashboard/jobs" },
        { icon: FileText, label: "Applications", path: "/dashboard/applications" },
        { icon: Sparkles, label: "Learning", path: "/dashboard/learning" },
        { icon: Settings, label: "Settings", path: "/dashboard/settings" },
    ];

    return (
        <div className="min-h-screen bg-background flex">
            {/* Sidebar */}
            <motion.aside
                initial={false}
                animate={{ width: isSidebarOpen ? 280 : 80 }}
                className="bg-surface border-r border-border hidden md:flex flex-col relative z-20 transition-all duration-300"
            >
                <div className="p-6 flex items-center justify-between">
                    {isSidebarOpen ? (
                        <h1 className="text-2xl font-bold font-heading bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                            Job Agent
                        </h1>
                    ) : (
                        <span className="text-2xl font-bold text-primary">JA</span>
                    )}
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="text-muted-foreground hover:text-white transition-colors"
                    >
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                <nav className="flex-1 px-4 space-y-2 mt-4">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center p-3 rounded-xl transition-all duration-200 group ${isActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-muted-foreground hover:bg-surface hover:text-white"
                                    }`}
                            >
                                <item.icon size={24} className={isActive ? "text-primary" : "group-hover:text-white"} />
                                {isSidebarOpen && (
                                    <span className="ml-3 font-medium">{item.label}</span>
                                )}
                                {isActive && isSidebarOpen && (
                                    <motion.div
                                        layoutId="activeIndicator"
                                        className="absolute left-0 w-1 h-8 bg-primary rounded-r-full"
                                    />
                                )}
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-border">
                    <Button
                        variant="ghost"
                        className={`w-full justify-start ${!isSidebarOpen && "justify-center px-0"}`}
                        onClick={handleLogout}
                    >
                        <LogOut size={20} className="text-red-400" />
                        {isSidebarOpen && <span className="ml-3 text-red-400">Logout</span>}
                    </Button>
                </div>
            </motion.aside>

            {/* Mobile Header */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-surface border-b border-border z-30 flex items-center justify-between px-4">
                <span className="text-xl font-bold text-primary">Job Agent</span>
                <Button variant="ghost" size="sm">
                    <Menu size={24} />
                </Button>
            </div>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
                <div className="p-8 pt-24 md:pt-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
