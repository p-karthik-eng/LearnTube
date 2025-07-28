"use client";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function LearningPage() {
  const { data: session } = useSession();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white border-b shadow-sm">
        <div className="text-2xl font-bold text-blue-600 select-none">LearnTube</div>
        <button
          className="rounded-full border p-1 hover:shadow"
          onClick={() => router.push("/profile")}
        >
          <img
            src={session?.user?.image || "/default-avatar.svg"}
            onError={e => { e.target.onerror = null; e.target.src = "/default-avatar.svg"; }}
            alt="Profile"
            className="w-9 h-9 rounded-full"
          />
        </button>
      </nav>
      {/* Main Content */}
      <div className="flex flex-col items-center justify-center mt-16">
        <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
          <h1 className="text-2xl font-bold mb-4">Welcome to the Learning Page!</h1>
          {session ? (
            <p className="text-lg">Hello, <span className="font-semibold">{session.user.name || session.user.email}</span>!</p>
          ) : (
            <p className="text-lg">Loading your info...</p>
          )}
          <p className="mt-4 text-gray-600">Start your learning journey here.</p>
        </div>
      </div>
    </div>
  );
} 