#!/usr/bin/env python3
"""ARGUS Demo Startup Launcher Script.

Executes startup check, verifies web frontend build, and launches FastAPI server.
"""

import os
import sys
import subprocess
import uvicorn

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from scripts.startup_check import run_startup_check


def main():
    print("Initiating ARGUS Demo Launcher...")

    # Step 1: Run Startup Check
    passed = run_startup_check()
    if not passed:
        print("ERROR: Startup check failed! Please ensure all required assets exist.")
        sys.exit(1)

    # Step 2: Build web frontend if web/dist missing
    web_dist = os.path.abspath("web/dist/index.html")
    if not os.path.exists(web_dist):
        print("web/dist not found. Building web frontend...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="web", check=True)
            print("Web build complete.")
        except Exception as e:
            print(f"Failed to build web frontend: {e}")
            sys.exit(1)

    # Step 3: Launch FastAPI Uvicorn Server
    print("\nStarting ARGUS Platform Server...")
    print("Serving API and Web Frontend at: http://localhost:8000\n")
    uvicorn.run("argus.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
