import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-5xl font-bold tracking-tight mb-4">
        Cine<span className="text-brand-500">Social</span>
      </h1>
      <p className="text-lg text-gray-400 mb-8 text-center max-w-md">
        AI-powered film discovery. Rate on a 10-point scale. Watch together.
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="px-6 py-3 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
        >
          Sign In
        </Link>
        <Link
          href="/register"
          className="px-6 py-3 border border-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          Create Account
        </Link>
      </div>
    </main>
  );
}
