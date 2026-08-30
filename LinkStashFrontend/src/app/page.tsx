"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { useSession } from "@/lib/auth/session";

export default function HomePage() {
  const { user, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status !== "ready") return;
    router.replace(user ? "/bookmarks" : "/login");
  }, [status, user, router]);

  return (
    <div className="flex min-h-svh items-center justify-center">
      <Skeleton className="h-8 w-40" />
    </div>
  );
}
