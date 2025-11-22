import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { ArrowUpRight, Briefcase, CheckCircle, Clock, Settings } from "lucide-react";

export default function DashboardPage() {
    // Mock data for now
    const stats = [
        { label: "Jobs Scraped Today", value: "42", icon: Briefcase, color: "text-blue-400", bg: "bg-blue-400/10" },
        { label: "Pending Approval", value: "12", icon: Clock, color: "text-yellow-400", bg: "bg-yellow-400/10" },
        { label: "Applications Sent", value: "156", icon: CheckCircle, color: "text-green-400", bg: "bg-green-400/10" },
        { label: "Response Rate", value: "8.5%", icon: ArrowUpRight, color: "text-purple-400", bg: "bg-purple-400/10" },
    ];

    const recentActivity = [
        { id: 1, type: "match", message: "Matched 'Senior Python Engineer' at Google", time: "2 mins ago", score: 92 },
        { id: 2, type: "apply", message: "Applied to 'Backend Developer' at Netflix", time: "15 mins ago", status: "success" },
        { id: 3, type: "reject", message: "Rejected 'Java Developer' at Oracle", time: "1 hour ago", reason: "Low match score" },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold font-heading text-white">Dashboard</h1>
                <p className="text-muted-foreground">Welcome back! Here's what your agents have been up to.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <Card className="hover:bg-surface/80 transition-colors cursor-default">
                            <CardContent className="p-6 flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                                    <h3 className="text-2xl font-bold mt-1 text-white">{stat.value}</h3>
                                </div>
                                <div className={`p-3 rounded-xl ${stat.bg}`}>
                                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>

            {/* Activity Feed & Top Matches */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {recentActivity.map((activity) => (
                                <div key={activity.id} className="flex items-start space-x-4 border-b border-border last:border-0 pb-4 last:pb-0">
                                    <div className="mt-1">
                                        {activity.type === 'match' && <div className="w-2 h-2 rounded-full bg-blue-400" />}
                                        {activity.type === 'apply' && <div className="w-2 h-2 rounded-full bg-green-400" />}
                                        {activity.type === 'reject' && <div className="w-2 h-2 rounded-full bg-red-400" />}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-white">{activity.message}</p>
                                        <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                                    </div>
                                    {activity.score && (
                                        <Badge variant="default">{activity.score}% Match</Badge>
                                    )}
                                    {activity.status === 'success' && (
                                        <Badge variant="success">Applied</Badge>
                                    )}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Button className="w-full justify-start" variant="secondary">
                            <Briefcase className="mr-2 h-4 w-4" />
                            Review Pending Jobs
                        </Button>
                        <Button className="w-full justify-start" variant="outline">
                            <Settings className="mr-2 h-4 w-4" />
                            Update Preferences
                        </Button>
                        <div className="pt-4">
                            <div className="p-4 rounded-xl bg-primary/10 border border-primary/20">
                                <h4 className="font-medium text-primary mb-1">Agents Active</h4>
                                <p className="text-xs text-muted-foreground">
                                    Next scrape scheduled in 2 hours.
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
