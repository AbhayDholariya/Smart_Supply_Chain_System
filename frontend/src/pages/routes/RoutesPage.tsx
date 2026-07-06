import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { aiService } from "@/services/aiService";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const schema = z.object({
  origin: z.string().min(2, "Required"),
  destination: z.string().min(2, "Required"),
});
type FormValues = z.infer<typeof schema>;

interface RouteResult {
  recommended_route: string;
  estimated_duration_min: number | null;
  total_distance_km: number | null;
  note?: string;
}

export default function RoutesPage() {
  const [result, setResult] = useState<RouteResult | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      const { data } = await aiService.recommendRoute(values);
      setResult(data);
    } catch {
      toast.error("Route recommendation failed");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Route Optimization</h1>

      <Card className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Origin" error={errors.origin?.message} {...register("origin")} />
          <Input label="Destination" error={errors.destination?.message} {...register("destination")} />
          <Button type="submit" loading={isSubmitting}>
            Get Optimal Route
          </Button>
        </form>
      </Card>

      {result && (
        <Card className="max-w-xl">
          <h2 className="mb-3 font-semibold text-gray-700">Recommendation</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Route</dt>
              <dd className="font-medium">{result.recommended_route}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Est. Duration</dt>
              <dd className="font-medium">
                {result.estimated_duration_min ? `${result.estimated_duration_min} min` : "—"}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Distance</dt>
              <dd className="font-medium">
                {result.total_distance_km ? `${result.total_distance_km} km` : "—"}
              </dd>
            </div>
          </dl>
          {result.note && (
            <p className="mt-3 rounded-lg bg-yellow-50 p-2 text-xs text-yellow-700">{result.note}</p>
          )}
        </Card>
      )}
    </div>
  );
}
