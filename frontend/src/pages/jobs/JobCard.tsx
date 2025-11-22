import { motion } from "framer-motion";
import { Card, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { MapPin, DollarSign, Building, Check, X } from "lucide-react";

interface Job {
    id: string;
    title: string;
    company: string;
    location: string;
    salary: string;
    matchScore: number;
    reasoning: string;
    tags: string[];
    postedAt: string;
}

interface JobCardProps {
    job: Job;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
}

export default function JobCard({ job, onApprove, onReject }: JobCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            layout
        >
            <Card className="group hover:border-primary/50 transition-colors">
                <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h3 className="text-xl font-bold text-white group-hover:text-primary transition-colors">
                                {job.title}
                            </h3>
                            <div className="flex items-center text-muted-foreground mt-1 space-x-4">
                                <span className="flex items-center">
                                    <Building className="w-4 h-4 mr-1" />
                                    {job.company}
                                </span>
                                <span className="flex items-center">
                                    <MapPin className="w-4 h-4 mr-1" />
                                    {job.location}
                                </span>
                                <span className="flex items-center text-green-400">
                                    <DollarSign className="w-4 h-4 mr-1" />
                                    {job.salary}
                                </span>
                            </div>
                        </div>
                        <Badge
                            variant={job.matchScore >= 90 ? "success" : job.matchScore >= 70 ? "default" : "warning"}
                            className="text-sm px-3 py-1"
                        >
                            {job.matchScore}% Match
                        </Badge>
                    </div>

                    <div className="bg-surface/50 rounded-lg p-4 mb-4 border border-white/5">
                        <p className="text-sm text-muted-foreground italic">
                            "{job.reasoning}"
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-6">
                        {job.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="bg-white/5 border-white/10">
                                {tag}
                            </Badge>
                        ))}
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-border">
                        <span className="text-xs text-muted-foreground">Posted {job.postedAt}</span>
                        <div className="flex space-x-3">
                            <Button variant="ghost" size="sm" onClick={() => onReject(job.id)} className="text-red-400 hover:text-red-300 hover:bg-red-400/10">
                                <X className="w-4 h-4 mr-2" />
                                Reject
                            </Button>
                            <Button variant="primary" size="sm" onClick={() => onApprove(job.id)}>
                                <Check className="w-4 h-4 mr-2" />
                                Approve & Apply
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
