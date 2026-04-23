import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const MAX_ATTEMPTS = 5;
const WINDOW_MS = 15 * 60 * 1000;
const LOCKOUT_MS = 15 * 60 * 1000;

interface AttemptRecord {
  count: number;
  windowStart: number;
  lockedUntil?: number;
}

const attempts = new Map<string, AttemptRecord>();

// F12: cleanup expired entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [ip, record] of attempts.entries()) {
    if (
      now - record.windowStart > WINDOW_MS &&
      (!record.lockedUntil || now > record.lockedUntil)
    ) {
      attempts.delete(ip);
    }
  }
}, 5 * 60 * 1000);

function getClientIp(request: NextRequest): string {
  return (
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    request.headers.get("x-real-ip") ||
    "unknown"
  );
}

function checkRateLimit(ip: string): { allowed: boolean; retryAfterMs?: number } {
  const now = Date.now();
  const record = attempts.get(ip);
  if (!record) return { allowed: true };
  if (record.lockedUntil && now < record.lockedUntil) {
    return { allowed: false, retryAfterMs: record.lockedUntil - now };
  }
  if (now - record.windowStart > WINDOW_MS) {
    attempts.delete(ip);
    return { allowed: true };
  }
  if (record.count >= MAX_ATTEMPTS) {
    record.lockedUntil = now + LOCKOUT_MS;
    attempts.set(ip, record);
    return { allowed: false, retryAfterMs: LOCKOUT_MS };
  }
  return { allowed: true };
}

function recordFailure(ip: string): void {
  const now = Date.now();
  const record = attempts.get(ip);
  if (!record || now - record.windowStart > WINDOW_MS) {
    attempts.set(ip, { count: 1, windowStart: now });
  } else {
    record.count += 1;
    attempts.set(ip, record);
  }
}

function clearAttempts(ip: string): void {
  attempts.delete(ip);
}

export async function POST(request: NextRequest) {
  const ip = getClientIp(request);
  const { allowed, retryAfterMs } = checkRateLimit(ip);

  if (!allowed) {
    const retryAfterSec = Math.ceil((retryAfterMs ?? LOCKOUT_MS) / 1000);
    return NextResponse.json(
      { success: false, error: "Too many failed attempts. Try again later." },
      { status: 429, headers: { "Retry-After": String(retryAfterSec) } }
    );
  }

  const { password } = await request.json();

  if (password === process.env.ADMIN_PASSWORD) {
    clearAttempts(ip);
    const response = NextResponse.json({ success: true });
    response.cookies.set("mc_auth", process.env.AUTH_SECRET!, {
      httpOnly: true,
      secure: false,   // HTTP deployment — sem HTTPS por enquanto
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7,
      path: "/",
    });
    return response;
  }

  recordFailure(ip);
  return NextResponse.json({ success: false, error: "Invalid password" }, { status: 401 });
}
