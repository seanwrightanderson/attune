import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "outline" | "success" | "warning" | "muted";
}

const variantClasses: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default:  "bg-primary/20 text-accent-foreground border-primary/30",
  outline:  "border-border text-muted-foreground bg-transparent",
  success:  "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  warning:  "bg-amber-500/15 text-amber-400 border-amber-500/30",
  muted:    "bg-secondary text-secondary-foreground border-border",
};

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
