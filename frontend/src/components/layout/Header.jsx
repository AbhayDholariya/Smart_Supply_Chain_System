
import { Link } from "react-router-dom";
import { Bell, User } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useNotificationStore } from "@/store/notificationStore";

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const unreadCount = useNotificationStore((s) => s.unreadCount);

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 shadow-sm">
      <div />
      <div className="flex items-center gap-4">
        {/* Notification bell */}
        <Link to="/notifications" className="relative text-gray-500 hover:text-gray-900">
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </Link>

        {/* Profile */}
        <Link
          to="/profile"
          className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <User size={18} />
          <span>{user?.username ?? "Account"}</span>
        </Link>
      </div>
    </header>
  );
}
