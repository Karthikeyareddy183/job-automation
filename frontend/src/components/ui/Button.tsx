import * as React from "react";
import { cn } from "../../lib/utils";

// Note: We need to install class-variance-authority and @radix-ui/react-slot
// I will add them to the install list or just implement a simpler version for now.
// Simpler version for now to avoid extra deps if not needed, but standard is better.
// Let's stick to simple props for now to avoid install overhead, or just use standard button.

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', isLoading, children, ...props }, ref) => {
        const variants = {
            primary: "bg-primary hover:bg-primary-hover text-white shadow-lg shadow-primary/25",
            secondary: "bg-secondary hover:bg-secondary-hover text-white shadow-lg shadow-secondary/25",
            ghost: "hover:bg-surface text-muted-foreground hover:text-white",
            outline: "border border-border bg-transparent hover:bg-surface text-white",
        };

        const sizes = {
            sm: "h-9 px-3 text-xs",
            md: "h-11 px-6 text-sm",
            lg: "h-14 px-8 text-base",
        };

        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:pointer-events-none",
                    variants[variant],
                    sizes[size],
                    className
                )}
                ref={ref}
                disabled={isLoading || props.disabled}
                {...props}
            >
                {isLoading && (
                    <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                )}
                {children}
            </button>
        );
    }
);
Button.displayName = "Button";

export { Button };
