import { format, parseISO } from "date-fns";

export function formatDate(iso: string, pattern = "MMM d, yyyy") {
  return format(parseISO(iso), pattern);
}

export function formatDateTime(iso: string) {
  return format(parseISO(iso), "MMM d, yyyy HH:mm");
}
