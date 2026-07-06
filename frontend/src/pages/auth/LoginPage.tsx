import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      const { data: tokens } = await authService.login(values.email, values.password);
      // Pass the fresh access token directly — store isn't updated yet at this point
      const { data: user } = await authService.getMe(tokens.access);
      setAuth(user, tokens.access, tokens.refresh);
      navigate("/dashboard");
    } catch {
      toast.error("Invalid email or password");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Sign in</h2>
      <Input
        label="Email"
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register("email")}
      />
      <Input
        label="Password"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register("password")}
      />
      <Button type="submit" loading={isSubmitting} className="w-full">
        Sign in
      </Button>
      <p className="text-center text-sm text-gray-500">
        Don&apos;t have an account?{" "}
        <Link to="/register" className="font-medium text-primary-600 hover:underline">
          Register
        </Link>
      </p>
    </form>
  );
}
