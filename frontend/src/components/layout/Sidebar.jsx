
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Truck,
  Package,
  Users,
  Map,
  BarChart2,
  Bell,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useAuthStore } from "@/store/authStore";
import { useNotificationStore } from "@/store/notificationStore";

const navItems = [
  { to: "/dashboard", label: "Dashboard", Icon: LayoutDashboard },
  { to: "/shipments", label: "Shipments", Icon: Truck },
  { to: "/inventory", label: "Inventory", Icon: Package },
  { to: "/suppliers", label: "Suppliers", Icon: Users },
  { to: "/routes", label: "Routes", Icon: Map },
  { to: "/analytics", label: "Analytics", Icon: BarChart2 },
  { to: "/notifications", label: "Notifications", Icon: Bell },
];

export default function Sidebar() {
  const logout = useAuthStore((s) => s.logout);
  const unreadCount = useNotificationStore((s) => s.unreadCount);

  return (
    <aside className="flex w-64 flex-col bg-primary-900 text-white">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 text-lg font-bold tracking-tight">
        🔗 SmartChain
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navItems.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-700 text-white"
                  : "text-primary-100 hover:bg-primary-800 hover:text-white"
              )
            }
          >
            <Icon size={18} />
            <span>{label}</span>
            {label === "Notifications" && unreadCount > 0 && (
              <span className="ml-auto rounded-full bg-red-500 px-2 py-0.5 text-xs">
                {unreadCount}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
