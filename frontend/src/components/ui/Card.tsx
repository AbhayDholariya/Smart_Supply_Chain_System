import { cn } from "@/utils/cn";
import type { HTMLAttributes } from "react";

export default function Card({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-xl border border-gray-200 bg-white p-6 shadow-sm", className)}
      {...props}
    >
      {children}
    </div>
  );
}
