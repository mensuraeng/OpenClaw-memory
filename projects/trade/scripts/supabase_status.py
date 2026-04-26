#!/usr/bin/env python3
"""Lightweight Supabase readiness check for Trade.
Does not print secrets. Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or anon key later.
"""
import os

required = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print("Supabase not configured. Missing:", ", ".join(missing))
    raise SystemExit(2)
print("Supabase environment looks configured (secrets hidden).")
