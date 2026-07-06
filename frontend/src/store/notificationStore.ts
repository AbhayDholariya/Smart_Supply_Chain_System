import { create } from "zustand";
import type { Notification } from "@/types/notification";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  setNotifications: (items: Notification[]) => void;
  markAllRead: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,
  setNotifications: (items) =>
    set({
      notifications: items,
      unreadCount: items.filter((n) => !n.is_read).length,
    }),
  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),
}));
