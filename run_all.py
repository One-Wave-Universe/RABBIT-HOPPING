#!/usr/bin/env python3
"""Run all Rabbit Hopping test suites."""
import subprocess, sys

suites = ["rabbit_hopping.py", "memory_rebuild.py", "quadratic_memory.py"]
failed = False
for s in suites:
    print(f"\n=== {s} ===")
    r = subprocess.run([sys.executable, s], capture_output=False)
    if r.returncode != 0:
        failed = True
        print(f"FAILED: {s}")
if failed:
    sys.exit(1)
print("\nAll suites passed.")
