import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import type { AxiosError } from "axios";
import { authService } from "@/services/authService";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const schema = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  role: z.enum(["admin", "supplier", "warehouse_manager", "transporter", "customer"]),
});
type FormValues = z.infer<typeof schema>;

/** Pull the first human-readable message out of a DRF error response. */
function extractApiError(err: unknown): string {
  const error = err as AxiosError<Record<string, string | string[]>>;
  const data = error?.response?.data;
  if (!data) return "Registration failed. Please try again.";

  // DRF returns field errors as { field: ["msg"] } or non-field as { detail: "msg" }
  for (const key of ["email", "username", "password", "non_field_errors", "detail"]) {
    if (data[key]) {
      const val = data[key];
      return Array.isArray(val) ? val[0] : String(val);
    }
  }

  // Fallback: grab the first error from any field
  const first = Object.values(data)[0];
  if (first) return Array.isArray(first) ? first[0] : String(first);

  return "Registration failed. Please try again.";
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: "customer" },
  });

  const onSubmit = async (values: FormValues) => {
    try {
      await authService.register(values);
      toast.success("Account created — please sign in");
      navigate("/login");
    } catch (err) {
      toast.error(extractApiError(err));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Create account</h2>
      <Input label="Username" error={errors.username?.message} {...register("username")} />
      <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
      <Input label="Password" type="password" error={errors.password?.message} {...register("password")} />
      <div className="flex flex-col gap-1">
        <label htmlFor="role" className="text-sm font-medium text-gray-700">Role</label>
        <select
          id="role"
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          {...register("role")}
        >
          <option value="customer">Customer</option>
          <option value="supplier">Supplier</option>
          <option value="warehouse_manager">Warehouse Manager</option>
          <option value="transporter">Transporter</option>
          <option value="admin">Administrator</option>
        </select>
      </div>
      <Button type="submit" loading={isSubmitting} className="w-full">
        Register
      </Button>
      <p className="text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-primary-600 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
