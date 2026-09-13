// Single source of truth for the API origin. This lived in two files before,
// and the copies drifted: the tenant page pointed at :8080 while the API
// listens on :8000.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
