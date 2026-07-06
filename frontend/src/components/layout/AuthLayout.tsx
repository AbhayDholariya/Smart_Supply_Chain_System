import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-900 to-primary-600 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white">Smart Supply Chain</h1>
          <p className="mt-1 text-primary-100">AI-powered logistics platform</p>
        </div>
        <div className="rounded-2xl bg-white p-8 shadow-xl">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
