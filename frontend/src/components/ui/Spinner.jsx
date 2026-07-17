
import { cn } from "@/utils/cn";

export default function Spinner({ className }) {
  return (
    <svg
      className={cn("h-6 w-6 animate-spin text-primary-600", className)}
      viewBox="0 0 24 24"
      fill="none"
      aria-label="Loading"
      role="status"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}
