import { useAuthStore } from "@/store/authStore";
import Card from "@/components/ui/Card";

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);

  if (!user) return null;

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
      <Card>
        <dl className="space-y-3 text-sm">
          {[
            ["Username", user.username],
            ["Email", user.email],
            ["Role", user.role.replace("_", " ")],
            ["Phone", user.phone || "—"],
            ["Status", user.is_active ? "Active" : "Inactive"],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between border-b border-gray-100 pb-2 last:border-0">
              <dt className="text-gray-500">{label}</dt>
              <dd className="font-medium capitalize text-gray-800">{value}</dd>
            </div>
          ))}
        </dl>
      </Card>
    </div>
  );
}
