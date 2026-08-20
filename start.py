#!/usr/bin/env python3
"""
start.py -- Ovi Portfolio Launcher
Starts both servers with one command:  python start.py
  * Flask API  -> http://localhost:5050  (Ovi RAG chatbot backend)
  * Frontend   -> http://localhost:8080  (Portfolio website)
Press Ctrl+C to stop both servers.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OVI  = ROOT / "Ovi"

FRONTEND_PORT = 8080
BACKEND_PORT  = 5050

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
RED   = "\033[91m"
BOLD  = "\033[1m"
RESET = "\033[0m"

def banner():
    print(f"\n{BOLD}{CYAN}{'=' * 54}")
    print(f"  Ovi Portfolio -- Full Stack Launcher")
    print(f"{'=' * 54}{RESET}\n")

def start_backend():
    print(f"{YELLOW}Starting Ovi backend  (port {BACKEND_PORT})...{RESET}", flush=True)
    return subprocess.Popen(
        [sys.executable, "-u", "server.py"],
        cwd=str(OVI),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

def start_frontend():
    print(f"{YELLOW}Starting frontend     (port {FRONTEND_PORT})...{RESET}", flush=True)
    return subprocess.Popen(
        [sys.executable, "-u", "-m", "http.server", str(FRONTEND_PORT)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

def wait_for_backend(proc, timeout=15):
    deadline = time.time() + timeout
    enc = sys.stdout.encoding or "utf-8"
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        line = proc.stdout.readline()
        if line:
            # Safely handle characters that standard Windows CP1252 console can't show
            safe_line = line.encode(enc, errors="replace").decode(enc)
            print(f"  [Backend] {safe_line.strip()}", flush=True)
        if "Running on" in line or "Serving Flask" in line:
            return True
    return True

def main():
    # Configure unbuffered stdout redirection line-by-line and set UTF-8 encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        except Exception:
            pass

    banner()
    procs = []
    try:
        backend  = start_backend()
        procs.append(backend)
        wait_for_backend(backend, timeout=15)

        frontend = start_frontend()
        procs.append(frontend)
        time.sleep(1.5)

        url = f"http://localhost:{FRONTEND_PORT}"
        print(f"\n{BOLD}{GREEN}{'=' * 54}", flush=True)
        print(f"  Both servers are running!", flush=True)
        print(f"", flush=True)
        print(f"  Open your portfolio:", flush=True)
        print(f"      {CYAN}{url}{RESET}{BOLD}{GREEN}", flush=True)
        print(f"", flush=True)
        print(f"  Press Ctrl+C to stop all servers.", flush=True)
        print(f"{'=' * 54}{RESET}\n", flush=True)

        while True:
            if backend.poll() is not None:
                print(f"\n{RED}Backend server stopped unexpectedly!{RESET}", flush=True)
                break
            if frontend.poll() is not None:
                print(f"\n{RED}Frontend server stopped unexpectedly!{RESET}", flush=True)
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Shutting down...{RESET}", flush=True)
    finally:
        for p in procs:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        print(f"{GREEN}All servers stopped. Goodbye!{RESET}\n", flush=True)

if __name__ == "__main__":
    main()
