import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-6xl font-extrabold text-primary-600">404</h1>
      <p className="text-lg text-gray-600">Page not found</p>
      <Link to="/dashboard" className="text-primary-600 hover:underline text-sm font-medium">
        Go to Dashboard
      </Link>
    </div>
  );
}
