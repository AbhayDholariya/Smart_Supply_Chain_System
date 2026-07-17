import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";

// Pages
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

export default function App() {
  return (
    <Routes>
      {/* No auth required routes */}
      <Route element={<MainLayout />}>
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
