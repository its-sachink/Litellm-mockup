# Replica of the malicious cook.py
# Loaded automatically by cook.pth when Python starts.
# Safe lab version: only writes a marker file.
import os

_MARKER = "/tmp/cook_executed"

def _run():
    with open(_MARKER, "w") as f:
        f.write(f"cook.py executed by pid={os.getpid()}\n")

_run()
