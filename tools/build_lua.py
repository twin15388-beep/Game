"""Сборка Lua-модулей в gen_map.py.

Запуск (из корня репозитория):
    python3 tools/build_lua.py

Скрипт читает src/lua/**/*.lua, экранирует и генерирует файл `gen_lua.py`,
который затем импортируется в gen_map.py. Это держит Lua в отдельных файлах
(легко править) и не требует внешних зависимостей.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "lua")
OUT = os.path.join(ROOT, "gen_lua.py")

# порядок важен: shared — раньше остальных
SHARED = ["Config", "GameData", "Net", "Util", "Quests", "NPCData"]

SERVER = [
    "PlayerState", "Combat", "MobService", "BossService",
    "MagicService", "QuestService", "WorldService", "InteractService", "Main",
]

CLIENT = ["UIKit", "HUD", "SpellBar", "Panels", "Fx", "Controls", "ClientMain"]

CLIENT_MODULES = ["UIKit", "HUD", "SpellBar", "Panels", "Fx", "Controls"]


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def esc_lua(s):
    """Кладём Lua в python-строку с тройными кавычками."""
    if '"""' in s:
        raise ValueError("Lua содержит тройные кавычки — разбей файл")
    if "\\" in s:
        # обратные слэши в Lua допустимы, но в обычной python-строке их надо экранировать
        s = s.replace("\\", "\\\\")
    return s


def main():
    parts = []
    parts.append("# -*- coding: utf-8 -*-\n")
    parts.append('"""АВТОГЕНЕРАЦИЯ. Правь Lua в src/lua/**, затем: python3 tools/build_lua.py"""\n\n')

    parts.append("SHARED = {}\n")
    for name in SHARED:
        code = esc_lua(read(os.path.join(SRC, "shared", name + ".lua")))
        parts.append('SHARED["%s"] = """%s"""\n\n' % (name, code))

    parts.append("SERVER = {}\n")
    for name in SERVER:
        code = esc_lua(read(os.path.join(SRC, "server", name + ".lua")))
        parts.append('SERVER["%s"] = """%s"""\n\n' % (name, code))

    parts.append("CLIENT = {}\n")
    for name in CLIENT:
        code = esc_lua(read(os.path.join(SRC, "client", name + ".lua")))
        parts.append('CLIENT["%s"] = """%s"""\n\n' % (name, code))

    parts.append("CLIENT_MODULES = %r\n" % (CLIENT_MODULES,))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    size = os.path.getsize(OUT)
    print("gen_lua.py собран: %.1f КБ (%d shared, %d server, %d client)"
          % (size / 1024.0, len(SHARED), len(SERVER), len(CLIENT)))


if __name__ == "__main__":
    main()
