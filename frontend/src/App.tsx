import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import MainLayout from "@/components/layout/MainLayout";
import AuthLayout from "@/components/layout/AuthLayout";

// Pages
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import ShipmentsPage from "@/pages/shipments/ShipmentsPage";
import ShipmentDetailPage from "@/pages/shipments/ShipmentDetailPage";
import InventoryPage from "@/pages/inventory/InventoryPage";
import SuppliersPage from "@/pages/suppliers/SuppliersPage";
import RoutesPage from "@/pages/routes/RoutesPage";
import AnalyticsPage from "@/pages/analytics/AnalyticsPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import ProfilePage from "@/pages/profile/ProfilePage";
import NotFoundPage from "@/pages/NotFoundPage";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Protected routes */}
      <Route
        element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/shipments" element={<ShipmentsPage />} />
        <Route path="/shipments/:id" element={<ShipmentDetailPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/suppliers" element={<SuppliersPage />} />
        <Route path="/routes" element={<RoutesPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
