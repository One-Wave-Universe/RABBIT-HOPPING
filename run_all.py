#!/usr/bin/env python3
"""Run both Rabbit Hopping model tests and Memory Rebuild engine tests."""
import subprocess, sys

def run(mod):
    r = subprocess.run([sys.executable, mod], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)

if __name__ == "__main__":
    run("rabbit_hopping.py")
    run("memory_rebuild.py")
    print("ALL SYSTEMS GO. Rabbit is hopping and remembering.")
