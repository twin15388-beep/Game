#!/usr/bin/env python3
"""Полная сборка Emberfall v8 в одну команду:

    python3 build.py

Шаги:
  1. src/lua/**  ->  gen_lua.py        (Lua в python-строки)
  2. gen_lua.py + gen_map.py -> Emberfall_Map_v10.rbxlx
  3. release/Emberfall_v8.zip          (готовый архив для скачивания)
"""
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
RLX = "Emberfall_Map_v11.rbxlx"
ZIP_PATH = os.path.join(ROOT, "release", "Emberfall_v11.zip")


def run(*args):
    print("$", " ".join(args))
    res = subprocess.run(args, cwd=ROOT)
    if res.returncode != 0:
        sys.exit(res.returncode)


def main():
    run(sys.executable, os.path.join("tools", "build_lua.py"))
    run(sys.executable, "gen_map.py")

    # проверки, если доступен lupa
    try:
        import lupa  # noqa: F401
        run(sys.executable, os.path.join("tools", "lua_syntax_check.py"))
        run(sys.executable, os.path.join("tools", "smoke_test.py"))
    except ImportError:
        print("(lupa не установлен — проверки Lua пропущены: pip install lupa)")

    os.makedirs(os.path.join(ROOT, "release"), exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(ROOT, RLX), RLX)
        for name in ("gen_map.py", "gen_lua.py", "README.md", "HANDOFF.md", "build.py"):
            z.write(os.path.join(ROOT, name), name)
        for folder, _, files in os.walk(os.path.join(ROOT, "src")):
            for f in files:
                full = os.path.join(folder, f)
                z.write(full, os.path.relpath(full, ROOT))
        for folder, _, files in os.walk(os.path.join(ROOT, "tools")):
            for f in files:
                full = os.path.join(folder, f)
                z.write(full, os.path.relpath(full, ROOT))

    size = os.path.getsize(ZIP_PATH) / 1e6
    print("\nГотово: %s (%.1f МБ)" % (ZIP_PATH, size))


if __name__ == "__main__":
    main()
