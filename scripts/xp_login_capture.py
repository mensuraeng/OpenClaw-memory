#!/usr/bin/env python3
"""XP Experiência — login capture (one-shot, headed, persistent).

Opens Chromium on DISPLAY=:99 with a persistent user_data_dir. Waits for
the user to complete login via noVNC (CPF+password+app token, with
"lembrar dispositivo" checked). Detects the logged-in state by URL and
by presence of the post-login dashboard, then saves `storage_state.json`
and closes the browser.

Output layout:
  /root/.openclaw/credentials/xp-experiencia/
    browser_profile/      (persistent Chromium profile — cache, local storage)
    storage_state.json    (cookies + localStorage for Playwright reuse)

Exit codes:
  0 — saved successfully
  1 — timeout (no login within MAX_WAIT_SECONDS)
  2 — other error
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

CRED_DIR = Path("/root/.openclaw/credentials/xp-experiencia")
PROFILE_DIR = CRED_DIR / "browser_profile"
STORAGE_PATH = CRED_DIR / "storage_state.json"
LOGIN_URL = "https://experiencia.xpi.com.br/conta/#/"
LOGIN_HOST = "experiencia.xpi.com.br"
MAX_WAIT_SECONDS = 900  # 15 min


async def main() -> int:
    from playwright.async_api import async_playwright

    CRED_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--password-store=basic",
                "--window-size=1280,960",
            ],
            ignore_default_args=["--enable-automation"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 920},
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print(f"[*] Navigating to {LOGIN_URL} …", flush=True)
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        print("[*] Waiting for user login via noVNC (CPF + senha + token, ", flush=True)
        print("    com 'lembrar dispositivo' MARCADO)…", flush=True)

        # Detection strategy: poll URL. After login, user should end up on
        # experiencia.xpi.com.br with a path beyond just `/login` or the
        # initial auth redirect to accounts.xpi.com.br. We look for the
        # dashboard URL pattern.
        for i in range(MAX_WAIT_SECONDS):
            await asyncio.sleep(1)
            url = page.url
            host = (urlparse(url).hostname or "").lower()
            path = urlparse(url).path.lower()

            # Logged-in signal: host is experiencia.xpi.com.br AND path
            # suggests dashboard (not /login, not /autenticar).
            is_logged_in = (
                host == LOGIN_HOST
                and ("login" not in path)
                and ("autenticar" not in path)
            )
            if is_logged_in:
                # Extra confirmation: give the page a moment to settle and
                # check for cookies that only appear post-auth.
                await asyncio.sleep(5)
                cookies = await context.cookies()
                xp_cookies = [c for c in cookies if "xpi" in c.get("domain", "")]
                if len(xp_cookies) >= 3:
                    print(
                        f"[+] Login detected at {url} "
                        f"({len(xp_cookies)} xpi cookies)",
                        flush=True,
                    )
                    break
            if i % 15 == 0:
                print(f"    [{i}s] host={host} path={path[:60]}", flush=True)
        else:
            print("[-] Timeout: login not detected within 15 min", flush=True)
            await context.close()
            return 1

        print(f"[*] Saving storage_state to {STORAGE_PATH} …", flush=True)
        await context.storage_state(path=str(STORAGE_PATH))
        os.chmod(STORAGE_PATH, 0o600)

        # Also write a summary of what was captured (without secrets)
        state = json.loads(Path(STORAGE_PATH).read_text())
        cookies = state.get("cookies", [])
        http_only = [c for c in cookies if c.get("httpOnly")]
        xpi_cookies = [c for c in cookies if "xpi" in c.get("domain", "")]
        print(f"[+] Saved {len(cookies)} cookies "
              f"({len(http_only)} httpOnly, {len(xpi_cookies)} for xpi)",
              flush=True)
        print(f"[+] xpi domains: "
              f"{sorted(set(c['domain'] for c in xpi_cookies))}",
              flush=True)

        await context.close()
        print("[+] Login capture complete. Browser closed.", flush=True)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(2)
