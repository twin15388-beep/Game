"""Проверка синтаксиса всех Lua-файлов через lupa (LuaJIT).
Запуск: pip install lupa && python3 tools/lua_syntax_check.py
"""
import glob
import os
import sys
from lupa import LuaRuntime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOADER = """
function(src, name)
    local fn
    local ok, err
    if loadstring then
        ok, err = loadstring(src, name)
    else
        ok, err = load(src, name)
    end
    if ok then return "OK" else return "FAIL: " .. tostring(err) end
end
"""

def main():
    lua = LuaRuntime(unpack_returned_tuples=True)
    loader = lua.eval(LOADER)
    files = sorted(glob.glob(os.path.join(ROOT, "src", "lua", "**", "*.lua"), recursive=True))
    bad = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        result = loader(src, os.path.relpath(path, ROOT))
        if result != "OK":
            bad += 1
            print(result)
    print("Проверено %d файлов, ошибок: %d" % (len(files), bad))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
