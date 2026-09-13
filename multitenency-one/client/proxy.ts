import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const host = request.headers.get("host") ?? "";

  const hostname = host.split(":")[0];
  const parts = hostname.split(".");

  // Local development: john.localhost:3000
  if (hostname.endsWith("localhost")) {
    const subdomain = parts[0];

    // Root localhost — load the landing page normally
    if (subdomain === "localhost") {
      return NextResponse.next();
    }

    // Already rewritten — don't rewrite again
    if (pathname.startsWith("/tenant")) {
      return NextResponse.next();
    }

    return NextResponse.rewrite(new URL(`/tenant/${subdomain}`, request.url));
  }

  // Production: john.yourdomain.com
  if (parts.length > 2) {
    const subdomain = parts[0];

    if (subdomain !== "www") {
      if (pathname.startsWith("/tenant")) {
        return NextResponse.next();
      }

      return NextResponse.rewrite(new URL(`/tenant/${subdomain}`, request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)",
  ],
};
