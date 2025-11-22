import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import AuthLayout from "./pages/auth/AuthLayout";
import LoginPage from "./pages/auth/LoginPage";
import SignupPage from "./pages/auth/SignupPage";
import DashboardLayout from "./layouts/DashboardLayout";
import DashboardPage from "./pages/dashboard/DashboardPage";
import JobsPage from "./pages/jobs/JobsPage";

const queryClient = new QueryClient();

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <Routes>
                    {/* Auth Routes */}
                    <Route path="/auth" element={<AuthLayout />}>
                        <Route path="login" element={<LoginPage />} />
                        <Route path="signup" element={<SignupPage />} />
                        <Route index element={<Navigate to="login" replace />} />
                    </Route>

                    {/* Dashboard Routes */}
                    <Route path="/dashboard" element={<DashboardLayout />}>
                        <Route index element={<DashboardPage />} />
                        <Route path="jobs" element={<JobsPage />} />
                        {/* <Route path="applications" element={<ApplicationsPage />} /> */}
                        {/* <Route path="learning" element={<LearningPage />} /> */}
                        {/* <Route path="settings" element={<SettingsPage />} /> */}
                    </Route>

                    {/* Root Redirect */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />

                    {/* 404 */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
                <Toaster position="top-right" toastOptions={{
                    style: {
                        background: '#1e293b',
                        color: '#fff',
                        border: '1px solid #334155',
                    },
                }} />
            </BrowserRouter>
        </QueryClientProvider>
    );
}

export default App;
