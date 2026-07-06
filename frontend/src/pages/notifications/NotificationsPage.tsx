import { Bell } from "lucide-react";
import { useNotifications, useMarkAllRead } from "@/hooks/useNotifications";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import { formatDateTime } from "@/utils/formatDate";
import { cn } from "@/utils/cn";

const typeColor: Record<string, string> = {
  shipment_delay: "bg-red-50 border-red-200",
  low_stock: "bg-yellow-50 border-yellow-200",
  delivery_status: "bg-blue-50 border-blue-200",
  supplier_issue: "bg-orange-50 border-orange-200",
  system: "bg-gray-50 border-gray-200",
};

export default function NotificationsPage() {
  const { data, isLoading } = useNotifications();
  const { mutate: markAllRead, isPending } = useMarkAllRead();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => markAllRead()}
          loading={isPending}
        >
          Mark all as read
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : data?.results.length ? (
        <ul className="space-y-2">
          {data.results.map((n) => (
            <li
              key={n.id}
              className={cn(
                "flex items-start gap-3 rounded-xl border p-4",
                typeColor[n.notification_type] ?? "bg-white border-gray-200",
                !n.is_read && "ring-1 ring-primary-300"
              )}
            >
              <Bell size={16} className="mt-0.5 shrink-0 text-gray-400" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{n.title}</p>
                <p className="text-xs text-gray-500">{n.message}</p>
                <p className="mt-1 text-xs text-gray-400">{formatDateTime(n.created_at)}</p>
              </div>
              {!n.is_read && (
                <span className="h-2 w-2 rounded-full bg-primary-500 mt-1.5 shrink-0" aria-label="Unread" />
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="py-10 text-center text-gray-400">No notifications.</p>
      )}
    </div>
  );
}
