import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_ROUTES = new Set(["/login"]);
const PUBLIC_API_PREFIXES = ["/api/auth/", "/api/health", "/api/linkedin/callback"];

// F11: Timing-safe string comparison (Edge Runtime compatible)
function timingSafeCompare(a: string, b: string): boolean {
  if (!a || !b) return false;
  const encoder = new TextEncoder();
  const aBytes = encoder.encode(a);
  const bBytes = encoder.encode(b);
  if (aBytes.length !== bBytes.length) return false;
  let diff = 0;
  for (let i = 0; i < aBytes.length; i++) {
    diff |= aBytes[i] ^ bBytes[i];
  }
  return diff === 0;
}

function isAuthenticated(request: NextRequest): boolean {
  const authCookie = request.cookies.get("mc_auth");
  if (!authCookie || !process.env.AUTH_SECRET) return false;
  return timingSafeCompare(authCookie.value, process.env.AUTH_SECRET);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_ROUTES.has(pathname)) return NextResponse.next();
  if (PUBLIC_API_PREFIXES.some((p) => pathname.startsWith(p))) return NextResponse.next();

  if (!isAuthenticated(request)) {
    if (pathname.startsWith("/api/")) {
      return NextResponse.json(
        { error: "Unauthorized", message: "Authentication required" },
        { status: 401 }
      );
    }
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
