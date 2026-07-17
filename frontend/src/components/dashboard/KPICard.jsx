
import Card from "@/components/ui/Card";
import { cn } from "@/utils/cn";

export default function KPICard({
  label,
  value,
  icon: Icon,
  trend,
  trendUp,
  className,
}) {
  return (
    <Card className={cn("flex items-start justify-between", className)}>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
        {trend && (
          <p
            className={cn(
              "mt-1 text-xs font-medium",
              trendUp ? "text-green-600" : "text-red-500"
            )}
          >
            {trend}
          </p>
        )}
      </div>
      <div className="rounded-lg bg-primary-50 p-3">
        <Icon size={22} className="text-primary-600" />
      </div>
    </Card>
  );
}
