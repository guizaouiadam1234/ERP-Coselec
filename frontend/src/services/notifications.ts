import api from "./api";

export type NotificationItem = {
  id: number;
  user_id: number;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
  reference_id?: number | null;
};

export async function getNotifications(unreadOnly = false) {
  const response = await api.get("/notifications/", {
    params: { unread_only: unreadOnly },
  });

  return response.data as NotificationItem[];
}

export async function markNotificationAsRead(notificationId: number) {
  const response = await api.patch(`/notifications/${notificationId}/read/`);
  return response.data as NotificationItem;
}
