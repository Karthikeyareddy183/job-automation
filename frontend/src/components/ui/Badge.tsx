import * as React from "react";
import { cn } from "../../lib/utils";

const badgeVariants = {
    default: "bg-primary/20 text-primary border-primary/50",
    secondary: "bg-secondary/20 text-secondary border-secondary/50",
    success: "bg-green-500/20 text-green-400 border-green-500/50",
    warning: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
    destructive: "bg-red-500/20 text-red-400 border-red-500/50",
    outline: "text-foreground",
};

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement> {
    variant?: keyof typeof badgeVariants;
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
    return (
        <div
            className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                badgeVariants[variant],
                className
            )}
            {...props}
        />
    );
}

export { Badge };
