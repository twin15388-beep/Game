"""Прогон игровой логики Emberfall без Roblox.

Запуск:  python3 tools/smoke_test.py
Требует lupa (pip install lupa). Падение = проваленные проверки.
"""
import glob
import os
import sys

from lupa import LuaRuntime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "lua")
HARNESS = os.path.join(ROOT, "tools", "smoke.lua")

SHARED = ["Config", "GameData", "Net", "Util", "Quests", "NPCData", "Dungeons"]
SERVER = ["PlayerState", "Combat", "MobService", "BossService", "QuestService"]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    lua = LuaRuntime(unpack_returned_tuples=True)

    src_table = lua.table()
    for group, names, folder in (("shared", SHARED, "shared"), ("server", SERVER, "server")):
        sub = lua.table()
        for name in names:
            sub[name] = read(os.path.join(SRC, folder, name + ".lua"))
        src_table[group] = sub

    lua.globals().SRC = src_table

    with open(HARNESS, encoding="utf-8") as f:
        harness = f.read()

    failures = lua.execute(harness)
    print("Провалов: %d" % failures)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
