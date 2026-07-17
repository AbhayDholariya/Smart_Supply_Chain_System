
import { format, parseISO } from "date-fns";

export function formatDate(iso, pattern = "MMM d, yyyy") {
  return format(parseISO(iso), pattern);
}

export function formatDateTime(iso) {
  return format(parseISO(iso), "MMM d, yyyy HH:mm");
}
