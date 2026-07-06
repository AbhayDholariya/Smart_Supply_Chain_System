import { cn } from "@/utils/cn";
import type { HTMLAttributes, ThHTMLAttributes, TdHTMLAttributes } from "react";

export function Table({ className, ...props }: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200">
      <table className={cn("min-w-full divide-y divide-gray-200 bg-white text-sm", className)} {...props} />
    </div>
  );
}

export function Thead({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <thead className={cn("bg-gray-50", className)} {...props} />;
}

export function Th({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn("px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500", className)}
      {...props}
    />
  );
}

export function Tbody({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={cn("divide-y divide-gray-100", className)} {...props} />;
}

export function Tr({ className, ...props }: HTMLAttributes<HTMLTableRowElement>) {
  return <tr className={cn("hover:bg-gray-50 transition-colors", className)} {...props} />;
}

export function Td({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className={cn("px-4 py-3 text-gray-700", className)} {...props} />;
}
