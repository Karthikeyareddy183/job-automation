import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import JobCard from "./JobCard";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Search, Filter } from "lucide-react";
import toast from "react-hot-toast";

// Mock Data
const MOCK_JOBS = [
    {
        id: "1",
        title: "Senior Full Stack Engineer",
        company: "TechCorp AI",
        location: "San Francisco (Remote)",
        salary: "$160k - $200k",
        matchScore: 95,
        reasoning: "Perfect match for your React + Python experience. They use FastAPI and Next.js, exactly your stack.",
        tags: ["React", "Python", "FastAPI", "AWS"],
        postedAt: "2 hours ago"
    },
    {
        id: "2",
        title: "Backend Developer",
        company: "DataFlow Systems",
        location: "New York (Hybrid)",
        salary: "$140k - $170k",
        matchScore: 88,
        reasoning: "Strong match, but requires onsite presence 2 days/week. Salary is within your range.",
        tags: ["Python", "Django", "PostgreSQL", "Redis"],
        postedAt: "5 hours ago"
    },
    {
        id: "3",
        title: "AI Research Engineer",
        company: "Future Minds",
        location: "Remote",
        salary: "$180k - $240k",
        matchScore: 72,
        reasoning: "High salary but requires PhD which you don't have listed. Might be a reach.",
        tags: ["PyTorch", "LLMs", "Research", "Python"],
        postedAt: "1 day ago"
    }
];

export default function JobsPage() {
    const [jobs, setJobs] = useState(MOCK_JOBS);
    const [searchQuery, setSearchQuery] = useState("");

    const handleApprove = (id: string) => {
        toast.success("Job approved! Agent will apply shortly.");
        setJobs(jobs.filter(j => j.id !== id));
    };

    const handleReject = (id: string) => {
        toast("Job rejected", { icon: '🗑️' });
        setJobs(jobs.filter(j => j.id !== id));
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold font-heading text-white">Job Matches</h1>
                    <p className="text-muted-foreground">
                        {jobs.length} jobs waiting for your review
                    </p>
                </div>

                <div className="flex items-center space-x-3 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                            placeholder="Search jobs..."
                            className="pl-9"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Button variant="outline" size="sm">
                        <Filter className="w-4 h-4 mr-2" />
                        Filter
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
                <AnimatePresence mode="popLayout">
                    {jobs.map((job) => (
                        <JobCard
                            key={job.id}
                            job={job}
                            onApprove={handleApprove}
                            onReject={handleReject}
                        />
                    ))}
                </AnimatePresence>

                {jobs.length === 0 && (
                    <div className="text-center py-20 bg-surface/30 rounded-2xl border border-dashed border-border">
                        <p className="text-muted-foreground">No more jobs to review!</p>
                        <Button variant="ghost" className="mt-4 text-primary">
                            Refresh Feed
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
