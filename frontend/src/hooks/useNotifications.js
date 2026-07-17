import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationService } from "@/services/notificationService";
import { useNotificationStore } from "@/store/notificationStore";
import { useEffect } from "react";

export function useNotifications() {
  const setNotifications = useNotificationStore((s) => s.setNotifications);
  const query = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationService.getAll().then((r) => r.data),
  });

  useEffect(() => {
    if (query.data) setNotifications(query.data.results);
  }, [query.data, setNotifications]);

  return query;
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  const markAllRead = useNotificationStore((s) => s.markAllRead);
  return useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      markAllRead();
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
