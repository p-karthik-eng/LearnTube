"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function TestCoursePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/generate-learning-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate course');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewCourse = () => {
    if (url) {
      router.push(`/learning?url=${encodeURIComponent(url)}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Course Generation Test</h1>
        
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">YouTube URL:</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full p-3 border border-gray-300 rounded-lg"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Generating..." : "Generate Course"}
          </button>
        </form>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <strong>Success!</strong> Course generated successfully.
            <button
              onClick={handleViewCourse}
              className="ml-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              View Course
            </button>
          </div>
        )}

        {result && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Generated Course Data:</h2>
            <div className="mb-4">
              <strong>Course Title:</strong> {result.course_data?.courseInfo?.title}
            </div>
            <div className="mb-4">
              <strong>Total Lessons:</strong> {result.course_data?.courseInfo?.totalLessons}
            </div>
            <div className="mb-4">
              <strong>Duration:</strong> {result.course_data?.courseInfo?.duration}
            </div>
            <div className="mb-4">
              <strong>Processing Time:</strong> {result.processing_stats?.processing_time_seconds}s
            </div>
            <div className="mb-4">
              <strong>Lessons Generated:</strong> {result.processing_stats?.lessons_generated}
            </div>
            <div className="mb-4">
              <strong>Total Quizzes:</strong> {result.processing_stats?.total_quizzes}
            </div>
            
            <details className="mt-4">
              <summary className="cursor-pointer font-semibold">View Full JSON</summary>
              <pre className="mt-2 bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
} 