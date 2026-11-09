#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_map.py — генератор карты «Emberfall — Пепел Вечности» (v1: мир).
Запуск:  python3 gen_map.py
Результат: Emberfall_Map_v1.rbxlx (открывать в Roblox Studio: File → Open from File)

Структура Workspace:
  SpawnLocation
  World/           — весь ландшафт и декор по зонам
  GameLogic/       — маркеры для будущих систем (мобы, боссы, NPC, триггеры)
"""
import math
import random

from gen_lua import SHARED, SERVER, CLIENT, CLIENT_MODULES

SEED = 20261108
rng = random.Random(SEED)

# ----------------------------------------------------------------------------
# XML-писатель
# ----------------------------------------------------------------------------
_lines = []
_depth = 0
_ref = 0


def _w(s):
    _lines.append(s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(v):
    v = round(float(v), 4)
    if v == int(v):
        return str(int(v))
    return ("%g" % v)


def begin_item(cls, name):
    global _ref, _depth
    _ref += 1
    _w("  " * _depth + '<Item class="%s" referent="RBX%d">' % (cls, _ref))
    _depth += 1
    _w("  " * _depth + "<Properties>")
    _depth += 1
    _w("  " * _depth + '<string name="Name">%s</string>' % esc(name))


def p_raw(s):
    _w("  " * _depth + s)


def p_str(n, v):
    p_raw('<string name="%s">%s</string>' % (n, esc(v)))


def p_bool(n, v):
    p_raw('<bool name="%s">%s</bool>' % (n, "true" if v else "false"))


def p_float(n, v):
    p_raw('<float name="%s">%s</float>' % (n, fmt(v)))


def p_int(n, v):
    p_raw('<int name="%s">%d</int>' % (n, v))


# ЧИСЛОВЫЕ ЗНАЧЕНИЯ ENUM ДЛЯ ФОРМАТА RBXLX (token = int, имена запрещены!)
MATERIAL_IDS = {
    "Plastic": 256, "SmoothPlastic": 272, "Neon": 288,
    "Wood": 512, "WoodPlanks": 528,
    "Marble": 784, "Slate": 800, "Concrete": 816, "Granite": 832,
    "Brick": 848, "Pebble": 864, "Cobblestone": 880, "Rock": 896,
    "Sandstone": 912, "Basalt": 788,
    "CorrodedMetal": 1040, "DiamondPlate": 1056, "Foil": 1072, "Metal": 1088,
    "Grass": 1280, "Sand": 1296, "Fabric": 1288, "Snow": 1328, "Mud": 1344,
    "Ground": 1360,
    "Ice": 1536, "Glacier": 1552, "CrackedLava": 1560, "Water": 2048,
}
PARTTYPE_IDS = {"Ball": 0, "Block": 1, "Cylinder": 2}
SURFACE_IDS = {"Smooth": 0, "Studs": 8}
NORMALID_IDS = {"Right": 0, "Top": 1, "Front": 2, "Left": 3, "Bottom": 4, "Back": 5}
SIZING_IDS = {"FixedSize": 0, "PixelsPerStud": 1}


def p_token(n, v):
    if not isinstance(v, int):
        raise ValueError("token %s=%r должен быть int (enum rbxlx)!" % (n, v))
    p_raw('<token name="%s">%d</token>' % (n, v))


def p_pstr(n, v):
    p_raw('<ProtectedString name="%s">%s</ProtectedString>' % (n, esc(v)))


def p_vec3(n, x, y, z):
    p_raw('<Vector3 name="%s"><X>%s</X><Y>%s</Y><Z>%s</Z></Vector3>'
          % (n, fmt(x), fmt(y), fmt(z)))


def p_color3(n, r, g, b):
    p_raw('<Color3 name="%s"><R>%s</R><G>%s</G><B>%s</B></Color3>'
          % (n, fmt(r / 255.0), fmt(g / 255.0), fmt(b / 255.0)))


def p_color3u8(n, r, g, b):
    v = 0xFF000000 + (int(r) << 16) + (int(g) << 8) + int(b)
    p_raw('<Color3uint8 name="%s">%d</Color3uint8>' % (n, v))


def rot_ypr(yaw=0.0, pitch=0.0, roll=0.0):
    y, x, z = math.radians(yaw), math.radians(pitch), math.radians(roll)
    cy, sy = math.cos(y), math.sin(y)
    cx, sx = math.cos(x), math.sin(x)
    cz, sz = math.cos(z), math.sin(z)

    def mul(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)]
                for i in range(3)]

    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mul(Ry, mul(Rx, Rz))


def p_cframe(n, pos, yaw=0.0, pitch=0.0, roll=0.0):
    R = rot_ypr(yaw, pitch, roll)
    parts = ['<CoordinateFrame name="%s">' % n]
    parts.append("<X>%s</X><Y>%s</Y><Z>%s</Z>" % (fmt(pos[0]), fmt(pos[1]), fmt(pos[2])))
    for i in range(3):
        for j in range(3):
            parts.append("<R%d%d>%s</R%d%d>" % (i, j, fmt(R[i][j]), i, j))
    parts.append("</CoordinateFrame>")
    p_raw("".join(parts))


def end_props():
    global _depth
    _depth -= 1
    _w("  " * _depth + "</Properties>")


def end_item():
    global _depth
    _depth -= 1
    _w("  " * _depth + "</Item>")


_folder_depth = 0


def folder(name):
    global _folder_depth
    if PLANNING:
        return
    _folder_depth += 1
    begin_item("Folder", name)
    end_props()


def endfolder():
    global _folder_depth
    if PLANNING or _folder_depth <= 0:
        return
    _folder_depth -= 1
    end_item()


# ----------------------------------------------------------------------------
# Базовые примитивы
# ----------------------------------------------------------------------------
PLANNING = False


def part(name, size, pos, yaw=0.0, pitch=0.0, roll=0.0, color=(163, 162, 165),
         material="Plastic", transparency=0.0, cancollide=True, anchored=True,
         shape=None, cls="Part", reflectance=None, light=None, fire=None):
    """light = dict(brightness, range, color, shadows); fire = dict(size, heat, color, secondary)"""
    if PLANNING:
        return
    begin_item(cls, name)
    p_bool("Anchored", anchored)
    p_bool("CanCollide", cancollide)
    p_vec3("size", *size)
    p_cframe("CFrame", pos, yaw, pitch, roll)
    p_color3u8("Color3uint8", *color)
    p_token("Material", MATERIAL_IDS[material])  # только int!
    if cls == "Part":
        p_token("shape", PARTTYPE_IDS[shape or "Block"])
    p_float("Transparency", transparency)
    p_token("TopSurface", SURFACE_IDS["Smooth"])
    p_token("BottomSurface", SURFACE_IDS["Smooth"])
    if reflectance is not None:
        p_float("Reflectance", reflectance)
    end_props()
    if fire:
        begin_item("Fire", "Fire")
        p_float("size", fire.get("size", 5))
        p_float("heat", fire.get("heat", 6))
        p_color3("Color", *fire.get("color", (255, 140, 60)))
        p_color3("SecondaryColor", *fire.get("secondary", (130, 70, 25)))
        end_props()
        end_item()
    if light:
        begin_item("PointLight", "Light")
        p_float("Brightness", light.get("brightness", 1.5))
        p_float("Range", light.get("range", 24))
        p_color3("Color", *light.get("color", (255, 190, 120)))
        p_bool("Shadows", light.get("shadows", False))
        end_props()
        end_item()
    end_item()


def split_span(a, b):
    span = b - a
    if span <= 2000:
        return [(a, b)]
    n = int(math.ceil(span / 2000.0))
    step = span / n
    return [(a + i * step, a + (i + 1) * step) for i in range(n)]


def slab(name, x0, z0, x1, z1, top, bottom, color, material,
         transparency=0.0, cancollide=True):
    for ax, bx in split_span(x0, x1):
        for az, bz in split_span(z0, z1):
            part(name, (bx - ax, top - bottom, bz - az),
                 ((ax + bx) / 2.0, (top + bottom) / 2.0, (az + bz) / 2.0),
                 color=color, material=material, transparency=transparency,
                 cancollide=cancollide)


def disc(name, cx, cz, y_top, r, thickness, color, material,
         transparency=0.0, cancollide=True, light=None):
    """Плоский диск (цилиндр, повёрнутый плашмя). Верх на y_top."""
    part(name, (thickness, r * 2, r * 2), (cx, y_top - thickness / 2.0, cz),
         roll=90, shape="Cylinder", color=color, material=material,
         transparency=transparency, cancollide=cancollide, light=light)


def v_cyl(name, cx, cz, y_bottom, h, dia, color, material,
          transparency=0.0, cancollide=True, light=None, tilt_pitch=0.0, tilt_roll=0.0):
    """Вертикальный цилиндр (колонна/ствол)."""
    part(name, (h, dia, dia), (cx, y_bottom + h / 2.0, cz),
         roll=90 + tilt_roll, pitch=tilt_pitch, shape="Cylinder", color=color,
         material=material, transparency=transparency, cancollide=cancollide,
         light=light)


def l2w(cx, cz, yaw_deg, lx, lz):
    a = math.radians(yaw_deg)
    return (cx + lx * math.cos(a) + lz * math.sin(a),
            cz - lx * math.sin(a) + lz * math.cos(a))


def angle_gap(a, b):
    d = (a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


# ----------------------------------------------------------------------------
# Маркеры игровых систем (GameLogic)
# ----------------------------------------------------------------------------
def zone_trigger(zone_id, x0, z0, x1, z1):
    part("ZoneTrigger_" + zone_id, (x1 - x0, 340, z1 - z0),
         ((x0 + x1) / 2.0, 170, (z0 + z1) / 2.0),
         color=(0, 255, 0), material="Neon", transparency=1, cancollide=False)


# v11: точки мобов, заказанные из биомов, ставятся позже в GameLogic/MobSpawns
MOB_SPAWN_EXTRA = []


def register_mob(zone, x, z, y):
    """Заказать точку моба из любого места карты (эмитится в build_game_logic)."""
    if PLANNING:
        return
    MOB_SPAWN_EXTRA.append((zone, float(x), float(z), float(y)))


def mob_spawn(zone, idx, x, z, y):
    part("MobSpawn_%s_%02d" % (zone, idx), (1.6, 1.6, 1.6), (x, y + 1.0, z),
         color=(255, 60, 50), material="Neon", transparency=0.55, cancollide=False)


def boss_spawn(boss_id, x, z, y):
    part("BossSpawn_" + boss_id, (4, 4, 4), (x, y + 2.5, z),
         color=(170, 80, 255), material="Neon", transparency=0.4, cancollide=False)


def npc_spot(role, x, z, y):
    part("NPC_" + role, (2.4, 2.4, 2.4), (x, y + 1.6, z),
         color=(80, 220, 255), material="Neon", transparency=0.35, cancollide=False)


def arena_trigger(boss_id, x, z, y, r=75):
    part("ArenaTrigger_" + boss_id, (60, r * 2, r * 2), (x, y + 26, z), roll=90,
         shape="Cylinder", color=(255, 0, 255), material="Neon",
         transparency=1, cancollide=False)


# ----------------------------------------------------------------------------
# Префабы декора
# ----------------------------------------------------------------------------
def tree_gloom(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 7, "decor")
    th = rng.uniform(9, 14) * s
    part("Tree", (2 * s, th, 2 * s), (x, y + th / 2, z),
         yaw=rng.uniform(0, 360), color=(44, 36, 40), material="Wood")
    cw = rng.uniform(7, 10) * s
    part("Tree_Canopy", (cw, rng.uniform(5, 7) * s, cw), (x, y + th + 2 * s, z),
         yaw=rng.uniform(0, 360), color=rng.choice([(36, 46, 40), (30, 40, 36), (40, 44, 52)]),
         material="Grass", cancollide=False)
    part("Tree_Canopy2", (cw * 0.6, 3 * s, cw * 0.6), (x, y + th + 5.5 * s, z),
         yaw=rng.uniform(0, 360), color=(30, 38, 34), material="Grass", cancollide=False)


def pine(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 6, "decor")
    th = 7 * s
    part("Pine", (1.6 * s, th, 1.6 * s), (x, y + th / 2, z),
         color=(60, 48, 40), material="Wood")
    lv = [(7.5, 3), (5.5, 2.6), (3.5, 2.2)]
    cy = y + th
    for w, h in lv:
        part("Pine_Layer", (w * s, h * s, w * s), (x, cy + h * s / 2, z),
             yaw=rng.uniform(0, 45), color=(44, 70, 58), material="Grass",
             cancollide=False)
        cy += h * s
    part("Pine_Snow", (2.4 * s, 1.4 * s, 2.4 * s), (x, cy + 0.7 * s, z),
         yaw=rng.uniform(0, 45), color=(214, 222, 232), material="Snow",
         cancollide=False)


def dead_tree(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 6, "decor")
    th = rng.uniform(8, 12) * s
    part("DeadTree", (1.8 * s, th, 1.8 * s), (x, y + th / 2, z),
         yaw=rng.uniform(0, 360), pitch=rng.uniform(-6, 6), color=(52, 44, 36),
         material="Wood")
    part("DeadTree_Branch", (1.0 * s, rng.uniform(4, 6) * s, 1.0 * s),
         (x + rng.uniform(-1.5, 1.5), y + th * 0.75, z + rng.uniform(-1.5, 1.5)),
         yaw=rng.uniform(0, 360), pitch=rng.uniform(20, 40), color=(52, 44, 36),
         material="Wood", cancollide=False)
    part("DeadTree_Branch2", (0.8 * s, rng.uniform(3, 5) * s, 0.8 * s),
         (x + rng.uniform(-2, 2), y + th * 0.55, z + rng.uniform(-2, 2)),
         yaw=rng.uniform(0, 360), pitch=rng.uniform(-40, -20), color=(48, 40, 34),
         material="Wood", cancollide=False)


def palm_dead(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 6, "decor")
    th = 10 * s
    tilt = rng.uniform(8, 18)
    tyaw = rng.uniform(0, 360)
    part("Palm", (1.4 * s, th, 1.4 * s), (x, y + th / 2, z), yaw=tyaw,
         pitch=tilt, color=(96, 78, 58), material="Wood")
    hx, hz = x, z
    hy = y + th
    for f in (0, 90, 180, 270):
        fx, fz = l2w(hx, hz, tyaw, math.cos(math.radians(f)) * 2.4 * s,
                     math.sin(math.radians(f)) * 2.4 * s)
        part("Palm_Frond", (4.6 * s, 0.5 * s, 1.5 * s), (fx, hy - 0.2, fz),
             yaw=tyaw + f, pitch=-16, color=(84, 88, 60), material="Grass",
             cancollide=False)


def rock(x, z, y, s=1.0, mat="Rock", col=(70, 72, 78)):
    y = sy(x, z, y)
    occupy(x, z, 5, "decor")
    r = rng.uniform(2.5, 6.5) * s
    part("Rock", (r, r, r), (x, y + r * 0.22, z), yaw=rng.uniform(0, 360),
         pitch=rng.uniform(-10, 10), roll=rng.uniform(-10, 10),
         color=col, material=mat)


def mushroom(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 4, "decor")
    h = rng.uniform(2.5, 4.5) * s
    part("Mushroom_Stem", (h, 1.4 * s, 1.4 * s), (x, y + h / 2, z), roll=90,
         shape="Cylinder", color=(200, 195, 175), material="SmoothPlastic")
    part("Mushroom_Cap", (2.8 * s, 1.6 * s, 2.8 * s), (x, y + h + 0.4, z),
         shape="Ball", color=(150, 60, 190), material="Neon", cancollide=False)


def reed(x, z, y):
    y = sy(x, z, y)
    part("Reed", (0.7, rng.uniform(3, 5), 0.7), (x, y + 2, z),
         yaw=rng.uniform(0, 360), pitch=rng.uniform(-8, 8), color=(64, 70, 44),
         material="Grass", cancollide=False)


def crystal(x, z, y, s=1.0, hue="cyan"):
    y = sy(x, z, y)
    col = (110, 220, 255) if hue == "cyan" else (190, 110, 255)
    for i in range(3):
        h = rng.uniform(3, 7) * s
        dx, dz = l2w(x, z, rng.uniform(0, 360), rng.uniform(-1.5, 1.5) * s,
                     rng.uniform(-1.5, 1.5) * s)
        part("Crystal", (1.2 * s, h, 1.2 * s), (dx, y + h / 2, dz),
             yaw=rng.uniform(0, 360), pitch=rng.uniform(-14, 14),
             roll=rng.uniform(-14, 14), color=col, material="Neon")
    if rng.random() < 0.4:
        part("Crystal_Glow", (0.1, 0.1, 0.1), (x, y + 2, z), transparency=1,
             cancollide=False,
             light=dict(brightness=1.2, range=18, color=col))


def brazier(x, z, y):
    y = sy(x, z, y)
    disc("Brazier_Bowl", x, z, y + 1.4, 2.2, 1.4, (45, 45, 50), "Metal")
    part("Brazier_Flame", (1.4, 1.8, 1.4), (x, y + 2.5, z), color=(255, 120, 30),
         material="Neon", cancollide=False, transparency=0.15,
         fire=dict(size=5, heat=7),
         light=dict(brightness=1.6, range=24, color=(255, 140, 50)))


def lamppost(x, z, y):
    y = sy(x, z, y)
    part("LampPost", (0.5, 9, 0.5), (x, y + 4.5, z), color=(50, 50, 54),
         material="Metal")
    part("LampPost_Head", (1.3, 1.5, 1.3), (x, y + 9.5, z), color=(255, 190, 110),
         material="Neon", cancollide=False,
         light=dict(brightness=1.4, range=28, color=(255, 180, 100)))


def tombstone(x, z, y):
    y = sy(x, z, y)
    yaw = rng.uniform(0, 360)
    col = rng.choice([(130, 128, 122), (110, 108, 102), (120, 116, 108)])
    if rng.random() < 0.25:
        part("Grave_Cross", (0.8, 3.4, 0.8), (x, y + 1.7, z), yaw=yaw,
             color=col, material="Slate")
        part("Grave_CrossBar", (1.8, 0.7, 0.7), (x, y + 2.4, z), yaw=yaw,
             color=col, material="Slate")
    else:
        pitch = rng.choice([0, 0, 0, rng.uniform(-9, 9)])
        part("Grave", (2, 3, 0.6), (x, y + 1.5, z), yaw=yaw, pitch=pitch,
             color=col, material="Slate")


def water_pool(x, z, y, r, col=(44, 66, 48)):
    y = sy(x, z, y)
    disc("WaterPool", x, z, y + 0.75, r, 0.7, col, "Water",
         transparency=0.35, cancollide=False)


def lava_pool(x, z, y, r):
    y = sy(x, z, y)
    disc("Hazard_Lava", x, z, y + 0.55, r, 1.0, (255, 96, 18), "Neon",
         light=dict(brightness=1.3, range=20, color=(255, 110, 30))
         if rng.random() < 0.3 else None)


# ----------------------------------------------------------------------------
# Постройки
# ----------------------------------------------------------------------------
# ============================================================================
# v12: РЕЕСТР ЗАНЯТЫХ МЕСТ — чтобы ничего не ставилось друг на друга
# ============================================================================
OCCUPIED = []   # (x, z, r, kind): kind = "build" | "road" | "cave"


def occupy(x, z, r, kind="build"):
    """Отметить место как занятое (постройки, дороги, входы в данжи)."""
    if not OCCUPIED_ACTIVE:
        return
    OCCUPIED.append((float(x), float(z), float(r), kind))


def is_free(x, z, pad=0.0, kinds=None):
    """Свободно ли место: не пересекается с уже отмеченными объектами."""
    for (ox, oz, orad, kind) in OCCUPIED:
        if kinds is not None and kind not in kinds:
            continue
        if math.hypot(x - ox, z - oz) < orad + pad:
            return False
    return True


OCCUPIED_ACTIVE = True
# v12: запомненные места первого прохода — чтобы второй проход их тоже уважал
OCCUPIED_PLAN = []
OCCUPIED_REAL = []


def occ_save():
    global OCCUPIED_PLAN, OCCUPIED_REAL
    del OCCUPIED[:]
    OCCUPIED.extend(OCCUPIED_PLAN)


def occ_done():
    """Конец прохода: набор занятых мест накапливается (план ∪ реальный)."""
    OCCUPIED_PLAN[:] = []
    OCCUPIED_PLAN.extend(OCCUPIED)
    OCCUPIED_REAL[:] = []
    OCCUPIED_REAL.extend(OCCUPIED)


def footprint(cx, cz, yaw, w, d):
    """Радиус описанной окружности вокруг прямоугольного основания."""
    return 0.5 * math.hypot(w, d)


def house(name, cx, cz, gy, w, d, h, yaw=0.0,
          wall=(176, 168, 150), roof=(70, 50, 38),
          wall_mat="WoodPlanks", roof_mat="WoodPlanks",
          windows=True, chimney=True):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, footprint(cx, cz, yaw, w, d) + 6)
    part(name + "_Body", (w, h, d), (cx, gy + h / 2.0, cz), yaw=yaw,
         color=wall, material=wall_mat)
    rh = d * 0.42
    wx, wz = l2w(cx, cz, yaw, 0, -d / 4.0)
    part(name + "_RoofA", (w + 2.4, rh, d / 2.0 + 1.2), (wx, gy + h + rh / 2.0, wz),
         yaw=yaw, color=roof, material=roof_mat, cls="WedgePart")
    wx, wz = l2w(cx, cz, yaw, 0, d / 4.0)
    part(name + "_RoofB", (w + 2.4, rh, d / 2.0 + 1.2), (wx, gy + h + rh / 2.0, wz),
         yaw=yaw + 180, color=roof, material=roof_mat, cls="WedgePart")
    dx, dz = l2w(cx, cz, yaw, 0, d / 2.0 + 0.16)
    part(name + "_Door", (2.4, 3.8, 0.3), (dx, gy + 1.9, dz), yaw=yaw,
         color=(28, 22, 20), material="Wood", cancollide=False)
    if windows:
        for sx in (-w / 3.0, w / 3.0):
            wx2, wz2 = l2w(cx, cz, yaw, sx, d / 2.0 + 0.14)
            part(name + "_Win", (1.4, 1.4, 0.28), (wx2, gy + h * 0.62, wz2),
                 yaw=yaw, color=(255, 190, 90), material="Neon",
                 transparency=0.25, cancollide=False)
    if chimney:
        cx2, cz2 = l2w(cx, cz, yaw, w / 4.0, 0)
        ch = h + rh + 2.5
        part(name + "_Chimney", (1.6, ch, 1.6), (cx2, gy + ch / 2.0, cz2),
             yaw=yaw, color=(88, 64, 58), material="Brick")


def tavern(cx, cz, gy, yaw=0.0):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 22)
    house("Tavern", cx, cz, gy, 24, 18, 11, yaw=yaw, wall=(94, 74, 54),
          roof=(66, 46, 34))
    px, pz = l2w(cx, cz, yaw, 0, 12.5)
    part("Tavern_Porch", (12, 0.6, 7), (px, gy + 0.3, pz), yaw=yaw,
         color=(80, 62, 46), material="WoodPlanks")
    for sx in (-5, 5):
        qx, qz = l2w(cx, cz, yaw, sx, 15.5)
        part("Tavern_Post", (0.8, 5, 0.8), (qx, gy + 2.5, qz), yaw=yaw,
             color=(70, 54, 40), material="Wood")
    sx2, sz2 = l2w(cx, cz, yaw, 8, 9.4)
    part("Tavern_Sign", (3.4, 2, 0.3), (sx2, gy + 6, sz2), yaw=yaw,
         color=(255, 170, 60), material="Neon", cancollide=False,
         light=dict(brightness=1.0, range=16, color=(255, 170, 70)))


def chapel(cx, cz, gy, yaw=0.0):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 26)
    part("Chapel_Body", (20, 16, 34), (cx, gy + 8, cz), yaw=yaw,
         color=(150, 146, 138), material="Cobblestone")
    rh = 10
    wx, wz = l2w(cx, cz, yaw, 0, -8.5)
    part("Chapel_RoofA", (22, rh, 18), (wx, gy + 16 + rh / 2.0, wz), yaw=yaw,
         color=(58, 60, 68), material="Slate", cls="WedgePart")
    wx, wz = l2w(cx, cz, yaw, 0, 8.5)
    part("Chapel_RoofB", (22, rh, 18), (wx, gy + 16 + rh / 2.0, wz), yaw=yaw + 180,
         color=(58, 60, 68), material="Slate", cls="WedgePart")
    tx, tz = l2w(cx, cz, yaw, 6, -12)
    part("Chapel_Tower", (9, 26, 9), (tx, gy + 13, tz), yaw=yaw,
         color=(140, 136, 128), material="Cobblestone")
    part("Chapel_SpireA", (10, 7, 5), (tx, gy + 26 + 3.5, tz), yaw=yaw,
         color=(48, 50, 58), material="Slate", cls="WedgePart")
    part("Chapel_SpireB", (10, 7, 5), (tx, gy + 26 + 3.5, tz), yaw=yaw + 180,
         color=(48, 50, 58), material="Slate", cls="WedgePart")
    dx, dz = l2w(cx, cz, yaw, 0, 17.2)
    part("Chapel_Door", (4.5, 6, 0.4), (dx, gy + 3, dz), yaw=yaw,
         color=(30, 24, 20), material="Wood", cancollide=False)
    rx, rz = l2w(cx, cz, yaw, 0, 17.25)
    part("Chapel_Rose", (3.4, 3.4, 0.35), (rx, gy + 10, rz), yaw=yaw,
         color=(150, 200, 255), material="Neon", transparency=0.2,
         cancollide=False, shape="Ball")


def smithy(cx, cz, gy, yaw=0.0):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 18)
    house("Smithy", cx, cz, gy, 16, 13, 9, yaw=yaw, wall=(82, 78, 74),
          roof=(52, 40, 36), windows=False)
    chx, chz = l2w(cx, cz, yaw, 0, -4)
    part("Smithy_Chimney", (4, 14, 4), (chx, gy + 7, chz), yaw=yaw,
         color=(60, 56, 54), material="Brick")
    fx, fz = l2w(cx, cz, yaw, 0, 6.8)
    part("Smithy_Forge", (3, 2.2, 1.2), (fx, gy + 1.1, fz), yaw=yaw,
         color=(255, 120, 30), material="Neon", cancollide=False, transparency=0.15,
         fire=dict(size=4, heat=8),
         light=dict(brightness=1.6, range=18, color=(255, 120, 40)))
    ax, az = l2w(cx, cz, yaw, -5, 8.5)
    part("Smithy_Anvil", (2.2, 1.6, 1.2), (ax, gy + 0.8, az), yaw=yaw,
         color=(40, 40, 46), material="Metal")


def well(cx, cz, gy):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 10)
    disc("Well", cx, cz, gy + 2.2, 3.5, 2.2, (110, 106, 100), "Cobblestone")
    part("Well_PostA", (0.8, 5, 0.8), (cx - 2.8, gy + 2.5, cz), color=(70, 54, 40),
         material="Wood")
    part("Well_PostB", (0.8, 5, 0.8), (cx + 2.8, gy + 2.5, cz), color=(70, 54, 40),
         material="Wood")
    part("Well_RoofA", (8.5, 2.5, 4.5), (cx, gy + 6.2, cz - 1.2),
         color=(60, 44, 34), material="WoodPlanks", cls="WedgePart")
    part("Well_RoofB", (8.5, 2.5, 4.5), (cx, gy + 6.2, cz + 1.2), yaw=180,
         color=(60, 44, 34), material="WoodPlanks", cls="WedgePart")


def stall(cx, cz, gy, yaw=0.0):
    gy = sy(cx, cz, gy)
    for sx in (-2.5, 2.5):
        px, pz = l2w(cx, cz, yaw, sx, 0)
        part("Stall_Post", (0.6, 6, 0.6), (px, gy + 3, pz), yaw=yaw,
             color=(70, 54, 40), material="Wood")
    px, pz = l2w(cx, cz, yaw, 0, 0)
    part("Stall_Counter", (6, 2.6, 2.2), (px, gy + 1.3, pz), yaw=yaw,
         color=(96, 76, 56), material="WoodPlanks")
    px, pz = l2w(cx, cz, yaw, 0, -1.4)
    part("Stall_Awning", (7.5, 0.4, 4.5), (px, gy + 6, pz), yaw=yaw,
         pitch=14, color=rng.choice([(120, 50, 50), (60, 80, 120), (70, 110, 70)]),
         material="Fabric", cancollide=False)


def witch_hut(cx, cz, gy):
    gy = sy(cx, cz, gy)
    house("WitchHut", cx, cz, gy, 10, 9, 7, yaw=15, wall=(60, 50, 44),
          roof=(40, 36, 42), windows=False, chimney=False)
    part("WitchHut_Window", (1.4, 1.4, 0.3),
         (cx + 3.6, gy + 4, cz + 4.7), yaw=15, color=(120, 255, 120),
         material="Neon", transparency=0.3, cancollide=False)
    disc("Cauldron", cx + 8, cz + 4, gy + 2.2, 2, 2.4, (40, 60, 40), "Metal")
    part("Cauldron_Brew", (2.8, 0.4, 2.8), (cx + 8, gy + 2.4, cz + 4),
         color=(90, 255, 130), material="Neon", cancollide=False,
         fire=dict(size=3, heat=4, color=(120, 255, 140), secondary=(40, 120, 50)),
         light=dict(brightness=1.1, range=14, color=(100, 255, 140)))


def heart_tree(cx, cz, gy):
    gy = sy(cx, cz, gy)
    v_cyl("HeartTree_Trunk", cx, cz, gy, 64, 16, (72, 48, 84), "Wood")
    layers = [(40, 14, 66, 0), (34, 12, 78, 45), (26, 10, 88, 12), (16, 8, 96, 70)]
    for w, h, yy, yw in layers:
        part("HeartTree_Canopy", (w, h, w), (cx, yy, cz), yaw=yw,
             color=(52, 40, 72), material="Grass", cancollide=False)
    for i in range(4):
        a = math.pi * 2 * i / 4 + 0.4
        part("HeartTree_Rune", (0.8, 6, 0.8),
             (cx + math.sin(a) * 8.2, gy + 14 + i * 8, cz + math.cos(a) * 8.2),
             color=(180, 100, 255), material="Neon", cancollide=False)
    for i in range(5):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(12, 22)
        crystal(cx + math.sin(a) * rr, cz + math.cos(a) * rr, gy, 1.2, "violet")


def lighthouse(cx, cz, gy):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 22)
    v_cyl("Lighthouse_Base", cx, cz, gy, 14, 20, (200, 192, 175), "Concrete")
    v_cyl("Lighthouse_Mid", cx, cz, gy + 14, 12, 17, (140, 60, 50), "Brick")
    v_cyl("Lighthouse_Top", cx, cz, gy + 26, 10, 15, (200, 192, 175), "Concrete")
    v_cyl("Lighthouse_Lantern", cx, cz, gy + 36, 6, 13, (255, 200, 110), "Neon",
          light=dict(brightness=2.5, range=150, color=(255, 200, 120)))
    part("Lighthouse_Roof", (13, 8, 13), (cx, gy + 44, cz), shape="Ball",
         color=(60, 50, 48), material="Metal", cancollide=False)


def shipwreck(cx, cz, gy):
    gy = sy(cx, cz, gy)
    part("Ship_Hull", (40, 6, 12), (cx, gy + 2.5, cz), yaw=32, pitch=7,
         color=(80, 58, 40), material="Wood")
    part("Ship_Deck", (34, 1.2, 10), (cx, gy + 6, cz), yaw=32, pitch=7,
         color=(66, 48, 34), material="WoodPlanks", cancollide=False)
    for i, (ox, oz, ry) in enumerate([(-14, 3, 50), (-4, -5, 130), (8, 4, 70)]):
        ox2, oz2 = l2w(cx, cz, 32, ox, oz)
        part("Ship_Rib", (2, 7, 1.6), (ox2, gy + 5.5, oz2), yaw=32 + ry,
             pitch=24, color=(58, 42, 30), material="Wood", cancollide=False)
    mx, mz = l2w(cx, cz, 32, 2, 0)
    part("Ship_Mast", (26, 2, 2), (mx, gy + 14, mz), yaw=32, pitch=20,
         color=(72, 52, 36), material="Wood")
    part("Ship_Bowsprit", (12, 1.4, 1.4), (cx + 20, gy + 6.5, cz - 8), yaw=32,
         pitch=-18, color=(72, 52, 36), material="Wood", cancollide=False)


def ruin_columns(cx, cz, gy, n=8, spread=60):
    gy = sy(cx, cz, gy)
    for i in range(n):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(8, spread)
        x, z = cx + math.sin(a) * rr, cz + math.cos(a) * rr
        h = rng.uniform(5, 14)
        v_cyl("Ruin_Column", x, z, gy, h, 3.6, (170, 168, 160), "Marble",
              tilt_pitch=rng.uniform(-4, 4), tilt_roll=rng.uniform(-4, 4))
    part("Ruin_Lintel", (16, 3, 4), (cx + 14, gy + 1.6, cz + 10), yaw=30,
         pitch=72, color=(168, 166, 158), material="Marble")


def fortress_ruins(cx, cz, gy):
    gy = sy(cx, cz, gy)
    # стены с проломами
    wall_defs = [
        (-80, 0, 0, 60), (-20, 0, 0, 40), (40, 0, 0, 50),
        (-70, 80, 0, 50), (10, 80, 0, 60), (70, 80, 0, 30),
        (-80, 40, 90, 40), (70, 40, 90, 40),
    ]
    for i, (ox, oz, ry, ln) in enumerate(wall_defs):
        wx, wz = cx + ox, cz + oz
        part("Fort_Wall_%d" % i, (ln, 18, 6), (wx, gy + 9, wz), yaw=ry,
             color=(60, 58, 62), material="Cobblestone")
    for i, (ox, oz) in enumerate([(-80, 0), (70, 0), (-80, 80), (70, 80)]):
        tx, tz = cx + ox, cz + oz
        v_cyl("Fort_Tower_%d" % i, tx, tz, gy, 26, 18, (66, 64, 68), "Cobblestone")
        if i % 2 == 0:
            v_cyl("Fort_TowerTop_%d" % i, tx + 1, tz - 2, gy + 24, 8, 12,
                  (60, 58, 62), "Cobblestone", tilt_pitch=6)
    lava_pool(cx - 20, cz + 40, gy, 14)
    lava_pool(cx + 40, cz + 55, gy, 10)
    for i in range(8):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(20, 70)
        rock(cx + math.sin(a) * rr, cz + math.cos(a) * rr, gy, 0.9, "Basalt",
             (44, 42, 46))
    brazier(cx, cz + 20, gy)
    brazier(cx + 30, cz + 20, gy)


def crypt(cx, cz, gy):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 34)
    """Крипта-данж: можно войти — саркофаги, факелы, босс Крипт-Призрак, сундук."""
    W, D, H = 22, 28, 12
    stone = (108, 104, 98)
    part("Crypt_Floor", (W, 1, D), (cx, gy + 0.5, cz), color=(96, 92, 88),
         material="Cobblestone")
    part("Crypt_WallBack", (W, H, 2), (cx, gy + H / 2 + 1, cz - D / 2 + 1),
         color=stone, material="Cobblestone")
    for side in (1, -1):
        part("Crypt_WallSide", (2, H, D),
             (cx + side * (W / 2 - 1), gy + H / 2 + 1, cz), color=stone,
             material="Cobblestone")
    for side in (1, -1):
        part("Crypt_WallFront", (W / 2 - 3, H, 2),
             (cx + side * (W / 4 + 1.5), gy + H / 2 + 1, cz + D / 2 - 1),
             color=stone, material="Cobblestone")
    part("Crypt_Lintel", (8, H - 7, 2), (cx, gy + 7 + (H - 7) / 2, cz + D / 2 - 1),
         color=stone, material="Cobblestone")
    part("Crypt_RoofA", (W + 2, 5, D / 2 + 1), (cx, gy + H + 1 + 2.5, cz - D / 4),
         color=(48, 48, 52), material="Slate", cls="WedgePart")
    part("Crypt_RoofB", (W + 2, 5, D / 2 + 1), (cx, gy + H + 1 + 2.5, cz + D / 4),
         yaw=180, color=(48, 48, 52), material="Slate", cls="WedgePart")
    for sx in (-7, 7):
        for sz in (-8, 8):
            part("Crypt_Column", (2.4, H - 2, 2.4),
                 (cx + sx, gy + 1 + (H - 2) / 2, cz + sz), color=(118, 114, 108),
                 material="Marble")
    for sz in (-10, 0, 9):
        part("Crypt_Sarcophagus", (6, 2.6, 3), (cx - 4, gy + 2.3, cz + sz),
             color=(124, 120, 114), material="Marble")
    torch_wall(cx - 6, cz + D / 2 - 3.5, gy + 1, 0)
    torch_wall(cx + 6, cz + D / 2 - 3.5, gy + 1, 0)
    torch_wall(cx - 6, cz - D / 2 + 3.5, gy + 1, 180)
    boss_spawn("CryptWraith", cx, cz + 4, gy + 1)
    arena_trigger("CryptWraith", cx, cz, gy + 1, r=40)
    chest_marker(cx + 5, cz - 10, gy + 1, "Crypt")


def bone_pit(cx, cz, gy):
    gy = sy(cx, cz, gy)
    disc("BonePit", cx, cz, gy + 0.35, 22, 0.8, (30, 28, 30), "Rock")
    for i in range(12):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(4, 19)
        part("Bone", (rng.uniform(1.8, 3.2), 0.8, 0.8),
             (cx + math.sin(a) * rr, gy + 0.9, cz + math.cos(a) * rr),
             yaw=rng.uniform(0, 360), color=(216, 210, 190), material="SmoothPlastic",
             cancollide=False)
    for i in range(4):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(6, 16)
        part("Skull", (1.8, 1.8, 1.8), (cx + math.sin(a) * rr, gy + 1.2, cz + math.cos(a) * rr),
             shape="Ball", color=(222, 216, 196), material="SmoothPlastic")


def frost_shrine(cx, cz, gy):
    gy = sy(cx, cz, gy)
    part("Shrine_Base", (14, 1.5, 14), (cx, gy + 0.75, cz), color=(170, 200, 230),
         material="Glacier")
    for sx, sz in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        part("Shrine_Pillar", (2.5, 10, 2.5), (cx + sx, gy + 5.75, cz + sz),
             color=(180, 205, 235), material="Glacier")
    part("Shrine_Altar", (4, 2.5, 2.5), (cx, gy + 2.5, cz), color=(160, 190, 225),
         material="Glacier")
    part("Shrine_Rune", (3, 0.3, 3), (cx, gy + 3.9, cz), color=(120, 220, 255),
         material="Neon", cancollide=False,
         light=dict(brightness=1.2, range=16, color=(120, 220, 255)))
    crystal(cx - 9, cz + 7, gy, 1.0, "cyan")
    crystal(cx + 9, cz - 7, gy, 1.0, "cyan")


def mesa(cx, cz, gy, w1, w2, w3):
    """Гора-столовая шишка из трёх плит + снежная шапка."""
    part("Peak_A", (w1, 24, w1), (cx, gy + 12, cz), yaw=12,
         color=(120, 124, 136), material="Rock")
    part("Peak_B", (w2, 20, w2), (cx + 4, gy + 32, cz - 3), yaw=28,
         color=(150, 156, 170), material="Rock")
    part("Peak_C", (w3, 16, w3), (cx - 2, gy + 48, cz + 2), yaw=40,
         color=(200, 208, 220), material="Snow")
    part("Peak_Cap", (w3 * 0.7, w3 * 0.5, w3 * 0.7), (cx, gy + 60, cz),
         shape="Ball", color=(222, 228, 238), material="Snow", cancollide=False)


def boss_arena_circular(name, cx, cz, gy, r=55, pillar_col=(120, 124, 136),
                        pillar_mat="Rock", boss_id=None, n_pillars=8,
                        fire=True):
    disc(name + "_Platform", cx, cz, gy + 0.6, r, 1.2, (88, 86, 92), "Basalt")
    for i in range(n_pillars):
        a = math.pi * 2 * i / n_pillars
        px, pz = cx + math.sin(a) * (r - 8), cz + math.cos(a) * (r - 8)
        part(name + "_Pillar_%d" % i, (5, 18, 5), (px, gy + 9, pz),
             yaw=math.degrees(a), pitch=rng.uniform(-3, 3),
             color=pillar_col, material=pillar_mat)
    if fire:
        for i in range(4):
            a = math.pi * 2 * i / 4 + math.pi / 4
            bx, bz = cx + math.sin(a) * (r * 0.45), cz + math.cos(a) * (r * 0.45)
            brazier(bx, bz, gy + 0.6)
    if boss_id:
        boss_spawn(boss_id, cx, cz, gy + 0.6)
        arena_trigger(boss_id, cx, cz, gy + 0.6, r=r + 22)


# ----------------------------------------------------------------------------
# v1.5: лагеря, палатки, мосты, река, водопад, горы, указатели
# ----------------------------------------------------------------------------
def p_udim2(n, xs, xsc, ys, ysc):
    p_raw('<UDim2 name="%s"><XS>%s</XS><XScale>%s</XScale><YS>%s</YS>'
          '<YScale>%s</YScale></UDim2>'
          % (n, fmt(xs), fmt(xsc), fmt(ys), fmt(ysc)))


def campfire(x, z, gy):
    gy = sy(x, z, gy)
    for i in range(7):
        a = math.pi * 2 * i / 7
        rock(x + math.sin(a) * 1.9, z + math.cos(a) * 1.9, gy, 0.35, "Rock",
             (58, 56, 54))
    part("CampFire_Log1", (3.4, 0.8, 0.8), (x, gy + 0.5, z), yaw=25,
         color=(74, 54, 38), material="Wood")
    part("CampFire_Log2", (3.4, 0.8, 0.8), (x, gy + 0.95, z), yaw=95,
         color=(66, 48, 34), material="Wood")
    part("CampFire_Flame", (1.1, 1.7, 1.1), (x, gy + 1.9, z), color=(255, 140, 50),
         material="Neon", cancollide=False, transparency=0.15,
         fire=dict(size=5, heat=7),
         light=dict(brightness=1.7, range=32, color=(255, 150, 60)))


def tent(x, z, gy, yaw=0.0, w=7, d=8, h=4.6, color=(96, 74, 58)):
    occupy(x, z, max(w, d) * 0.8)
    gy = sy(x, z, gy)
    s = d / 2.0
    ang = math.degrees(math.atan2(h, s))
    panel_len = math.hypot(h, s) + 1.5
    for side in (1, -1):
        lx, lz = l2w(x, z, yaw, side * s / 2, 0)
        part("Tent_Panel", (w + 1.4, 0.5, panel_len), (lx, gy + h / 2, lz),
             yaw=yaw, roll=side * -ang, color=color, material="Fabric")
    bx, bz = l2w(x, z, yaw, 0, -d / 2 + 0.6)
    part("Tent_Back", (w * 0.72, h * 0.95, 0.5), (bx, gy + h * 0.47, bz), yaw=yaw,
         color=(max(color[0] - 32, 10), max(color[1] - 26, 10),
                max(color[2] - 24, 10)), material="Fabric", cancollide=False)
    for fx in (-w / 2 + 0.7, w / 2 - 0.7):
        px, pz = l2w(x, z, yaw, fx, d / 2 - 0.5)
        part("Tent_Pole", (0.45, h + 0.6, 0.45), (px, gy + (h + 0.6) / 2, pz),
             color=(70, 54, 40), material="Wood")


def bandit_camp(x, z, gy, yaw=0.0, tent_cols=((96, 74, 58), (88, 66, 52)),
                banner_col=(150, 40, 40), name="Camp", ntents=2):
    occupy(x, z, 34)
    """Временная база: частокол из кольев, палатки, костёр, ящики, знамя."""
    r = 17
    n = 20
    for i in range(n):
        a = math.pi * 2 * i / n
        if angle_gap(a, 0) < 0.32:
            continue  # вход
        lx, lz = r * math.sin(a), r * math.cos(a)
        wx, wz = l2w(x, z, yaw, lx, lz)
        hh = rng.uniform(4.6, 6.4)
        part(name + "_Stake", (0.9, hh, 0.9), (wx, gy + hh / 2 - 0.4, wz),
             yaw=math.degrees(a) + rng.uniform(-8, 8), pitch=rng.uniform(-3, 3),
             roll=rng.uniform(-2, 2), color=(76, 58, 42), material="Wood")
    for i in range(n):
        a1 = math.pi * 2 * i / n
        a2 = math.pi * 2 * (i + 1) / n
        if angle_gap((a1 + a2) / 2, 0) < 0.36:
            continue
        l1x, l1z = r * math.sin(a1), r * math.cos(a1)
        l2x, l2z = r * math.sin(a2), r * math.cos(a2)
        mx, mz = (l1x + l2x) / 2, (l1z + l2z) / 2
        wx, wz = l2w(x, z, yaw, mx, mz)
        seglen = math.hypot(l2x - l1x, l2z - l1z)
        ryaw = yaw + math.degrees(math.atan2(l2x - l1x, l2z - l1z))
        for hy in (2.3, 3.5):
            part(name + "_Rail", (0.4, 0.4, seglen), (wx, gy + hy, wz), yaw=ryaw,
                 color=(70, 54, 40), material="Wood", cancollide=False)
    # палатки по кругу
    tpos = [(-8, 5, 12), (8, -4, -15), (1, -9, 180)]
    for i in range(ntents):
        lx, lz, ty = tpos[i % len(tpos)]
        tx, tz = l2w(x, z, yaw, lx, lz)
        tent(tx, tz, gy, yaw=yaw + ty, color=tent_cols[i % len(tent_cols)])
    campfire(x, z, gy)
    # ящики и брёвна
    for i, (cxo, czo) in enumerate([(-4, -6), (-2.6, -7.6), (5, 6)]):
        bx, bz = l2w(x, z, yaw, cxo, czo)
        part(name + "_Crate", (2.2, 2.2, 2.2), (bx, gy + 1.1, bz),
             yaw=rng.uniform(0, 90), color=(110, 84, 56), material="WoodPlanks")
    for i, (bxo, bzo, byaw) in enumerate([(4.5, 1.5, 70), (-4.5, 2, 20)]):
        bx, bz = l2w(x, z, yaw, bxo, bzo)
        part(name + "_Bench", (3.6, 0.9, 0.9), (bx, gy + 0.45, bz), yaw=yaw + byaw,
             color=(84, 64, 46), material="Wood")
    # знамя у входа
    bx, bz = l2w(x, z, yaw, 3.5, r - 3)
    part(name + "_BannerPole", (0.5, 9, 0.5), (bx, gy + 4.5, bz), color=(60, 46, 36),
         material="Wood")
    fx, fz = l2w(x, z, yaw, 4.9, r - 3)
    part(name + "_Flag", (2.6, 1.8, 0.2), (fx, gy + 7.8, fz), yaw=yaw,
         color=banner_col, material="Fabric", cancollide=False)


def wooden_bridge(x, z, gy, yaw=0.0, span=36, width=8):
    gy = sy(x, z, gy)
    deck_y = gy + 1.0
    n = 5
    seg = span / n
    for i in range(n):
        t = (i + 0.5) / n
        off = (t - 0.5) * span
        hump = math.sin(math.pi * t) * 1.4
        lx, lz = l2w(x, z, yaw, off, 0)
        part("Bridge_Deck", (seg + 0.7, 0.5, width), (lx, deck_y + hump, lz),
             yaw=yaw, color=(84, 62, 44), material="WoodPlanks")
    for side in (1, -1):
        for i in range(n + 1):
            t = i / float(n)
            off = (t - 0.5) * span
            hump = math.sin(math.pi * t) * 1.4
            lx, lz = l2w(x, z, yaw, off, side * (width / 2 - 0.4))
            part("Bridge_Post", (0.5, 2.6 + hump, 0.5),
                 (lx, gy - 1.2 + (2.6 + hump) / 2, lz), yaw=yaw,
                 color=(70, 52, 38), material="Wood")
        for i in range(n):
            t = (i + 0.5) / n
            off = (t - 0.5) * span
            hump = math.sin(math.pi * t) * 1.4 + 1.2
            lx, lz = l2w(x, z, yaw, off, side * (width / 2 - 0.4))
            part("Bridge_Rail", (seg, 0.4, 0.4), (lx, deck_y + hump, lz),
                 yaw=yaw, color=(96, 72, 50), material="Wood", cancollide=False)


def stone_footbridge(x, z, gy, yaw=0.0, span=40, width=5):
    gy = sy(x, z, gy)
    n = 5
    seg = span / n
    for i in range(n):
        t = (i + 0.5) / n
        off = (t - 0.5) * span
        hump = math.sin(math.pi * t) * 1.2
        lx, lz = l2w(x, z, yaw, off, 0)
        part("FootBridge", (width, 0.6, seg + 0.4), (lx, gy + 1.1 + hump, lz),
             yaw=yaw, color=(128, 124, 116), material="Cobblestone")
        if i % 2 == 0:
            for side in (1, -1):
                rx, rz = l2w(x, z, yaw, off + seg / 2, side * (width / 2))
                part("FootBridge_Post", (0.6, 1.6, 0.6),
                     (rx, gy + 1.4 + hump + 0.8, rz), yaw=yaw,
                     color=(118, 114, 106), material="Cobblestone")


def canyon_sky_bridge(x, z, yaw=0.0, span=74, width=7, deck_y=46.0, base_y=42.0):
    """Висячий мост через каньон: башни по краям, провисший настил, канаты."""
    for side in (1, -1):
        lx, lz = l2w(x, z, yaw, side * span / 2, 0)
        part("SkyBridge_Tower", (5, 12, 5), (lx, base_y + 5, lz), yaw=yaw,
             color=(56, 50, 44), material="Wood")
        part("SkyBridge_Platform", (7, 0.7, width + 2), (lx, deck_y + 0.35, lz),
             yaw=yaw, color=(88, 66, 46), material="WoodPlanks")
    n = 7
    seg = span / n
    for i in range(n):
        t = (i + 0.5) / n
        off = (t - 0.5) * span
        sag = -math.sin(math.pi * t) * 2.2
        lx, lz = l2w(x, z, yaw, off, 0)
        part("SkyBridge_Deck", (seg + 0.5, 0.4, width), (lx, deck_y + sag, lz),
             yaw=yaw, color=(88, 66, 46), material="WoodPlanks")
        for side in (1, -1):
            rx, rz = l2w(x, z, yaw, off, side * (width / 2 - 0.3))
            part("SkyBridge_Rope", (seg, 0.3, 0.3), (rx, deck_y + sag + 1.4, rz),
                 yaw=yaw, color=(122, 102, 72), material="Fabric", cancollide=False)


def waterfall(x, z, top_y, bottom_y, width=24, yaw=0.0):
    h = top_y - bottom_y
    n = max(2, int(h // 12))
    seg = h / n
    for i in range(n):
        y1 = top_y - seg * i
        part("Waterfall", (width, seg + 1, 1.8), (x, y1 - seg / 2, z), yaw=yaw,
             color=(165, 195, 215), material="Water", transparency=0.25 + 0.08 * i,
             cancollide=False)
    disc("Waterfall_Foam", x, z, bottom_y + 0.9, width * 0.75, 1.2,
         (190, 215, 230), "Water", transparency=0.35, cancollide=False)
    part("Waterfall_Glow", (0.1, 0.1, 0.1), (x, bottom_y + 3, z), transparency=1,
         cancollide=False,
         light=dict(brightness=1.0, range=32, color=(170, 210, 230)))


def river_build(points, gy, width=18, color=(30, 64, 80)):
    """Река по ломаной: полосы воды чуть выше земли (можно вброд).
    Возвращает точки для запретных зон деревьев."""
    pts = []
    for i in range(len(points) - 1):
        ax, az = points[i]
        bx, bz = points[i + 1]
        dx, dz = bx - ax, bz - az
        dist = math.hypot(dx, dz)
        n = max(1, int(dist // 11))
        yaw = math.degrees(math.atan2(dx, dz))
        for k in range(n + 1):
            t = k / float(n)
            x, z = ax + dx * t, az + dz * t
            if pts and math.hypot(x - pts[-1][0], z - pts[-1][1]) < 6:
                continue
            pts.append((x, z))
            part("River", (width, 0.5, 12.5), (x, gy + 0.12, z), yaw=yaw,
                 color=color, material="Water", transparency=0.15,
                 cancollide=False)
    return pts


def signpost(x, z, gy, yaw=0.0, lines=""):
    gy = sy(x, z, gy)
    """Деревянный указатель с надписью (SurfaceGui)."""
    for sx in (-2.1, 2.1):
        px, pz = l2w(x, z, yaw, sx, 0)
        part("Sign_Post", (0.5, 6.5, 0.5), (px, gy + 3.25, pz), color=(66, 50, 38),
             material="Wood")
    part("Sign_Plank", (5.6, 2.8, 0.35), (x, gy + 5.4, z), yaw=yaw,
         color=(96, 72, 48), material="WoodPlanks")
    begin_item("SurfaceGui", "SignGui")
    p_token("Face", NORMALID_IDS["Front"])
    p_token("SizingMode", SIZING_IDS["PixelsPerStud"])
    p_int("PixelsPerStud", 40)
    p_float("MaxDistance", 140)
    end_props()
    begin_item("TextLabel", "Text")
    p_udim2("Size", 0, 1, 0, 1)
    p_float("BackgroundTransparency", 1)
    p_color3("TextColor3", 255, 240, 214)
    p_token("Font", 4)  # SourceSansBold
    p_bool("TextScaled", True)
    p_bool("TextWrapped", True)
    p_str("Text", lines)
    end_props()
    end_item()
    end_item()


def truss(name, size, pos, color=(96, 76, 56)):
    """Лазовая ферма — по ней можно ЛЕЗАТЬ как по лестнице."""
    begin_item("TrussPart", name)
    p_bool("Anchored", True)
    p_bool("CanCollide", True)
    p_vec3("size", *size)
    p_cframe("CFrame", pos)
    p_color3u8("Color3uint8", *color)
    p_token("TopSurface", SURFACE_IDS["Smooth"])
    p_token("BottomSurface", SURFACE_IDS["Smooth"])
    end_props()
    end_item()


# ============================================================================
# v12: КВАДРАТНЫЕ ГОРЫ «КАК В WORLD OF MAGIC»
# ============================================================================
def _blocky_contour(x, z, w, d, notches, seed):
    """Контур горы из прямоугольника с выступами (notches = [(сторона, отступ)…]).
    Возвращает список (x0, z0, x1, z1) — набор прямоугольников, из которых
    собирается «квадратный» ярус с рваными краями."""
    rects = [(x - w / 2, z - d / 2, x + w / 2, z + d / 2)]
    for (side, t, out) in notches:
        if side in (0, 2):                      # выступ на север / юг
            bw = w * rng.uniform(0.22, 0.42)
            cx = x + (t * (w / 2 - bw * 0.7))
            zz = z - d / 2 - out if side == 0 else z + d / 2 + out
            rects.append((cx - bw / 2, zz - out, cx + bw / 2, zz + out))
        else:                                   # выступ на запад / восток
            bd = d * rng.uniform(0.22, 0.42)
            cz = z + (t * (d / 2 - bd * 0.7))
            xx = x - w / 2 - out if side == 3 else x + w / 2 + out
            rects.append((xx - out, cz - bd / 2, xx + out, cz + bd / 2))
    return rects


def wom_mountain(x, z, gy, base_w=210, h=160, snow=0.66, seed=0,
                 ledges=True, steps=True, mat="Rock", snow_mat="Snow",
                 col=(108, 114, 124), cave=True, tag=None):
    """ГОРА В СТИЛЕ World of Magic: не конус, а СТОПКА КВАДРАТНЫХ ЯРУСОВ.
    Каждый ярус — прямоугольная плита; ярусы смещены друг относительно друга,
    у части — боковые ВЫСТУПЫ-уступы. Перепад между ярусами 2.5 студа,
    поэтому по выступам можно залезть пешком (как по ступеням)."""
    tag = tag or "WM%d" % seed
    add_flat(x, z, base_w * 0.72, gy, 95.0)
    tiers = max(6, int(round(h / 2.5)))
    tier_h = h / float(tiers)
    w, d = base_w, base_w * rng.uniform(0.86, 1.0)
    y = gy
    # ---------- стопка ярусов ----------
    for i in range(tiers):
        t = i / float(max(1, tiers - 1))
        # ярусы сужаются «лестницей», но с рывками — так гора выглядит блочной
        if i and i % 3 == 0:
            w *= rng.uniform(0.80, 0.90)
            d *= rng.uniform(0.80, 0.90)
        # смещение центра яруса: гора получается «пьяной», как скалы WoM
        ox = math.sin(seed * 1.7 + i * 1.9) * base_w * 0.045
        oz = math.cos(seed * 2.3 + i * 1.3) * base_w * 0.045
        top_tier = (i == tiers - 1)
        colr = col
        matr = mat
        if t > snow:
            colr = (230, 236, 244)
            matr = snow_mat
        elif t > snow - 0.14:
            # каменная кромка под снегом
            colr = tuple(int(c * 0.86 + 24) for c in col)
        # сама плита
        part("%s_Tier%d" % (tag, i), (w, tier_h + 0.3, d),
             (x + ox, y + tier_h / 2, z + oz), yaw=0,
             color=colr, material=matr)
        # ---------- боковые ВЫСТУПЫ (главная фишка) ----------
        if ledges and i % 2 == 0 and w > 70:
            for k in range(rng.randint(2, 4)):
                side = rng.randint(0, 3)
                out = rng.uniform(14, 30)
                bw = w * rng.uniform(0.18, 0.34)
                bd = d * rng.uniform(0.16, 0.30)
                if side in (0, 2):
                    bx = x + ox + rng.uniform(-w * 0.3, w * 0.3)
                    bz = z + oz + (-d / 2 - out / 2 if side == 0 else d / 2 + out / 2)
                    part("%s_Ledge%d_%d" % (tag, i, k), (bw, tier_h + 0.3, out + 4),
                         (bx, y + tier_h / 2, bz), color=colr, material=matr)
                    # «зуб» под выступом — смотрится как скальная полка
                    part("%s_LedgeBrace%d_%d" % (tag, i, k),
                         (bw * 0.7, tier_h * 1.6, out * 0.6),
                         (bx, y - tier_h * 0.5, bz), color=tuple(int(c * 0.8) for c in colr),
                         material=matr)
                else:
                    bz = z + oz + rng.uniform(-d * 0.3, d * 0.3)
                    bx = x + ox + (-w / 2 - out / 2 if side == 3 else w / 2 + out / 2)
                    part("%s_Ledge%d_%d" % (tag, i, k), (out + 4, tier_h + 0.3, bd),
                         (bx, y + tier_h / 2, bz), color=colr, material=matr)
                    part("%s_LedgeBrace%d_%d" % (tag, i, k),
                         (out * 0.6, tier_h * 1.6, bd * 0.7),
                         (bx, y - tier_h * 0.5, bz), color=tuple(int(c * 0.8) for c in colr),
                         material=matr)
        # ---------- «рваная» кромка: блоки по периметру ----------
        per = max(4, int((w + d) / 26))
        for k in range(per):
            a = math.pi * 2 * k / per + i * 0.7 + seed
            rx = x + ox + math.sin(a) * (w * 0.5 - 2)
            rz = z + oz + math.cos(a) * (d * 0.5 - 2)
            part("%s_Edge%d_%d" % (tag, i, k),
                 (rng.uniform(10, 20), tier_h * rng.uniform(0.8, 1.25), rng.uniform(10, 20)),
                 (rx, y + tier_h * 0.45, rz), yaw=rng.choice((0, 0, 45)),
                 color=colr, material=matr)
        y += tier_h
    # ---------- вершина: плоское «плато» с камнем и сундуком ----------
    part("%s_Summit" % tag, (w * 0.92, 1.4, d * 0.92), (x + ox, y + 0.7, z + oz),
         color=(96, 86, 78), material="Rock")
    for k in range(3):
        rock(x + ox + rng.uniform(-w * 0.3, w * 0.3),
             z + oz + rng.uniform(-d * 0.3, d * 0.3), y, rng.uniform(1.4, 2.6),
             mat, (128, 128, 130))
    chest_marker(x + ox, z + oz, y + 1.2, "%sSummit" % tag)
    crystal(x + ox - 6, z + oz + 6, y + 1.2, 1.2, "cyan")
    # ---------- ступени-выступы по спирали (чтобы точно залезть) ----------
    if steps:
        sn = max(8, int(h / 9))
        for i in range(sn):
            t = i / float(sn - 1)
            a = t * math.pi * 4.0 + seed
            rr = base_w * 0.62 * (1.0 - t * 0.66)
            part("%s_Step%d" % (tag, i), (rng.uniform(12, 18), 1.2, rng.uniform(10, 14)),
                 (x + math.sin(a) * rr, gy + t * (h - 6), z + math.cos(a) * rr),
                 yaw=math.degrees(a) + 90, color=(122, 120, 116), material=mat)
            if i % 5 == 0:
                torch_wall(x + math.sin(a) * rr, z + math.cos(a) * rr,
                           gy + t * (h - 6) + 1, 0)
    # ---------- пещера у подножия ----------
    if cave:
        ca = seed * 1.9
        cave_system("%s Cave" % tag, x + math.sin(ca) * base_w * 0.58,
                    z + math.cos(ca) * base_w * 0.58, gy, depth=mountain_cave_depth(gy),
                    nodes=((70, 30), (160, 110)), width=17, height=13,
                    tag="%sCave" % tag, extra_chests=2,
                    cap_col=tuple(int(c * 0.9) for c in col), cap_mat=mat)
    # ---------- валуны у подножия ----------
    for _ in range(10):
        a = rng.uniform(0, math.pi * 2)
        rr = base_w * rng.uniform(0.5, 0.66)
        rock(x + math.sin(a) * rr, z + math.cos(a) * rr, gy,
             rng.uniform(1.0, 2.2), mat, (118, 118, 124))
    occupy(x, z, base_w * 0.6, "mountain")
    return y


def mountain_cave_depth(gy):
    """Глубина пещеры: не уходим ниже уровня моря."""
    return max(10.0, min(20.0, gy - 5.0))


def mountain_chain(name, points, gy, base_w=200, h=160, snow=0.66, seed=0,
                   col=(108, 114, 124), mat="Rock"):
    """Цепь квадратных гор: вершины соединяются «сёдлами» из блоков,
    поэтому с одной горы можно перейти на другую по гребню."""
    res = []
    for i, (mx, mz) in enumerate(points):
        top = wom_mountain(mx, mz, gy, base_w=base_w * rng.uniform(0.9, 1.1),
                           h=h * rng.uniform(0.85, 1.1), snow=snow,
                           seed=seed + i * 3, col=col, mat=mat,
                           tag="%s%d" % (name, i))
        res.append((mx, mz, top))
    # сёдла между соседними вершинами
    for i in range(len(points) - 1):
        ax, az = points[i]
        bx, bz = points[i + 1]
        dist = math.hypot(bx - ax, bz - az)
        n = max(3, int(dist / 40))
        yaw = math.degrees(math.atan2(bx - ax, bz - az))
        for k in range(1, n):
            t = k / float(n)
            px, pz = ax + (bx - ax) * t, az + (bz - az) * t
            hh = 2.5 + 22 * math.sin(math.pi * t)
            bw = base_w * (0.30 + 0.16 * math.sin(math.pi * t))
            part("%s_Saddle%d_%d" % (name, i, k), (bw, hh, bw * 0.8),
                 (px, gy + hh / 2, pz), yaw=yaw,
                 color=tuple(int(c * 0.9) for c in col), material=mat)
            # ступень на седло
            part("%s_SaddleStep%d_%d" % (name, i, k), (bw * 1.2, 1.2, 8),
                 (px, gy + hh, pz), yaw=yaw + 90,
                 color=(126, 124, 120), material=mat)
    return res


def mega_mesa(x, z, gy, base_w=140, h=110, snow=60, cell=85.0):
    """ГОРА с проходимыми ступенями: перепад между кольцами <= 2.6 студа,
    поэтому подъём берётся пешком (и запрыгивается), а не «стопка карт»."""
    add_flat(x, z, base_w * 0.62, gy, 70.0)   # подножие — ровная площадка
    n = max(6, int(round(h / 2.6)))
    tier_h = h / float(n)
    step_out = max(3.0, tier_h * 2.75)   # горизонтальный отступ кольца
    w = base_w
    for i in range(n):
        y = gy + i * tier_h
        t = (y - gy) / float(h)
        if y > snow:
            col, mat = (228, 233, 241), "Snow"
        else:
            g = int(104 + t * 52)
            col, mat = (g, g + 3, g + 11), "Rock"
        # кольцо из блоков: получается неровная, но проходимая гора
        cnt = max(6, int(w * 2.06 / max(11.0, step_out * 1.6)))
        for k in range(cnt):
            a = math.pi * 2 * k / cnt + i * 0.11
            px = x + math.sin(a) * (w / 2.0)
            pz = z + math.cos(a) * (w / 2.0)
            part("Peak_Ring%d_%d" % (i, k),
                 (max(11.0, step_out * 2.4), tier_h + 0.45, max(11.0, step_out * 2.4)),
                 (px, y + tier_h / 2.0, pz), yaw=math.degrees(a) + rng.uniform(-12, 12),
                 color=col, material=mat)
        # верхняя площадка каждого яруса
        if i % 2 == 1:
            part("Peak_Ledged%d" % i, (w * 0.55, tier_h * 0.9, 6.0),
                 (x, y + tier_h * 0.45, z), yaw=(i * 23) % 180,
                 color=col, material=mat, cancollide=False)
        w = max(11.0, w - step_out * 1.75)
    # вершина
    part("Peak_Snowcap", (w * 1.5, tier_h * 1.6, w * 1.5),
         (x, gy + h + tier_h * 0.6, z), shape="Ball",
         color=(234, 240, 248), material="Snow", cancollide=False)
    for _ in range(7):
        rr = base_w * 0.52
        rock(x + rng.uniform(-rr, rr), z + rng.uniform(-rr, rr), sy(x, z, gy),
             rng.uniform(0.9, 1.6), "Rock", (110, 112, 118))
    # тропа-серпантин: плоские ступени от подножия к вершине
    for i in range(int(n * 0.75)):
        t = i / float(max(1, int(n * 0.75)))
        a = t * math.pi * 3.4
        rr = base_w * 0.62 * (1.0 - t * 0.72)
        px, pz = x + math.sin(a) * rr, z + math.cos(a) * rr
        py = gy + t * (h * 0.78)
        part("Peak_Path%d" % i, (round(step_out * 2.2), tier_h + 0.2, round(step_out * 2.2)),
             (px, py, pz), yaw=math.degrees(a) + 90,
             color=(120, 118, 112), material="Rock")
    return gy + h



def town(name, x, z, gy, radius=95, houses=10, pal=None, wall_mat="WoodPlanks",
         roof_mat="WoodPlanks", palisade=False, sign_text=None, plaza=True,
         tavern_=True, smithy_=True, chapel_=False, tower=True, market=False,
         rows=2, well_pos=None, yaw0=0.0, watch=None):
    """НАСТОЯЩИЙ ГОРОД: площадь с фонтаном, радиальные улицы, дома рядами,
    таверна, кузня, башня, рынок, фонари, забор. Всё ставится на ровную площадку."""
    pal = pal or {}
    wall = pal.get("wall", (152, 134, 106))
    roof = pal.get("roof", (80, 62, 46))
    add_flat(x, z, radius + 52, gy, 90.0)
    occupy(x, z, radius + 34, "build")     # v12: всё внутри города — занято
    gyt = gy + 0.55
    # площадь и мостовая улиц
    if plaza:
        disc(name + "_Plaza", x, z, gyt, radius * 0.34, 0.9,
             (112, 108, 100), "Cobblestone")
        well(well_pos[0] if well_pos else x, well_pos[1] if well_pos else z, gyt)
    streets = 4
    for i in range(streets):
        a = math.pi * 2 * i / streets + yaw0
        sx = x + math.sin(a) * radius * 0.62
        sz = z + math.cos(a) * radius * 0.62
        road(x, z, sx, sz, gyt, width=7, color=(104, 100, 92), mat="Cobblestone")
    # дома двумя кольцами
    placed = 0
    ring_idx = 0
    n_total = houses
    while placed < n_total and ring_idx < 4:
        ring_idx += 1
        rr = radius * (0.55 + 0.14 * (ring_idx - 1))
        n_slot = max(6, int(n_total / max(1, rows)))
        for i in range(n_slot):
            if placed >= n_total:
                break
            a = math.pi * 2 * i / n_slot + 0.42 + ring_idx * 0.21
            hx = x + math.sin(a) * rr
            hz = z + math.cos(a) * rr
            house("%s_House%d" % (name, placed), hx, hz, gy,
                  rng.uniform(11.5, 14.5), rng.uniform(9.5, 11.5),
                  rng.uniform(8, 10), yaw=math.degrees(a) + 90,
                  wall=wall, roof=roof, wall_mat=wall_mat, roof_mat=roof_mat)
            placed += 1
    # главные здания у площади
    if tavern_:
        tx = x + math.sin(yaw0 + 1.1) * radius * 0.40
        tz = z + math.cos(yaw0 + 1.1) * radius * 0.40
        tavern(tx, tz, gy, yaw=math.degrees(yaw0 + 1.1) + 90)
    if smithy_:
        sx2 = x + math.sin(yaw0 + 3.6) * radius * 0.40
        sz2 = z + math.cos(yaw0 + 3.6) * radius * 0.40
        smithy(sx2, sz2, gy, yaw=math.degrees(yaw0 + 3.6) + 90)
    if chapel_:
        chapel(x + math.sin(yaw0 + 4.9) * radius * 0.46,
               z + math.cos(yaw0 + 4.9) * radius * 0.46, gy,
               yaw=math.degrees(yaw0 + 4.9) + 90)
    if tower:
        tx3 = x + math.sin(yaw0 + 2.5) * radius * 0.80
        tz3 = z + math.cos(yaw0 + 2.5) * radius * 0.80
        watch_tower(tx3, tz3, gy, tag=name)
    if market:
        market_square(x, z, gyt, n=7, radius=radius * 0.24)
    # фонари по площади и улицам
    for i in range(6):
        a = math.pi * 2 * i / 6 + 0.3
        lamppost(x + math.sin(a) * radius * 0.30, z + math.cos(a) * radius * 0.30, gy)
    for i in range(6):
        a = math.pi * 2 * i / 6 + yaw0
        lx, lz = x + math.sin(a) * radius * 0.66, z + math.cos(a) * radius * 0.66
        if is_free(lx, lz, 4):
            lamppost(lx, lz, gy)
    # забор/частокол по кругу с проёмами у улиц
    if palisade:
        n = max(30, int(radius * 0.75))
        for i in range(n):
            a = math.pi * 2 * i / n
            if any(angle_gap(a, math.pi * 2 * k / streets + yaw0) < 0.20
                   for k in range(streets)):
                continue
            px, pz = x + math.sin(a) * (radius + 14), z + math.cos(a) * (radius + 14)
            part(name + "_Palisade", (1.3, 7.2, 1.3), (px, gy + 3.4, pz),
                 yaw=math.degrees(a), color=(92, 74, 56), material="Wood")
    # деревья и клумбы внутри — только на пустых местах у площади (v12)
    for i in range(8):
        a = math.pi * 2 * i / 8 + 0.9
        px = x + math.sin(a) * radius * 0.30
        pz = z + math.cos(a) * radius * 0.30
        if not is_free(px, pz, 7):
            continue
        if i % 2:
            tree_nice(px, pz, gy, rng.uniform(0.8, 1.1))
        else:
            bush(px, pz, gy)
    for i in range(40):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(radius * 0.36, radius * 0.9)
        flower(x + math.sin(a) * rr, z + math.cos(a) * rr, gy)
    if sign_text:
        signpost(x, z - radius - 18, gy, 0, sign_text)
    # фонарная башня-маяк (если просили)
    if watch:
        lighthouse(x + watch[0], z + watch[1], gy)
    return gy


def small_village(name, x, z, gy, n_houses=5, radius=48, pal=None,
                  wall_mat="WoodPlanks", roof_mat="WoodPlanks", palisade=False,
                  sign_text=None, well_pos=None):
    """Быстрая деревня: дома по кругу, колодец, забор, указатель, фонари."""
    pal = pal or {}
    wall = pal.get("wall", (150, 132, 106))
    roof = pal.get("roof", (78, 60, 44))
    add_flat(x, z, radius + 34, gy, 85.0)
    occupy(x, z, radius + 26, "build")     # v12
    for i in range(n_houses):
        a = math.pi * 2 * i / max(1, n_houses) + 0.35
        hx = x + math.sin(a) * radius * rng.uniform(0.55, 0.95)
        hz = z + math.cos(a) * radius * rng.uniform(0.55, 0.95)
        house("%s_House%d" % (name, i), hx, hz, gy, rng.uniform(11, 14),
              rng.uniform(9, 11), rng.uniform(7, 9), yaw=math.degrees(a) + 90,
              wall=wall, roof=roof, wall_mat=wall_mat, roof_mat=roof_mat)
    wpos = well_pos or (x, z)
    well(wpos[0], wpos[1], gy)
    campfire(x + rng.uniform(-16, 16), z + rng.uniform(-16, 16), gy)
    for i in range(3):
        a = math.pi * 2 * i / 3 + 1.1
        lamppost(x + math.sin(a) * radius * 0.45, z + math.cos(a) * radius * 0.45, gy)
    if palisade:
        n = 26
        for i in range(n):
            a = math.pi * 2 * i / n
            if angle_gap(a, 0.6) < 0.3:
                continue
            px, pz = x + math.sin(a) * (radius + 18), z + math.cos(a) * (radius + 18)
            part("%s_Palisade" % name, (1.2, 6.6, 1.2), (px, gy + 3.0, pz),
                 yaw=math.degrees(a), color=(92, 74, 56), material="Wood")
    if sign_text:
        signpost(x + radius * 0.8, z, gy, 90, sign_text)
    return gy



def hill_mound(x, z, gy, r=24, h=12, col=(96, 116, 66)):
    gy = sy(x, z, gy)
    """Холм: толстые ступени по 4.2 студа — заскакивается."""
    n = max(3, int(h / 4.2))
    for i in range(n):
        t = i / float(n)
        rr = r * (1.0 - 0.62 * t)
        part("Hill_Tier%d" % i, (rr * 2, 4.5, rr * 2),
             (x, gy + i * 4.2 + 2.25, z), yaw=i * 15,
             color=(min(col[0] + i * 6, 255), min(col[1] + i * 6, 255),
                    min(col[2] + i * 3, 255)), material="Ground")
    rock(x + r * 0.55, z - r * 0.4, gy, 0.8, "Rock", (100, 100, 104))


def watch_tower(x, z, gy, tag=""):
    occupy(x, z, 18)
    gy = sy(x, z, gy)
    """Сторожевая башня: лезь по ферме — наверху сундук."""
    rock(x - 3, z - 3, gy, 0.9, "Rock", (96, 96, 100))
    rock(x + 3, z + 2, gy, 0.8, "Rock", (96, 96, 100))
    truss("Tower_Truss_" + tag, (2, 18, 2), (x + 5.7, gy + 9, z))
    part("Tower_Deck_" + tag, (9, 1, 9), (x, gy + 18.5, z), color=(104, 80, 56),
         material="WoodPlanks")
    for sx, sz in [(-4, -4), (4, -4), (-4, 4), (4, 4)]:
        part("Tower_Post_" + tag, (0.8, 4, 0.8), (x + sx, gy + 21, z + sz),
             color=(84, 64, 46), material="Wood", cancollide=False)
    part("Tower_RoofA_" + tag, (10, 2.5, 5), (x, gy + 24.2, z - 2.5),
         color=(70, 50, 38), material="WoodPlanks", cls="WedgePart",
         cancollide=False)
    part("Tower_RoofB_" + tag, (10, 2.5, 5), (x, gy + 24.2, z + 2.5), yaw=180,
         color=(70, 50, 38), material="WoodPlanks", cls="WedgePart",
         cancollide=False)
    chest_marker(x + 2.5, z, gy + 19, "Tower" + tag)
    torch_wall(x - 4, z + 4, gy + 19, 0)


def standing_stones(x, z, gy):
    gy = sy(x, z, gy)
    for i in range(7):
        a = math.pi * 2 * i / 7
        sx, sz = x + math.sin(a) * 11, z + math.cos(a) * 11
        part("StandingStone", (2.4, rng.uniform(5, 8), 1.6), (sx, gy + 3, sz),
             yaw=math.degrees(a), pitch=rng.uniform(-5, 5),
             color=(124, 126, 132), material="Granite")
    part("StoneAltar", (4, 1.6, 4), (x, gy + 0.8, z), color=(134, 136, 140),
         material="Granite")
    crystal(x, z, gy + 1.6, 0.8, "violet")


def farm_field(x, z, gy, w=18, d=12, yaw=0.0):
    gy = sy(x, z, gy)
    part("Farm_Soil", (w, 0.6, d), (x, gy + 0.3, z), yaw=yaw, color=(96, 72, 50),
         material="Ground")
    rows = max(3, int(d / 2))
    for r in range(rows):
        rx, rz = l2w(x, z, yaw, 0, -d / 2 + 1 + r * 2)
        part("Farm_CropRow", (w - 1.6, 1.1, 0.9), (rx, gy + 1.1, rz), yaw=yaw,
             color=rng.choice([(104, 138, 62), (96, 128, 56), (140, 150, 70)]),
             material="Grass", cancollide=False)


def scarecrow(x, z, gy):
    gy = sy(x, z, gy)
    part("Scare_Pole", (0.5, 5, 0.5), (x, gy + 2.5, z), color=(90, 70, 50),
         material="Wood")
    part("Scare_Arms", (3.2, 0.4, 0.4), (x, gy + 3.6, z), color=(90, 70, 50),
         material="Wood", cancollide=False)
    part("Scare_Head", (1.1, 1.1, 1.1), (x, gy + 5.2, z), shape="Ball",
         color=(230, 160, 60), material="Fabric", cancollide=False)
    part("Scare_Hat", (1.6, 0.5, 1.6), (x, gy + 5.9, z), color=(120, 90, 50),
         material="Grass", cancollide=False)


def haystack(x, z, gy):
    gy = sy(x, z, gy)
    part("Haystack", (3.2, 2.6, 3.2), (x, gy + 1.3, z), yaw=rng.uniform(0, 90),
         color=(214, 178, 86), material="Grass")


def cart_wagon(x, z, gy, yaw=0.0):
    gy = sy(x, z, gy)
    part("Wagon_Bed", (6.5, 1.2, 3.4), (x, gy + 1.9, z), yaw=yaw,
         color=(96, 74, 52), material="WoodPlanks")
    fx, fz = l2w(x, z, yaw, 3.0, 0)
    part("Wagon_Front", (0.5, 1.8, 3.4), (fx, gy + 3.2, fz), yaw=yaw,
         color=(88, 68, 48), material="WoodPlanks", cancollide=False)
    bx, bz = l2w(x, z, yaw, -3.0, 0)
    part("Wagon_Back", (0.5, 1.8, 3.4), (bx, gy + 3.2, bz), yaw=yaw,
         color=(88, 68, 48), material="WoodPlanks", cancollide=False)
    for sx in (-2.2, 2.2):
        wx, wz = l2w(x, z, yaw, sx, 0)
        part("Wagon_Wheel", (0.6, 3.6, 3.6), (wx, gy + 1.6, wz), yaw=yaw + 90,
             pitch=90, color=(74, 56, 40), material="Wood")
    part("Wagon_Hay", (4.5, 1.4, 2.6), (x, gy + 3.1, z), yaw=yaw,
         color=(214, 178, 86), material="Grass", cancollide=False)


def fence_line(x0, z0, x1, z1, gy, off=8.0, step=24):
    gy = sy(x0, z0, gy)
    """Вереница столбиков с перекладинами вдоль дороги."""
    dx, dz = x1 - x0, z1 - z0
    dist = math.hypot(dx, dz)
    if dist < 1:
        return
    ux, uz = dx / dist, dz / dist
    px, pz = -uz, ux
    n = int(dist // step)
    yaw = math.degrees(math.atan2(dx, dz))
    for side in (1, -1):
        for i in range(n + 1):
            t = i / float(n)
            bx, bz = x0 + dx * t + px * off * side, z0 + dz * t + pz * off * side
            part("RoadFence", (0.6, 2.6, 0.6), (bx, gy + 1.3, bz),
                 yaw=rng.uniform(0, 180), color=(96, 80, 58), material="Wood")
            if i < n:
                mx = x0 + dx * (i + 0.5) / n + px * off * side
                mz = z0 + dz * (i + 0.5) / n + pz * off * side
                part("RoadFence_Rail", (step + 1.5, 0.35, 0.35),
                     (mx, gy + 2.1, mz), yaw=yaw, color=(104, 86, 62),
                     material="Wood", cancollide=False)


# ------------------------- v4: ГРАНДИОЗНЫЕ СООРУЖЕНИЯ ----------------------
def crenellate(name, cx, cz, y, w, d, yaw=0.0, step=5.5, col=(128, 126, 120)):
    """Зубцы (мерлоны) по периметру прямоугольной площадки."""
    for lx in range(int(-w / 2) + 1, int(w / 2), max(2, int(step))):
        for lz in (-d / 2 + 1, d / 2 - 1):
            px, pz = l2w(cx, cz, yaw, lx, lz)
            part(name, (2.4, 2.3, 2.4), (px, y + 1.15, pz), yaw=yaw, color=col,
                 material="Cobblestone", cancollide=False)
    for lz in range(int(-d / 2) + 3, int(d / 2) - 2, max(2, int(step))):
        for lx in (-w / 2 + 1, w / 2 - 1):
            px, pz = l2w(cx, cz, yaw, lx, lz)
            part(name, (2.4, 2.3, 2.4), (px, y + 1.15, pz), yaw=yaw, color=col,
                 material="Cobblestone", cancollide=False)


def banner(x, z, y, yaw=0.0, col=(158, 44, 44)):
    part("BannerPole", (0.4, 11, 0.4), (x, y + 5.5, z), color=(64, 50, 40),
         material="Wood")
    fx, fz = l2w(x, z, yaw, 0, 1.35)
    part("Banner_Cloth", (2.3, 6.5, 0.3), (fx, y + 5.5, fz), yaw=yaw, color=col,
         material="Fabric", cancollide=False)
    part("Banner_Tip", (1.9, 1.1, 0.3), (fx, y + 1.7, fz), yaw=yaw, color=col,
         material="Fabric", cancollide=False)


def statue_guardian(x, z, gy, yaw=0.0):
    gy = sy(x, z, gy)
    """Гигантская статуя стража (как у великих врат)."""
    stone = (138, 136, 130)
    part("Statue_Base", (8, 2.4, 8), (x, gy + 1.2, z), yaw=yaw, color=(124, 122, 116),
         material="Cobblestone")
    part("Statue_Legs", (5, 5.5, 3.4), (x, gy + 5.2, z), yaw=yaw, color=stone,
         material="Cobblestone")
    part("Statue_Torso", (6, 6.5, 3.8), (x, gy + 11.2, z), yaw=yaw, color=stone,
         material="Cobblestone")
    part("Statue_Shoulders", (8.2, 1.8, 4), (x, gy + 15.2, z), yaw=yaw,
         color=stone, material="Cobblestone")
    for side in (1, -1):
        ax, az = l2w(x, z, yaw, side * 4.2, 0)
        part("Statue_Arm", (2, 6, 2.2), (ax, gy + 11.5, az), yaw=yaw, color=stone,
             material="Cobblestone")
    part("Statue_Head", (3, 3, 3), (x, gy + 17.8, z), yaw=yaw, shape="Ball",
         color=stone, material="Cobblestone")
    part("Statue_Helm", (3.6, 1.1, 3.6), (x, gy + 19.7, z), yaw=yaw,
         color=(110, 108, 102), material="Metal", cancollide=False)


def citadel(cx, cz, gy):
    gy = sy(cx, cz, gy)
    occupy(cx, cz, 70)
    """ЦИТАДЕЛЬ ЛОРД-МАГИСТРА: 5 ярусов, башни, леса, знамёна, ~95 студов."""
    stone = (146, 144, 138)
    dark = (120, 118, 112)
    # подиум из трёх плит
    for i, (ww, hh) in enumerate([(80, 2), (70, 2), (60, 2)]):
        part("Citadel_Podium%d" % i, (ww, hh, ww), (cx, gy + 1 + i * 2, cz),
             color=dark, material="Cobblestone")
    # ярусы донжона с зубцами
    tiers = [(27, 16, 18), (22, 13, 34), (17, 12, 47), (12, 10, 59)]
    y = gy + 6
    for i, (w, h, _) in enumerate(tiers):
        part("Citadel_Tier%d" % i, (w, h, w), (cx, y + h / 2, cz), color=stone,
             material="Cobblestone")
        crenellate("Citadel_Merlon%d" % i, cx, cz, y + h, w, w, col=dark)
        # окна на южном и северном фасадах
        for sx in (-5, 0, 5):
            part("Citadel_Window%d_%d" % (i, sx), (1.3, 2.4, 0.4),
                 (cx + sx, y + h * 0.6, cz + w / 2 + 0.1), color=(255, 200, 110),
                 material="Neon", cancollide=False)
            part("Citadel_WindowB%d_%d" % (i, sx), (1.3, 2.4, 0.4),
                 (cx + sx, y + h * 0.6, cz - w / 2 - 0.1), color=(255, 200, 110),
                 material="Neon", cancollide=False)
        y += h
    # корона и шпиль
    part("Citadel_Crown", (8, 8, 8), (cx, y + 4, cz), color=(134, 132, 126),
         material="Cobblestone")
    crenellate("Citadel_CrownMerlon", cx, cz, y + 8, 8, 8, col=dark)
    part("Citadel_Spire", (9, 9, 9), (cx, y + 13.5, cz), shape="Ball",
         color=(112, 90, 70), material="WoodPlanks", cancollide=False)
    part("Citadel_SpireTip", (1, 7, 1), (cx, y + 21, cz), color=(70, 56, 44),
         material="Metal")
    # угловые башни с шарами
    for sx in (-1, 1):
        for sz in (-1, 1):
            tx, tz = cx + sx * 12, cz + sz * 12
            v_cyl("Citadel_Turret", tx, tz, gy + 6, 34, 9, stone, "Cobblestone")
            part("Citadel_TurretCap", (10, 5, 10), (tx, gy + 42, tz), shape="Ball",
                 color=(96, 52, 44), material="Fabric", cancollide=False)
            part("Citadel_TurretWin", (1.2, 2, 0.4), (tx, gy + 22, tz + 4.7),
                 color=(255, 200, 110), material="Neon", cancollide=False)
    # знамёна на фасаде
    banner(cx - 8.5, cz + 11.8, gy + 30, 0)
    banner(cx + 8.5, cz + 11.8, gy + 30, 0)
    banner(cx - 6.5, cz - 11.8, gy + 42, 180, (60, 70, 130))
    # вход: ворота на фасаде подиума, лестница-пандус, факелы
    part("Citadel_Gate", (7, 8, 1), (cx, gy + 4, cz + 30.3),
         color=(42, 32, 26), material="Wood")
    part("Citadel_GateArch", (10, 2.5, 2), (cx, gy + 9, cz + 30.3),
         color=(110, 108, 102), material="Cobblestone", cancollide=False)
    ramp(cx, cz + 40.5, gy, 6, 20, 12, "+Z")
    torch_wall(cx - 5, cz + 31.5, gy, 0)
    torch_wall(cx + 5, cz + 31.5, gy, 0)
    # строительные леса на восточной грани (можно лазить)
    sx0 = cx + 14.5
    truss("Citadel_Scaffold1", (1.8, 24, 1.8), (sx0, gy + 18, cz))
    part("Citadel_ScaffoldPlat1", (6, 0.7, 7), (sx0 + 1.5, gy + 30.5, cz + 3),
         color=(96, 74, 52), material="WoodPlanks")
    truss("Citadel_Scaffold2", (1.8, 26, 1.8), (sx0, gy + 43, cz))
    part("Citadel_ScaffoldPlat2", (6, 0.7, 7), (sx0 + 1.5, gy + 56.5, cz - 3),
         color=(96, 74, 52), material="WoodPlanks")
    truss("Citadel_Scaffold3", (1.8, 22, 1.8), (sx0, gy + 66, cz))
    brazier(cx, cz - 18, gy + 6)
    chest_marker(cx - 20, cz, gy + 6, "Citadel")


def great_gate(cx, cz, gy):
    gy = sy(cx, cz, gy)
    """ВЕЛИКИЕ ЮЖНЫЕ ВРАТА: колоссальная арка со статуями-стражами."""
    stone = (140, 138, 130)
    dark = (118, 116, 110)
    # крылья стены с зубцами
    for side in (1, -1):
        wx = cx + side * 32
        part("GreatGate_Wing", (36, 32, 10), (wx, gy + 16, cz), color=stone,
             material="Cobblestone")
        crenellate("GreatGate_WingMerlon", wx, cz, gy + 32, 36, 10, col=dark)
        part("GreatGate_Win", (1.4, 2.6, 0.4), (wx + side * 8, gy + 20, cz + 5.2),
             color=(255, 200, 110), material="Neon", cancollide=False)
        brazier(wx + side * 12, cz + 6.5, gy + 32.2)
    # пилоны и перекладина арки
    for side in (1, -1):
        px = cx + side * 14
        part("GreatGate_Pylon", (13, 36, 13), (px, gy + 18, cz), color=(150, 148, 140),
             material="Cobblestone")
        crenellate("GreatGate_PylonMerlon", px, cz, gy + 36, 13, 13, col=dark)
        torch_wall(px, cz + 7.2, gy + 10, 0)
    part("GreatGate_Lintel", (42, 9, 13), (cx, gy + 40.5, cz), color=(150, 148, 140),
         material="Cobblestone")
    crenellate("GreatGate_LintelMerlon", cx, cz, gy + 45, 42, 13, col=dark)
    part("GreatGate_Key", (5, 4, 1), (cx, gy + 34.5, cz + 6.7), color=(158, 44, 44),
         material="Fabric", cancollide=False)
    # статуи-стражи по сторонам
    statue_guardian(cx - 56, cz, gy, yaw=-90)
    statue_guardian(cx + 56, cz, gy, yaw=90)
    signpost(cx, cz + 12, gy, 180, "Великие Врата\nюг → Костяные Поля")


def floating_isle(cx, cz, top_y, r, tag, castle=False, grass=True):
    """Парящий остров: земля, скала снизу, висячий шип, кристаллы."""
    disc("SkyIsle_%s_Top" % tag, cx, cz, top_y, r, 3,
         (110, 142, 78) if grass else (216, 224, 234), "Grass" if grass else "Snow")
    disc("SkyIsle_%s_Rock" % tag, cx, cz, top_y - 4, r * 0.85, 6, (104, 102, 108),
         "Rock")
    part("SkyIsle_%s_Under1" % tag, (r * 0.9, 12, r * 0.9), (cx, top_y - 13, cz),
         yaw=rng.uniform(0, 90), color=(96, 94, 100), material="Rock")
    part("SkyIsle_%s_Under2" % tag, (r * 0.55, 10, r * 0.55), (cx, top_y - 24, cz),
         yaw=rng.uniform(0, 90), color=(88, 86, 92), material="Rock")
    part("SkyIsle_%s_Tip" % tag, (r * 0.35, r * 0.35, r * 0.35),
         (cx, top_y - 31, cz), shape="Ball", color=(80, 78, 84), material="Rock",
         cancollide=False)
    crystal(cx + r * 0.5, cz - r * 0.3, top_y, 1.1, "cyan")


def sky_castle(cx, cz, top_y):
    """Мини-замок на парящем острове."""
    stone = (176, 182, 196)
    part("SkyKeep_Body", (12, 18, 12), (cx, top_y + 9, cz), color=stone,
         material="Cobblestone")
    crenellate("SkyKeep_Merlon", cx, cz, top_y + 18, 12, 12, col=(150, 156, 170))
    part("SkyKeep_Tower", (6, 12, 6), (cx, top_y + 24, cz), color=(186, 192, 204),
         material="Cobblestone")
    part("SkyKeep_Spire", (8, 8, 8), (cx, top_y + 33, cz), shape="Ball",
         color=(90, 60, 70), material="Fabric", cancollide=False)
    part("SkyKeep_SpireTip", (0.8, 6, 0.8), (cx, top_y + 39, cz), color=(70, 50, 44),
         material="Metal")
    for sx in (-3, 3):
        part("SkyKeep_Win", (1.1, 2, 0.4), (cx + sx, top_y + 12, cz + 6.1),
             color=(255, 210, 120), material="Neon", cancollide=False)
    banner(cx - 4.5, cz + 6.4, top_y + 10, 0, (70, 90, 150))
    brazier(cx + 6, cz - 5, top_y)
    chest_marker(cx, cz - 8, top_y, "Sky")
    pine(cx - 9, cz + 7, top_y, 1.0)
    pine(cx + 8, cz + 8, top_y, 0.9)


def sky_ladder(points):
    """Небесная лестница: цепочка ферм с платформами (points: (x,z) снизу вверх)."""
    base_y = 20.5
    for i, pt in enumerate(points):
        x, z = pt[0], pt[1]
        y0 = base_y + i * 26
        h = 26
        truss("SkyLadder%d" % i, (2.4, h, 2.4), (x, y0 + h / 2, z))
        part("SkyLadder_Plat%d" % i, (9, 1, 9), (x, y0 + h + 0.5, z),
             color=(120, 118, 112), material="Cobblestone")
        torch_wall(x + 3.5, z + 3.5, y0 + h + 1, 0)
        rock(x - 4, z + 3, y0 + h + 1, 0.5, "Rock", (110, 110, 114))


def bastion_cannon(x, z, gy, yaw=-90):
    gy = sy(x, z, gy)
    """Береговая батарея: полукруглый бастион и ОГРОМНАЯ пушка."""
    stone = (150, 148, 140)
    disc("Bastion_Floor", x, z, gy + 1, 16, 2, stone, "Cobblestone")
    for i in range(5):
        a = math.pi * (-0.15 - i * 0.35) + math.pi / 2  # дуга к морю
        wx = x + math.cos(a) * 14
        wz = z + math.sin(a) * 14
        part("Bastion_Wall%d" % i, (12, 9, 5), (wx, gy + 4.5, wz),
             yaw=math.degrees(a) + 90, color=stone, material="Cobblestone")
        crenellate("Bastion_Merlon%d" % i, wx, wz, gy + 9, 10, 5,
                   yaw=math.degrees(a) + 90, col=(128, 126, 120))
    for sx in (-8, 8):
        part("Bastion_Mount", (4, 3, 4), (x + sx, gy + 2.5, z),
             color=(90, 88, 84), material="Metal")
    mx, mz = l2w(x, z, yaw, 0, 0)
    part("Bastion_Barrel", (18, 4.4, 4.4), (mx, gy + 6.5, mz), yaw=yaw, pitch=24,
         shape="Cylinder", color=(52, 54, 60), material="Metal")
    px, pz = l2w(x, z, yaw, 9.5, 0)
    part("Bastion_Muzzle", (2, 5.4, 5.4), (px, gy + 10.1, pz), yaw=yaw,
         shape="Cylinder", color=(40, 42, 48), material="Metal")
    bx, bz = l2w(x, z, yaw, -9.5, 0)
    part("Bastion_Breech", (5, 6, 6), (bx, gy + 4.5, bz), yaw=yaw, shape="Ball",
         color=(46, 48, 54), material="Metal")
    for i in range(6):
        sx2 = -10 + i * 4
        part("Bastion_Sandbag", (2.6, 1.2, 1.4), (x + sx2, gy + 2.6, z + 9),
             yaw=rng.uniform(-10, 10), color=(168, 150, 112), material="Fabric")
    crate_stack(x - 11, z - 8, gy + 2)
    barrel(x + 11, z - 8, gy + 2)


# ----------------------------------------------------------------------------
# v2: единый материк, растительность, порт, корабли, данжи, паркур, море
# ----------------------------------------------------------------------------
CONTINENT_POLY = [
    (-3550, -1100), (-3500, -2300), (-2950, -3180), (-2050, -3600),
    (-800, -3700), (700, -3620), (2000, -3300), (3000, -2780),
    (3600, -1950), (3760, -950), (3660, -50), (3800, 900),
    (3620, 1900), (3280, 2800), (2500, 3380), (1450, 3620),
    (150, 3700), (-1150, 3520),
    # v12: юго-западный выступ — Предгорья, Камнегорск и Квадратные Горы
    # раньше лежали ЗА границей материка, поэтому город оказывался в воде
    (-2300, 3480), (-3150, 3300), (-3560, 2560), (-3700, 1750),
    (-3720, 700), (-3800, -150),
]

ZONE_GROUND = [
    # (x0, z0, x1, z1, цвет, материал) — цвета смешиваются к краям зон
    (-3100, -3100, -800, -1000, (226, 233, 242), "Snow"),    # Морозные Пики
    (-860, -3300, 1400, -1100, (130, 98, 84), "Basalt"),     # Пустоши
    (650, -950, 3000, 1350, (130, 110, 64), "Mud"),          # Топи
    (650, 750, 3150, 3000, (210, 192, 144), "Sand"),         # Берег
    (-950, 750, 950, 3000, (140, 144, 94), "Ground"),        # Костяные поля
    (-3100, -950, -650, 1100, (72, 104, 62), "Ground"),      # Глумвуд
    (-3700, 1300, -2400, 3300, (146, 140, 126), "Slate"),    # v12: Каменные предгорья
]


def point_in_poly(x, z, poly=CONTINENT_POLY):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z):
            xin = (x2 - x1) * (z - z1) / (z2 - z1) + x1
            if x < xin:
                inside = not inside
    return inside


def poly_edge_dist(x, z):
    best = 1e9
    n = len(CONTINENT_POLY)
    for i in range(n):
        ax, az = CONTINENT_POLY[i]
        bx, bz = CONTINENT_POLY[(i + 1) % n]
        dx, dz = bx - ax, bz - az
        l2 = dx * dx + dz * dz
        t = 0 if l2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / l2))
        d = math.hypot(x - (ax + dx * t), z - (az + dz * t))
        if d < best:
            best = d
    return best


BASE_GRASS = (102, 134, 72)


def ground_style(x, z):
    """Цвет земли с ПЛАВНЫМ переходом между биомами (без резких линий)."""
    if math.hypot(x, z - 100) < 430:
        return (94, 122, 64), "Ground"
    best = None
    for (x0, z0, x1, z1, col, mat) in ZONE_GROUND:
        dx = max(x0 - x, 0, x - x1)
        dz = max(z0 - z, 0, z - z1)
        d = math.hypot(dx, dz)
        if d == 0:
            return col, mat
        if best is None or d < best[0]:
            best = (d, col, mat)
    d, col, mat = best
    t = min(1.0, d / 280.0)
    blended = tuple(int(col[i] * (1 - t) + BASE_GRASS[i] * t) for i in range(3))
    return blended, mat


def plateau_skirt(name, x0, z0, x1, z1, top, color, mat="Ground", grow=36):
    """Терраса-юбка вокруг плато: вместо обрыва — два низких ступеня."""
    slab(name + "_Skirt", x0 - grow, z0 - grow, x1 + grow, z1 + grow,
         top - 2.2, top - 12, color, mat)


def scatter(n, x0, z0, x1, z1, fn, excl=(), gy=8.0):
    out, tries = 0, 0
    while out < n and tries < n * 8 + 40:
        tries += 1
        x = rng.uniform(x0, x1)
        z = rng.uniform(z0, z1)
        if not point_in_poly(x, z):
            continue
        if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in excl):
            continue
        if not is_free(x, z, 8):
            continue
        fn(x, z, gy)
        out += 1


# ============================================================================
# v9: РЕЛЬЕФ — шумовая высотная карта, холмы, склоны, террасы
# ============================================================================
# Плоские «пятна» (деревни, лагеря, арены, дороги): внутри радиуса высота
# ровно y, дальше плавно (feather) переходит в природный рельеф.
FLATS = []
# v11: «дыры» подземелий — тут земля не ставится (лестница и залы)
CAVE_PITS = []
# Профили зон: (x0, z0, x1, z1, base, amp, freq)
ZONE_PROFILE = [
    ((-340, -240, 340, 440), 12.0, 1.1, 1 / 900.0),    # Пепельная Пристань
    ((-2380, -780, -660, 880), 14.0, 15.0, 1 / 620.0),  # Глумвуд
    ((-2400, -760, -60, -20), 15.0, 4.0, 1 / 700.0),   # перешеек
    ((-2560, -2560, -640, -760), 20.0, 20.0, 1 / 520.0),  # Морозные Пики
    ((-900, -2560, 1100, -1040), 16.0, 16.0, 1 / 560.0),  # Пепельные Пустоши
    ((620, -1020, 2400, 1080), 12.0, 3.4, 1 / 760.0),  # Топи Мирефен
    ((620, 760, 2520, 2400), 8.4, 5.0, 1 / 700.0),     # Затонувший Берег
    ((-1000, 760, 1000, 2400), 12.0, 11.0, 1 / 640.0),  # Костяные Поля
    ((-2600, 1500, -1900, 2100), 8.45, 6.0, 1 / 500.0),  # Полая Бездна
]
PLAINS_BASE = 9.0
PLAINS_AMP = 12.0


def add_flat(x, z, r, y, feather=55.0):
    if not PLANNING:
        return
    FLATS.append((float(x), float(z), float(r), float(y), float(feather)))


def add_flat_rect(x0, z0, x1, z1, y, feather=60.0):
    """Ровная площадка-прямоугольник: забиваем пятнами по сетке."""
    step = 70.0
    x = x0
    while x <= x1 + 0.1:
        z = z0
        while z <= z1 + 0.1:
            add_flat(x, z, 62.0, y, feather)
            z += step
        x += step


def _h2(i, j, seed):
    n = (i * 374761393 + j * 668265263 + seed * 11400714819323199488) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = (n ^ (n >> 16)) & 0xFFFFFFFF
    return n / 4294967295.0


def _sm(t):
    return t * t * (3.0 - 2.0 * t)


def vnoise(x, z, freq, seed=0):
    fx, fz = x * freq, z * freq
    i, j = math.floor(fx), math.floor(fz)
    tx, tz = _sm(fx - i), _sm(fz - j)
    a, b = _h2(i, j, seed), _h2(i + 1, j, seed)
    c, d = _h2(i, j + 1, seed), _h2(i + 1, j + 1, seed)
    return (a * (1 - tx) + b * tx) * (1 - tz) + (c * (1 - tx) + d * tx) * tz


def fbm(x, z, freq, octaves=4, seed=7, gain=0.5):
    total, amp, norm, f = 0.0, 1.0, 0.0, freq
    for o in range(octaves):
        total += vnoise(x, z, f, seed + o * 37) * amp
        norm += amp
        amp *= gain
        f *= 2.07
    return total / norm


def zone_profile(x, z):
    base, amp, freq = PLAINS_BASE, PLAINS_AMP, 1 / 720.0
    # предгорья на юго-западе и северо-востоке: там холмисто и высоко
    if x < -2200 and z > 900:
        return 26.0, 22.0, 1 / 480.0
    if x > 2200 and z < -1600:
        return 24.0, 20.0, 1 / 500.0
    best = None
    for (box, b, a, f) in ZONE_PROFILE:
        x0, z0, x1, z1 = box
        dx = max(x0 - x, 0, x - x1)
        dz = max(z0 - z, 0, z - z1)
        d = math.hypot(dx, dz)
        if d == 0:
            return b, a, f
        if best is None or d < best[0]:
            best = (d, b, a, f)
    if best:
        d, b, a, f = best
        t = min(1.0, d / 420.0)
        return (b * (1 - t) + PLAINS_BASE * t,
                a * (1 - t) + PLAINS_AMP * t, f)
    return base, amp, freq


def raw_height(x, z):
    base, amp, freq = zone_profile(x, z)
    n = fbm(x, z, freq, 4, 11) - 0.5
    ridge = abs(fbm(x, z, freq * 0.55, 3, 29) - 0.5) * 2.0
    h = base + n * amp * 2.0 + (ridge - 0.62) * amp * 1.1
    # v12: у границы материка рельеф мягко уходит в море, но БЕЗ плит-островов:
    # процесс «пляж» растянут на 260 студов и заканчивается ровно у кромки
    ed = poly_edge_dist(x, z)
    if ed < 260.0 and h < 18.0:
        # топим в море только НИЗКИЕ берега: высокие предгорья у кромки
        # остаются скалами, иначе Камнегорск и горы «уходили под воду»
        t = max(0.0, ed / 260.0) ** 0.6
        h = -2.2 * (1.0 - t) + h * t
    return h


def flat_pull(x, z, h):
    for (fx, fz, r, y, fe) in FLATS:
        d = math.hypot(x - fx, z - fz)
        if d < r + fe:
            t = 1.0 if d <= r else 1.0 - (d - r) / fe
            t = _sm(t)
            h = h * (1.0 - t) + y * t
    return h


PLATEAUS = []


def add_plateau_rect(x0, z0, x1, z1, top):
    PLATEAUS.append(("rect", x0, z0, x1, z1, float(top)))


def add_plateau_circle(x, z, r, top):
    PLATEAUS.append(("circle", x, z, r, 0.0, float(top)))


def plateau_top(x, z):
    best = None
    for entry in PLATEAUS:
        if entry[0] == "rect":
            _, x0, z0, x1, z1, top = entry
            if x0 <= x <= x1 and z0 <= z <= z1:
                if best is None or top > best:
                    best = top
        else:
            _, cx, cz, r, _, top = entry
            if math.hypot(x - cx, z - cz) <= r:
                if best is None or top > best:
                    best = top
    return best


def height_at(x, z):
    """Итоговая высота поверхности (используется декором и постройками)."""
    h = flat_pull(x, z, raw_height(x, z))
    top = plateau_top(x, z)
    if top is not None and top > h:
        return top
    return h


# ---------------- сетка земли ----------------

def sy(x, z, y):
    """Высота земли под декором (если вызывающий явно не задал высокую точку)."""
    try:
        h = height_at(x, z)
    except Exception:
        return y
    if abs(h - y) <= 15.0:
        return h
    return y



def terrace_steps(name, x0, z0, x1, z1, y_top, y_bottom, color, material,
                  tread=11.0, step=2.4, ring_color=None):
    """Терраса-пирамида: каждое кольцо выше предыдущего на `step` (<=2.6),
    поэтому наверх можно зайти пешком с любой стороны."""
    if y_top <= y_bottom:
        return
    n = max(1, int(math.ceil((y_top - y_bottom) / step)))
    cx, cz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    ring_color = ring_color or color
    for i in range(n):
        y = y_bottom + (i + 1) * (y_top - y_bottom) / float(n)
        inset = i * tread
        ax, bx = x0 + inset, x1 - inset
        az, bz = z0 + inset, z1 - inset
        if bx - ax < tread * 1.2 or bz - az < tread * 1.2:
            break
        t = i / float(max(1, n - 1))
        col = tuple(int(ring_color[k] * (0.86 + 0.16 * t)) for k in range(3))
        slab(name + "_Ring%d" % i, ax, az, bx, bz, y, y - 9.0, col, material)
    # внутренняя площадка
    inset = n * tread
    if (x1 - inset) - (x0 + inset) > 6 and (z1 - inset) - (z0 + inset) > 6:
        slab(name + "_Top", x0 + inset, z0 + inset, x1 - inset, z1 - inset,
             y_top, y_top - 9.0, color, material)


def in_cave_pit(cx, cz):
    """Точка попадает в «дыру» подземелья — землю там не ставим."""
    for (px0, pz0, px1, pz1) in CAVE_PITS:
        if px0 <= cx <= px1 and pz0 <= cz <= pz1:
            return True
    return False


def terrain_grid(name, x0, z0, x1, z1, cell=85.0, max_step=2.6,
                 color_override=None, mat_override=None, seed_jitter=6,
                 skip_boxes=(), road_flat=None):
    """Тайлы земли. Высоты сглаживаются так, чтобы соседние тайлы
    отличались не больше чем на max_step — тогда везде можно зайти пешком."""
    nx = max(2, int((x1 - x0) / cell))
    nz = max(2, int((z1 - z0) / cell))
    cw = (x1 - x0) / float(nx)
    cd = (z1 - z0) / float(nz)

    H = []
    for i in range(nx):
        col = []
        cx = x0 + (i + 0.5) * cw
        for j in range(nz):
            cz = z0 + (j + 0.5) * cd
            col.append(flat_pull(cx, cz, raw_height(cx, cz)))
        H.append(col)

    # эрозия: срезаем слишком высокие тайлы, чтобы перепад был <= max_step
    for _ in range(4):
        newH = [[0.0] * nz for _ in range(nx)]
        for i in range(nx):
            for j in range(nz):
                cap = H[i][j]
                if i > 0:
                    cap = min(cap, H[i - 1][j] + max_step)
                if i + 1 < nx:
                    cap = min(cap, H[i + 1][j] + max_step)
                if j > 0:
                    cap = min(cap, H[i][j - 1] + max_step)
                if j + 1 < nz:
                    cap = min(cap, H[i][j + 1] + max_step)
                newH[i][j] = cap
        H = newH

    count = 0
    for i in range(nx):
        cx = x0 + (i + 0.5) * cw
        for j in range(nz):
            cz = z0 + (j + 0.5) * cd
            if not point_in_poly(cx, cz):
                continue
            skipped = False
            for (sx0, sz0, sx1, sz1) in skip_boxes:
                if sx0 <= cx <= sx1 and sz0 <= cz <= sz1:
                    skipped = True
                    break
            if skipped:
                continue
            # v11: над подземельями земля вырезана (там лестница и залы)
            if in_cave_pit(cx, cz):
                continue
            h = H[i][j]
            # уклон для материала
            dh = 0.0
            if i > 0:
                dh = max(dh, abs(H[i][j] - H[i - 1][j]))
            if j > 0:
                dh = max(dh, abs(H[i][j] - H[i][j - 1]))
            col, mat = ground_style(cx, cz)
            if color_override:
                col = color_override
            if mat_override:
                mat = mat_override
            if dh > 1.6:
                # крутые места — камень
                col = (int(col[0] * 0.78 + 42), int(col[1] * 0.78 + 40),
                       int(col[2] * 0.8 + 40))
                mat = "Rock"
            jj = rng.randint(-seed_jitter, seed_jitter)
            col = (max(0, min(255, col[0] + jj)), max(0, min(255, col[1] + jj)),
                   max(0, min(255, col[2] + jj)))
            part(name, (cw + 0.6, 30.0, cd + 0.6),
                 (cx, h - 15.0, cz), color=col, material=mat)
            count += 1
    return count


def terrain_check(x0, z0, x1, z1, cell=85.0):
    """Проверка: максимальный перепад между соседними тайлами."""
    nx = max(2, int((x1 - x0) / cell))
    nz = max(2, int((z1 - z0) / cell))
    cw = (x1 - x0) / float(nx)
    cd = (z1 - z0) / float(nz)
    H = []
    for i in range(nx):
        col = []
        cx = x0 + (i + 0.5) * cw
        for j in range(nz):
            cz = z0 + (j + 0.5) * cd
            col.append(flat_pull(cx, cz, raw_height(cx, cz)))
        H.append(col)
    for _ in range(10):
        newH = [[0.0] * nz for _ in range(nx)]
        for i in range(nx):
            for j in range(nz):
                cap = H[i][j]
                if i > 0:
                    cap = min(cap, H[i - 1][j] + 2.6)
                if i + 1 < nx:
                    cap = min(cap, H[i + 1][j] + 2.6)
                if j > 0:
                    cap = min(cap, H[i][j - 1] + 2.6)
                if j + 1 < nz:
                    cap = min(cap, H[i][j + 1] + 2.6)
                newH[i][j] = cap
        H = newH
    worst = 0.0
    for i in range(nx):
        for j in range(nz):
            if i + 1 < nx:
                worst = max(worst, abs(H[i][j] - H[i + 1][j]))
            if j + 1 < nz:
                worst = max(worst, abs(H[i][j] - H[i][j + 1]))
    return worst, min(H[i][j] for i in range(nx) for j in range(nz)), \
        max(H[i][j] for i in range(nx) for j in range(nz))


# ------------------------- поверхностные слои -------------------------------
def _field(name, x0, z0, x1, z1, color, material, cell=95.0, lift=0.06,
           chance=1.0, transparency=0.0, collide=True):
    """Тонкий слой поверх рельефа (лавы/болота/песка) по сетке."""
    x = x0
    while x <= x1:
        z = z0
        while z <= z1:
            if point_in_poly(x, z) and rng.random() < chance:
                h = height_at(x, z)
                part(name, (cell + 1.0, 1.2, cell + 1.0), (x, h + lift - 0.6, z),
                     color=color, material=material, transparency=transparency,
                     cancollide=collide)
            z += cell
        x += cell


def lava_field(x0, z0, x1, z1):
    """Лава в трещинах Пустошей (светится, жжёт)."""
    for _ in range(190):
        x = rng.uniform(x0, x1)
        z = rng.uniform(z0, z1)
        if not point_in_poly(x, z):
            continue
        r = rng.uniform(7, 26)
        h = height_at(x, z)
        disc("LavaCrack", x, z, h + 0.12, r, 0.8, (255, 96, 18), "Neon",
             light=dict(brightness=0.7, range=r * 2.2, color=(255, 130, 40))
             if r > 16 else None)
    _field("AshDust", x0, z0, x1, z1, (104, 82, 70), "CrackedLava",
           cell=110.0, lift=-0.2, chance=0.35)


def swamp_field(x0, z0, x1, z1):
    """Болотные окна воды и мшистые кочки."""
    for _ in range(150):
        x = rng.uniform(x0, x1)
        z = rng.uniform(z0, z1)
        if not point_in_poly(x, z):
            continue
        r = rng.uniform(9, 30)
        h = height_at(x, z)
        disc("SwampPool", x, z, h + 0.05, r, 0.6, (54, 86, 62), "Water",
             transparency=0.25, cancollide=False)
        if rng.random() < 0.6:
            for _ in range(rng.randint(1, 3)):
                reed(x + rng.uniform(-r * 0.7, r * 0.7),
                     z + rng.uniform(-r * 0.7, r * 0.7), h)
    _field("MossPatch", x0, z0, x1, z1, (118, 126, 70), "Mud",
           cell=120.0, lift=-0.1, chance=0.4)


def sand_field(x0, z0, x1, z1):
    _field("CoastSand", x0, z0, x1, z1, (200, 184, 142), "Sand",
           cell=120.0, lift=-0.05, chance=0.75)


# ------------------------- растительность ----------------------------------
def tree_nice(x, z, y, s=1.0):
    """Пышное дерево-«помпон»: ствол + 4 сочных шара кроны (как в референсах)."""
    occupy(x, z, 7, "decor")
    y = sy(x, z, y)
    th = rng.uniform(9, 13) * s
    part("Tree_Trunk", (2.8 * s, th, 2.8 * s), (x, y + th / 2, z),
         yaw=rng.uniform(0, 360), color=(88, 66, 48), material="Wood")
    cy = y + th + 0.5 * s
    col = rng.choice([(74, 122, 58), (66, 114, 54), (84, 132, 64), (58, 108, 50)])
    part("Tree_Blob", (rng.uniform(10, 13) * s, rng.uniform(8, 10) * s,
                       rng.uniform(10, 13) * s), (x, cy + 2 * s, z),
         shape="Ball", color=col, material="Grass", cancollide=False)
    for k in range(2):
        a = rng.uniform(0, math.pi * 2)
        off = rng.uniform(4.2, 5.8) * s
        part("Tree_Blob2", (rng.uniform(5, 7) * s, rng.uniform(4, 5.5) * s,
                            rng.uniform(5, 7) * s),
             (x + math.sin(a) * off, cy + rng.uniform(0, 2.5) * s,
              z + math.cos(a) * off), shape="Ball", color=col,
             material="Grass", cancollide=False)
    part("Tree_BlobTop", (4.2 * s, 3.4 * s, 4.2 * s), (x, cy + 6.2 * s, z),
         shape="Ball", color=col, material="Grass", cancollide=False)


def bush(x, z, y, s=1.0):
    y = sy(x, z, y)
    occupy(x, z, 4, "decor")
    w = rng.uniform(2.6, 4.2) * s
    part("Bush", (w, w * 0.7, w), (x, y + w * 0.3, z), yaw=rng.uniform(0, 90),
         color=rng.choice([(50, 76, 44), (58, 84, 48), (44, 68, 40)]),
         material="Grass", cancollide=False)
    if rng.random() < 0.3:
        for i in range(3):
            a = rng.uniform(0, math.pi * 2)
            part("Berry", (0.4, 0.4, 0.4),
                 (x + math.sin(a) * w * 0.3, y + w * 0.55, z + math.cos(a) * w * 0.3),
                 shape="Ball", color=(200, 60, 70), material="Neon", cancollide=False)


def grass_tuft(x, z, y, col=None):
    y = sy(x, z, y)
    part("GrassTuft", (1.4, 1.0, 0.18), (x, y + 0.45, z), yaw=rng.uniform(0, 180),
         color=col or rng.choice([(74, 104, 52), (66, 96, 48), (84, 112, 58)]),
         material="Grass", cancollide=False)


def fern(x, z, y):
    y = sy(x, z, y)
    for k in (0, 90):
        part("Fern", (2.0, 1.1, 0.14), (x, y + 0.5, z), yaw=k + rng.uniform(-20, 20),
             pitch=-12, color=(52, 82, 44), material="Grass", cancollide=False)


def flower(x, z, y):
    y = sy(x, z, y)
    col = rng.choice([(210, 80, 160), (230, 90, 70), (240, 240, 200), (110, 160, 255)])
    part("Flower_Stem", (0.14, 1.1, 0.14), (x, y + 0.55, z), color=(60, 90, 50),
         material="Grass", cancollide=False)
    part("Flower", (0.45, 0.45, 0.45), (x, y + 1.2, z), shape="Ball", color=col,
         material="Neon", cancollide=False)


def fallen_log(x, z, y):
    y = sy(x, z, y)
    ln = rng.uniform(6, 10)
    yaw = rng.uniform(0, 360)
    part("Log", (ln, 1.3, 1.3), (x, y + 0.6, z), yaw=yaw, color=(78, 60, 44),
         material="Wood")
    ox, oz = l2w(x, z, yaw, ln * 0.2, 0.8)
    part("Log_Branch", (2.6, 0.8, 0.8), (ox, y + 1.0, oz), yaw=yaw + 55,
         pitch=22, color=(72, 54, 40), material="Wood", cancollide=False)
    if rng.random() < 0.5:
        part("Log_Moss", (ln * 0.5, 0.25, 1.35), (x, y + 1.3, z), yaw=yaw,
             color=(56, 80, 46), material="Grass", cancollide=False)


def stone_pile(x, z, y):
    y = sy(x, z, y)
    rock(x, z, y, 0.6, "Rock", (96, 96, 100))
    rock(x + rng.uniform(-2, 2), z + rng.uniform(-2, 2), y, 0.4, "Rock",
         (110, 110, 114))


def ruin_fragment(x, z, y):
    y = sy(x, z, y)
    if rng.random() < 0.5:
        v_cyl("RuinFrag_Column", x, z, y, rng.uniform(2, 5), 2.6, (172, 170, 160),
              "Marble", tilt_pitch=rng.uniform(-14, 14), tilt_roll=rng.uniform(-14, 14))
    else:
        part("RuinFrag_Block", (rng.uniform(2, 4), rng.uniform(1, 2.4),
                                rng.uniform(2, 4)), (x, y + 0.8, z),
             yaw=rng.uniform(0, 90), color=(160, 158, 150), material="Cobblestone")
    rock(x + rng.uniform(-3, 3), z + rng.uniform(-3, 3), y, 0.45, "Rock",
         (140, 138, 130))


def glowshroom(x, z, y):
    h = rng.uniform(1.5, 3)
    occupy(x, z, 3, "decor")
    part("GlowStem", (h, 0.9, 0.9), (x, y + h / 2, z), roll=90, shape="Cylinder",
         color=(180, 190, 170), material="SmoothPlastic")
    part("GlowCap", (1.8, 1.0, 1.8), (x, y + h + 0.3, z), shape="Ball",
         color=rng.choice([(110, 255, 160), (170, 120, 255), (90, 200, 255)]),
         material="Neon", cancollide=False)


def bone_scatter(x, z, y):
    for i in range(3):
        part("Bone_", (rng.uniform(1.6, 2.8), 0.7, 0.7),
             (x + rng.uniform(-3, 3), y + 0.5, z + rng.uniform(-3, 3)),
             yaw=rng.uniform(0, 360), color=(214, 208, 190),
             material="SmoothPlastic", cancollide=False)


# ------------------------- паркур и сундуки --------------------------------
def chest_marker(x, z, y, tag):
    part("Chest_Body_" + tag, (2.4, 1.5, 1.5), (x, y + 0.75, z),
         color=(196, 150, 60), material="Metal")
    part("Chest_Lid_" + tag, (2.4, 0.5, 1.5), (x, y + 1.7, z),
         color=(226, 184, 80), material="Metal", cancollide=False)
    part("Chest_Glow_" + tag, (0.1, 0.1, 0.1), (x, y + 2.5, z), transparency=1,
         cancollide=False, light=dict(brightness=1.2, range=18, color=(255, 210, 90)))


def torch_wall(x, z, y, yaw=0.0):
    px, pz = l2w(x, z, yaw, 0, 0)
    part("Torch_Bracket", (0.4, 0.4, 1.4), (px, y + 2.4, pz), yaw=yaw,
         color=(60, 48, 38), material="Wood", cancollide=False)
    part("Torch_Flame", (0.9, 1.3, 0.9), (px, y + 3.2, pz), color=(255, 160, 60),
         material="Neon", cancollide=False, transparency=0.15,
         fire=dict(size=4, heat=6),
         light=dict(brightness=1.4, range=22, color=(255, 150, 60)))


def parkour_rocks(p0, p1, y0, y1, n, col=(104, 106, 112), tag=""):
    """Цепочка платформ для прыжков от p0 к p1 с высотой y0 до y1."""
    for i in range(n):
        t = i / float(n - 1)
        bx = p0[0] + (p1[0] - p0[0]) * t + rng.uniform(-2.5, 2.5)
        bz = p0[1] + (p1[1] - p0[1]) * t + rng.uniform(-2.5, 2.5)
        by = y0 + (y1 - y0) * t
        r = rng.uniform(2.6, 3.6)
        part("ParkRocks_%s_%d" % (tag, i), (r * 2, rng.uniform(1.4, 2.4), r * 2),
             (bx, by + 0.6, bz), yaw=rng.uniform(0, 90), pitch=rng.uniform(-4, 4),
             color=col, material="Rock")
    # финальная площадка со сундуком
    part("Shrine_Platform_" + tag, (10, 1.2, 10), (p1[0], y1 + 0.6, p1[1]),
         color=(120, 118, 112), material="Cobblestone")
    part("Shrine_PillarA_" + tag, (1.6, 6, 1.6), (p1[0] - 4, y1 + 3, p1[1] - 4),
         color=(140, 138, 130), material="Cobblestone")
    part("Shrine_PillarB_" + tag, (1.6, 6, 1.6), (p1[0] + 4, y1 + 3, p1[1] + 4),
         color=(140, 138, 130), material="Cobblestone")
    brazier(p1[0], p1[1] - 3, y1 + 1.2)
    chest_marker(p1[0], p1[1] + 1.5, y1 + 1.2, tag)


# ------------------------- мосты v2 ----------------------------------------
def covered_bridge(x, z, gy, yaw=0.0, span=40, width=9):
    """Крытый мост через реку: настил, стены, крыша."""
    n = 5
    seg = span / n
    for i in range(n):
        t = (i + 0.5) / n
        off = (t - 0.5) * span
        lx, lz = l2w(x, z, yaw, off, 0)
        part("CovBridge_Deck", (seg + 0.6, 0.6, width), (lx, gy + 1.1, lz),
             yaw=yaw, color=(88, 66, 46), material="WoodPlanks")
        for side in (1, -1):
            wx, wz = l2w(x, z, yaw, off, side * (width / 2 - 0.3))
            part("CovBridge_Wall", (seg + 0.6, 4.4, 0.5), (wx, gy + 3.4, wz),
                 yaw=yaw, color=(96, 72, 50), material="WoodPlanks",
                 cancollide=False)
        part("CovBridge_Roof", (seg + 0.8, 0.5, width + 2.4), (lx, gy + 6.1, lz),
             yaw=yaw, color=(70, 50, 38), material="WoodPlanks", cancollide=False)
    for off in (-span / 2, span / 2):
        lx, lz = l2w(x, z, yaw, off, 0)
        part("CovBridge_Pylon", (2.4, 6, width), (lx, gy - 1.2, lz),
             color=(76, 58, 44), material="Cobblestone")


def rope_bridge(x0, z0, x1, z1, deck_y, width=4, mid_rock=True):
    """Верёвочный мост: столбы, провисший настил из досок, канаты (с наклоном)."""
    dx, dz = x1 - x0, z1 - z0
    dist = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz))
    n = max(6, int(dist // 6))
    mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
    if mid_rock and dist > 200:
        rock(mx, mz, deck_y - 16, 3.2, "Rock", (96, 98, 104))
    for i in range(n + 1):
        t = i / float(n)
        px, pz = x0 + dx * t, z0 + dz * t
        sag = -math.sin(math.pi * t) * (dist / 45.0)
        py = deck_y + sag
        part("RopeBridge_Plank", (5.2, 0.4, width), (px, py, pz), yaw=yaw,
             color=(104, 80, 56), material="WoodPlanks")
        if i < n:
            t2 = (i + 1) / float(n)
            py2 = deck_y - math.sin(math.pi * t2) * (dist / 45.0)
            segd = math.hypot(dx / n, py2 - py)
            pitch = math.degrees(math.asin((py2 - py) / segd))
            for side in (1, -1):
                rx, rz = l2w(px + dx / n / 2, pz + dz / n / 2, yaw,
                             0, side * (width / 2))
                part("RopeBridge_Rope", (segd + 0.5, 0.3, 0.3),
                     (rx, (py + py2) / 2 + 1.2, rz), yaw=yaw, pitch=pitch,
                     color=(130, 110, 80), material="Fabric", cancollide=False)
    for (ex, ez) in ((x0, z0), (x1, z1)):
        part("RopeBridge_Post", (0.9, 9, 0.9), (ex, deck_y + 3.5, ez),
             color=(84, 64, 46), material="Wood")
        rock(ex, ez, deck_y - 2.2, 1.4, "Rock", (100, 100, 104))


# ------------------------- порт и корабли ----------------------------------
def sailing_ship(name, x, z, y, yaw=0.0):
    part(name + "_Hull", (46, 7, 14), (x, y + 3.5, z), yaw=yaw,
         color=(84, 60, 42), material="Wood")
    part(name + "_Deck", (40, 1.2, 12), (x, y + 7.4, z), yaw=yaw,
         color=(104, 80, 56), material="WoodPlanks", cancollide=False)
    bx, bz = l2w(x, z, yaw, -21, 0)
    part(name + "_Stern", (8, 5, 12), (bx, y + 10, bz), yaw=yaw,
         color=(92, 66, 46), material="Wood", cancollide=False)
    bx, bz = l2w(x, z, yaw, 22, 0)
    part(name + "_Bow", (6, 4, 8), (bx, y + 9, bz), yaw=yaw,
         color=(92, 66, 46), material="Wood", cancollide=False)
    for mox in (-6, 6):
        mx, mz = l2w(x, z, yaw, mox, 0)
        part(name + "_Mast", (1.6, 26, 1.6), (mx, y + 21, mz), color=(72, 52, 36),
             material="Wood")
        part(name + "_Yard", (14, 0.8, 0.8), (mx, y + 31, mz), color=(72, 52, 36),
             material="Wood", cancollide=False)
        part(name + "_Sail", (12, 8, 0.5), (mx, y + 26.5, mz), color=(196, 188, 168),
             material="Fabric", cancollide=False)
        part(name + "_Flag", (3, 1.6, 0.3), (mx, y + 34.5, mz), yaw=rng.uniform(0, 90),
             color=(160, 40, 40), material="Fabric", cancollide=False)
    bx, bz = l2w(x, z, yaw, 28, 0)
    part(name + "_Bowsprit", (10, 1.2, 1.2), (bx, y + 10.5, bz), yaw=yaw,
         pitch=-12, color=(72, 52, 36), material="Wood", cancollide=False)


def pier(x, z, gy, yaw=0.0, length=130, width=10):
    """Деревянный причал в море."""
    n = int(length // 13)
    for i in range(n + 1):
        t = i / float(n)
        off = t * length
        lx, lz = l2w(x, z, yaw, off, 0)
        part("Pier_Deck", (13.5, 0.7, width), (lx, gy + 2.0, lz), yaw=yaw,
             color=(110, 86, 60), material="WoodPlanks")
        if i % 2 == 0:
            for side in (1, -1):
                px, pz = l2w(x, z, yaw, off, side * (width / 2 - 0.8))
                v_cyl("Pier_Piling", px, pz, -6, gy + 2.0 + 6, 1.6, (70, 52, 38),
                      "Wood")
    for off in (18, length - 18):
        lx, lz = l2w(x, z, yaw, off, width / 2 - 0.7)
        part("Pier_Bollard", (1.2, 1.2, 1.2), (lx, gy + 2.9, lz), color=(50, 50, 54),
             material="Metal")
    lx, lz = l2w(x, z, yaw, length - 6, 0)
    part("Pier_Lamp", (1.1, 1.1, 1.1), (lx, gy + 4.6, lz), color=(255, 200, 110),
         material="Neon", cancollide=False,
         light=dict(brightness=1.5, range=30, color=(255, 190, 100)))
    # сходня на берег
    bx, bz = l2w(x, z, yaw, -6, 0)
    part("Pier_Gang", (12, 0.6, width - 2), (bx, gy + 1.2, bz), yaw=yaw, pitch=-6,
         color=(104, 80, 56), material="WoodPlanks")


def port_crane(x, z, gy, yaw=0.0):
    part("Crane_Base", (7, 1.4, 7), (x, gy + 0.7, z), color=(96, 92, 88),
         material="Cobblestone")
    part("Crane_Post", (1.8, 13, 1.8), (x, gy + 7.2, z), color=(84, 64, 46),
         material="Wood")
    jx, jz = l2w(x, z, yaw, 6, 0)
    part("Crane_Jib", (18, 1.4, 1.4), (jx, gy + 13.4, jz), yaw=yaw, pitch=-7,
         color=(84, 64, 46), material="Wood")
    hx, hz = l2w(x, z, yaw, 13, 0)
    part("Crane_Rope", (0.3, 7, 0.3), (hx, gy + 9, hz), color=(150, 140, 120),
         material="Fabric", cancollide=False)
    part("Crane_Hook", (1.6, 1.6, 1.6), (hx, gy + 5, hz), color=(90, 70, 50),
         material="Wood", cancollide=False)


def barrel(x, z, y):
    v_cyl("Barrel", x, z, y, 2.4, 2.2, (110, 84, 56), "Wood")


def crate_stack(x, z, y):
    for i, (ox, oz, s) in enumerate([(0, 0, 2.4), (2.2, 0.6, 2.0), (0.4, 2.0, 1.8)]):
        part("Crate", (s, s, s), (x + ox, y + s / 2 + (0.2 if i == 1 else 0),
                                  z + oz), yaw=rng.uniform(0, 90),
             color=(128, 98, 64), material="WoodPlanks")


# ------------------------- вулкан ------------------------------------------
def volcano(cx, cz, gy):
    """v9: ОГРОМНЫЙ вулкан — рваный кратер, лавовые реки по 4 склонам,
    пепельные шлейфы, обсидиановые шипы, паркур внутрь кратера и логово."""
    add_flat(cx, cz, 300, gy, 90.0)

    # --- конус: 16 колец, каждое на 2.4 студа выше, отступ 9 студов ---
    n = 26
    tier_h = 2.4
    w = 300.0
    for i in range(n):
        y = gy + i * tier_h
        t = i / float(n)
        col = (int(48 + t * 34), int(42 + t * 30), int(46 + t * 26))
        cnt = max(10, int(w * 2.2 / 26))
        for k in range(cnt):
            a = math.pi * 2 * k / cnt + i * 0.13
            rr = w / 2.0 + rng.uniform(-4, 4)
            px = cx + math.sin(a) * rr
            pz = cz + math.cos(a) * rr
            part("Volcano_Ring%d_%d" % (i, k), (20, tier_h + 0.4, 20),
                 (px, y + tier_h / 2, pz), yaw=math.degrees(a) + rng.uniform(-14, 14),
                 color=col, material="Basalt")
        w = max(46.0, w - 9.4)

    rim_y = gy + n * tier_h
    # --- рваный край кратера ---
    for k in range(30):
        a = math.pi * 2 * k / 30
        rr = rng.uniform(24, 34)
        px, pz = cx + math.sin(a) * rr, cz + math.cos(a) * rr
        part("Volcano_Rim", (rng.uniform(6, 12), rng.uniform(4, 9), rng.uniform(6, 12)),
             (px, rim_y + rng.uniform(1, 4), pz), yaw=rng.uniform(0, 360),
             pitch=rng.uniform(-16, 16), color=(40, 36, 40), material="Basalt")
    # --- лавовое озеро в жерле ---
    disc("Volcano_Lava", cx, cz, rim_y - 1.2, 26, 2.0, (255, 96, 18), "Neon",
         light=dict(brightness=3.0, range=140, color=(255, 120, 40), shadows=True))
    disc("Volcano_LavaCore", cx, cz, rim_y - 0.8, 14, 1.2, (255, 190, 60), "Neon",
         light=dict(brightness=2.2, range=60, color=(255, 180, 70)))
    # пузыри лавы
    for _ in range(10):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(2, 20)
        part("Volcano_Bubble", (rng.uniform(3, 7), 1.4, rng.uniform(3, 7)),
             (cx + math.sin(a) * rr, rim_y - 0.7, cz + math.cos(a) * rr),
             shape="Ball", color=(255, 170, 50), material="Neon", cancollide=False)

    # --- пепельный шлейф и жар ---
    for i in range(4):
        part("Volcano_AshPlume", (0.1, 0.1, 0.1), (cx + rng.uniform(-8, 8),
             rim_y + 12 + i * 24, cz + rng.uniform(-8, 8)), transparency=1,
             cancollide=False,
             fire=dict(size=18 + i * 5, heat=1.4, color=(72, 68, 74),
                       secondary=(34, 32, 36)))
    part("Volcano_Heat", (0.1, 0.1, 0.1), (cx, rim_y + 3, cz), transparency=1,
         cancollide=False, fire=dict(size=16, heat=4, color=(255, 150, 60),
                                     secondary=(180, 70, 20)))

    # --- ЛАВОВЫЕ РЕКИ по четырём склонам ---
    for si, base_ang in enumerate((0.0, 1.6, 3.2, 4.7)):
        runw = w
        for i in range(n):
            t = i / float(n)
            y = rim_y - i * tier_h
            rr = (runw * 0.5) * (1.0 - t * 0.0)
            runw = max(46.0, runw + 9.4) if False else runw
        # проще: строим по кольцам сверху вниз
        for i in range(n):
            t = i / float(n)
            y = rim_y - i * tier_h
            ring = 300.0 - i * 9.4
            if ring < 52:
                ring = 52
            a = base_ang + math.sin(t * 6.0) * 0.22
            px = cx + math.sin(a) * (ring * 0.52)
            pz = cz + math.cos(a) * (ring * 0.52)
            part("Volcano_LavaRiver", (rng.uniform(7, 12), 1.1, 15),
                 (px, y + 0.9, pz), yaw=math.degrees(a) + rng.uniform(-10, 10),
                 color=(255, 104, 22), material="Neon", cancollide=False,
                 light=dict(brightness=1.1, range=26, color=(255, 120, 40))
                 if i % 4 == 0 else None)
    # лавовые озёра у подножия
    for a in (0.0, 1.6, 3.2, 4.7):
        lava_pool(cx + math.sin(a) * 210, cz + math.cos(a) * 210, gy, 30)

    # --- обсидиановые шипы вокруг ---
    for _ in range(70):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(170, 300)
        hh = rng.uniform(10, 32)
        part("Volcano_Spike", (rng.uniform(3, 7), hh, rng.uniform(3, 7)),
             (cx + math.sin(a) * rr, gy + hh / 2 - 1, cz + math.cos(a) * rr),
             yaw=rng.uniform(0, 360), pitch=rng.uniform(-12, 12),
             color=(30, 27, 34), material="Basalt")

    # --- паркур по спирали к краю кратера ---
    for i in range(14):
        a = 1.0 + i * 0.62
        rr = 250 - i * 13
        py = gy + 10 + i * 12
        px, pz = cx + math.sin(a) * rr, cz + math.cos(a) * rr
        part("Volcano_Plank%d" % i, (8.5, 1.0, 8.5), (px, py, pz), yaw=i * 27,
             color=(70, 56, 44), material="WoodPlanks")
        if i % 3 == 2:
            torch_wall(px, pz + 4, py, 0)

    # --- смотровая площадка на кромке + сундук ---
    part("Volcano_Summit", (16, 1.2, 16), (cx + 40, rim_y + 1.0, cz + 40),
         color=(78, 60, 46), material="WoodPlanks")
    for sx, sz in ((-7, -7), (7, -7), (-7, 7), (7, 7)):
        part("Volcano_SummitPost", (0.8, 4, 0.8), (cx + 40 + sx, rim_y + 3.0, cz + 40 + sz),
             color=(84, 64, 46), material="Wood")
    chest_marker(cx + 40, cz + 40, rim_y + 1.6, "Volcano")

    # --- пещеры у подножия (логово) ---
    for k, a in enumerate((0.9, 2.7, 4.4)):
        px = cx + math.sin(a) * 260
        pz = cz + math.cos(a) * 260
        part("Volcano_Cave", (26, 16, 20), (px, gy + 7, pz),
             yaw=math.degrees(a), color=(28, 24, 28), material="Basalt",
             cancollide=False)
        part("Volcano_CaveGlow", (4, 3, 4), (px, gy + 3, pz),
             color=(255, 120, 40), material="Neon", cancollide=False,
             light=dict(brightness=1.6, range=30, color=(255, 120, 40)))
        chest_marker(px + 4, pz, gy + 1.2, "Cave%d" % k)

    # --- горячие источники и пепельные камни ---
    for _ in range(40):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(270, 340)
        rock(cx + math.sin(a) * rr, cz + math.cos(a) * rr, gy,
             rng.uniform(0.9, 1.9), "Basalt", (54, 50, 54))


# ============================================================================
# v11: КАРСТОВЫЕ ГОРЫ — огромные «зубы» до 240 студов
# ============================================================================
def karst_shard(x, z, gy, base_w=260, h=210, snow_above=None, seed_hue=0,
                legs=9, spire_col=(112, 116, 124), canopy=True, tag=None):
    """Грандиозный карстовый массив: ярусы-основания и пучок башен-игл.
    Перепад между ярусами 2.5 студа — наверх реально залезть пешком,
    а тропа-серпантин петляет между башнями."""
    add_flat(x, z, base_w * 0.72, gy, 95.0)
    tiers = [(base_w, 16), (base_w * 0.86, 15), (base_w * 0.72, 14),
             (base_w * 0.58, 13)]
    y = gy
    for i, (w, hh) in enumerate(tiers):
        part("Karst_Base%d" % i, (w, hh, w), (x, y + hh / 2, z),
             yaw=(i * 7 + seed_hue * 11) % 90,
             color=tuple(min(255, c + i * 6) for c in spire_col), material="Rock")
        y += hh
    n_steps = max(6, int((h * 0.55) / 2.5))
    tier_h = (h * 0.55) / float(n_steps)
    w = base_w * 0.5
    for i in range(n_steps):
        part("Karst_Step%d" % i, (w, tier_h + 0.4, w), (x, y + tier_h / 2, z),
             yaw=(i * 11 + seed_hue * 7) % 180,
             color=(126, 130, 138), material="Rock")
        for k in range(3):
            a = math.pi * 2 * k / 3 + i * 0.7
            rock(x + math.sin(a) * (w * 0.46), z + math.cos(a) * (w * 0.46),
                 y + tier_h, rng.uniform(0.9, 1.6), "Rock", (108, 112, 118))
        y += tier_h
        w = max(46.0, w - base_w * 0.045)
    top_y = y
    for i in range(legs):
        a = math.pi * 2 * i / legs + seed_hue * 0.4
        rr = base_w * 0.20 if i % 2 else base_w * 0.30
        px, pz = x + math.sin(a) * rr, z + math.cos(a) * rr
        sh = rng.uniform(h * 0.30, h * 0.46)
        sw = rng.uniform(base_w * 0.10, base_w * 0.16)
        part("Karst_Spire%d" % i, (sw, sh, sw),
             (px, top_y + sh / 2, pz), yaw=rng.uniform(0, 40),
             color=tuple(min(255, c + 8) for c in spire_col), material="Rock")
        if canopy:
            part("Karst_SpireCap%d" % i, (sw * 1.15, 3.4, sw * 1.15),
                 (px, top_y + sh + 1.2, pz), shape="Ball",
                 color=(72, 108, 62), material="Grass", cancollide=False)
            tree_nice(px + rng.uniform(-8, 8), pz + rng.uniform(-8, 8), top_y + sh, 0.9)
        if snow_above is not None and top_y + sh > snow_above:
            part("Karst_Snow%d" % i, (sw * 0.95, 2.2, sw * 0.95),
                 (px, top_y + sh + 2.6, pz), shape="Ball",
                 color=(232, 238, 246), material="Snow", cancollide=False)
    part("Karst_Pinacle", (base_w * 0.13, h * 0.30, base_w * 0.13),
         (x, top_y + h * 0.15, z), yaw=18, color=(150, 154, 162), material="Rock")
    path_n = max(10, int(h / 9))
    for i in range(path_n):
        t = i / float(path_n - 1)
        a = t * math.pi * 4.2 + seed_hue
        rr = base_w * 0.62 * (1.0 - t * 0.72)
        py = gy + t * (top_y - gy + 6)
        part("Karst_Path%d" % i, (12, 1.2, 9),
             (x + math.sin(a) * rr, py, z + math.cos(a) * rr),
             yaw=math.degrees(a) + 90, color=(120, 118, 112), material="Rock")
        if i % 4 == 0:
            torch_wall(x + math.sin(a) * rr, z + math.cos(a) * rr, py + 1, 0)
    part("Karst_Summit", (18, 1.4, 18), (x, top_y + 0.8, z),
         color=(94, 76, 56), material="WoodPlanks")
    for sx, sz in ((-8, -8), (8, -8), (-8, 8), (8, 8)):
        part("Karst_SummitPost", (0.7, 5, 0.7), (x + sx, top_y + 3.2, z + sz),
             color=(84, 64, 46), material="Wood")
    chest_marker(x + 6, z + 6, top_y + 1.6, tag or ("Karst%d" % seed_hue))
    return top_y


def pit_conflict(minx, minz, maxx, maxz, pad=24.0):
    """v12: не вырезаем землю там, где уже стоят дома/города."""
    for (ox, oz, r, kind) in OCCUPIED:
        if kind != "build":
            continue
        if (minx - r - pad) < ox < (maxx + r + pad) and \
           (minz - r - pad) < oz < (maxz + r + pad):
            return True
    return False


def _pit_rect(x, z, depth, nodes, width):
    ex0, ez0 = x, z + depth * 2.0 + 6.0
    pts = [(ex0 + dx, ez0 + dz) for (dx, dz) in nodes]
    pad = width * 1.6 + 36
    return (min([x] + [px for px, _ in pts]) - pad,
            min([z] + [pz for _, pz in pts]) - pad,
            max([x] + [px for px, _ in pts]) + pad,
            max([z] + [pz for _, pz in pts]) + pad)


def reserve_cave_pit(x0, z0, x1, z1):
    if PLANNING:
        CAVE_PITS.append((float(x0), float(z0), float(x1), float(z1)))


def cave_system(name, x, z, gy, depth=20.0, nodes=((70, 0), (150, 60), (95, 150)),
                width=18, height=13, floor_mat="Slate", floor_col=(54, 52, 58),
                boss=None, tag="Cave", extra_chests=2, stair_at=None,
                cap_col=(96, 92, 84), cap_mat="Rock"):
    """ПОДЗЕМНЫЙ ДАНЖ: лестница-колодец с поверхности, залы и коридоры внизу.
    `x, z` — верх лестницы (на поверхности), `nodes` — залы (смещения от низа
    лестницы). Земля над данжем вырезается из рельефа и закрывается каменной
    шапкой, поэтому внутри реально темно и ничто не пересекается."""
    depth = min(depth, max(10.0, gy - 4.0))
    floor_y = gy - depth
    # ---- v12: если проём накрывает город/дома — отодвигаем вход в данж ----
    for attempt in range(1, 13):
        minx, minz, maxx, maxz = _pit_rect(x, z, depth, nodes, width)
        if not pit_conflict(minx, minz, maxx, maxz):
            break
        ang = attempt * 1.9
        dist = 90.0 * attempt
        x = x + math.sin(ang) * dist
        z = z + math.cos(ang) * dist
        add_flat(x, z, 70, gy, 60.0)
    # ---- начало подземелья: низ лестницы ----
    ex0, ez0 = x, z + depth * 2.0 + 6.0
    pts = [(ex0 + dx, ez0 + dz) for (dx, dz) in nodes]
    minx, minz, maxx, maxz = _pit_rect(x, z, depth, nodes, width)
    reserve_cave_pit(minx, minz, maxx, maxz)
    occupy(x, z, 26, "cave")
    add_flat((minx + maxx) / 2.0, (minz + maxz) / 2.0,
             max(maxx - minx, maxz - minz) * 0.55 + 20, gy, 70.0)

    # ---- лестница вниз: ступени по 2.0 студа, стены по бокам ----
    steps = max(6, int(depth / 2.0))
    step_len = 4.2
    total_len = steps * step_len
    for i in range(steps):
        sy_ = gy - (i + 1) * (depth / float(steps))
        part("%s_Stair%d" % (tag, i), (10, 1.2, step_len + 0.6),
             (x, sy_ + 0.6, z + 6 + i * step_len),
             color=(112, 108, 100), material="Cobblestone")
        # стены колодца
        for side in (1, -1):
            part("%s_StairWall%d_%d" % (tag, i, side), (1.6, depth + 8, step_len + 0.6),
                 (x + side * 6, sy_ + (depth + 8) / 2, z + 6 + i * step_len),
                 color=(88, 86, 82), material="Cobblestone")
            part("%s_StairWallTop%d_%d" % (tag, i, side), (1.6, 3, step_len + 0.6),
                 (x + side * 6, gy + 1.5, z + 6 + i * step_len),
                 color=(96, 92, 84), material="Cobblestone")
        if i % 3 == 1:
            torch_wall(x + 5, z + 6 + i * step_len, sy_ + 3, 0)
    # арка над лестницей
    for side in (1, -1):
        part("%s_ArchPost%d" % (tag, side), (3.2, 9, 3.2),
             (x + side * 7.4, gy + 4.5, z + 2), color=(104, 100, 92),
             material="Cobblestone")
    part("%s_ArchLintel" % tag, (19, 3, 4), (x, gy + 9.5, z + 2),
         color=(108, 104, 96), material="Cobblestone")
    part("%s_ArchRune" % tag, (6, 1.4, 0.6), (x, gy + 8.2, z + 4.1),
         color=(255, 170, 70), material="Neon", cancollide=False,
         light=dict(brightness=1.6, range=28, color=(255, 170, 70)))

    # ---- коридоры и залы внизу ----
    for i in range(len(pts) - 1):
        ax, az = pts[i]
        bx, bz = pts[i + 1]
        dx, dz = bx - ax, bz - az
        dist = math.hypot(dx, dz)
        n = max(2, int(dist // 12))
        yaw = math.degrees(math.atan2(dx, dz))
        for k in range(n + 1):
            t = k / float(n)
            px, pz = ax + dx * t, az + dz * t
            part("%s_Floor_%d_%d" % (tag, i, k), (width, 1, dist / n + 2),
                 (px, floor_y - 0.5, pz), yaw=yaw, color=floor_col, material=floor_mat)
            for side in (1, -1):
                wx, wz = l2w(px, pz, yaw, side * width / 2.0, 0)
                part("%s_Wall_%d_%d" % (tag, i, k), (1.6, height, dist / n + 2),
                     (wx, floor_y + height / 2 - 1, wz), yaw=yaw,
                     color=tuple(c - 8 for c in floor_col), material=floor_mat)
            part("%s_Ceil_%d_%d" % (tag, i, k), (width + 4, 2, dist / n + 2),
                 (px, floor_y + height - 1, pz), yaw=yaw,
                 color=tuple(c - 16 for c in floor_col), material=floor_mat)
            if k % 4 == 0:
                torch_wall(px, pz, floor_y + 4, yaw)
    # нижняя площадка у лестницы
    part("%s_Landing" % tag, (width + 6, 1, 18), (ex0, floor_y - 0.5, ez0 - 10),
         color=floor_col, material=floor_mat)
    for side in (1, -1):
        part("%s_LandingWall%d" % (tag, side), (1.6, height, 18),
             (ex0 + side * (width + 6) / 2.0, floor_y + height / 2 - 1, ez0 - 10),
             color=tuple(c - 8 for c in floor_col), material=floor_mat)
    part("%s_LandingCeil" % tag, (width + 10, 2, 18),
         (ex0, floor_y + height - 1, ez0 - 10),
         color=tuple(c - 16 for c in floor_col), material=floor_mat)
    for i, (px, pz) in enumerate(pts):
        last = (i == len(pts) - 1)
        r = width * (2.1 if last else 1.4)
        part("%s_Hall_%d" % (tag, i), (r * 2, 1, r * 2), (px, floor_y - 0.5, pz),
             color=floor_col, material=floor_mat)
        for k in range(10):
            a = math.pi * 2 * k / 10
            vx, vz = math.sin(a), math.cos(a)
            blocked = False
            if i + 1 < len(pts):
                nx, nz = pts[i + 1][0] - px, pts[i + 1][1] - pz
                nl = max(1.0, math.hypot(nx, nz))
                if (vx * nx + vz * nz) / nl > 0.72:
                    blocked = True
            if i > 0:
                pvx, pvz = px - pts[i - 1][0], pz - pts[i - 1][1]
                pl = max(1.0, math.hypot(pvx, pvz))
                if (vx * pvx + vz * pvz) / pl > 0.72:
                    blocked = True
            if blocked:
                continue
            part("%s_HallWall_%d_%d" % (tag, i, k), (r * 0.62, height + 4, 3),
                 (px + vx * r, floor_y + height / 2, pz + vz * r),
                 yaw=math.degrees(a), color=tuple(c - 6 for c in floor_col),
                 material=floor_mat)
        part("%s_HallCeil_%d" % (tag, i), (r * 2.3, 3, r * 2.3),
             (px, floor_y + height + 2, pz), color=tuple(c - 18 for c in floor_col),
             material=floor_mat)
        if i % 2 == 0:
            crystal(px + r * 0.5, pz - r * 0.4, floor_y, 1.1,
                    "cyan" if i % 4 == 0 else "violet")
        if last and boss:
            boss_spawn(boss, px, pz, floor_y + 0.5)
            arena_trigger(boss, px, pz, floor_y + 0.5, r=r * 1.4)
            part("%s_BossDais" % tag, (16, 1.2, 16), (px, floor_y + 0.2, pz),
                 color=(70, 60, 76), material="Marble")
            for k in range(6):
                a = math.pi * 2 * k / 6
                brazier(px + math.sin(a) * 12, pz + math.cos(a) * 12, floor_y + 1)
            chest_marker(px + 9, pz + 9, floor_y + 0.6, tag + "Boss")
    for k in range(extra_chests):
        px, pz = pts[(k + 1) % len(pts)]
        chest_marker(px - 7 - k * 3, pz + 7, floor_y + 0.4, "%sLoot%d" % (tag, k))

    # ---- каменная шапка над данжем (вместо вырезанной земли) ----
    # шапка ставится «рамкой»: над лестницей оставлен проём, иначе не войти
    cap_col = cap_col
    cap_mat = cap_mat
    ox0, ox1 = x - 9.5, x + 9.5
    oz0, oz1 = z - 10, z + depth * 2.1 + 14
    slab("%s_CapL" % tag, minx, minz, ox0, maxz, gy + 2.8, gy,
         cap_col, cap_mat)
    slab("%s_CapR" % tag, ox1, minz, maxx, maxz, gy + 2.8, gy,
         cap_col, cap_mat)
    slab("%s_CapB" % tag, ox0, minz, ox1, oz0, gy + 2.8, gy,
         cap_col, cap_mat)
    slab("%s_CapF" % tag, ox0, oz1, ox1, maxz, gy + 2.8, gy,
         cap_col, cap_mat)
    # приподнятый каменный горб над залами (чтобы не выглядело плоско)
    hx = (minx + maxx) / 2.0 + (ox1 - ox0)
    hz = (oz1 + maxz) / 2.0
    part("%s_CapTop" % tag, ((maxx - ox1) * 0.9, 4.4, (maxz - oz1) * 0.9),
         (hx, gy + 4.6, hz), yaw=8,
         color=tuple(min(255, c + 8) for c in cap_col), material=cap_mat)
    for _ in range(16):
        rock(hx + rng.uniform(-(maxx - ox1) * 0.4, (maxx - ox1) * 0.4),
             hz + rng.uniform(-(maxz - oz1) * 0.4, (maxz - oz1) * 0.4),
             gy + 2.8, rng.uniform(0.8, 1.8), cap_mat, (112, 108, 100))
    for _ in range(10):
        dead_tree(hx + rng.uniform(-(maxx - ox1) * 0.4, (maxx - ox1) * 0.4),
                  hz + rng.uniform(-(maxz - oz1) * 0.4, (maxz - oz1) * 0.4),
                  gy + 2.8, rng.uniform(0.8, 1.2))
    # бортик вокруг проёма, чтобы никто не свалился случайно в темноту
    for (bx, bz, bw, bd) in ((0, oz0, (ox1 - ox0) + 4, 2), (0, oz1, (ox1 - ox0) + 4, 2),
                             (-(ox1 - ox0) / 2.0, (oz0 + oz1) / 2.0, 2, oz1 - oz0),
                             ((ox1 - ox0) / 2.0, (oz0 + oz1) / 2.0, 2, oz1 - oz0)):
        part("%s_PitRim" % tag, (bw, 1.6, bd), (x + bx, gy + 3.4, bz),
             color=cap_col, material=cap_mat, cancollide=False)
    signpost(x + 12, z - 4, gy, 0, name + "\nвход в подземелье ↓")
    return pts


# ------------------------- подводный мир -----------------------------------

def kelp(x, z, floor_y=-6.0):
    h = rng.uniform(4, 9)
    part("Kelp", (0.4, h, 0.4), (x, floor_y + h / 2, z),
         yaw=rng.uniform(0, 90), roll=rng.uniform(-6, 6), color=(40, 96, 62),
         material="Grass", cancollide=False)
    part("Kelp_Leaf", (1.6, 0.3, 0.5), (x, floor_y + h, z), yaw=rng.uniform(0, 90),
         color=(52, 110, 70), material="Grass", cancollide=False)


def sunken_ruins(x, z):
    """Затонувшие руины на мелководье."""
    disc("Sunken_Floor", x, z, -5.2, 42, 1.4, (150, 140, 118), "Sand")
    for i in range(5):
        a = math.pi * 2 * i / 5
        h = rng.uniform(4, 9)
        v_cyl("Sunken_Column", x + math.sin(a) * 22, z + math.cos(a) * 22, -6, h,
              3.2, (160, 156, 146), "Marble", tilt_pitch=rng.uniform(-16, 16))
    part("Sunken_Arch", (16, 3, 4), (x + 8, -3.5, z - 6), yaw=30, pitch=64,
         color=(160, 156, 146), material="Marble")
    crystal(x - 12, z + 10, -6, 1.0, "cyan")


def sea_serpent_bones(x, z):
    disc("SerpBones_Floor", x, z, -5.2, 34, 1.2, (128, 124, 106), "Sand")
    for i in range(6):
        t = i / 5.0
        part("SerpRib", (2.2, 10 - abs(2.5 - t * 5), 1.0),
             (x - 26 + t * 52, -4.5, z + math.sin(t * 6) * 4), roll=12,
             color=(210, 204, 186), material="SmoothPlastic", cancollide=False)
    part("SerpSkull", (5, 3.4, 3.4), (x + 32, -4.2, z), shape="Ball",
         color=(218, 212, 192), material="SmoothPlastic", cancollide=False)


def sunken_boat(x, z):
    part("SunkenBoat", (12, 3, 5), (x, -4.4, z), yaw=40, roll=18,
         color=(76, 58, 42), material="Wood", cancollide=False)
    part("SunkenBoat_Mast", (9, 0.8, 0.8), (x + 3, -2.2, z + 2), yaw=40, pitch=65,
         color=(66, 48, 34), material="Wood", cancollide=False)


def sea_monster_marker(mid, x, z):
    part("SeaMonster_%d" % mid, (6, 6, 6), (x, -28, z), color=(160, 60, 255),
         material="Neon", transparency=0.35, cancollide=False)


# ------------------------- ледяная гробница (данж) --------------------------
def ice_spike_cluster(x, z, gy):
    gy = sy(x, z, gy)
    """Кластер ледяных шипов (как глетчеры на белых равнинах)."""
    for i in range(rng.randint(3, 5)):
        h = rng.uniform(8, 18)
        dx, dz = l2w(x, z, rng.uniform(0, 360), rng.uniform(-4, 4),
                     rng.uniform(-4, 4))
        part("IceSpike", (2.4, h, 2.4), (dx, gy + h / 2, dz),
             yaw=rng.uniform(0, 90), pitch=rng.uniform(-8, 8),
             roll=rng.uniform(-8, 8), color=(172, 206, 236), material="Glacier")


def townhouse_row(name, x, z, gy, yaw=0.0, units=4, uw=11, ud=9, uh=9):
    """Ряд примыкающих друг к другу городских домов — плотная застройка."""
    for i in range(units):
        off = (i - (units - 1) / 2.0) * uw
        ux, uz = l2w(x, z, yaw, off, 0)
        hh = uh + rng.choice((0, 1, 2))
        house("%s_U%d" % (name, i), ux, uz, gy, uw - 0.6, ud, hh,
              yaw=yaw + rng.choice((0, 180)),
              wall=rng.choice([(150, 132, 104), (146, 126, 100), (140, 128, 106)]),
              roof=rng.choice([(84, 58, 44), (90, 62, 46), (76, 56, 42)]),
              chimney=(i % 2 == 0))


def outpost(name, x, z, gy, tag):
    """Каменный форт-пост: стены с воротами, башня, костёр, палатка, сундук."""
    stone, dark = (128, 124, 116), (108, 104, 98)
    W2 = 23
    part(name + "_WallN", (W2 * 2, 7, 2.5), (x, gy + 3.5, z - W2), color=stone,
         material="Cobblestone")
    part(name + "_WallE", (2.5, 7, W2 * 2), (x + W2, gy + 3.5, z), color=stone,
         material="Cobblestone")
    part(name + "_WallW", (2.5, 7, W2 * 2), (x - W2, gy + 3.5, z), color=stone,
         material="Cobblestone")
    part(name + "_WallS1", (W2 - 7, 7, 2.5), (x - (W2 + 7) / 2.0, gy + 3.5, z + W2),
         color=stone, material="Cobblestone")
    part(name + "_WallS2", (W2 - 7, 7, 2.5), (x + (W2 + 7) / 2.0, gy + 3.5, z + W2),
         color=stone, material="Cobblestone")
    for sx in (-W2, W2):
        for sz in (-W2, W2):
            part(name + "_Pillar", (4.5, 10.5, 4.5), (x + sx, gy + 5.25, z + sz),
                 color=dark, material="Cobblestone")
            torch_wall(x + sx, z + sz + (5.8 if sz > 0 else -5.8), gy + 10.5, 0)
    # башня в дальнем углу с лестницей-фермой
    tx, tz = x - W2 + 7, z - W2 + 7
    v_cyl(name + "_Tower", tx, tz, gy, 17, 8.5, stone, "Cobblestone")
    part(name + "_TowerDeck", (10, 1, 10), (tx, gy + 17.5, tz), color=(104, 80, 56),
         material="WoodPlanks")
    truss(name + "_TowerLadder", (2, 17, 2), (tx + 6.5, gy + 8.5, tz))
    chest_marker(tx, tz + 2.5, gy + 18, "Outpost" + tag)
    campfire(x + 2, z + 2, gy)
    tent(x + 9, z - 8, gy, yaw=25, color=(120, 96, 70))
    crate_stack(x - 9, z - 7, gy)
    part(name + "_Log", (6, 1.1, 1.1), (x - 4, gy + 0.55, z + 7), yaw=18,
         color=(84, 64, 46), material="Wood")
    banner(x + 10, z + W2 - 2, gy, 0)


def ancient_tree(x, z, gy, s=2.3):
    """ДРЕВНЕЕ гигантское дерево-помпон (~40 студов) — достопримечательность."""
    tree_nice(x, z, gy, s)
    part("Tree_RootA", (4 * s, 2.2, 2.2), (x + 2 * s, gy + 1.1, z),
         yaw=30, color=(80, 60, 44), material="Wood", cancollide=False)
    part("Tree_RootB", (4 * s, 2.2, 2.2), (x - 2 * s, gy + 1.1, z + 1),
         yaw=100, color=(80, 60, 44), material="Wood", cancollide=False)


def ice_tomb(cx, cz, gy, yaw=0.0):
    occupy(cx, cz, 50)
    """Данж-подземелье: ледяная усыпальница с коридором и залом."""
    W, D, H = 34, 48, 14
    ice, trim = (168, 196, 222), (140, 172, 205)
    part("IceTomb_Floor", (W, 1, D), (cx, gy + 0.5, cz), color=(150, 182, 210),
         material="Glacier")
    # стены зала (задняя, боковые, передняя с дверью)
    part("IceTomb_WallBack", (W, H, 2), (cx, gy + H / 2 + 1, cz - D / 2 + 1),
         yaw=yaw, color=ice, material="Glacier")
    for side in (1, -1):
        wx, wz = l2w(cx, cz, yaw, side * (W / 2 - 1), 0)
        part("IceTomb_WallSide", (2, H, D), (wx, gy + H / 2 + 1, wz), yaw=yaw,
             color=ice, material="Glacier")
    for side in (1, -1):
        fx, fz = l2w(cx, cz, yaw, side * (W / 4 + 1.5), D / 2 - 1)
        part("IceTomb_WallFront", (W / 2 - 7, H, 2), (fx, gy + H / 2 + 1, fz),
             yaw=yaw, color=ice, material="Glacier")
    fx, fz = l2w(cx, cz, yaw, 0, D / 2 - 1)
    part("IceTomb_Lintel", (8, H - 7, 2), (fx, gy + 7 + (H - 7) / 2, fz), yaw=yaw,
         color=ice, material="Glacier")
    # крыша
    part("IceTomb_RoofA", (W + 2, 5, D / 2 + 1),
         (cx, gy + H + 1 + 2.5, cz - D / 4), yaw=yaw, color=trim, material="Glacier",
         cls="WedgePart")
    part("IceTomb_RoofB", (W + 2, 5, D / 2 + 1),
         (cx, gy + H + 1 + 2.5, cz + D / 4), yaw=yaw + 180, color=trim,
         material="Glacier", cls="WedgePart")
    # интерьер: колонны, саркофаг, кристаллы
    for sx in (-9, 9):
        for sz in (-12, 12):
            part("IceTomb_Pillar", (3, H - 2, 3), (cx + sx, gy + 1 + (H - 2) / 2,
                                                   cz + sz), color=trim,
                 material="Glacier")
    part("IceTomb_Sarcophagus", (7, 2.6, 3.4), (cx, gy + 2.3, cz - 4),
         color=(190, 214, 235), material="Glacier")
    crystal(cx - 11, cz + 16, gy + 1, 1.1, "cyan")
    crystal(cx + 11, cz - 16, gy + 1, 1.1, "cyan")
    torch_wall(cx - 5, cz + D / 2 - 3, gy + 1, 0)
    torch_wall(cx + 5, cz + D / 2 - 3, gy + 1, 0)
    boss_spawn("FrostWraith", cx, cz, gy + 1)
    arena_trigger("FrostWraith", cx, cz, gy + 1, r=48)
    chest_marker(cx, cz + 16, gy + 1, "FrostDen")


# ------------------------- острова-спутники --------------------------------
def islet(x, z, bridge_from=None, tag="A"):
    disc("Islet%s_Sand" % tag, x, z, 3.6, 52, 6, (196, 180, 140), "Sand")
    part("Islet%s_Rock" % tag, (36, 12, 30), (x, 7, z), yaw=rng.uniform(0, 90),
         color=(96, 98, 104), material="Rock")
    palm_dead(x + 14, z - 10, 3.6, 1.1)
    palm_dead(x - 12, z + 14, 3.6, 0.9)
    chest_marker(x, z + 4, 3.6, "Islet" + tag)
    crystal(x - 16, z - 12, 3.6, 1.0, rng.choice(["cyan", "violet"]))
    if bridge_from:
        rope_bridge(bridge_from[0], bridge_from[1], x, z, 8.0)


# ----------------------------------------------------------------------------
# Сборка мира
# ----------------------------------------------------------------------------
BASE_TOP = 8.0
SAND_TOP = 4.0

BASE_RECTS = [
    (-700, -700, 700, 700),
    (-2300, -900, -300, 900),
    (-2500, -2500, -500, -700),
    (-800, -2500, 1000, -1100),
    (600, -900, 2300, 1000),
    (700, 800, 2400, 2300),
    (-900, 800, 900, 2300),
    (-2400, 700, -700, 2300),
    # перешейки через проливы (сухопутные маршруты)
    (-1700, -1040, -1100, -690),   # Глумвуд -> Морозные Пики
    (-100, -1160, 100, -690),      # Центр -> Пепельные Пустоши
]


def build_sea(parent):
    """Море. Плиты нарезаны и в местах подземелий пропущены — иначе вода
    проходит сквозь залы данжей, которые уходят ниже уровня моря."""
    folder("Sea")
    TILE = 512.0
    n = int(3072 / TILE)
    for i in range(-n, n):
        for j in range(-n, n):
            cx, cz = i * TILE + TILE / 2, j * TILE + TILE / 2
            if in_cave_pit(cx, cz):
                continue
            part("Sea", (TILE, 3, TILE), (cx, -1.5, cz),
                 color=(24, 52, 66), material="Water", transparency=0.1,
                 cancollide=False)
            part("DeepWater", (TILE, 26, TILE), (cx, -17, cz),
                 color=(14, 34, 46), material="Water", transparency=0.4,
                 cancollide=False)
            part("Abyss", (TILE, 3, TILE), (cx, -35.5, cz),
                 color=(10, 14, 18), material="Basalt")
    endfolder()


def build_continent(parent):
    """v9: рельефный материк. Сначала задаём "плоские пятна" под деревни,
    лагеря, арены и дороги, затем генерируем сетку земли с холмами."""
    folder("Landmass")

    # ---------------- плоскостные зоны (ровно, чтобы дома не висели) ----------
    # Пепельная Пристань
    add_flat_rect(-340, -240, 340, 440, 12.0, 70.0)
    # Глумвуд: Тенегрив, Сердце-Древо, лагерь разбойников
    add_flat(-1250, 330, 105, 14.0, 85.0)
    add_flat(-1500, 50, 70, 14.0, 90.0)
    add_flat(-1000, 320, 72, 14.0, 80.0)
    # Костяные Поля: Хутор, кладбище, крипта, лагерь культа, врата
    add_flat(-520, 1020, 95, 12.0, 80.0)
    add_flat(0, 1550, 190, 12.0, 85.0)
    add_flat(300, 1850, 90, 12.0, 85.0)
    add_flat(300, 1200, 85, 12.0, 80.0)
    add_flat(0, 700, 80, 8.0, 90.0)
    # Затонувший Берег: порт, слобода, маяк, руины
    add_flat(1750, 2600, 230, 4.0, 90.0)
    add_flat(1350, 2180, 130, 8.4, 80.0)
    add_flat(2150, 2100, 90, 8.4, 80.0)
    add_flat(1600, 1450, 140, 8.4, 90.0)
    # Морозные Пики: обитель, гробница, лагерь охотников
    add_flat(-1750, -1150, 110, 20.0, 85.0)
    add_flat(-2200, -1150, 100, 20.0, 80.0)
    add_flat(-1350, -1250, 85, 20.0, 80.0)
    # Пустоши: лагерь мародёров, руины крепости
    add_flat(520, -1380, 85, 16.0, 80.0)
    add_flat(250, -1850, 95, 16.0, 80.0)
    # Топи: рыбацкий стан
    add_flat(1050, 550, 90, 12.0, 80.0)

    # ---- v11: площадки под новые города, данжи и достопримечательности ----
    add_flat(-1950, -620, 235, 14.0, 95.0)    # Дуплино
    add_flat(-900, -380, 300, 14.0, 100.0)    # Эльдервуд
    add_flat(150, 2500, 270, 12.0, 100.0)     # Заречье
    add_flat(-560, 2600, 230, 12.0, 95.0)     # Красный каньон
    add_flat(2600, 830, 320, 16.0, 110.0)     # Арканум
    add_flat(2700, 1400, 260, 14.0, 100.0)    # рисовые террасы
    add_flat(-3150, 2600, 320, 26.0, 110.0)   # Камнегорск
    add_flat(-2700, 3000, 260, 26.0, 100.0)   # карст A
    add_flat(-3450, 1700, 240, 26.0, 100.0)   # карст B
    add_flat(-2550, 2000, 240, 26.0, 100.0)   # Пик Ветров
    add_flat(1650, -3300, 300, 14.0, 100.0)   # Свободная Гавань
    add_flat(2100, 3300, 280, 12.0, 100.0)    # Пальмовый Берег
    add_flat(-500, -1900, 200, 16.0, 95.0)    # Аш-Каран
    add_flat(1620, -200, 210, 12.0, 95.0)     # Затонувший Храм
    add_flat(-2050, -1750, 230, 20.0, 95.0)   # Логово Змея

    # ---------------- сетка земли --------------------------------------------
    total = terrain_grid("Ground", -3780, -3780, 3760, 3760, cell=68.0, max_step=2.5)
    print("  [рельеф] тайлов земли: %d" % total)
    worst, lo, hi = terrain_check(-3780, -3780, 3760, 3760, cell=68.0)
    print("  [рельеф] макс. перепад %.2f, высоты %.1f..%.1f" % (worst, lo, hi))

    # пляжи по кромке материка
    beach_ring()

    # ---------------- отмели, подводные руины, валуны -------------------------
    for _ in range(210):
        x = rng.uniform(-2600, 2600)
        z = rng.uniform(-2600, 2600)
        if point_in_poly(x, z) or poly_edge_dist(x, z) > 320:
            continue
        part("Shelf_Floor", (120, 2, 120), (x, -6.0, z), color=(168, 156, 126),
             material="Sand")
        part("Shelf_Water", (120, 7.2, 120), (x, -2.9, z), color=(40, 90, 105),
             material="Water", transparency=0.3, cancollide=False)

    kelp_n = 0
    for _ in range(420):
        x = rng.uniform(-2600, 2600)
        z = rng.uniform(-2600, 2600)
        if point_in_poly(x, z) or poly_edge_dist(x, z) > 260:
            continue
        if kelp_n < 220:
            for _ in range(rng.randint(1, 3)):
                kelp(x, z)
            kelp_n += 1

    sunken_ruins(1750, 2620)
    sea_serpent_bones(1200, 2780)
    sunken_boat(2350, 2520)

    # валуны на берегу
    for _ in range(140):
        x = rng.uniform(-2600, 2600)
        z = rng.uniform(-2600, 2600)
        if not point_in_poly(x, z):
            continue
        d = poly_edge_dist(x, z)
        if 12 < d < 150:
            rock(x, z, height_at(x, z) - 0.4, rng.uniform(0.8, 1.4), "Rock",
                 (110, 112, 118))
    endfolder()


def beach_ring():
    """Песчаная кромка ВДОЛЬ НАСТОЯЩЕГО берега материка.
    v12: раньше песок сыпался кольцом по радиусу и резал карту поперёк —
    теперь берём точки у самой границы полигона (poly_edge_dist ≈ 0..60)."""
    placed = 0
    step = 46.0
    for i in range(-3760, 3760, int(step)):
        for j in range(-3760, 3760, int(step)):
            if not point_in_poly(i, j):
                continue
            ed = poly_edge_dist(i, j)
            if not (6.0 < ed < 52.0):
                continue
            if is_free(i, j, 4) is False and OCCUPIED:
                pass
            h = height_at(i, j)
            if h < -1.0:
                continue
            part("Beach", (56, 5, 56), (i, h - 2.8, j),
                 color=(198, 182, 142), material="Sand")
            placed += 1
            if rng.random() < 0.10:
                rock(i + rng.uniform(-20, 20), j + rng.uniform(-20, 20), h,
                     rng.uniform(0.7, 1.2), "Rock", (108, 108, 114))
    return placed


def road(x0, z0, x1, z1, top_y, width=9, color=(98, 94, 90), mat="Cobblestone"):
    """Дорога: земля вокруг выравнивается под полотно, сегменты идут по рельефу."""
    occupy((x0 + x1) / 2.0, (z0 + z1) / 2.0,
           math.hypot(x1 - x0, z1 - z0) / 2.0 + width, "road")
    dx, dz = x1 - x0, z1 - z0
    dist = math.hypot(dx, dz)
    n = max(1, int(dist // 14))
    yaw = math.degrees(math.atan2(dx, dz))
    # заранее выравниваем полосу земли под дорогой
    steps = max(2, int(dist // 60))
    for i in range(steps + 1):
        t = i / float(steps)
        add_flat(x0 + dx * t, z0 + dz * t, width * 2.4, top_y, 55.0)
    prev = None
    for i in range(n + 1):
        t = i / float(n)
        px, pz = x0 + dx * t, z0 + dz * t
        y = height_at(px, pz)
        if prev is not None:
            y = prev + max(-2.2, min(2.2, y - prev))
        prev = y
        part("Road", (width, 0.5, 14), (px, y + 0.25, pz),
             yaw=yaw, color=color, material=mat)


def ramp(cx, cz, base_y, rise, length, width, direction):
    """Пологий подъём ступенями (крутые WedgePart больше не используем —
    земля v9 проходима сама по себе, а пандус нужен только как тропа)."""
    yaw = {"+Z": 0, "-Z": 180, "+X": 90, "-X": -90}[direction]
    n = max(3, int(rise / 2.2))
    for i in range(n):
        t = i / float(n)
        part("RampStep", (width, 1.0, length / n + 1.0),
             (cx, base_y + (i + 1) * rise / n, cz), yaw=yaw,
             color=(96, 92, 88), material="Cobblestone")


# ------------------------- ЗОНЫ --------------------------------------------


# ============================================================================
# v9: ДЕТАЛИЗАЦИЯ — рельефная растительность, цветы, корабли, быт
# ============================================================================
def forest_fill(name, x0, z0, x1, z1, density=0.55, cell=150.0,
                trees=("tree_nice",), scale=(0.8, 1.35), bushes=True,
                grass=True, rocks=True, flowers=None, skip=()):
    """Заполняет область растительностью, сажая всё на рельеф."""
    funcs = {"tree_nice": tree_nice, "tree_gloom": tree_gloom, "pine": pine,
             "dead_tree": dead_tree, "palm_dead": palm_dead}
    x = x0
    while x <= x1:
        z = z0
        while z <= z1:
            if point_in_poly(x, z) and rng.random() < density:
                skip_here = False
                for (sx, sz, sr) in skip:
                    if math.hypot(x - sx, z - sz) < sr:
                        skip_here = True
                        break
                if skip_here or not is_free(x, z, 14):
                    skip_here = True
                if not skip_here:
                    h = height_at(x, z)
                    if h > -0.5:
                        fn = funcs[rng.choice(trees)]
                        fn(x + rng.uniform(-30, 30), z + rng.uniform(-30, 30), h,
                           rng.uniform(*scale))
                        if bushes and rng.random() < 0.6:
                            bush(x + rng.uniform(-40, 40), z + rng.uniform(-40, 40),
                                 h, rng.uniform(0.7, 1.3))
                        if grass and rng.random() < 0.8:
                            for _ in range(rng.randint(1, 4)):
                                grass_tuft(x + rng.uniform(-45, 45),
                                           z + rng.uniform(-45, 45), h)
                        if rocks and rng.random() < 0.18:
                            rock(x + rng.uniform(-40, 40), z + rng.uniform(-40, 40),
                                 h, rng.uniform(0.6, 1.3))
                        if flowers and rng.random() < flowers:
                            for _ in range(rng.randint(1, 3)):
                                flower(x + rng.uniform(-45, 45),
                                       z + rng.uniform(-45, 45), h)
            z += cell
        x += cell


def ship(cx, cz, gy, yaw=0.0, size=1.0, sails=True, col=(96, 74, 52)):
    """Парусник: корпус, мачты, паруса, носовая фигура."""
    L, W, H = 64 * size, 20 * size, 12 * size
    part("Ship_Hull", (W, H, L), (cx, gy + H / 2 + 1, cz), yaw=yaw,
         color=col, material="WoodPlanks")
    # заострённый нос
    nx, nz = l2w(cx, cz, yaw, 0, L / 2 + 5 * size)
    part("Ship_Bow", (W * 0.62, H, 14 * size), (nx, gy + H / 2 + 1, nz), yaw=yaw,
         color=col, material="WoodPlanks", cls="Part")
    # палуба
    part("Ship_Deck", (W - 3, 0.8, L - 6), (cx, gy + H + 1.4, cz), yaw=yaw,
         color=(132, 104, 74), material="WoodPlanks")
    # мачты и паруса
    for i, off in enumerate((-L * 0.28, 0.0, L * 0.28)):
        mx, mz = l2w(cx, cz, yaw, 0, off)
        mh = (30 + i * 6) * size
        part("Ship_Mast", (1.4, mh, 1.4), (mx, gy + H + mh / 2, mz), color=(78, 58, 40),
             material="Wood")
        if sails:
            sx, sz = l2w(cx, cz, yaw, 0, off)
            part("Ship_Sail", (1.0, mh * 0.62, W * 1.5), (sx, gy + H + mh * 0.58, sz),
                 yaw=yaw, color=(228, 222, 206), material="Fabric", cancollide=False)
        part("Ship_Yard", (2.0, 1.0, W * 1.7), (mx, gy + H + mh * 0.86, mz), yaw=yaw,
             color=(88, 66, 46), material="Wood", cancollide=False)
    # кормовая надстройка и штурвал
    ax, az = l2w(cx, cz, yaw, 0, -L * 0.42)
    part("Ship_Cabin", (W * 0.8, 7 * size, 14 * size), (ax, gy + H + 4.5, az), yaw=yaw,
         color=(110, 84, 58), material="WoodPlanks")
    # флаг
    fx, fz = l2w(cx, cz, yaw, 0, L * 0.3)
    part("Ship_Flag", (0.3, 4, 6), (fx, gy + H + 34 * size, fz), yaw=yaw,
         color=(150, 40, 40), material="Fabric", cancollide=False)


def dock(name, x, z, gy, length=90, width=12, yaw=0.0):
    """Причал на сваях с фонарями и бочками."""
    for i in range(int(length // 12) + 1):
        px, pz = l2w(x, z, yaw, 0, -i * 12)
        part(name + "_Plank", (width, 0.8, 13), (px, gy + 3.2, pz), yaw=yaw,
             color=(112, 88, 62), material="WoodPlanks")
        for sx in (-1, 1):
            bx, bz = l2w(px, pz, yaw, sx * (width / 2 - 1), 0)
            part(name + "_Post", (1.0, 9, 1.0), (bx, gy - 1.2, bz),
                 color=(84, 66, 46), material="Wood")
        if i % 3 == 0:
            lx, lz = l2w(px, pz, yaw, width / 2 - 1.5, 0)
            part(name + "_Lantern", (1.2, 1.6, 1.2), (lx, gy + 4.6, lz),
                 color=(255, 200, 110), material="Neon", cancollide=False,
                 light=dict(brightness=1.4, range=26, color=(255, 200, 110)))
        if rng.random() < 0.3:
            bx, bz = l2w(px, pz, yaw, rng.uniform(-3, 3), rng.uniform(-3, 3))
            part(name + "_Barrel", (2.2, 2.6, 2.2), (bx, gy + 4.9, bz),
                 shape="Cylinder", color=(108, 82, 56), material="WoodPlanks")


def market_square(x, z, gy, n=6, radius=34):
    """Рыночная площадь: лавки по кругу, флажки, бочки, ящики."""
    for i in range(n):
        a = math.pi * 2 * i / n
        sx = x + math.sin(a) * radius
        sz = z + math.cos(a) * radius
        stall(sx, sz, gy + 0.55, yaw=math.degrees(a) + 90)
        bx, bz = l2w(sx, sz, math.degrees(a) + 90, 0, 8)
        part("Market_Crate", (2.0, 2.0, 2.0), (bx, gy + 1.0, bz),
             yaw=rng.uniform(0, 90), color=(114, 88, 58), material="WoodPlanks")
    # гирлянда флажков над площадью
    for i in range(14):
        a = math.pi * 2 * i / 14
        fx, fz = x + math.sin(a) * (radius - 6), z + math.cos(a) * (radius - 6)
        part("Market_Flag", (1.4, 1.0, 0.2), (fx, gy + 8.5, fz), yaw=math.degrees(a),
             color=rng.choice([(200, 70, 60), (240, 200, 80), (90, 150, 210),
                               (120, 200, 120)]),
             material="Fabric", cancollide=False)
    well(x, z, gy)



def build_village(parent):
    folder("EmberfallVillage")
    GY = 12.0
    slab("VillageGround", -330, -230, 330, 430, GY, 6, (94, 122, 64), "Grass")
    plateau_skirt("VillageGround", -330, -230, 330, 430, GY, (94, 122, 64))

    # стена по кругу r=300, центр (0,100)
    N = 26
    for k in range(N):
        a = 2 * math.pi * k / N
        if angle_gap(a, 0) < 0.24 or angle_gap(a, math.pi) < 0.24:
            continue
        px, pz = 300 * math.sin(a), 100 + 300 * math.cos(a)
        part("Wall", (72, 14, 6), (px, GY + 7, pz), yaw=math.degrees(a),
             color=(100, 98, 96), material="Cobblestone")
        for mo in (-20, 0, 20):
            mx, mz = l2w(px, pz, math.degrees(a), mo, 0)
            part("Wall_Merlon", (3, 2.6, 3), (mx, GY + 15.3, mz),
                 yaw=math.degrees(a), color=(100, 98, 96), material="Cobblestone",
                 cancollide=False)

    # ворота (север z=-200, юг z=400)
    for gz, road_yaw in [(-200, 0), (400, 180)]:
        for sx in (-11, 11):
            part("GatePillar", (6, 18, 6), (sx, GY + 9, gz), color=(112, 110, 106),
                 material="Cobblestone")
        part("GateLintel", (30, 4, 8), (0, GY + 20, gz),
             color=(112, 110, 106), material="Cobblestone")
        part("GateTorch", (1.2, 1.2, 1.2), (0, GY + 18, gz), color=(255, 150, 60),
             material="Neon", cancollide=False,
             light=dict(brightness=1.8, range=34, color=(255, 150, 60)))
    # башни фланкируют ворота: лезь по ферме на площадку
    for gx2, gz2 in [(-26, -200), (26, -200), (-26, 400), (26, 400)]:
        v_cyl("GateTower", gx2, gz2, GY, 24, 10, (108, 106, 102), "Cobblestone")
        part("GateTower_Deck", (12, 1, 12), (gx2, GY + 24.5, gz2),
             color=(100, 98, 94), material="Cobblestone")
        truss("GateTower_Ladder", (2, 24, 2), (gx2 + 7.2, GY + 12, gz2))
        part("GateTower_Roof", (13, 3, 13), (gx2, GY + 27, gz2), shape="Ball",
             color=(96, 52, 44), material="Fabric", cancollide=False)
        torch_wall(gx2, gz2 + 5.5, GY + 25, 0)

    # площадь и центр
    disc("Plaza", 0, 110, GY + 0.55, 55, 0.8, (110, 106, 100), "Cobblestone")
    well(0, 110, GY + 0.55)

    # постройки
    chapel(-150, 30, GY, yaw=8)
    tavern(135, 225, GY, yaw=-10)
    smithy(-95, -85, GY, yaw=0)
    house("HouseA", 65, -70, GY, 14, 11, 8, yaw=14)
    house("HouseB", -45, 240, GY, 13, 10, 8, yaw=-12)
    house("HouseC", 185, 120, GY, 14, 11, 8, yaw=96)
    house("HouseD", -195, 150, GY, 13, 10, 8, yaw=-85)
    house("HouseE", 55, 340, GY, 14, 11, 8, yaw=6)
    house("HouseF", -120, 330, GY, 12, 10, 8, yaw=-6)
    house("HouseG", 230, 40, GY, 13, 10, 8, yaw=-100)
    house("HouseH", -230, 260, GY, 13, 10, 8, yaw=85)
    house("HouseI", 60, -170, GY, 12, 10, 8, yaw=170)
    citadel(150, -60, GY)
    signpost(96, -66, GY, -90, "Цитадель Лорд-Магистра ↑")
    # кварталы таунхаусов — плотная городская застройка
    townhouse_row("TownRowA", -26, -110, GY, yaw=90, units=4)
    townhouse_row("TownRowB", 40, 158, GY, yaw=0, units=4)
    market_square(0, 165, GY, n=7, radius=40)
    stall(45, 58, GY + 0.55, yaw=10)
    stall(-70, -30, GY + 0.55, yaw=70)
    stall(80, 250, GY + 0.55, yaw=250)
    stall(-48, 60, GY + 0.55, yaw=-15)
    stall(38, 168, GY + 0.55, yaw=190)

    # свет и деревья
    for (lx, lz) in [(25, 35), (-25, 35), (25, 185), (-25, 185), (90, 110),
                     (-90, 110), (0, -90), (0, 270), (150, 220), (-160, 60)]:
        lamppost(lx, lz, GY)
    for (tx, tz) in [(-260, -40), (240, -30), (-230, 240), (250, 260),
                     (-60, -190), (80, -180)]:
        tree_gloom(tx, tz, GY, 0.8)

    # дороги от ворот
    road(0, -250, 0, -680, BASE_TOP)           # север (до пролива)
    road(-352, 100, -688, 100, BASE_TOP)       # запад
    road(-712, 100, -1460, 100, 14.0)          # к Сердцу-Древу
    road(-1460, 100, -1540, 100, 14.0)         # подход к мосту
    road(-1580, 100, -1700, 100, 14.0)         # за мост через реку
    road(-1440, 100, -1440, -690, 14.0)        # тракт на Перешеек
    road(352, 100, 688, 100, BASE_TOP)         # восток
    road(712, 100, 1480, 60, 12.0)             # в топи
    road(0, 416, 0, 880, BASE_TOP)             # юг
    road(0, 920, 0, 1500, 12.0)                # к кладбищу
    road(250, 1800, -860, 1460, 12.0)          # к каньону Бездны
    road(340, 440, 900, 1100, BASE_TOP)        # к берегу
    road(920, 1120, 2100, 2050, 8.4)           # к маяку

    # пандусы от плато на низину
    ramp(0, -238, BASE_TOP, 4, 16, 14, "-Z")
    ramp(0, 408, BASE_TOP, 4, 16, 14, "+Z")
    ramp(-338, 100, BASE_TOP, 4, 16, 14, "-X")
    ramp(338, 100, BASE_TOP, 4, 16, 14, "+X")

    # --- пруд с каменным мостиком ---
    water_pool(215, 330, GY, 26)
    stone_footbridge(215, 330, GY, yaw=0, span=46, width=5)
    for (rx, rz) in [(196, 312), (234, 352), (240, 318), (198, 352)]:
        reed(rx, rz, GY)
    tree_gloom(188, 368, GY, 0.9)
    tree_gloom(250, 300, GY, 1.0)

    # --- табличка версии у спавна (проверка что открыт правильный файл) ---
    signpost(8, 146, GY + 0.55, 0, "EMBERFALL v12\nквадратные горы, города, данжи")

    # --- указатели у ворот ---
    signpost(0, -214, GY, 0, "← Морозные Пики | Глумвуд ←\nПепельные Пустоши →")
    signpost(-214, 100, GY, 90, "Глумвуд и Сердце-Древо\n← запад")
    signpost(214, 100, GY, -90, "Топи Мирефен →\nвосток")
    signpost(0, 414, GY, 180, "Костяные Поля и Бездна\nюг")

    # --- роща вдоль стен (внутри) ---
    for i in range(22):
        a = math.pi * 2 * i / 22 + 0.13
        if any(angle_gap(a, ga) < 0.30 for ga in (0, math.pi / 2, math.pi, -math.pi / 2)):
            continue
        rr = rng.uniform(292, 312)
        tree_gloom(math.sin(a) * rr, 100 + math.cos(a) * rr, GY,
                   rng.uniform(0.9, 1.3))

    # --- цветы и трава на газонах ---
    scatter(90, -300, -200, 300, 400,
            lambda x, z, gy: grass_tuft(x, z, GY), excl=[(0, 110, 70)],
            gy=GY)
    scatter(45, -300, -200, 300, 400,
            lambda x, z, gy: flower(x, z, GY), excl=[(0, 110, 80)], gy=GY)

    # --- окрестные луга: деревья, кусты, камни, руины ---
    VILLAGE_EXCL = [(-860, -380, 85), (-880, 470, 90), (-480, 760, 80),
                    (500, 770, 85), (200, -950, 75), (-200, -950, 75),
                    (0, -620, 14), (60, 1050, 14), (560, 40, 14),
                    (-350, 500, 18), (-200, 390, 16), (30, -235, 8),
                    (180, -480, 34), (-260, -420, 38), (430, -260, 32),
                    (560, 560, 36), (-520, 620, 34), (240, 760, 32),
                    (-640, -120, 30), (660, -500, 33), (215, 330, 40),
                    (-580, -240, 34), (760, 250, 34),
                    (-430, -280, 16), (450, -150, 16), (620, 420, 16),
                    (-680, 560, 16), (-260, 880, 16), (420, 940, 16),
                    (840, -260, 16), (-840, 40, 16),
                    (0, 110, 70)]

    def plains_tree(x, z, gy):
        if abs(x) < 55 or abs(z - 100) < 55:
            return
        if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in VILLAGE_EXCL):
            return
        tree_nice(x, z, gy, rng.uniform(0.9, 1.6))

    def plains_small(x, z, gy):
        if abs(x) < 50 or abs(z - 100) < 50 or math.hypot(x, z - 100) < 390:
            return
        if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in VILLAGE_EXCL):
            return
        rng.choice([bush, bush, grass_tuft, fern, flower, stone_pile])(x, z, gy)

    scatter(460, -750, -850, 750, 1050, plains_tree)
    scatter(900, -750, -850, 750, 1050, plains_small)
    scatter(26, -1050, -1200, 1050, 1400,
            lambda x, z, gy: (ruin_fragment(x, z, gy) if abs(x) > 60
                              and abs(z - 100) > 60 else None))
    scatter(40, -1050, -1200, 1050, 1400,
            lambda x, z, gy: (fallen_log(x, z, gy) if abs(x) > 60
                              and abs(z - 100) > 60 else None))

    # --- паркур «Круча Дозора»: камни на западном обрыве, сундук наверху ---
    parkour_rocks((-360, 260), (-560, 150), 12, 34, 9, tag="Overlook")
    signpost(-332, 262, GY, 90, "Круча Дозора ↑\n(паркур)")

    # --- ГОРЫ-ХРЕБТЫ на границах (перелазь по ступеням или иди в воротах) ---
    wom_mountain(-860, -380, 14, base_w=120 * 1.3, h=100 * 1.45, snow=0.66, seed=39)
    wom_mountain(-880, 470, 14, base_w=130 * 1.3, h=112 * 1.45, snow=0.66, seed=2)
    wom_mountain(-480, 760, 8, base_w=115 * 1.3, h=92 * 1.45, snow=0.66, seed=41)
    wom_mountain(500, 770, 8, base_w=120 * 1.3, h=96 * 1.45, snow=0.66, seed=1)
    wom_mountain(200, -950, 8, base_w=105 * 1.3, h=85 * 1.45, snow=0.66, seed=26)
    wom_mountain(-200, -950, 8, base_w=105 * 1.3, h=85 * 1.45, snow=0.66, seed=10)

    # --- холмы на равнине ---
    for (hx, hz, hr, hh) in [(180, -480, 26, 12), (-260, -420, 30, 14),
                             (430, -260, 24, 10), (560, 560, 28, 13),
                             (-520, 620, 26, 12), (240, 760, 24, 10),
                             (-640, -120, 22, 9), (660, -500, 25, 11)]:
        hill_mound(hx, hz, 8, hr, hh)

    # --- сторожевые башни, стоунхендж, телега, заборы вдоль дорог ---
    watch_tower(0, -620, 8, "North")
    watch_tower(60, 1050, 12, "South")
    watch_tower(560, 40, 8, "East")
    standing_stones(-350, 500, 8)
    cart_wagon(30, -235, 8, yaw=75)
    fence_line(0, 430, 0, 880, 8, off=9)
    fence_line(352, 100, 688, 100, 8, off=9)
    farm_field(-200, 390, 12.0, 20, 14, yaw=0)
    scarecrow(-212, 380, 12.0)

    # --- ВЕЛИКИЕ ЮЖНЫЕ ВРАТА на тракте ---
    great_gate(0, 700, 8.0)

    # --- ДРЕВНИЕ деревья-великаны на равнинах (достопримечательности) ---
    for (ax, az) in [(-430, -280), (450, -150), (620, 420), (-680, 560),
                     (-260, 880), (420, 940), (840, -260), (-840, 40)]:
        ancient_tree(ax, az, 8, rng.uniform(2.1, 2.5))

    # --- каменные форты-посты на дорогах ---
    outpost("OutpostWest", -580, -240, 8, "W")
    outpost("OutpostEast", 760, 250, 8, "E")
    signpost(-552, -208, 8, 25, "Форт-пост Запад")
    signpost(732, 282, 8, -25, "Форт-пост Восток")

    endfolder()


def build_gloomwood(parent):
    folder("Gloomwood")
    GY = 14.0
    ramp(-700, 100, BASE_TOP, 6, 24, 12, "-X")

    # Сердце-Древо
    heart_tree(-1500, 50, GY)

    # --- Река Ледяная: от замёрзшего озера к западному морю ---
    river_pts = river_build([(-1150, -700), (-1250, -450), (-1450, -200),
                             (-1500, -100), (-1560, 100), (-1650, 350),
                             (-1900, 500), (-2290, 570)], GY, width=18)
    for i, (rx, rz) in enumerate(river_pts):
        if i % 2 == 0:
            side = 1 if i % 4 == 0 else -1
            reed(rx + side * 9, rz + rng.uniform(-3, 3), GY)

    # --- мосты через реку (западный теперь крытый) ---
    covered_bridge(-1560, 100, GY, yaw=90, span=40, width=9)
    wooden_bridge(-1440, -212, GY, yaw=0, span=34, width=7)

    # --- скалы «Клыки» (видны от северных ворот деревни) ---
    wom_mountain(-1000, -620, GY, base_w=72 * 1.3, h=62 * 1.45, snow=0.66, seed=77)
    wom_mountain(-1130, -540, GY, base_w=90 * 1.3, h=80 * 1.45, snow=0.66, seed=8)
    wom_mountain(-1320, -590, GY, base_w=76 * 1.3, h=68 * 1.45, snow=0.66, seed=27)

    # --- лагеря разбойников (3 штуки) ---
    bandit_camp(-1000, 320, GY, yaw=15, name="BanditCamp")
    bandit_camp(-2050, 640, GY, yaw=110, name="BanditCampNorth",
                banner_col=(130, 50, 40), ntents=3)
    bandit_camp(-880, -430, GY, yaw=250, name="BanditCampRoad",
                tent_cols=((80, 62, 48), (70, 56, 46)), banner_col=(100, 40, 40))

    # --- деревня лесорубов ДУПЛИНО ---
    small_village("Duplino", -1850, -320, GY, n_houses=6, radius=52,
                  pal={"wall": (120, 96, 70), "roof": (62, 46, 34)},
                  palisade=True, sign_text="ДУПЛИНО\\nлесорубов",
                  well_pos=(-1850, -320))
    for _ in range(24):
        tx = rng.uniform(-1950, -1750)
        tz = rng.uniform(-420, -220)
        fallen_log(tx, tz, GY)

    # --- густой лес (v9): сажаем на рельеф, обходим деревни и лагеря ---
    forest_fill("Gloomwood", -2320, -680, -700, 780, density=0.62, cell=118.0,
                trees=("tree_gloom", "tree_gloom", "tree_nice", "dead_tree"),
                scale=(0.85, 1.5),
                skip=[(-1250, 330, 130), (-1500, 50, 90), (-1000, 320, 95),
                      (-2050, 640, 90), (-880, -430, 85), (-1850, -320, 120),
                      (-1150, -450, 90), (-2290, 570, 80)])

    # --- ТЕНЕГРИВ: лесная деревня (дома, лавка, колодец, огород, палисад) ---
    house("Tenegriv_HouseA", -1250, 330, GY, 13, 10, 8, yaw=12, wall=(96, 78, 58),
          roof=(58, 44, 34))
    house("Tenegriv_HouseB", -1286, 362, GY, 12, 9, 7, yaw=-24, wall=(92, 74, 56),
          roof=(54, 42, 32))
    house("Tenegriv_HouseC", -1214, 368, GY, 12, 9, 7, yaw=96, wall=(98, 80, 60),
          roof=(60, 46, 36))
    well(-1252, 356, GY)
    campfire(-1232, 344, GY)
    stall(-1274, 336, GY, yaw=80)
    lamppost(-1236, 358, GY)
    lamppost(-1266, 328, GY)
    signpost(-1214, 330, GY, -90, "ТЕНЕГРИВ\nлесная деревня")
    farm_field(-1300, 300, GY + 0.55, 16, 12, yaw=20)
    scarecrow(-1310, 292, GY + 0.55)
    for i in range(16):
        a = math.pi * 2 * i / 16
        if angle_gap(a, 0.6) < 0.35:
            continue
        px, pz = -1250 + math.sin(a) * 46, 330 + math.cos(a) * 46
        part("Tenegriv_Palisade", (1.1, 6.5, 1.1), (px, GY + 2.9, pz),
             yaw=math.degrees(a), color=(80, 62, 46), material="Wood")
    road(-1150, 100, -1150, 250, 14.0, width=6, color=(60, 64, 54), mat="Ground")
    road(-1150, 250, -1240, 310, 14.0, width=6, color=(60, 64, 54), mat="Ground")
    for (hx, hz, hr, hh) in [(-850, 700, 26, 11), (-1900, -300, 30, 13),
                             (-1700, -500, 26, 11), (-2100, 150, 24, 10),
                             (-1250, -450, 24, 10)]:
        hill_mound(hx, hz, GY, hr, hh, (56, 76, 50))

    # --- Перешеек к Морозным Пикам (через равнину) ---
    ramp(-1440, -720, 8, 6, 24, 14, "-Z")
    road(-1440, -760, -1440, -1000, 8.0, width=8, color=(70, 66, 60),
         mat="Ground")
    ramp(-1440, -1022, 8, 12, 36, 14, "-Z")
    signpost(-1440, 118, GY, 0, "Перешеек →\nМорозные Пики")

    exclusion = [(-1500, 50, 130), (-2050, 550, 40), (-700, 100, 60),
                 (-1000, 320, 32), (-1560, 100, 30), (-1440, -212, 26),
                 (-1000, -620, 80), (-1130, -540, 90), (-1320, -590, 80),
                 (-1440, 0, 26), (-1440, -400, 26), (-1440, -650, 26),
                 (-1250, 340, 80), (-850, 700, 34), (-1900, -300, 38),
                 (-1700, -500, 34), (-2100, 150, 32), (-1250, -450, 32),
                 (-860, -380, 85), (-880, 470, 90)]
    exclusion += [(px, pz, 40) for (px, pz) in river_pts[::3]]
    exclusion += [(-940, -560, 30), (-980, -300, 30), (-1010, 0, 30),
                  (-1030, 300, 30), (-1040, 560, 30), (-1045, 780, 30)]
    placed = 0
    attempts = 0
    while placed < 460 and attempts < 2600:
        attempts += 1
        x = rng.uniform(-2240, -760)
        z = rng.uniform(-640, 740)
        if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in exclusion):
            continue
        tree_gloom(x, z, GY, rng.uniform(0.8, 1.5))
        placed += 1
    for _ in range(70):
        mushroom(rng.uniform(-2200, -800), rng.uniform(-640, 740), GY,
                 rng.uniform(0.8, 1.6))
    for _ in range(85):
        rock(rng.uniform(-2240, -780), rng.uniform(-660, 760), GY,
             rng.uniform(0.8, 1.6), "Rock", (66, 66, 72))
    witch_hut(-2050, 550, GY)

    # --- река доходит до моря: водопад с плато и низовья ---
    waterfall(-2312, 580, GY, 8.0, width=18, yaw=0)
    river_build([(-2330, 585), (-2470, 600), (-2620, 640)], 8.0, width=16,
                color=(30, 64, 80))

    # --- густая растительность: кусты, папоротники, трава, валежник ---
    exclusion2 = exclusion
    scatter(280, -2240, -640, -760, 740,
            lambda x, z, gy: bush(x, z, GY), excl=exclusion2, gy=GY)
    scatter(260, -2240, -640, -760, 740,
            lambda x, z, gy: fern(x, z, GY), excl=exclusion2, gy=GY)
    scatter(420, -2240, -640, -760, 740,
            lambda x, z, gy: grass_tuft(x, z, GY, (52, 74, 48)), excl=exclusion2,
            gy=GY)
    scatter(90, -2240, -640, -760, 740,
            lambda x, z, gy: fallen_log(x, z, GY), excl=exclusion2, gy=GY)
    scatter(90, -2240, -640, -760, 740,
            lambda x, z, gy: stone_pile(x, z, GY), excl=exclusion2, gy=GY)
    scatter(30, -2240, -640, -760, 740,
            lambda x, z, gy: ruin_fragment(x, z, GY), excl=exclusion2, gy=GY)
    scatter(200, -2240, -640, -760, 740,
            lambda x, z, gy: tree_gloom(x, z, GY, rng.uniform(0.8, 1.3)),
            excl=exclusion2, gy=GY)
    scatter(80, -2240, -640, -760, 740,
            lambda x, z, gy: tree_nice(x, z, GY, rng.uniform(1.1, 1.6)),
            excl=exclusion2, gy=GY)

    # --- ЗАПАДНАЯ РЕКА: от Глумвуда через равнину к южному морю ---
    river_build([(-940, -560), (-980, -300), (-1010, 0), (-1030, 300),
                 (-1040, 560), (-1045, 780)], GY, width=20)
    waterfall(-1047, 800, GY, 8.0, width=22, yaw=0)
    river_west = [(-1052, 815), (-1050, 1000), (-1100, 1300), (-1200, 1600),
                  (-1330, 1900), (-1480, 2200), (-1650, 2500), (-1800, 2750),
                  (-1900, 2930)]
    river_build(river_west, 8.0, width=20)
    waterfall(-1915, 2950, 8.0, 0.5, width=24, yaw=0)
    # мост западной дороги через новую реку (вторая мостина на тракте)
    covered_bridge(-1032, 100, 14.0, yaw=90, span=44, width=9)
    signpost(-1060, 830, 8, 45, "Западная река\nводопад ↓ к морю")

    endfolder()


def build_frostpeak(parent):
    folder("Frostpeak")
    # ступенчатые склоны: наверх можно ЗАЙТИ пешком (шаг 2.4 студа)
    add_plateau_rect(-2320, -2320, -880, -980, 20.0)
    add_plateau_rect(-2120, -2120, -1080, -1180, 32.0)
    add_plateau_rect(-1920, -1920, -1280, -1380, 46.0)
    add_plateau_rect(-1770, -1770, -1430, -1530, 62.0)
    terrace_steps("FrostT1", -2320, -2320, -880, -980, 20.0, 8.0,
                  (216, 222, 232), "Snow", tread=13.0, step=2.4)
    terrace_steps("FrostT2", -2120, -2120, -1080, -1180, 32.0, 20.0,
                  (210, 218, 230), "Snow", tread=12.0, step=2.4)
    terrace_steps("FrostT3", -1920, -1920, -1280, -1380, 46.0, 32.0,
                  (168, 196, 222), "Glacier", tread=11.0, step=2.4)
    terrace_steps("FrostT4", -1770, -1770, -1430, -1530, 62.0, 46.0,
                  (222, 228, 238), "Snow", tread=10.0, step=2.4)
    # ледяные торосы по склонам для фактуры
    for _ in range(70):
        tx = rng.uniform(-2280, -900)
        tz = rng.uniform(-2280, -1000)
        hh = rng.uniform(3, 9)
        part("FrostRidge", (rng.uniform(3, 7), hh, rng.uniform(3, 7)),
             (tx, 20 + rng.uniform(0, 10), tz), yaw=rng.uniform(0, 360),
             pitch=rng.uniform(-12, 12), color=(198, 216, 232), material="Glacier")

    ramp(-1100, -1650, 20, 12, 40, 16, "-X")
    ramp(-1300, -1550, 32, 14, 44, 16, "-X")
    ramp(-1600, -1550, 46, 16, 44, 16, "-Z")

    # горы-великаны (взбираются по ступеням-слоям)
    wom_mountain(-2050, -2100, 20, base_w=185 * 1.3, h=145 * 1.45, snow=0.66, seed=37)
    wom_mountain(-1150, -2150, 20, base_w=145 * 1.3, h=120 * 1.45, snow=0.66, seed=34)

    # замёрзшее озеро
    slab("FrozenLake", -1250, -1750, -1050, -1550, 20.5, 19.7, (150, 190, 220),
         "Ice", transparency=0.2)

    # замёрзший ручей от озера на север террасы
    for (ax, az, bx, bz) in [(-1050, -1650, -1050, -2290)]:
        dx, dz = bx - ax, bz - az
        dist = math.hypot(dx, dz)
        n = int(dist // 12)
        yawd = math.degrees(math.atan2(dx, dz))
        for k in range(n + 1):
            t = k / float(n)
            part("FrozenStream", (14, 0.5, 13), (ax + dx * t, 20.55, az + dz * t),
                 yaw=yawd, color=(150, 190, 220), material="Ice", transparency=0.15)
    # водопад с террасы на равнину, низовья и вторая ступень к морю
    waterfall(-1050, -2310, 20.5, 8.0, width=22, yaw=0)
    for k in range(14):
        part("FrozenStream2", (14, 0.5, 13), (-1050, 8.55, -2330 - k * 22),
             color=(150, 190, 220), material="Ice", transparency=0.15)
    waterfall(-1050, -2640, 8.0, 0.5, width=26, yaw=0)

    # Горная Обитель — деревня у подножия
    hamlet_excl = [(-1750, -1150, 40), (-2200, -1150, 60)]
    house("Hamlet_HouseA", -1750, -1150, 20, 14, 11, 8, yaw=15)
    house("Hamlet_HouseB", -1786, -1120, 20, 12, 10, 8, yaw=-20)
    house("Hamlet_HouseC", -1716, -1186, 20, 12, 10, 8, yaw=100)
    well(-1766, -1156, 20)
    campfire(-1738, -1178, 20)
    for i in range(14):
        a = math.pi * 2 * i / 14
        px, pz = -1750 + math.sin(a) * 52, -1150 + math.cos(a) * 52
        part("Hamlet_Palisade", (1.1, 7, 1.1), (px, 20 + 3.1, pz),
             yaw=math.degrees(a), color=(88, 70, 52), material="Wood")
    signpost(-1712, -1120, 20, -45, "Горная Обитель\n← Ледяная Гробница (-450)")
    lamppost(-1735, -1140, 20)
    lamppost(-1765, -1170, 20)

    # --- деревня ВЕТРОГРАД на второй террасе ---
    small_village("Vetrograd", -1500, -1350, 32.0, n_houses=5, radius=46,
                  pal={"wall": (200, 204, 210), "roof": (110, 128, 150)},
                  wall_mat="Concrete", roof_mat="Slate", palisade=True,
                  sign_text="ВЕТРОГРАД\\nсеверные охотники",
                  well_pos=(-1500, -1350))

    # Ледяная Гробница — подземелье с боссом Морозным Призраком
    ice_tomb(-2200, -1150, 20, yaw=25)

    # Ледовый паркур к арене Колосса
    parkour_rocks((-1400, -1520), (-1560, -1660), 22, 60, 10,
                  col=(170, 200, 230), tag="Peaks")
    signpost(-1396, -1512, 20, 40, "Восхождение ↑\n(паркур к арене)")

    # ---- v11: ДАНЖИ МОРОЗНЫХ ПИКОВ ----
    # ледяные пещеры (прорубь в леднике) + арена Архипастыря на обрыве
    cave_system("Ледяные пещеры", -1650, -1400, 20.0, depth=20.0,
                nodes=((75, 30), (165, 110), (100, 190)),
                width=19, height=14, floor_mat="Glacier", floor_col=(150, 182, 208),
                tag="IceCave", extra_chests=3,
                cap_col=(200, 218, 234), cap_mat="Glacier")
    for i in range(26):
        ice_spike_cluster(rng.uniform(-1850, -1450), rng.uniform(-1560, -1200), 20.0)
    register_mob("Frostpeak", -1720, -1440, 20.0)
    register_mob("Frostpeak", -1580, -1360, 20.0)
    register_mob("Frostpeak", -1660, -1300, 20.0)
    chest_marker(-1620, -1380, 20.6, "IceCaveSurf")

    boss_arena_circular("WindPeakArena", -1520, -900, 20.0, r=58,
                        pillar_col=(196, 214, 236), pillar_mat="Glacier",
                        boss_id="WindArchon", n_pillars=10)
    for i in range(10):
        a = math.pi * 2 * i / 10
        part("WindPeakTooth", (5, rng.uniform(18, 34), 5),
             (-1520 + math.sin(a) * 72, 20 + 12, -900 + math.cos(a) * 72),
             pitch=rng.uniform(-8, 8), color=(206, 224, 240), material="Glacier")
    signpost(-1470, -930, 20.0, 60, "ПИК ВЕТРОВ\nарена Архипастыря")

    # лагерь охотников на первой террасе
    bandit_camp(-1350, -1250, 20, yaw=-30, tent_cols=((120, 110, 96), (104, 96, 84)),
                banner_col=(70, 90, 120), name="HunterCamp")

    frost_shrine(-1600, -1700, 32)
    boss_arena_circular("FrostArena", -1600, -1650, 62, r=55,
                        pillar_col=(170, 200, 230), pillar_mat="Glacier",
                        boss_id="FrostColossus")

    # --- ПАРЯЩИЙ АРХИПЕЛАГ над озером + НЕБЕСНАЯ ЛЕСТНИЦА ---
    sky_ladder([(-1015, -1560), (-1040, -1590), (-1065, -1620), (-1090, -1650)])
    floating_isle(-1150, -1650, 128, 40, "Main")
    sky_castle(-1150, -1650, 128)
    floating_isle(-1250, -1720, 134, 22, "B")
    floating_isle(-1080, -1735, 122, 18, "C")
    floating_isle(-1150, -1560, 165, 15, "D", grass=False)
    floating_isle(-1222, -1602, 150, 12, "E", grass=False)
    rope_bridge(-1090, -1650, -1118, -1652, 125.5)
    rope_bridge(-1162, -1668, -1242, -1712, 130.5)
    rope_bridge(-1138, -1676, -1088, -1726, 125.5)
    waterfall(-1150, -1612, 126, 21, width=16, yaw=0)
    signpost(-990, -1530, 20.5, 130, "Небесная лестница ↑\n(на парящие острова)")

    exclusion = [(-1600, -1650, 120), (-1600, -1700, 50), (-1500, -980, 60),
                 (-1100, -1650, 60), (-1300, -1550, 60), (-1600, -1550, 60),
                 (-1150, -2150, 150), (-2050, -2100, 165), (-1250, -1650, 120),
                 (-1350, -1250, 34), (-930, -1300, 40), (-930, -990, 45),
                 (-1440, -900, 30), (-1750, -1150, 90), (-1750, -1500, 80),
                 (-1950, -1750, 32), (-1250, -1350, 32), (-2050, -1450, 30),
                 (-1400, -1520, 30)]
    terraces = [(-2260, -2260, -940, -1040, 20, 160), (-2060, -2060, -1140, -1240, 32, 75),
                (-1860, -1860, -1340, -1440, 46, 30)]
    for (x0, z0, x1, z1, gy, count) in terraces:
        placed = 0
        attempts = 0
        while placed < count and attempts < count * 8:
            attempts += 1
            x = rng.uniform(x0, x1)
            z = rng.uniform(z0, z1)
            if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in exclusion):
                continue
            pine(x, z, gy, rng.uniform(0.9, 1.5))
            placed += 1
    for _ in range(110):
        rock(rng.uniform(-2200, -1000), rng.uniform(-2200, -1100), 20,
             rng.uniform(0.8, 1.7), "Rock", (120, 124, 136))
    for (hx, hz) in [(-1950, -1750), (-1250, -1350), (-2050, -1450)]:
        hill_mound(hx, hz, 20, 26, 12, (198, 210, 224))
    for _ in range(30):
        x = rng.uniform(-2200, -1000)
        z = rng.uniform(-2250, -1100)
        if any(math.hypot(x - ex, z - ez) < er for ex, ez, er in exclusion):
            continue
        crystal(x, z, 20, rng.uniform(0.8, 1.6), "cyan")

    # глетчеры-шипы и снежные холмы на белых равнинах
    for (sx, sz) in [(-1150, -1250), (-950, -1300), (-1250, -1100),
                     (-1750, -1050), (-2150, -1250), (-1450, -1050),
                     (-2050, -1900), (-950, -1950), (-1900, -1300),
                     (-1250, -2100)]:
        ice_spike_cluster(sx, sz, 20)
    for (hx, hz) in [(-1000, -1150), (-2200, -1500), (-1300, -1050)]:
        hill_mound(hx, hz, 20, 24, 10, (206, 218, 232))

    endfolder()


def build_ashwaste(parent):
    folder("Ashwaste")
    GY = 16.0
    lava_field(-700, -2400, 900, -1200)

    # перешеек из деревни: дорога через бывший пролив и подъём
    road(0, -690, 0, -1110, 8.0, width=9)
    ramp(0, -1140, 8, 8, 44, 14, "-Z")

    # обсидиановые шпили
    for _ in range(110):
        x = rng.uniform(-750, 950)
        z = rng.uniform(-2450, -1200)
        if math.hypot(x - 100, z + 2100) < 120:
            continue
        if math.hypot(x - 520, z + 1380) < 60:
            continue
        if math.hypot(x - 750, z + 2320) < 135 or math.hypot(x + 560, z + 1220) < 115:
            continue
        part("Spike", (rng.uniform(2, 4.5), rng.uniform(12, 26), rng.uniform(2, 4.5)),
             (x, GY + rng.uniform(5, 12), z), yaw=rng.uniform(0, 360),
             pitch=rng.uniform(-9, 9), roll=rng.uniform(-9, 9),
             color=(38, 35, 42), material="Basalt")
    for _ in range(24):
        px, pz = rng.uniform(-700, 900), rng.uniform(-2400, -1200)
        if math.hypot(px - 520, pz + 1380) < 70:
            continue
        if math.hypot(px - 100, pz + 2100) < 95:
            continue
        lava_pool(px, pz, GY, rng.uniform(6, 16))
    for _ in range(45):
        rock(rng.uniform(-750, 950), rng.uniform(-2450, -1200), GY, 1.2,
             "Basalt", (52, 48, 52))
    for _ in range(30):
        x, z = rng.uniform(-700, 950), rng.uniform(-2400, -1200)
        if math.hypot(x - 100, z + 2100) < 100:
            continue
        part("EmberRock", (1.6, 1.2, 1.6), (x, GY + 0.6, z), yaw=rng.uniform(0, 90),
             color=(255, 120, 40), material="Neon", cancollide=False)

    # горные кромки по краям Пустошей + ВУЛКАН с жерлом и лавопадом
    wom_mountain(750, -2320, GY, base_w=130 * 1.3, h=108 * 1.45, snow=0.66, seed=29)
    wom_mountain(-560, -1220, GY, base_w=105 * 1.3, h=95 * 1.45, snow=0.66, seed=9)
    volcano(300, -2250, GY)
    signpost(52, -2130, GY, 150, "Вулкан Пепла ↑\n(паркур к жерлу)")

    # лагерь мародёров
    bandit_camp(520, -1380, GY, yaw=200, tent_cols=((70, 60, 56), (58, 50, 48)),
                banner_col=(180, 60, 30), name="MarauderCamp")

    fortress_ruins(250, -1850, GY)

    # --- мёртвый лес Пустошей ---
    forest_fill("AshDead", -780, -2450, 980, -1150, density=0.32, cell=170.0,
                trees=("dead_tree",), scale=(0.9, 1.6), bushes=False,
                skip=[(300, -2250, 330), (100, -2100, 150), (520, -1380, 110),
                      (250, -1850, 120), (-350, -1550, 110)])

    # --- ФОРТ МАРОДЁРОВ: частокол, башни, костры ---
    add_flat(-350, -1550, 95, GY, 80.0)
    for i in range(34):
        a = math.pi * 2 * i / 34
        if angle_gap(a, 1.0) < 0.22:
            continue
        px, pz = -350 + math.sin(a) * 62, -1550 + math.cos(a) * 62
        part("MarauderFort_Stake", (1.4, 8.5, 1.4), (px, GY + 4.0, pz),
             yaw=math.degrees(a), color=(72, 58, 46), material="Wood")
    for i in range(4):
        a = math.pi * 2 * i / 4 + 0.4
        px, pz = -350 + math.sin(a) * 62, -1550 + math.cos(a) * 62
        v_cyl("MarauderFort_Tower", px, pz, GY, 14, 9, (66, 54, 44), "Wood")
        part("MarauderFort_Deck", (11, 1, 11), (px, GY + 14.4, pz),
             color=(78, 62, 48), material="WoodPlanks")
        truss("MarauderFort_Ladder", (2, 12, 2), (px + 5.4, GY + 6, pz))
    tent(-350, -1580, GY, yaw=20, w=9, d=11, h=5.4, color=(70, 58, 48))
    tent(-320, -1530, GY, yaw=100, w=8, d=10, h=5.0, color=(62, 52, 44))
    tent(-380, -1520, GY, yaw=250, w=8, d=10, h=5.0, color=(58, 48, 42))
    campfire(-350, -1550, GY)
    chest_marker(-336, -1562, GY + 0.6, "MarauderFort")
    part("MarauderFort_Banner", (3.4, 6.0, 0.2), (-350, GY + 10.0, -1488),
         color=(180, 60, 30), material="Fabric", cancollide=False)
    boss_arena_circular("AshArena", 100, -2100, GY, r=65, pillar_col=(38, 35, 42),
                        pillar_mat="Basalt", boss_id="Ashlord")
    for i in range(8):
        a = math.pi * 2 * i / 8
        lava_pool(100 + math.sin(a) * 88, -2100 + math.cos(a) * 88, GY, 9)
    endfolder()


def build_mirefen(parent):
    folder("Mirefen")
    GY = 12.0
    swamp_field(740, -860, 2260, 960)
    ramp(700, 100, BASE_TOP, 4, 16, 12, "+X")

    # центральный водоём и арена
    water_pool(1500, 100, GY, 130)
    disc("MirefenIsland", 1500, 100, GY + 0.9, 55, 1.4, (52, 46, 34), "Mud")
    for i in range(10):
        a = math.pi * 2 * i / 10
        rock(1500 + math.sin(a) * 45, 100 + math.cos(a) * 45, GY + 0.8, 0.9,
             "Mud", (44, 40, 30))
    for i in range(6):
        a = math.pi * 2 * i / 6 + 0.3
        brazier(1500 + math.sin(a) * 30, 100 + math.cos(a) * 30, GY + 0.9)
    boss_spawn("SwampMother", 1500, 100, GY + 0.9)
    arena_trigger("SwampMother", 1500, 100, GY + 0.9, r=100)
    # колье каменных клыков вокруг арены Матери Болот
    for i in range(14):
        a = math.pi * 2 * i / 14 + 0.2
        part("Mire_Spike", (4.5, rng.uniform(12, 20), 4.5),
             (1500 + math.sin(a) * 74, GY + 6, 100 + math.cos(a) * 74),
             yaw=math.degrees(a), pitch=rng.uniform(-7, 7),
             color=(58, 54, 44), material="Basalt")

    for _ in range(20):
        px, pz = rng.uniform(800, 2200), rng.uniform(-800, 900)
        if math.hypot(px - 1500, pz - 100) < 190:
            continue
        if math.hypot(px - 1050, pz - 550) < 70:
            continue
        water_pool(px, pz, GY, rng.uniform(8, 24))
    for _ in range(150):
        x, z = rng.uniform(760, 2240), rng.uniform(-840, 940)
        if math.hypot(x - 1500, z - 100) < 190:
            continue
        if math.hypot(x - 1050, z - 550) < 42:
            continue
        dead_tree(x, z, GY, rng.uniform(1.1, 1.9))
    for _ in range(80):
        x, z = rng.uniform(760, 2240), rng.uniform(-840, 940)
        if math.hypot(x - 1500, z - 100) < 150:
            continue
        reed(x, z, GY)
    for _ in range(30):
        rock(rng.uniform(760, 2240), rng.uniform(-840, 940), GY, 1.0, "Mud",
             (48, 44, 34))

    # руины хижин
    for (hx, hz) in [(1100, -400), (1700, 300), (1300, 600)]:
        part("HutWall1", (10, 6, 1.2), (hx, GY + 3, hz), yaw=rng.uniform(0, 180),
             color=(64, 56, 44), material="Wood")
        part("HutWall2", (1.2, 5, 8), (hx + 5, GY + 2.5, hz + 3),
             pitch=rng.uniform(-6, 6), color=(60, 52, 42), material="Wood")
        part("HutFallen", (8, 1.2, 1.2), (hx - 3, GY + 0.8, hz + 5),
             yaw=rng.uniform(0, 360), roll=80, color=(56, 48, 40), material="Wood",
             cancollide=False)
        rock(hx + 6, hz - 4, GY, 0.9, "Mud", (50, 46, 36))

    # рыбацкий стан на сваях у болота
    bandit_camp(1050, 550, GY, yaw=45, tent_cols=((84, 80, 60), (74, 70, 54)),
                banner_col=(60, 110, 140), name="FisherCamp", ntents=2)
    for (bx, bz) in [(1030, 570), (1075, 535)]:
        part("FishingBoat", (9, 1.6, 3), (bx, GY + 0.8, bz), yaw=rng.uniform(0, 90),
             color=(70, 54, 38), material="Wood", cancollide=False)

    # светящиеся грибы и трава топей
    scatter(60, 800, -800, 2200, 900,
            lambda x, z, gy: glowshroom(x, z, GY),
            excl=[(1500, 100, 200), (1050, 550, 45)], gy=GY)
    scatter(150, 800, -800, 2200, 900,
            lambda x, z, gy: grass_tuft(x, z, GY, (96, 92, 54)),
            excl=[(1500, 100, 200), (1050, 550, 45)], gy=GY)
    endfolder()


def build_sunken_coast(parent):
    folder("SunkenCoast")
    GY = 8.4
    sand_field(820, 920, 2380, 2280)
    slab("CoastGrass", 900, 1000, 2200, 2150, GY + 0.4, GY - 1.6, (120, 130, 80),
         "Ground")

    lighthouse(2150, 2100, 8.4)
    shipwreck(1900, 1250, 8.0)
    ruin_columns(1450, 1800, 8.4)

    # --- ПОРТ «Ржавый Крюк»: причалы, корабли, кран, склад ---
    port_x, port_z, port_gy = 1750, 2600, 4.0
    house("Port_Warehouse", port_x, 2530, port_gy, 26, 16, 10, yaw=0,
          wall=(110, 96, 78), roof=(84, 62, 46))
    for i, off in enumerate((-26, 2, 30)):
        pier(port_x + off, port_z, port_gy, yaw=-90, length=125 - abs(off) // 2)
    port_crane(port_x - 44, 2596, port_gy, yaw=-70)
    crate_stack(port_x + 40, 2600, port_gy)
    crate_stack(port_x + 46, 2612, port_gy)
    for i in range(5):
        barrel(port_x - 30 + i * 3.2, 2604, port_gy)
    lamppost(port_x - 40, 2585, port_gy)
    lamppost(port_x + 40, 2585, port_gy)
    signpost(port_x, 2560, port_gy, 180, "ПОРТ «Ржавый Крюк»\nкорабли → море")
    sailing_ship("Port_Ship1", 1700, 2800, 0.0, yaw=-8)
    sailing_ship("Port_Ship2", 1810, 2830, 0.0, yaw=6)

    # --- БЕРЕГОВАЯ БАТАРЕЯ: бастион с огромной пушкой, стережёт пролив ---
    bastion_cannon(1960, 2680, 4, yaw=90)
    signpost(1930, 2645, 4, 180, "Береговая батарея\n(сторожа пролив)")
    # лодки у причалов
    for i, (bx, bz, byaw) in enumerate([(1690, 2700, 20), (1800, 2680, -30),
                                        (1745, 2745, 80)]):
        part("Port_Rowboat%d" % i, (10, 1.6, 3.4), (bx, 1.0, bz), yaw=byaw,
             color=(84, 62, 44), material="Wood", cancollide=False)

    # --- пальмы и прибрежный колорит ---
    forest_fill("CoastPalm", 850, 950, 2300, 2250, density=0.34, cell=150.0,
                trees=("palm_dead",), scale=(0.9, 1.4), bushes=False,
                skip=[(1750, 2600, 260), (1350, 2180, 150), (2150, 2100, 110),
                      (1180, 1600, 110), (2250, 1750, 110)])

    # --- пиратская бухта и деревня контрабандистов ---
    bandit_camp(2250, 1750, 8.4, yaw=300, tent_cols=((64, 54, 44), (56, 48, 42)),
                banner_col=(150, 40, 60), name="PirateCove", ntents=3)
    small_village("Kontrabanda", 1180, 1600, 8.4, n_houses=5, radius=46,
                  pal={"wall": (140, 126, 108), "roof": (86, 70, 52)},
                  sign_text="КОНТРАБАНДА\\nбухта", well_pos=(1180, 1600))

    # --- корабли в порту ---
    ship(1830, 2760, 2.0, yaw=190, size=1.0)
    ship(1600, 2810, 2.0, yaw=205, size=0.8)
    ship(2050, 2720, 2.0, yaw=170, size=1.15)
    dock("PortDockA", 1750, 2660, 2.0, length=110, width=13, yaw=0)
    dock("PortDockB", 1880, 2650, 2.0, length=84, width=11, yaw=15)
    dock("PortDockC", 1620, 2680, 2.0, length=70, width=10, yaw=-12)

    # --- Рыбацкая слобода ---
    fx, fz = 1350, 2180
    house("FishVillage_HouseA", fx, fz, GY, 12, 10, 7, yaw=0, wall=(120, 104, 82),
          roof=(70, 58, 44))
    house("FishVillage_HouseB", fx + 30, fz + 18, GY, 11, 9, 7, yaw=90,
          wall=(112, 98, 78), roof=(66, 54, 42))
    house("FishVillage_HouseC", fx - 6, fz + 44, GY, 12, 10, 7, yaw=-14,
          wall=(116, 100, 80), roof=(72, 60, 46))
    campfire(fx + 14, fz + 28, GY)
    stall(fx - 22, fz + 20, GY, yaw=90)
    for i, (bx, bz, byaw) in enumerate([(fx + 42, fz - 8, 10), (fx + 52, fz + 4, -24)]):
        part("FishVillage_Boat%d" % i, (9, 1.6, 3), (bx, GY + 0.8, bz), yaw=byaw,
             color=(78, 58, 42), material="Wood", cancollide=False)
    signpost(fx, fz - 14, GY, 0, "Рыбацкая слобода\n→ Порт")
    lamppost(fx + 16, fz + 12, GY)

    # --- острова-спутники с верёвочными мостами и сундуками ---
    islet(2700, 2600, bridge_from=(2450, 2320), tag="A")
    islet(-2650, -2600, bridge_from=(-2350, -2380), tag="B")

    # гора-мыс, холмы и сторожевая башня
    wom_mountain(1600, 1450, 8.4, base_w=120 * 1.3, h=95 * 1.45, snow=0.66, seed=85)
    for (hx, hz, hr, hh) in [(1000, 1100, 26, 11), (1150, 1950, 24, 10),
                             (2050, 1450, 26, 12), (900, 2050, 24, 10),
                             (1750, 1550, 22, 9)]:
        hill_mound(hx, hz, 8.4, hr, hh, (150, 156, 96))
    watch_tower(1150, 1300, 8.4, "Coast")

    for _ in range(30):
        x, z = rng.uniform(850, 2300), rng.uniform(950, 2250)
        if math.hypot(x - 2150, z - 2100) < 80 or math.hypot(x - 1450, z - 1800) < 80:
            continue
        if math.hypot(x - 1350, z - 2200) < 90 or math.hypot(x - 1750, z - 2530) < 90:
            continue
        if math.hypot(x - 1600, z - 1450) < 120:
            continue
        if math.hypot(x - 1150, z - 1300) < 20:
            continue
        palm_dead(x, z, 8.4, rng.uniform(0.8, 1.2))
    for _ in range(60):
        x, z = rng.uniform(850, 2350), rng.uniform(950, 2250)
        if math.hypot(x - 1600, z - 1450) < 110:
            continue
        rock(x, z, 8.4, 1.0, "Sandstone", (170, 158, 130))
    scatter(40, 850, 950, 2350, 2250,
            lambda x, z, gy: ruin_fragment(x, z, 8.4)
            if math.hypot(x - 1600, z - 1450) > 110 else None)
    scatter(140, 850, 950, 2350, 2250,
            lambda x, z, gy: grass_tuft(x, z, 8.4, (152, 148, 92)))
    endfolder()


def build_bonefields(parent):
    folder("Bonefields")
    GY = 12.0
    ramp(0, 908, BASE_TOP, 4, 16, 12, "+Z")

    # кладбище
    for gx in range(-5, 6):
        for gz in range(-2, 3):
            if rng.random() < 0.3:
                continue
            x = gx * 22 + rng.uniform(-4, 4)
            z = 1550 + gz * 20 + rng.uniform(-3, 3)
            tombstone(x, z, GY)

    # ограда
    for (ax, az, bx, bz) in [(-140, 1440, 140, 1440), (140, 1440, 140, 1660),
                             (140, 1660, -140, 1660), (-140, 1660, -140, 1440)]:
        seg = 12
        dx, dz = bx - ax, bz - az
        dist = math.hypot(dx, dz)
        n = int(dist // seg)
        yaw = math.degrees(math.atan2(dx, dz))
        for i in range(n + 1):
            t = i / float(n) if n else 0
            px, pz = ax + dx * t, az + dz * t
            part("FencePost", (0.5, 2.4, 0.5), (px, GY + 1.2, pz), color=(60, 56, 50),
                 material="Wood")
            part("FenceRail", (seg, 0.4, 0.4), (px, GY + 1.8, pz), yaw=yaw,
                 color=(66, 60, 52), material="Wood", cancollide=False)

    crypt(300, 1850, GY)
    bone_pit(-450, 1850, GY)

    # дорога к каньону Полой Бездны
    road(250, 1800, -860, 1460, 12.0, width=8, color=(84, 80, 72))

    # лагерь культа у кладбища
    bandit_camp(300, 1200, GY, yaw=160, tent_cols=((60, 50, 66), (52, 44, 60)),
                banner_col=(120, 40, 160), name="CultCamp", ntents=3)

    # --- редколесье и кости ---
    forest_fill("BoneTrees", -880, 820, 880, 2280, density=0.26, cell=175.0,
                trees=("dead_tree", "tree_gloom"), scale=(0.8, 1.3),
                skip=[(0, 1550, 210), (300, 1850, 110), (300, 1200, 105),
                      (-520, 1020, 120), (620, 1450, 100)])

    # --- деревня могильщиков СУХОЙ ЛОГ ---
    small_village("SuhoyLog", 620, 1450, 12.0, n_houses=4, radius=42,
                  pal={"wall": (128, 124, 104), "roof": (72, 70, 60)},
                  palisade=True, sign_text="СУХОЙ ЛОГ\\nмогильщики",
                  well_pos=(620, 1450))

    # --- ХУТОР ОВРАЖНЫЙ: фермерская деревня ---
    house("Khutor_HouseA", -520, 1020, GY, 13, 10, 8, yaw=8, wall=(150, 128, 96),
          roof=(128, 104, 60))
    house("Khutor_HouseB", -556, 1052, GY, 12, 9, 7, yaw=-18, wall=(146, 124, 92),
          roof=(122, 100, 58))
    house("Khutor_HouseC", -486, 1056, GY, 12, 9, 7, yaw=90, wall=(152, 130, 98),
          roof=(130, 106, 62))
    well(-522, 1046, GY)
    stall(-548, 1030, GY, yaw=70)
    farm_field(-560, 990, GY + 0.55, 20, 14, yaw=0)
    farm_field(-470, 992, GY + 0.55, 18, 12, yaw=90)
    scarecrow(-548, 990, GY + 0.55)
    haystack(-478, 1035, GY)
    haystack(-470, 1042, GY)
    haystack(-486, 1046, GY)
    lamppost(-500, 1030, GY)
    signpost(-480, 1010, GY, 90, "ХУТОР ОВРАЖНЫЙ\nфермы")
    road(-100, 1020, -460, 1020, GY, width=6, color=(88, 84, 74), mat="Ground")
    cart_wagon(-430, 1030, GY, yaw=20)

    # холмы и дольмены
    hill_mound(-650, 1000, GY, 26, 12, (124, 128, 88))
    hill_mound(650, 1080, GY, 28, 13, (124, 128, 88))
    hill_mound(-620, 2150, GY, 26, 11, (124, 128, 88))
    hill_mound(720, 2080, GY, 24, 10, (124, 128, 88))
    hill_mound(260, 970, GY, 22, 9, (124, 128, 88))
    standing_stones(-200, 2000, GY)

    # форт-пост на тракте к каньону
    outpost("OutpostBone", -380, 1850, GY, "B")
    signpost(-352, 1882, GY, -15, "Форт-пост Костей")

    for _ in range(150):
        x, z = rng.uniform(-850, 850), rng.uniform(850, 2250)
        if 1440 < z < 1680 and -160 < x < 160:
            continue
        if math.hypot(x - 300, z - 1200) < 40:
            continue
        if math.hypot(x + 520, z - 1020) < 100:
            continue
        if math.hypot(x + 650, z - 1000) < 40 or math.hypot(x - 650, z - 1080) < 40:
            continue
        if math.hypot(x + 620, z - 2150) < 40 or math.hypot(x - 720, z - 2080) < 40:
            continue
        if math.hypot(x + 200, z - 2000) < 30:
            continue
        if math.hypot(x + 380, z - 1850) < 36:
            continue
        dead_tree(x, z, GY, rng.uniform(0.8, 1.3))
    for _ in range(25):
        rock(rng.uniform(-850, 850), rng.uniform(850, 2250), GY, 1.1, "Rock",
             (92, 90, 84))
    scatter(90, -850, 850, 850, 2250,
            lambda x, z, gy: tombstone(x, z, GY),
            excl=[(300, 1850, 30), (0, 1550, 190), (300, 1200, 30),
                  (-520, 1020, 100), (-650, 1000, 40), (650, 1080, 42),
                  (-620, 2150, 40), (720, 2080, 38), (-200, 2000, 22)])
    scatter(40, -850, 850, 850, 2250, lambda x, z, gy: bone_scatter(x, z, GY),
            excl=[(0, 1550, 190)])
    scatter(15, -850, 850, 850, 2250, lambda x, z, gy: ruin_fragment(x, z, GY),
            excl=[(0, 1550, 190)])
    endfolder()


def build_hollow_deep(parent):
    folder("HollowDeep")
    FLOOR = 8.45
    CX, CZ = -2200, 1850

    # каньон
    sx, sz = -850, 1450
    ex, ez = -2050, 1750
    dx, dz = ex - sx, ez - sz
    dist = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz))
    ux, uz = dx / dist, dz / dist
    px, pz = -uz, ux
    n = int(dist // 100)
    for i in range(n + 1):
        t = i / float(n)
        mx, mz = sx + dx * t, sz + dz * t
        for side in (1, -1):
            wx, wz = mx + px * 34 * side, mz + pz * 34 * side
            part("CanyonWall", (105, 34, 13), (wx, FLOOR + 17, wz), yaw=yaw,
                 pitch=rng.uniform(-2, 2), color=(58, 56, 62), material="Slate")
        if i % 2 == 1:
            crystal(mx + rng.uniform(-20, 20), mz + rng.uniform(-20, 20), FLOOR,
                    0.9, rng.choice(["cyan", "violet"]))

    # пещера
    disc("CaveFloor", CX, CZ, FLOOR, 118, 1.0, (45, 44, 50), "Rock")
    dirx, dirz = -2050 - CX, 1750 - CZ
    dl = math.hypot(dirx, dirz)
    dirx, dirz = dirx / dl, dirz / dl
    N = 22
    for k in range(N):
        a = 2 * math.pi * k / N
        vx, vz = math.sin(a), math.cos(a)
        if (vx * dirx + vz * dirz) > 0.88:
            continue
        wx, wz = CX + 110 * vx, CZ + 110 * vz
        part("CaveWall", (36, 46, 12), (wx, FLOOR + 23, wz), yaw=math.degrees(a),
             color=(54, 52, 58), material="Slate")
    # своды
    for gx in (-2290, -2200, -2110):
        for gz in (1790, 1850, 1910):
            part("CaveRoof", (110, 12, 110), (gx, 60, gz), yaw=rng.uniform(0, 30),
                 color=(48, 46, 52), material="Slate")
    for _ in range(8):
        rock(CX + rng.uniform(-100, 100), CZ + rng.uniform(-100, 100), 66, 2.2,
             "Rock", (54, 52, 58))
    # арка входа
    ax, az = CX + 105 * dirx, CZ + 105 * dirz
    perpx, perpz = -dirz, dirx
    for side in (1, -1):
        part("CaveArch", (6, 30, 6), (ax + perpx * 12 * side, FLOOR + 15, az + perpz * 12 * side),
             color=(58, 56, 62), material="Slate")
    part("CaveLintel", (34, 6, 8), (ax, FLOOR + 31, az), yaw=yaw_of(dirx, dirz),
         color=(58, 56, 62), material="Slate")

    # кристаллы внутри
    for _ in range(22):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(20, 95)
        crystal(CX + math.sin(a) * rr, CZ + math.cos(a) * rr, FLOOR,
                rng.uniform(0.9, 1.5), rng.choice(["cyan", "violet"]))

    # дайс и трон Безымянного Короля
    disc("Dais", CX, CZ, FLOOR + 3.4, 30, 2.4, (52, 50, 56), "Basalt")
    disc("DaisStep", CX, CZ, FLOOR + 1.4, 38, 1.2, (48, 46, 52), "Basalt")
    part("Throne_Seat", (7, 5, 4), (CX, FLOOR + 5.9, CZ - 3), color=(40, 38, 45),
         material="Basalt")
    part("Throne_Back", (7, 12, 2), (CX, FLOOR + 10.5, CZ - 5), color=(40, 38, 45),
         material="Basalt")
    for sxx in (-4.5, 4.5):
        part("Throne_Arm", (2, 6, 4), (CX + sxx, FLOOR + 6.9, CZ - 3),
             color=(44, 42, 50), material="Basalt")
    for i in range(6):
        a = math.pi * 2 * i / 6
        brazier(CX + math.sin(a) * 22, CZ + math.cos(a) * 22, FLOOR + 3.4)
    for _ in range(10):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(45, 90)
        part("Bone", (2.6, 0.8, 0.8),
             (CX + math.sin(a) * rr, FLOOR + 0.9, CZ + math.cos(a) * rr),
             yaw=rng.uniform(0, 360), color=(210, 204, 186), material="SmoothPlastic",
             cancollide=False)

    boss_spawn("NamelessKing", CX, CZ, FLOOR + 3.4)
    arena_trigger("NamelessKing", CX, CZ, FLOOR + 3.4, r=105)

    # висячий мост через каньон (виден от входа)
    canyon_sky_bridge(-1450, 1600, yaw=yaw_of(-1200, 300) + 90)

    # паркур: уступы по стенам каньона (спуск ко дну)
    parkour_rocks((-900, 1420), (-1060, 1530), 12, 10, 7,
                  col=(72, 70, 76), tag="Canyon")
    signpost(-890, 1408, 12, 30, "Уступы Бездны ↓\n(спуск в каньон)")
    endfolder()


def yaw_of(dx, dz):
    return math.degrees(math.atan2(dx, dz))


def build_islands(parent):
    folder("Islands")
    spots = [(3300, -900), (-3400, 700), (900, 3400), (-1600, -3300), (2900, 2900)]
    for i, (x, z) in enumerate(spots):
        r = rng.uniform(55, 85)
        add_plateau_circle(x, z, r * 1.05, 4.0)
        disc("Island%d_Sand" % i, x, z, 4.0, r, 6, (188, 172, 134), "Sand")
        part("Island%d_Hill" % i, (r * 0.9, 14, r * 0.9), (x, 8, z), yaw=rng.uniform(0, 90),
             color=(90, 92, 98), material="Rock")
        for t in range(2):
            palm_dead(x + rng.uniform(-r / 2, r / 2), z + rng.uniform(-r / 2, r / 2),
                      4.0, 1.0)
        crystal(x + rng.uniform(-10, 10), z + rng.uniform(-10, 10), 4.0, 1.1,
                rng.choice(["cyan", "violet"]))
        rock(x + rng.uniform(-r / 2, r / 2), z + rng.uniform(-r / 2, r / 2), 4.0, 1.2,
             "Rock", (90, 92, 98))
    endfolder()


# ============================================================================
# v9: НОВЫЕ ЗЕМЛИ — предгорья, архипелаг, южные острова
# ============================================================================
def build_highlands(parent):
    """Дымные Предгорья (юго-запад): высокие холмы, шахты, деревня Каменный Брод."""
    folder("Highlands")
    GY = 26.0
    add_flat(-2900, 1900, 150, 26.0, 90.0)      # Каменный Брод
    add_flat(-2750, 2450, 95, 26.0, 80.0)       # шахта
    add_flat(-3150, 1400, 90, 26.0, 80.0)       # лагерь горных бандитов

    # деревня Каменный Брод
    for i, (dx, dz, yaw) in enumerate([(-30, -20, 12), (26, -18, -20),
                                       (4, 34, 96), (-34, 22, 200), (36, 26, 70)]):
        house("KamenBrod_House%d" % i, -2900 + dx, 1900 + dz, GY, 13, 10, 8,
              yaw=yaw, wall=(150, 140, 124), roof=(92, 74, 58), wall_mat="Slate")
    well(-2896, 1912, GY)
    smithy(-2934, 1876, GY, yaw=20)
    stall(-2870, 1878, GY + 0.55, yaw=-30)
    lamppost(-2880, 1930, GY)
    lamppost(-2920, 1886, GY)
    signpost(-2850, 1900, GY, 90, "КАМЕННЫЙ БРОД\nшахты предгорий")
    for i in range(22):
        a = math.pi * 2 * i / 22
        if angle_gap(a, 1.4) < 0.36:
            continue
        px, pz = -2900 + math.sin(a) * 62, 1900 + math.cos(a) * 62
        part("Brod_Palisade", (1.1, 6.4, 1.1), (px, GY + 2.8, pz),
             yaw=math.degrees(a), color=(96, 78, 58), material="Wood")

    # шахта: вход в скале, рельсы, вагонетка, фонари
    rock(-2750, 2462, GY, 3.0, "Rock", (108, 106, 104))
    part("Mine_Entrance", (10, 9, 5), (-2750, GY + 4.5, 2452),
         color=(56, 50, 46), material="Basalt", cancollide=False)
    for sx in (-6, 6):
        part("Mine_Beam", (1.2, 9.6, 1.2), (-2750 + sx, GY + 4.8, 2445),
             color=(84, 62, 44), material="Wood")
    part("Mine_Lintel", (14, 1.4, 1.4), (-2750, GY + 9.4, 2445),
         color=(84, 62, 44), material="Wood")
    for i in range(9):
        part("Mine_Rail", (1.0, 0.4, 3.0), (-2750, GY + 0.55, 2436 - i * 6),
             color=(96, 96, 102), material="Metal")
    part("Mine_Cart", (4.4, 3.0, 5.4), (-2750, GY + 2.2, 2400),
         color=(90, 74, 58), material="WoodPlanks")
    part("Mine_CartOre", (3.4, 1.2, 4.0), (-2750, GY + 3.9, 2400),
         color=(150, 120, 80), material="Cobblestone")
    chest_marker(-2742, 2398, GY + 0.6, "Mine")
    torch_wall(-2742, 2444, GY + 4.0, 0)
    torch_wall(-2758, 2444, GY + 4.0, 0)

    # лагерь горных бандитов на выступе
    bandit_camp(-3150, 1400, GY, yaw=75, tent_cols=((88, 70, 54), (76, 62, 50)),
                banner_col=(120, 70, 30), name="HighlandBandits", ntents=3)

    # горы и каменные гряды
    wom_mountain(-3250, 2350, GY, base_w=190 * 1.3, h=135 * 1.45, snow=0.66, seed=56)
    wom_mountain(-2650, 2900, GY, base_w=165 * 1.3, h=110 * 1.45, snow=0.66, seed=76)
    wom_mountain(-3450, 950, GY, base_w=150 * 1.3, h=98 * 1.45, snow=0.66, seed=25)
    for _ in range(90):
        x, z = rng.uniform(-3500, -2300), rng.uniform(900, 3000)
        if math.hypot(x + 2900, z - 1900) < 110 or math.hypot(x + 2750, z - 2450) < 90:
            continue
        rock(x, z, sy(x, z, GY), rng.uniform(0.9, 1.8), "Granite", (118, 116, 112))
    for _ in range(45):
        x, z = rng.uniform(-3500, -2300), rng.uniform(900, 3000)
        pine(x, z, sy(x, z, GY), rng.uniform(0.9, 1.5))

    # --- цветы и мелкий быт Предгорий ---
    for _ in range(420):
        fx, fz = rng.uniform(-3400, -2300), rng.uniform(1000, 2900)
        if point_in_poly(fx, fz) and rng.random() < 0.6:
            flower(fx, fz, height_at(fx, fz))
    for _ in range(60):
        x, z = rng.uniform(-3400, -2400), rng.uniform(1000, 2900)
        if rng.random() < 0.4:
            stone_pile(x, z, height_at(x, z))
    endfolder()


def build_archipelago(parent):
    """Северный архипелаг: 6 островов с руинами, гробницами и пиратской бухтой."""
    folder("Archipelago")
    isles = [
        (-2000, -3400, 200, "FrostIsle"),
        (-1150, -3500, 165, "RuinIsle"),
        (-300, -3450, 185, "WolfIsle"),
        (700, -3400, 175, "BoneIsle"),
        (1650, -3300, 190, "PirateIsle"),
        (2500, -3050, 160, "SmokeIsle"),
    ]
    for i, (x, z, r, tag) in enumerate(isles):
        add_plateau_circle(x, z, r * 1.05, 14.0)
        disc(tag + "_Base", x, z, 6.0, r, 12, (176, 168, 140), "Sand")
        disc(tag + "_Hill", x, z, 14.0, r * 0.72, 22, (104, 122, 84), "Ground")
        # скальное основание
        disc(tag + "_Rock", x, z, 0.5, r * 1.02, 16, (88, 88, 92), "Rock")
        for _ in range(14):
            a = rng.uniform(0, math.pi * 2)
            rr = rng.uniform(0, r * 0.6)
            tree_gloom(x + math.sin(a) * rr, z + math.cos(a) * rr, 14.0,
                       rng.uniform(0.7, 1.1))
        for _ in range(10):
            a = rng.uniform(0, math.pi * 2)
            rr = rng.uniform(r * 0.55, r * 0.95)
            rock(x + math.sin(a) * rr, z + math.cos(a) * rr, 6.0,
                 rng.uniform(0.8, 1.4), "Rock", (110, 110, 116))

    # руины и достопримечательности по островам
    ruin_columns(-1150, -3500, 14.0, n=10, spread=80)
    ice_tomb(-2000, -3400, 14.0, yaw=20)
    bandit_camp(1650, -3300, 14.0, yaw=40, tent_cols=((70, 58, 48), (60, 50, 44)),
                banner_col=(40, 70, 120), name="PirateCove", ntents=3)
    watch_tower(-300, -3450, 14.0, tag="WolfIsle")
    crypt(700, -3400, 14.0)
    volcano(2500, -3050, 10.0)
    for (x, z, tag) in [(-1150, -3420, "RuinIsle"), (700, -3320, "BoneIsle"),
                        (-2000, -3320, "FrostIsle")]:
        chest_marker(x, z, 14.8, tag)

    # каменные арки-мосты между двумя ближними островами
    for i in range(11):
        t = i / 10.0
        ax = -1150 + (-300 + 1150) * t
        az = -3500 + (-3450 + 3500) * t
        part("ArchBridge", (26, 1.2, 16), (ax, 15.0 + math.sin(t * math.pi) * 8, az),
             yaw=math.degrees(math.atan2(-300 + 1150, -3450 + 3500)),
             color=(120, 116, 108), material="Cobblestone")
    endfolder()


def build_south_isles(parent):
    """Южные острова: рыбацкие деревни, маяк-близнец, коралловые отмели."""
    folder("SouthIsles")
    isles = [
        (-900, 3400, 210, "FisherIsle"),
        (500, 3450, 180, "CornIsle"),
        (2100, 3300, 200, "TwinLightIsle"),
        (3100, 2400, 170, "CoralIsle"),
    ]
    for (x, z, r, tag) in isles:
        add_plateau_circle(x, z, r * 1.05, 12.0)
        disc(tag + "_Base", x, z, 5.0, r, 10, (200, 186, 148), "Sand")
        disc(tag + "_Ground", x, z, 12.0, r * 0.7, 18, (108, 130, 80), "Ground")
        for _ in range(16):
            a = rng.uniform(0, math.pi * 2)
            rr = rng.uniform(0, r * 0.65)
            palm_dead(x + math.sin(a) * rr, z + math.cos(a) * rr, 12.0, 1.1)
        for _ in range(8):
            a = rng.uniform(0, math.pi * 2)
            rr = rng.uniform(r * 0.5, r * 0.95)
            rock(x + math.sin(a) * rr, z + math.cos(a) * rr, 5.0,
                 rng.uniform(0.7, 1.3), "Rock", (116, 112, 104))

    # деревня рыбаков
    for i, (dx, dz, yaw) in enumerate([(-26, -16, 10), (24, -20, -14), (2, 30, 90)]):
        house("Fisher_House%d" % i, -900 + dx, 3400 + dz, 12.0, 12, 9, 7,
              yaw=yaw, wall=(150, 132, 104), roof=(74, 92, 96))
    for i in range(4):
        part("Fisher_Pier", (5, 1, 34), (-900 + i * 16, 8.0, 3400 + 150),
             color=(96, 78, 58), material="WoodPlanks")
    campfire(-880, 3400, 12.0)
    chest_marker(-870, 3410, 12.6, "FisherIsle")

    # маяк-близнец (v12: строго на берегу, не посреди города)
    # маяк на собственном маленьком островке, соединённом с берегом мостиком
    add_plateau_circle(2380, 3510, 96, 12.0)
    disc("TwinLightIslet_Sand", 2380, 3510, 5.0, 92, 8, (200, 186, 148), "Sand")
    disc("TwinLightIslet_Ground", 2380, 3510, 12.0, 60, 16, (108, 130, 80), "Ground")
    lighthouse(2380, 3510, 12.0)
    for i in range(9):
        part("TwinLight_Bridge", (12, 0.8, 14), (2280 + i * 11, 12.4, 3428 + i * 9),
             yaw=-40, color=(96, 78, 58), material="WoodPlanks")
    for i, (x, z) in enumerate([(500, 3450), (2100, 3260), (3100, 2360)]):
        crystal(x, z, 12.0, 1.2, rng.choice(["cyan", "violet"]))
    farm_field(500, 3450, 12.55, 26, 18, yaw=20)
    scarecrow(500, 3430, 12.55)
    endfolder()



# ============================================================================
# v11: ГУСТЫЕ ЛЕСА — «стены» деревьев с полянами и тропами
# ============================================================================
def dense_forest(name, x0, z0, x1, z1, density=0.80, cell=84.0,
                 trees=("tree_nice", "tree_nice", "pine"), scale=(1.4, 2.4),
                 clearance=(), floor_col=(58, 86, 48), floor_mat="Ground",
                 glow=False, giants=0):
    """ГУСТАЯ ЧАЩА: крупные деревья почти вплотную, валежник, папоротники.
    Деревья нарочно большие (1.4–2.4×), поэтому лес читается как стена зелени
    даже при умеренном числе деталей."""
    funcs = {"tree_nice": tree_nice, "tree_gloom": tree_gloom, "pine": pine,
             "dead_tree": dead_tree, "palm_dead": palm_dead}
    x = x0
    while x <= x1:
        z = z0
        while z <= z1:
            if point_in_poly(x, z):
                skip_here = False
                for (cx, cz, cr) in clearance:
                    if math.hypot(x - cx, z - cz) < cr:
                        skip_here = True
                        break
                # v12: лес не сажается на дома, дороги, горы и входы в данжи
                if not skip_here and is_free(x, z, 16) and rng.random() < density:
                    h = height_at(x, z)
                    if h > -0.5:
                        fn = funcs[rng.choice(list(trees))]
                        fn(x + rng.uniform(-22, 22), z + rng.uniform(-22, 22), h,
                           rng.uniform(*scale))
                        if rng.random() < 0.55:
                            fn(x + rng.uniform(-30, 30), z + rng.uniform(-30, 30), h,
                               rng.uniform(*scale) * 0.8)
                        if rng.random() < 0.5:
                            bush(x + rng.uniform(-36, 36), z + rng.uniform(-36, 36), h,
                                 rng.uniform(1.2, 2.2))
                        if rng.random() < 0.45:
                            fern(x + rng.uniform(-38, 38), z + rng.uniform(-38, 38), h)
                        if rng.random() < 0.30:
                            fallen_log(x + rng.uniform(-38, 38),
                                       z + rng.uniform(-38, 38), h)
                        if rng.random() < 0.10:
                            stone_pile(x + rng.uniform(-38, 38),
                                       z + rng.uniform(-38, 38), h)
                        if glow and rng.random() < 0.28:
                            glowshroom(x + rng.uniform(-36, 36),
                                       z + rng.uniform(-36, 36), h)
            z += cell
        x += cell
    # деревья-исполины (маяки леса)
    for _ in range(giants):
        gx = rng.uniform(x0, x1)
        gz = rng.uniform(z0, z1)
        if not point_in_poly(gx, gz):
            continue
        if any(math.hypot(gx - cx, gz - cz) < cr + 30 for (cx, cz, cr) in clearance):
            continue
        ancient_tree(gx, gz, height_at(gx, gz), rng.uniform(2.6, 3.8))
    # «подстилка» под кронами: тёмные пятна, чтобы лес читался как чаща
    for _ in range(int(((x1 - x0) * (z1 - z0)) / 70000)):
        gx = rng.uniform(x0, x1)
        gz = rng.uniform(z0, z1)
        if not point_in_poly(gx, gz):
            continue
        if any(math.hypot(gx - cx, gz - cz) < cr + 20 for (cx, cz, cr) in clearance):
            continue
        if not is_free(gx, gz, 6):
            continue
        disc("ForestFloor_" + name, gx, gz, height_at(gx, gz) + 0.22,
             rng.uniform(55, 110), 0.5, floor_col, floor_mat, cancollide=False)


# ============================================================================
# v11: НОВЫЕ ЗЕМЛИ — города, чащи, горная цепь, побережье и подземелья
# ============================================================================
def build_v11_forests(parent):
    """v11: густые чащи по всем новым землям (без домов, дорог и данжей)."""
    folder("ForestsV11")
    clearance = [
        # юг
        (150, 2500, 300), (-560, 2600, 240), (-150, 1800, 120), (700, 2200, 120),
        (-900, 2100, 110), (400, 3000, 150), (-1200, 2600, 140), (900, 2900, 140),
        # восток
        (2600, 830, 330), (3000, 1400, 300), (2350, 500, 140), (2900, -100, 170),
        (2200, -800, 140), (3200, 300, 160),
        # предгорья
        (-3150, 2600, 340), (-2700, 3000, 270), (-3450, 1700, 250),
        (-2550, 2000, 250), (-3000, 2300, 120), (-3350, 2450, 130),
        # север
        (-1950, -620, 250), (-900, -380, 310), (-1420, -500, 60),
        # архипелаг / южные острова / пустоши / топи / мороз
        (1650, -3300, 310), (2100, 3300, 300), (-500, -1900, 220),
        (1620, -200, 230), (-2050, -1750, 250),
    ]
    groups = [
        # (имя, x0, z0, x1, z1, density, cell, trees, scale)
        ("Veldt", -1300, 1650, 1000, 3250, 0.82, 82.0,
         ("tree_nice", "tree_nice", "pine"), (1.5, 2.5), 26),
        ("VeldtEast", 1000, 2600, 2100, 3350, 0.72, 92.0,
         ("tree_nice", "palm_dead"), (1.4, 2.2), 8),
        ("EastWood", 2150, -400, 3300, 1250, 0.84, 82.0,
         ("tree_nice", "tree_nice", "pine"), (1.5, 2.6), 22),
        ("EastRidge", 2700, 1250, 3450, 2100, 0.70, 92.0,
         ("pine", "tree_nice"), (1.3, 2.2), 10),
        ("HighlandPine", -3500, 1150, -2350, 2400, 0.74, 88.0,
         ("pine", "pine", "tree_nice"), (1.2, 2.1), 14),
        ("HighlandPine2", -3450, 2400, -2350, 3050, 0.66, 92.0,
         ("pine", "tree_nice"), (1.2, 2.0), 8),
        ("NorthThicket", -2350, -880, -650, -250, 0.86, 78.0,
         ("tree_gloom", "tree_nice", "pine"), (1.4, 2.4), 18),
    ]
    for (fname, x0, z0, x1, z1, dens, cell, trees, scl, ng) in groups:
        dense_forest(fname, x0, z0, x1, z1, density=dens, cell=cell, trees=trees,
                     scale=scl, clearance=clearance, giants=ng,
                     glow=(fname == "NorthThicket"))


# ============================================================================
# v11: ЗАПЕЧАТАННЫЕ ПИКИ — горный хребет (самые высокие горы на карте)
# ============================================================================
    endfolder()


def mountain_range(name, points, gy, base_w=150, h=180, snow=0.62,
                   seed=0, caves=True):
    """Цепь гор: у каждой вершины ступенчатый конус (шаг 2.5), тропа по спирали,
    снежная шапка и пещера у подножия. Всё проходимо пешком."""
    tops = []
    for idx, (mx, mz) in enumerate(points):
        add_flat(mx, mz, base_w * 0.80, gy, 95.0)
        n = max(6, int(h / 2.5))
        tier_h = h / float(n)
        w = base_w
        shrink = base_w * 0.052
        for i in range(n):
            y = gy + i * tier_h
            t = i / float(n - 1)
            col = (int(96 + t * 34), int(100 + t * 34), int(108 + t * 38))
            mat = "Rock"
            if t > snow:
                col, mat = (228, 234, 242), "Snow"
            part("%s_Tier%d_%d" % (name, idx, i), (w, tier_h + 0.35, w),
                 (mx, y + tier_h / 2, mz), yaw=(i * 9 + seed * 13) % 180,
                 color=tuple(min(255, c + rng.randint(-4, 4)) for c in col),
                 material=mat)
            if i % 2 == 0:
                for k in range(4):
                    a = math.pi * 2 * k / 4 + i * 0.8
                    gx = mx + math.sin(a) * w * 0.47
                    gz = mz + math.cos(a) * w * 0.47
                    part("%s_Rubble%d_%d_%d" % (name, idx, i, k),
                         (rng.uniform(7, 13), tier_h * 0.9, rng.uniform(7, 13)),
                         (gx, y + tier_h * 0.45, gz), yaw=math.degrees(a),
                         color=col, material=mat)
            w = max(26.0, w - shrink)
        top_y = gy + h
        part("%s_Cap%d" % (name, idx), (w * 1.6, tier_h * 2.2, w * 1.6),
             (mx, top_y + tier_h * 0.8, mz), shape="Ball",
             color=(236, 242, 250), material="Snow", cancollide=False)
        part("%s_Summit%d" % (name, idx), (16, 1.2, 16), (mx, top_y + 0.7, mz),
             color=(92, 76, 58), material="WoodPlanks")
        chest_marker(mx + 4, mz + 4, top_y + 1.5, "%s%d" % (name, idx))
        pn = max(9, int(h / 11))
        for i in range(pn):
            t = i / float(pn - 1)
            a = t * math.pi * 3.6 + idx + seed
            rr = base_w * 0.58 * (1.0 - t * 0.74)
            part("%s_Path%d_%d" % (name, idx, i), (11, 1.1, 8),
                 (mx + math.sin(a) * rr, gy + t * (h - 4), mz + math.cos(a) * rr),
                 yaw=math.degrees(a) + 90, color=(118, 116, 112), material="Rock")
            if i % 5 == 0:
                torch_wall(mx + math.sin(a) * rr, mz + math.cos(a) * rr,
                           gy + t * (h - 4) + 1, 0)
        if caves:
            a = math.pi * 2 * idx / max(1, len(points)) + 0.7
            cave_system("%s Cave%d" % (name, idx),
                        mx + math.sin(a) * base_w * 0.52,
                        mz + math.cos(a) * base_w * 0.52, gy, depth=18.0,
                        nodes=((70, 30), (150, 110)), width=17, height=13,
                        tag="%sCave%d" % (name, idx), extra_chests=2,
                        cap_col=(96, 92, 86), cap_mat="Rock")
        tops.append((mx, mz, top_y))
    return tops


def build_sealed_peaks(parent):
    """ЗАПЕЧАТАННЫЕ ПИКИ: хребет КВАДРАТНЫХ гор (в стиле World of Magic)."""
    folder("SealedPeaks")
    GY = 18.0
    east = [(2320, 1080), (2620, 1560), (2440, 2060), (2060, 2540),
            (1560, 2960), (960, 3240)]
    north = [(2740, -1160), (3120, -390)]
    south = [(-260, 3300), (360, 3330)]
    res = []
    res += mountain_chain("WM_East", east, GY, base_w=190, h=175, snow=0.60, seed=3)
    res += mountain_chain("WM_North", north, GY, base_w=170, h=160, snow=0.62, seed=17)
    res += mountain_chain("WM_South", south, GY, base_w=160, h=145, snow=0.68, seed=29)
    # перевал: дорога между двумя горами
    road(2280, 900, 2400, 1300, GY, width=9, color=(110, 106, 98))
    signpost(2300, 900, GY, 180, "ЗАПЕЧАТАННЫЕ ПИКИ\nквадратные горы · перевал")
    for (mx, mz, ty) in res:
        register_mob("Highlands", mx + 130, mz + 70, GY)
    endfolder()


def build_gloomwood_north(parent):
    """Северная чаща: ВЕЛИКАЯ РОЩА с исполинами, тропа между городами,
    Пещеры Дупла (данж) и быт лесорубов (дома стоят из build_v12_settlements)."""
    folder("GloomNorth")
    GY = 14.0
    giants = [(-1500, -150), (-1250, -60), (-1700, -420), (-1050, -520),
              (-1450, 140), (-760, -140), (-2050, -120), (-1600, -760),
              (-1180, -890), (-2150, -370)]
    for (gx, gz) in giants:
        if not is_free(gx, gz, 30):
            continue
        ancient_tree(gx, gz, GY, rng.uniform(3.4, 4.6))
        occupy(gx, gz, 34, "decor")
        for k in range(3):
            a = rng.uniform(0, math.pi * 2)
            mushroom(gx + math.sin(a) * rng.uniform(18, 34),
                     gz + math.cos(a) * rng.uniform(18, 34), GY, rng.uniform(1.2, 2.2))
    road(-1950, -620, -900, -380, GY, width=8, color=(72, 62, 48), mat="Ground")
    signpost(-1420, -500, GY, 60, "ВЕЛИКАЯ РОЩА\nисполины")

    # пилорама Дуплино
    for i in range(6):
        part("Duplino_Log", (14, 1.8, 1.8), (-1950 + rng.uniform(-40, 40),
             -690 + i * 2.4, GY + 0.9), yaw=rng.uniform(-8, 8),
             color=(96, 72, 50), material="Wood")
    part("Duplino_Sawmill", (18, 1.2, 12), (-1950, GY + 1.2, -560),
         color=(104, 78, 54), material="WoodPlanks")
    for sx in (-8, 8):
        part("Duplino_SawPost", (1.2, 8, 1.2), (-1950 + sx, GY + 4, -560),
             color=(84, 62, 44), material="Wood")
    chest_marker(-1942, -556, GY + 1.6, "Duplino")
    # ворота Эльдервуда из костяных стволов
    for side in (-1, 1):
        part("Elderwood_Gate", (3.2, 16, 3.2), (-900 + side * 13, GY + 8, -484),
             yaw=10, color=(70, 54, 42), material="Wood")
    part("Elderwood_GateLintel", (30, 2.6, 3.4), (-900, GY + 16.5, -484),
         color=(74, 58, 44), material="Wood")

    cave_system("Пещеры Дупла", -1950, -780, GY, depth=18.0,
                nodes=((95, 40), (185, 130), (110, 240), (230, 300)),
                width=20, height=15, floor_mat="Slate", floor_col=(56, 52, 48),
                tag="DuplinoCave", extra_chests=3,
                cap_col=(88, 74, 58), cap_mat="Wood")
    register_mob("Gloomwood", -1860, -700, GY)
    register_mob("Gloomwood", -2030, -690, GY)
    npc_spot("Woodcutter", -1930, -600, GY)
    endfolder()


def build_south_veldt(parent):
    """Южный вельд: КРАСНЫЙ КАНЬОН с висячими мостами и уступами,
    каменный мост у Заречья и Шахта «Красный Камень» (данж)."""
    folder("SouthVeldt")
    GY = 12.0
    stone_footbridge(150, 2380, GY, yaw=0, span=64, width=8)
    signpost(210, 2410, GY, -80, "КАМЕННЫЙ МОСТ\n→ Костяные Поля")

    cx, cz = -560, 2620
    for i in range(26):
        t = i / 25.0
        wx = cx + (t - 0.5) * 700
        for side in (1, -1):
            part("Veldt_CanyonWall", (60, rng.uniform(38, 58), 26),
                 (wx, GY + 24, cz + side * rng.uniform(120, 165)),
                 yaw=rng.uniform(-6, 6), color=(186, 118, 82), material="Sandstone")
            occupy(wx, cz + side * 140, 32, "mountain")
        if i % 3 == 0:
            crystal(wx, cz - 130, GY + 40, 1.1, "violet")
    canyon_sky_bridge(cx, cz, yaw=0, span=260, width=9, deck_y=GY + 54, base_y=GY + 50)
    for i in range(3):
        part("Veldt_Ledge", (26, 2.4, 12),
             (cx - 220 + i * 220, GY + 30 + i * 8, cz + 60),
             color=(176, 112, 78), material="Sandstone")
    parkour_rocks((cx - 300, cz + 40), (cx - 120, cz - 20), GY + 46, GY + 4, 9,
                  col=(184, 122, 86), tag="Veldt")
    register_mob("Bonefields", cx - 240, cz, GY + 2)
    register_mob("Bonefields", cx + 140, cz + 40, GY + 2)

    cave_system("Шахта Красный Камень", 120, 2680, GY, depth=20.0,
                nodes=((90, 30), (180, 120), (90, 200)),
                width=19, height=14, floor_mat="Slate", floor_col=(92, 64, 50),
                boss="MarrowTyrant", tag="RedMine", extra_chests=3,
                cap_col=(180, 116, 80), cap_mat="Sandstone")
    npc_spot("Prospector", 120, 2620, GY)
    endfolder()


def build_terraces(parent):
    """Восточные террасы: башня Арканума, паркур-платформы и рисовые ступени."""
    folder("Terraces")
    GY = 16.0
    add_flat(2600, 830, 230, GY, 100.0)
    # башня магов (город ставится отдельно в build_v12_settlements)
    v_cyl("Arcanum_TowerA", 2600, 900, GY, 78, 20, (168, 158, 196), "Concrete")
    for i in range(6):
        part("Arcanum_TowerRing%d" % i, (26, 1.6, 26), (2600, GY + 14 + i * 12, 900),
             yaw=i * 9, color=(150, 142, 178), material="Slate")
    part("Arcanum_TowerCap", (24, 12, 24), (2600, GY + 88, 900), shape="Ball",
         color=(96, 84, 150), material="Neon", cancollide=False,
         light=dict(brightness=2.2, range=90, color=(150, 120, 255)))
    part("Arcanum_TowerSpire", (1.6, 24, 1.6), (2600, GY + 104, 900),
         color=(70, 60, 110), material="Metal")
    occupy(2600, 900, 40, "build")
    for i in range(7):
        a = i * 0.9
        rr = 120 - i * 12
        part("Arcanum_Plat%d" % i, (10, 1.0, 10),
             (2600 + math.sin(a) * rr, GY + 12 + i * 11, 830 + math.cos(a) * rr),
             yaw=i * 21, color=(140, 132, 176), material="Slate")
    chest_marker(2600, 900, GY + 90, "Arcanum")

    for i in range(16):
        tx = 2980 + i * 46
        part("Terrace_Step%d" % i, (150, 2.2, 420),
             (tx, GY - i * 2.4, 1400), yaw=0,
             color=(126, 156, 84) if i % 2 == 0 else (110, 142, 74),
             material="Ground")
        part("Terrace_Water%d" % i, (140, 0.5, 400),
             (tx, GY - i * 2.4 + 1.3, 1400), color=(56, 96, 118), material="Water",
             transparency=0.25, cancollide=False)
        part("Terrace_Wall%d" % i, (3, 5, 420), (tx + 75, GY - i * 2.4 - 1.2, 1400),
             color=(150, 132, 100), material="Sandstone")
        occupy(tx, 1400, 90, "build")
    for i in range(6):
        house("Terrace_Farm%d" % i, 3040 + i * 88, 1560 + (i % 2) * 60,
              GY - int(i * 1.4) * 2.4, 10, 8, 6.5,
              yaw=rng.uniform(-20, 20), wall=(150, 132, 100), roof=(96, 74, 52))
    signpost(2970, 1180, GY, 0, "РИСОВЫЕ ТЕРРАСЫ\nступени к морю")
    register_mob("SunkenCoast", 2900, 700, GY)
    register_mob("Archipelago", 3120, 1200, GY)
    npc_spot("Archmage", 2540, 880, GY)
    npc_spot("RiceFarmer", 3040, 1500, GY)
    endfolder()


def build_highlands_new(parent):
    """Предгорья: КАМНЕГОРСК-крепость, квадратные горы и Забытые Шахты (данж)."""
    folder("HighlandsNew")
    GY = 26.0
    add_flat(-3150, 2600, 240, GY, 100.0)

    # город Камнегорск ставится первым в build_v12_settlements

    # ---- КВАДРАТНЫЕ ГОРЫ Предгорий ----
    mountain_chain("WM_HighA", [(-2700, 3000), (-2400, 2790)], GY,
                   base_w=190, h=175, snow=0.7, seed=41)
    mountain_chain("WM_HighB", [(-3450, 1700), (-3250, 1450)], GY,
                   base_w=170, h=150, snow=0.72, seed=53)

    # ---- ПИК ВЕТРОВ: отдельная квадратная гора с ареной наверху ----
    peak_x, peak_z = -2550, 2000
    top = wom_mountain(peak_x, peak_z, GY, base_w=175, h=190, snow=0.55,
                       seed=61, col=(146, 152, 164), cave=False, tag="WindPeak")
    part("WindPeak_Altar", (14, 2.2, 14), (peak_x, top + 1.6, peak_z),
         color=(128, 140, 156), material="Marble")
    for i in range(6):
        a = math.pi * 2 * i / 6
        part("WindPeak_Pillar%d" % i, (3, 12, 3),
             (peak_x + math.sin(a) * 22, top + 7, peak_z + math.cos(a) * 22),
             color=(150, 158, 172), material="Marble")
    boss_spawn("WindArchon", peak_x, peak_z, top + 2.6)
    arena_trigger("WindArchon", peak_x, peak_z, top + 2.6, r=70)
    signpost(-2900, 2620, GY, 20, "ПИК ВЕТРОВ ↑\nарена Архипастыря")
    road(-3150, 2620, -2650, 2100, GY, width=10, color=(112, 106, 96))

    # ---- ЗАБЫТЫЕ ШАХТЫ ----
    cave_system("Забытые Шахты", -2820, 2380, GY, depth=20.0,
                nodes=((100, 40), (210, 120), (120, 230), (250, 300), (150, 380)),
                width=22, height=16, floor_mat="Slate", floor_col=(86, 74, 62),
                boss="StoneWarden", tag="OldMine", extra_chests=4,
                cap_col=(120, 112, 100), cap_mat="Granite")
    for i in range(10):
        part("OldMine_Rail", (1.2, 0.5, 6), (-2820, GY + 0.5, 2350 - i * 8),
             color=(96, 96, 102), material="Metal")
    part("OldMine_Cart", (4.4, 3, 5.4), (-2820, GY + 2.2, 2300),
         color=(90, 74, 58), material="WoodPlanks")
    register_mob("Highlands", -3000, 2500, GY)
    register_mob("Highlands", -3250, 2700, GY)
    register_mob("Highlands", -2600, 2300, GY)
    npc_spot("MineOverseer", -3110, 2340, GY)
    endfolder()


def build_archipelago_new(parent):
    """Свободная Гавань: корабли, причалы, маяк и ЗАТОНУВШИЙ ФРЕГАТ (данж)."""
    folder("ArchipelagoNew")
    GY = 14.0
    for (sx, sz, syaw, sc) in [(1560, -3160, 12, 1.0), (1740, -3150, -8, 0.9),
                               (1650, -3080, 30, 1.15)]:
        ship(sx, sz, 0.0, yaw=syaw, size=sc, col=(84, 66, 48))
    dock("HarborDockA", 1650, -3180, 0.0, length=110, width=13, yaw=0)
    dock("HarborDockB", 1770, -3200, 0.0, length=84, width=11, yaw=20)
    lighthouse(1520, -3400, GY)
    signpost(1650, -3420, GY, 180, "СВОБОДНАЯ ГАВАНЬ\nпиратский порт")

    cave_system("Затонувший Фрегат", 1860, -3120, GY, depth=18.0,
                nodes=((75, 30), (160, 110), (95, 190)),
                width=20, height=15, floor_mat="WoodPlanks", floor_col=(80, 62, 46),
                boss="PirateAdmiral", tag="DrownedShip", extra_chests=3,
                cap_col=(56, 58, 62), cap_mat="Slate")
    for i in range(3):
        part("DrownedShip_Mast%d" % i, (1.6, 42 + i * 8, 1.6),
             (1860 + i * 14 - 14, GY + 24, -3020), color=(70, 54, 40),
             material="Wood", pitch=rng.uniform(-12, 12))
    part("DrownedShip_Deck", (56, 2.4, 22), (1860, GY + 3, -3010), yaw=14,
         color=(84, 66, 48), material="WoodPlanks")
    for i in range(10):
        part("DrownedShip_Rib%d" % i, (2, 16, 2), (1830 + i * 6, GY + 8, -3006),
             yaw=rng.uniform(-16, 16), pitch=rng.uniform(-10, 10),
             color=(76, 58, 42), material="Wood")
    register_mob("Archipelago", 1700, -3250, GY)
    register_mob("Archipelago", 1560, -3230, GY)
    npc_spot("PirateCaptain", 1600, -3300, GY)
    endfolder()


def build_south_isles_new(parent):
    """Пальмовый Берег: пальмы, маяк и КОРАЛЛОВЫЙ ГРОТ (данж)."""
    folder("SouthIslesNew")
    GY = 12.0
    for i in range(24):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(140, 200)
        px, pz = 2100 + math.sin(a) * rr, 3300 + math.cos(a) * rr
        if not is_free(px, pz, 14):
            continue
        palm_dead(px, pz, GY, rng.uniform(1.0, 1.5))
        occupy(px, pz, 10, "decor")
    cave_system("Коралловый Грот", 1980, 3420, GY, depth=16.0,
                nodes=((80, 20), (170, 90), (100, 160)),
                width=19, height=14, floor_mat="Sandstone", floor_col=(128, 122, 112),
                boss="CoralQueen", tag="CoralGrotto", extra_chests=3,
                cap_col=(186, 172, 146), cap_mat="Sandstone")
    for i in range(16):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(40, 130)
        crystal(1980 + math.sin(a) * rr, 3420 + math.cos(a) * rr, GY,
                rng.uniform(0.9, 1.6), "violet" if i % 2 else "cyan")
    register_mob("SouthIsles", 2050, 3350, GY)
    register_mob("SouthIsles", 2160, 3250, GY)
    npc_spot("Islander", 2150, 3320, GY)
    endfolder()


def build_ashwaste_new(parent):
    """Пустоши: КУЗНЯ В ЖЕРЛЕ (данж внутри вулкана) + мёртвый город у лавы."""
    folder("AshwasteNew")
    GY = 16.0

    # ---- КУЗНЯ В ЖЕРЛЕ: данж в теле вулкана (300,-2250) ----
    cave_system("Кузня в Жерле", 220, -2080, GY, depth=30.0,
                nodes=((95, 40), (200, 130), (300, 120), (230, 240)),
                width=23, height=17, floor_mat="Basalt", floor_col=(64, 44, 40),
                boss="VolcanoForge", tag="Forge", extra_chests=4,
                cap_col=(46, 40, 44), cap_mat="Basalt")
    for i in range(6):
        a = math.pi * 2 * i / 6
        lava_pool(220 + math.sin(a) * 36, -2080 + math.cos(a) * 36, GY, 9)
    part("Forge_Anvil", (6, 3, 4), (250, GY + 1.5, -2140), color=(56, 52, 56),
         material="Metal")
    part("Forge_Chimney", (6, 30, 6), (196, GY + 15, -2076),
         color=(52, 46, 44), material="Basalt")
    part("Forge_Glow", (2, 2, 2), (196, GY + 31, -2076), color=(255, 130, 40),
         material="Neon", cancollide=False,
         light=dict(brightness=2.0, range=44, color=(255, 130, 40)))

    # ---- МЁРТВЫЙ ГОРОД АШ-КАРАН: разрушенные дома у лавы ----
    acx, acz = -500, -1900
    add_flat(acx, acz, 160, GY, 90.0)
    disc("AshKaran_Square", acx, acz, GY + 0.5, 60, 0.9, (76, 66, 60), "Cobblestone")
    for i in range(10):
        a = math.pi * 2 * i / 10 + 0.3
        hx = acx + math.sin(a) * rng.uniform(55, 115)
        hz = acz + math.cos(a) * rng.uniform(55, 115)
        hw = rng.uniform(12, 17)
        hh = rng.uniform(9, 15)
        part("AshKaran_WallA", (hw, hh, 2), (hx, GY + hh / 2, hz), yaw=math.degrees(a),
             color=(74, 62, 56), material="Slate")
        part("AshKaran_WallB", (2, hh * 0.8, hw * 0.8),
             (hx + math.cos(a) * hw / 2, GY + hh * 0.4, hz - math.sin(a) * hw / 2),
             yaw=math.degrees(a), color=(70, 58, 52), material="Slate")
        if rng.random() < 0.7:
            part("AshKaran_Roof", (hw, 1.6, hw * 0.7),
                 (hx, GY + hh + 1.2, hz), yaw=math.degrees(a) + rng.uniform(-30, 30),
                 pitch=rng.uniform(-14, 14), color=(60, 52, 48), material="Slate",
                 cls="WedgePart")
    for i in range(8):
        a = math.pi * 2 * i / 8
        part("AshKaran_Column", (2.6, rng.uniform(8, 14), 2.6),
             (acx + math.sin(a) * 44, GY + 6, acz + math.cos(a) * 44),
             pitch=rng.uniform(-10, 10), color=(90, 84, 78), material="Marble")
    for _ in range(26):
        a = rng.uniform(0, math.pi * 2)
        rr = rng.uniform(20, 150)
        lava_pool(acx + math.sin(a) * rr, acz + math.cos(a) * rr, GY,
                  rng.uniform(6, 16))
    signpost(acx, acz - 70, GY, 0, "АШ-КАРАН\nмёртвый город")
    register_mob("Ashwaste", acx + 60, acz + 40, GY)
    register_mob("Ashwaste", acx - 70, acz - 30, GY)
    npc_spot("AshenSmith", 240, -2110, GY)
    endfolder()
    return GY


def build_mirefen_new(parent):
    """Топи: ЗАТОНУВШИЙ ХРАМ ГНИЛИ (данж на воде) + ГНИЛЬЦЫ (деревня на сваях)."""
    folder("MirefenNew")
    GY = 12.0

    # ---- ГНИЛЬЦЫ уже есть, добавляем свайный квартал и храм ----
    for i in range(10):
        a = math.pi * 2 * i / 10
        house("Stilt_House%d" % i, 1750 + math.sin(a) * rng.uniform(60, 110),
              700 + math.cos(a) * rng.uniform(60, 110), GY, 11, 9, 7,
              yaw=math.degrees(a) + 90, wall=(110, 108, 78), roof=(74, 82, 56))
        part("Stilt_Post", (1.2, 7, 1.2),
             (1750 + math.sin(a) * 72, GY + 3.5, 700 + math.cos(a) * 72),
             color=(70, 62, 46), material="Wood")
    # ---- ЗАТОНУВШИЙ ХРАМ: данж под водой/болотом ----
    cave_system("Затонувший Храм Гнили", 1620, -200, GY, depth=22.0,
                nodes=((90, 40), (190, 140), (110, 250)),
                width=21, height=15, floor_mat="Slate", floor_col=(62, 72, 52),
                boss="BogHydra", tag="RotTemple", extra_chests=3,
                cap_col=(74, 84, 60), cap_mat="Cobblestone")
    # руины храма над данжем
    for i in range(12):
        a = math.pi * 2 * i / 12
        part("RotTemple_Column", (3, rng.uniform(8, 16), 3),
             (1620 + math.sin(a) * 60, GY + 7, -200 + math.cos(a) * 60),
             pitch=rng.uniform(-8, 8), color=(84, 94, 70), material="Slate")
    part("RotTemple_Altar", (10, 2.6, 10), (1620, GY + 1.4, -200),
         color=(92, 104, 76), material="Slate")
    for i in range(6):
        glowshroom(1620 + rng.uniform(-70, 70), -200 + rng.uniform(-70, 70), GY)
    register_mob("Mirefen", 1680, -260, GY)
    register_mob("Mirefen", 1560, -140, GY)
    npc_spot("BogPriest", 1620, -300, GY)
    endfolder()
    return GY


def build_frostpeak_new(parent):
    """Морозные Пики: ЛОГОВО ЛЕДЯНОГО ЗМЕЯ в леднике + ледяные арки."""
    folder("FrostpeakNew")
    GY = 20.0

    cave_system("Логово Ледяного Змея", -2050, -1750, GY, depth=24.0,
                nodes=((100, 40), (200, 120), (120, 220), (240, 280)),
                width=22, height=16, floor_mat="Glacier", floor_col=(140, 176, 206),
                boss="GlacierWyrm", tag="WyrmLair", extra_chests=4,
                cap_col=(196, 214, 232), cap_mat="Glacier")
    for i in range(18):   # ледяные шипы над логовом
        ice_spike_cluster(-2150 + rng.uniform(-80, 200), -1750 + rng.uniform(-80, 220),
                          GY)
    for i in range(8):
        a = math.pi * 2 * i / 8
        part("Wyrm_Rib", (2.6, rng.uniform(16, 26), 2.6),
             (-2050 + math.sin(a) * 70, GY + 10, -1750 + math.cos(a) * 70),
             pitch=rng.uniform(-14, 14), color=(176, 206, 232), material="Glacier")
    register_mob("Frostpeak", -1980, -1700, GY)
    register_mob("Frostpeak", -2130, -1810, GY)
    npc_spot("IceScholar", -2050, -1650, GY)
    endfolder()
    return GY


def build_v12_settlements(parent):
    """v12 «ВСЁ ПО МЕСТАМ»: все города, деревни и лагеря стоят ПЕРВЫМИ.
    Дальше лес, горы и декор сами обходят занятые места (реестр OCCUPIED),
    поэтому ничего не растёт сквозь дома и не висит на крышах."""
    folder("SettlementsV12")
    # ---- города v11 ----
    town("Duplino", -1950, -620, 14.0, radius=92, houses=11,
         pal={"wall": (140, 116, 88), "roof": (86, 58, 42)},
         palisade=True, tower=True, market=True,
         sign_text="ДУПЛИНО\nдеревня лесорубов")
    town("Elderwood", -900, -380, 14.0, radius=110, houses=13,
         pal={"wall": (120, 96, 74), "roof": (64, 44, 36)},
         palisade=False, tower=True, market=True, chapel_=True,
         sign_text="ЭЛЬДЕРВУД\nвольные лесорубы")
    town("Zarechye", 150, 2500, 12.0, radius=118, houses=14,
         pal={"wall": (166, 146, 112), "roof": (108, 70, 48)},
         palisade=True, tower=True, market=True, chapel_=True,
         sign_text="ЗАРЕЧЬЕ\nгород у слияния рек")
    town("Arcanum", 2600, 830, 16.0, radius=132, houses=15,
         pal={"wall": (176, 168, 196), "roof": (86, 74, 128)},
         wall_mat="Concrete", roof_mat="Slate",
         palisade=False, tower=True, market=True, chapel_=True,
         sign_text="АРКАНУМ\nгород магов")
    town("Kamnegorsk", -3150, 2600, 26.0, radius=126, houses=13,
         pal={"wall": (150, 146, 138), "roof": (92, 76, 62)},
         wall_mat="Cobblestone", palisade=False, tower=True, market=True,
         chapel_=True, sign_text="КАМНЕГОРСК\nкрепость горняков")
    town("FreeHarbor", 1650, -3300, 14.0, radius=120, houses=13,
         pal={"wall": (140, 118, 92), "roof": (74, 58, 46)},
         palisade=True, tower=True, market=True,
         sign_text="СВОБОДНАЯ ГАВАНЬ\nвольные капитаны")
    town("PalmCoast", 2100, 3300, 12.0, radius=118, houses=12,
         pal={"wall": (206, 190, 158), "roof": (86, 128, 122)},
         roof_mat="Slate", palisade=False, tower=True, market=True,
         sign_text="ПАЛЬМОВЫЙ БЕРЕГ\nюжные острова")
    # ---- лагеря разбойников (все в одном месте, с пометкой в реестре) ----
    for (camp_name, cxx, czz, cyy, cyaw) in [
            ("VeldtRaiders", -150, 1800, 12.0, 30),
            ("CanyonBandits", -560, 2900, 12.0, 200),
            ("RidgePoachers", -3000, 2300, 26.0, 75),
            ("ForestCutters", -2300, -800, 14.0, 120),
            ("DuneWreckers", 2250, 3150, 12.0, 250)]:
        bandit_camp(cxx, czz, cyy, yaw=cyaw, name=camp_name, ntents=3)
    endfolder()


def build_trade_routes(parent):
    """Торговые пути по новым землям + мосты через проливы."""
    folder("TradeRoutes")
    road(-2900, 1500, -1100, 1350, 20.0, width=10, color=(104, 98, 88))
    road(-1100, 1350, -200, 1200, 16.0, width=10, color=(104, 98, 88))
    road(1650, 2200, 3080, 2400, 8.4, width=9, color=(150, 138, 110), mat="Sandstone")
    road(700, 3300, 2100, 3300, 12.0, width=9, color=(150, 138, 110), mat="Sandstone")
    road(-900, 3200, 200, 2600, 14.0, width=9, color=(120, 112, 96))
    road(-2400, 2100, -2900, 1600, 26.0, width=11, color=(112, 106, 96))
    # мосты-арки между островами архипелага
    for i in range(12):
        t = i / 11.0
        ax = 1650 + (2500 - 1650) * t
        az = -3300 + (-3050 + 3300) * t
        part("ArchPirate", (22, 1.4, 15), (ax, 16.0 + math.sin(t * math.pi) * 7, az),
             color=(126, 120, 110), material="Cobblestone")
    for i in range(10):
        t = i / 9.0
        ax = -900 + (500 + 900) * t
        az = 3400 + 10 * math.sin(t * math.pi)
        part("ArchSouth", (24, 1.4, 14), (ax, 15.0 + math.sin(t * math.pi) * 6, az),
             color=(150, 138, 112), material="Sandstone")
    endfolder()



def build_game_logic(parent):
    folder("GameLogic")

    folder("ZoneTriggers")
    zone_trigger("Emberfall", -340, -240, 340, 440)
    zone_trigger("Gloomwood", -2320, -900, -680, 820)
    zone_trigger("Frostpeak", -2520, -2520, -680, -820)
    zone_trigger("Ashwaste", -820, -2520, 1020, -1080)
    zone_trigger("Mirefen", 680, -920, 2320, 1020)
    zone_trigger("SunkenCoast", 680, 880, 2420, 2320)
    zone_trigger("Bonefields", -920, 880, 920, 3400)
    zone_trigger("HollowDeep", -2330, 1730, -2070, 1970)
    zone_trigger("Highlands", -3560, 900, -2280, 3200)
    zone_trigger("Archipelago", -2300, -3700, 2760, -2820)
    zone_trigger("SouthIsles", -1150, 3120, 3350, 3700)
    zone_trigger("SunkenCoast", 2280, -100, 3450, 2200)  # восточные террасы
    zone_trigger("Bonefields", -1300, 1650, 900, 3400)  # южный вельд
    endfolder()

    folder("MobSpawns")
    # v11: точки мобов, заказанные из биомов и подземелий
    for i, (zone, mxa, mza, mya) in enumerate(MOB_SPAWN_EXTRA):
        mob_spawn(zone, 90 + i, mxa, mza, mya)
    for i, (x, z) in enumerate([(-1100, -300), (-1900, 200), (-1300, 500),
                                (-2000, -400), (-900, 300), (-1700, 650)]):
        mob_spawn("Gloomwood", i + 1, x, z, 14.0)
    for i, (x, z, y) in enumerate([(-2000, -1400, 20), (-1200, -1900, 20),
                                   (-1650, -1400, 32), (-1400, -1950, 32),
                                   (-1600, -1650, 46)]):
        mob_spawn("Frostpeak", i + 1, x, z, y)
    for i, (x, z) in enumerate([(200, -1500), (600, -1900), (-300, -1600),
                                (0, -2300), (700, -1300), (400, -2100)]):
        mob_spawn("Ashwaste", i + 1, x, z, 16.0)
    for i, (x, z) in enumerate([(1000, -500), (1900, -600), (1200, 700),
                                (2000, 600), (850, 300), (2100, -200)]):
        mob_spawn("Mirefen", i + 1, x, z, 12.0)
    for i, (x, z) in enumerate([(1200, 1400), (1900, 1900), (1000, 2000),
                                (2200, 1300), (1500, 1050)]):
        mob_spawn("SunkenCoast", i + 1, x, z, 8.4)
    for i, (x, z) in enumerate([(-600, 1300), (500, 1250), (-400, 1900),
                                (600, 2000), (0, 1050), (-700, 2100)]):
        mob_spawn("Bonefields", i + 1, x, z, 12.0)
    for i, (x, z) in enumerate([(-1500, 400), (-1900, 800), (-1750, 100),
                                (-1200, 200)]):
        mob_spawn("Gloomwood", i + 7, x, z, 14.0)
    for i, (x, z) in enumerate([(-2100, 1700), (-1950, 1800), (-2250, 1780),
                                (-2150, 1920)]):
        mob_spawn("HollowDeep", i + 1, x, z, 8.45)
    for i, (x, z, gy, nm) in enumerate([
            (-1000, 320, 14.0, "Bandits"), (-1350, -1250, 20.0, "Hunters"),
            (520, -1380, 16.0, "Marauders"), (300, 1200, 12.0, "Cult"),
            (1050, 550, 12.0, "Fishers")]):
        for j in range(3):
            a = math.pi * 2 * j / 3 + 0.5
            mob_spawn(nm, j + 1, x + math.sin(a) * 9, z + math.cos(a) * 9, gy)
    endfolder()

    # --- новые земли: предгорья, архипелаг, южные острова ---
    for i, (x, z, y) in enumerate([(-3100, 1600, 26), (-2750, 2200, 26),
                                   (-3300, 2600, 26), (-2500, 1700, 26),
                                   (-2900, 2900, 30), (-2400, 2500, 28)]):
        mob_spawn("Highlands", i + 1, x, z, y)
    for i, (x, z, y) in enumerate([(-2000, -3400, 14), (-1150, -3500, 14),
                                   (-300, -3450, 14), (700, -3400, 14),
                                   (1650, -3300, 14), (2500, -3050, 10)]):
        mob_spawn("Archipelago", i + 1, x, z, y)
    for i, (x, z, y) in enumerate([(-900, 3400, 12), (500, 3450, 12),
                                   (2100, 3300, 12), (3100, 2400, 10),
                                   (1200, 3200, 8)]):
        mob_spawn("SouthIsles", i + 1, x, z, y)

    # больше точек в старых зонах (гуще мир)
    for i, (x, z, y) in enumerate([(-1150, -80, 14), (-1650, -250, 14),
                                   (-2150, 100, 14), (-800, 620, 14),
                                   (-1900, -520, 14), (-1400, 760, 14)]):
        mob_spawn("Gloomwood", i + 11, x, z, y)
    for i, (x, z, y) in enumerate([(-820, 1300, 26), (-700, 1900, 28),
                                   (620, 1600, 20), (-350, 2100, 24)]):
        mob_spawn("Highlands", i + 7, x, z, y)
    for i, (x, z, y) in enumerate([(900, 1300, 8.4), (1500, 1300, 8.4),
                                   (2300, 2200, 8.4), (1000, 2500, 8.4)]):
        mob_spawn("SunkenCoast", i + 6, x, z, y)
    for i, (x, z, y) in enumerate([(1400, -200, 12), (1900, 400, 12),
                                   (2200, -600, 12), (800, -700, 12)]):
        mob_spawn("Mirefen", i + 7, x, z, y)
    for i, (x, z, y) in enumerate([(-600, -1700, 16), (700, -2400, 16),
                                   (-400, -2200, 16), (900, -1800, 16)]):
        mob_spawn("Ashwaste", i + 7, x, z, y)
    for i, (x, z, y) in enumerate([(-300, 1400, 12), (700, 2000, 12),
                                   (-700, 1800, 12)]):
        mob_spawn("Bonefields", i + 7, x, z, y)

    folder("BossSpawns")
    # боссы ставятся вместе с аренами; тут дубликатов нет
    endfolder()

    folder("NPCSpots")
    npc_spot("Blacksmith", -62, -58, 12.0)
    npc_spot("QuestKeeper", 30, 70, 12.0)
    npc_spot("Merchant", -30, 150, 12.0)
    npc_spot("Healer", 90, 150, 12.0)
    npc_spot("GateCaptain", 0, -160, 12.0)
    npc_spot("Herbalist", -1290, 300, 14.0)
    npc_spot("Hunter", -1210, 362, 14.0)
    npc_spot("Farmer", -560, 1002, 12.0)
    npc_spot("Portmaster", 1750, 2612, 4.0)
    npc_spot("Fishmonger", 1382, 2205, 8.4)
    npc_spot("Miner", -2750, 2420, 26.0)
    npc_spot("Highlander", -2880, 1900, 26.0)
    npc_spot("Pirate", 1650, -3280, 14.0)
    npc_spot("Villager", -1500, -1330, 32.0)
    npc_spot("Mogilshik", 620, 1440, 12.0)
    endfolder()

    folder("ArenaTriggers")
    # триггеры арен ставятся вместе с аренами
    endfolder()

    folder("SeaMonsterSpawns")
    for i, (x, z) in enumerate([(0, -3500), (3500, 500), (-3500, 1500),
                                (500, 3800)]):
        sea_monster_marker(i + 1, x, z)
    endfolder()

    folder("BoatSpawns")
    for i, (x, z) in enumerate([(1700, 2800), (1810, 2830), (1750, 2760)]):
        part("BoatSpawn_%d" % (i + 1), (16, 6, 16), (x, 3, z), color=(90, 200, 255),
             material="Neon", transparency=0.6, cancollide=False)
    endfolder()

    endfolder()


# ----------------------------------------------------------------------------
# Сервисы и скрипты
# ----------------------------------------------------------------------------
ZONE_CONFIG_LUA = '''--[[
    Emberfall — Пепел Вечности
    Конфигурация зон (v1.5 — карта + погода + лагеря).
    Используется системами спавна мобов, квестов и UI зон.
--]]

local ZoneConfig = {
    GameName = "Emberfall — Пепел Вечности",

    Zones = {
        { Id = "Emberfall",   Name = "Пепельная Пристань",      Level = "1-10",  Safe = true,
          Desc = "Последний город людей. Хаб: квесты, торговцы, кузница, пруд." },
        { Id = "Gloomwood",   Name = "Глумвуд — Мрачный Лес",   Level = "10-20", Safe = false,
          Desc = "Лес под властью Сердца-Древа. Река Ледяная, лагерь разбойников, скалы Клыки." },
        { Id = "Frostpeak",   Name = "Морозные Пики",           Level = "20-35", Safe = false,
          Desc = "Горы-великаны, замёрзшее озеро и водопад. Босс: Ледяной Колосс." },
        { Id = "Ashwaste",    Name = "Пепельные Пустоши",       Level = "35-50", Safe = false,
          Desc = "Выжженные земли и руины крепости. Босс: Пепельный Владыка." },
        { Id = "Mirefen",     Name = "Топи Мирефен",            Level = "25-40", Safe = false,
          Desc = "Ядовитые болота. Босс: Мать Болот. Рыбацкий стан." },
        { Id = "SunkenCoast", Name = "Затонувший Берег",        Level = "15-25", Safe = false,
          Desc = "Обломки флота, маяк и утонувшие руины. Призраки пиратов." },
        { Id = "Bonefields",  Name = "Костяные Поля",           Level = "30-45", Safe = false,
          Desc = "Кладбище, крипта и лагерь культа. Нежить." },
        { Id = "HollowDeep",  Name = "Полая Бездна (данж)",     Level = "50+",   Safe = false,
          Desc = "Каньон с висячим мостом и кристальная пещера. Босс: Безымянный Король." },
    },

    -- Временные базы (лагеря) — точки для квестов и спавна врагов
    Camps = {
        { Id = "BanditCamp",   Name = "Лагерь разбойников", Zone = "Gloomwood",  Pos = {-1000, 320} },
        { Id = "HunterCamp",   Name = "Стан охотников",     Zone = "Frostpeak",  Pos = {-1350, -1250} },
        { Id = "MarauderCamp", Name = "Мародёры Пустошей",  Zone = "Ashwaste",   Pos = {520, -1380} },
        { Id = "CultCamp",     Name = "Лагерь культа",      Zone = "Bonefields", Pos = {300, 1200} },
        { Id = "FisherCamp",   Name = "Рыбацкий стан",      Zone = "Mirefen",    Pos = {1050, 550} },
        -- v11: новые лагеря
        { Id = "VeldtRaiders", Name = "Налётчики вельда",     Zone = "Bonefields", Pos = {-150, 1800} },
        { Id = "CanyonBandits", Name = "Бандиты каньона",     Zone = "Bonefields", Pos = {-560, 2900} },
        { Id = "RidgePoachers", Name = "Браконьеры хребта",   Zone = "Highlands",  Pos = {-3000, 2300} },
        { Id = "ForestCutters", Name = "Лесорубы-отступники", Zone = "Gloomwood",  Pos = {-2300, -800} },
        { Id = "DuneWreckers", Name = "Крушители дюн",        Zone = "SouthIsles", Pos = {2250, 3150} },
    },

    -- Погода циклится скриптом WeatherSystem: Ясно/Облачно/Дождь/Гроза/Туман
    DayLengthSeconds = 2400,

    -- Ключевые локации v2 (для квестов и навигации)
    Locations = {
        { Id = "Port",          Name = "Порт «Ржавый Крюк»",  Pos = {1750, 2600} },
        { Id = "FisherVillage", Name = "Рыбацкая слобода",    Pos = {1350, 2180} },
        { Id = "Hamlet",        Name = "Горная Обитель",      Pos = {-1750, -1150} },
        { Id = "IceTomb",       Name = "Ледяная Гробница",    Pos = {-1750, -1500} },
        { Id = "Crypt",         Name = "Крипта",              Pos = {300, 1850} },
        { Id = "Volcano",       Name = "Вулкан Пепла",        Pos = {300, -2250} },
        { Id = "Overlook",      Name = "Круча Дозора",        Pos = {-560, 150} },
        { Id = "WaterfallSea",  Name = "Водопад к морю",      Pos = {-1050, -2640} },
        { Id = "IsletA",        Name = "Остров-спутник A",    Pos = {2700, 2600} },
        { Id = "IsletB",        Name = "Остров-спутник B",    Pos = {-2650, -2600} },
        { Id = "Tenegriv",      Name = "Тенегрив",            Pos = {-1250, 330} },
        { Id = "Khutor",        Name = "Хутор Овражный",      Pos = {-520, 1020} },
        { Id = "TowerSouth",    Name = "Сторожевая башня",    Pos = {60, 1050} },
        { Id = "Citadel",       Name = "Цитадель Лорд-Магистра", Pos = {150, -60} },
        { Id = "GreatGate",     Name = "Великие Южные Врата", Pos = {0, 700} },
        { Id = "SkyIsles",      Name = "Парящий архипелаг",   Pos = {-1150, -1650} },
        { Id = "Bastion",       Name = "Береговая батарея",   Pos = {1960, 2680} },
        { Id = "OutpostW",      Name = "Форт-пост Запад",     Pos = {-580, -240} },
        { Id = "OutpostE",      Name = "Форт-пост Восток",    Pos = {760, 250} },
        { Id = "OutpostB",      Name = "Форт-пост Костей",    Pos = {-380, 1850} },
        { Id = "RiverWest",     Name = "Западная река",       Pos = {-1050, 800} },
        -- v11: новые города и подземелья
        { Id = "Elderwood",     Name = "Эльдервуд",           Pos = {-900, -380} },
        { Id = "GreatGrove",    Name = "Великая Роща",        Pos = {-1500, -150} },
        { Id = "DuplinoCave",   Name = "Пещеры Дупла",        Pos = {-1950, -780} },
        { Id = "Zarechye",      Name = "Заречье",             Pos = {150, 2500} },
        { Id = "RedCanyon",     Name = "Красный каньон",      Pos = {-560, 2600} },
        { Id = "RedMine",       Name = "Шахта Красный Камень", Pos = {120, 2680} },
        { Id = "Arcanum",       Name = "Арканум",             Pos = {2600, 830} },
        { Id = "RiceTerraces",  Name = "Рисовые террасы",     Pos = {3000, 1300} },
        { Id = "Kamnegorsk",    Name = "Камнегорск",          Pos = {-3150, 2600} },
        { Id = "WindPeak",      Name = "Пик Ветров",          Pos = {-2550, 2000} },
        { Id = "OldMine",       Name = "Забытые Шахты",       Pos = {-2820, 2380} },
        { Id = "FreeHarbor",    Name = "Свободная Гавань",    Pos = {1650, -3300} },
        { Id = "DrownedShip",   Name = "Затонувший Фрегат",   Pos = {1860, -3120} },
        { Id = "PalmCoast",     Name = "Пальмовый Берег",     Pos = {2100, 3300} },
        { Id = "CoralGrotto",   Name = "Коралловый Грот",     Pos = {1980, 3420} },
        { Id = "VolcanoForge",  Name = "Кузня в Жерле",       Pos = {220, -2080} },
        { Id = "AshKaran",      Name = "Аш-Каран",            Pos = {-500, -1900} },
        { Id = "RotTemple",     Name = "Затонувший Храм Гнили", Pos = {1620, -200} },
        { Id = "WyrmLair",      Name = "Логово Ледяного Змея", Pos = {-2050, -1750} },
    },

    -- v11: ГОРОДА (полноценные, с площадью, рынком и стражами)
    Cities = {
        { Id = "EmberfallCity", Name = "Пепельная Пристань", Pos = {0, 100},  Zone = "Emberfall" },
        { Id = "Elderwood",     Name = "Эльдервуд",          Pos = {-900, -380}, Zone = "Gloomwood" },
        { Id = "Duplino",       Name = "Дуплино",            Pos = {-1950, -620}, Zone = "Gloomwood" },
        { Id = "Zarechye",      Name = "Заречье",            Pos = {150, 2500},  Zone = "Bonefields" },
        { Id = "Arcanum",       Name = "Арканум",            Pos = {2600, 830},  Zone = "SunkenCoast" },
        { Id = "Kamnegorsk",    Name = "Камнегорск",         Pos = {-3150, 2600}, Zone = "Highlands" },
        { Id = "FreeHarbor",    Name = "Свободная Гавань",   Pos = {1650, -3300}, Zone = "Archipelago" },
        { Id = "PalmCoast",     Name = "Пальмовый Берег",    Pos = {2100, 3300}, Zone = "SouthIsles" },
    },

    -- v11: ПОДЗЕМЕЛЬЯ (данжи) — вход, зона, босс
    Dungeons = {
        { Id = "DuplinoCave",  Name = "Пещеры Дупла",          Pos = {-1950, -780}, Zone = "Gloomwood" },
        { Id = "RedMine",      Name = "Шахта Красный Камень",  Pos = {120, 2680},   Zone = "Bonefields", Boss = "MarrowTyrant" },
        { Id = "OldMine",      Name = "Забытые Шахты",         Pos = {-2820, 2380}, Zone = "Highlands",  Boss = "StoneWarden" },
        { Id = "DrownedShip",  Name = "Затонувший Фрегат",     Pos = {1860, -3120}, Zone = "Archipelago", Boss = "PirateAdmiral" },
        { Id = "CoralGrotto",  Name = "Коралловый Грот",       Pos = {1980, 3420},  Zone = "SouthIsles", Boss = "CoralQueen" },
        { Id = "Forge",        Name = "Кузня в Жерле",         Pos = {220, -2080},  Zone = "Ashwaste",   Boss = "VolcanoForge" },
        { Id = "RotTemple",    Name = "Затонувший Храм Гнили", Pos = {1620, -200},  Zone = "Mirefen",    Boss = "BogHydra" },
        { Id = "WyrmLair",     Name = "Логово Ледяного Змея",  Pos = {-2050, -1750}, Zone = "Frostpeak", Boss = "GlacierWyrm" },
        { Id = "WindPeak",     Name = "Пик Ветров",            Pos = {-2550, 2000}, Zone = "Highlands",  Boss = "WindArchon" },
    },

    -- Плавание: скрипт SwimSystem держит игрока на поверхности моря.
    -- Морские чудовища: маркеры SeaMonster_1..4 в глубине (0,-3500), (3500,500),
    -- (-3500,1500), (500,3800). Лодки: маркеры BoatSpawn_* у порта.
}

return ZoneConfig
'''

BOOTSTRAP_LUA = '''-- Emberfall — Пепел Вечности | WorldBootstrap (v1: карта)
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))

-- Плавный цикл дня и ночи (полные сутки = 40 минут)
local DAY_LENGTH = 2400
Lighting.ClockTime = 10.5

task.spawn(function()
	while true do
		local dt = task.wait(1)
		Lighting.ClockTime = (Lighting.ClockTime + dt * 24 / DAY_LENGTH) % 24
	end
end)

print(("[Emberfall] %s — карта %s загружена"):format(Config.GameName, Config.Version))
'''

WEATHER_LUA = '''-- Emberfall | Система погоды: Ясно / Облачно / Дождь / Гроза / Туман
local TweenService = game:GetService("TweenService")
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Atmosphere = Lighting:FindFirstChildOfClass("Atmosphere")
local Clouds = workspace.Terrain and workspace.Terrain:FindFirstChildOfClass("Clouds")

local STATES = {
	{ Name = "Ясно",    Cover = 0.16, Density = 0.12, FogEnd = 9000, Brightness = 3.6, Rain = false },
	{ Name = "Облачно", Cover = 0.55, Density = 0.30, FogEnd = 2600, Brightness = 2.1, Rain = false },
	{ Name = "Дождь",   Cover = 0.88, Density = 0.38, FogEnd = 1700, Brightness = 1.5, Rain = true },
	{ Name = "Гроза",   Cover = 1.0,  Density = 0.46, FogEnd = 1100, Brightness = 1.1, Rain = true, Flash = true },
	{ Name = "Туман",   Cover = 0.35, Density = 0.50, FogEnd = 800,  Brightness = 1.6, Rain = false },
}

local weatherValue = Instance.new("StringValue")
weatherValue.Name = "WeatherCurrent"
weatherValue.Value = "Ясно"
weatherValue.Parent = ReplicatedStorage

local function makeRain(character)
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root or root:FindFirstChild("RainAttachment") then
		return
	end
	local att = Instance.new("Attachment")
	att.Name = "RainAttachment"
	att.Position = Vector3.new(0, 38, 0)
	local pe = Instance.new("ParticleEmitter")
	pe.Name = "Rain"
	pe.Rate = 140
	pe.Lifetime = NumberRange.new(0.75, 0.95)
	pe.Speed = NumberRange.new(75, 85)
	pe.EmissionDirection = Enum.NormalId.Bottom
	pe.SpreadAngle = Vector2.new(4, 4)
	pe.Size = NumberSequence.new(0.16)
	pe.Transparency = NumberSequence.new(0.45)
	pe.Color = ColorSequence.new(Color3.fromRGB(170, 190, 210))
	pe.Parent = att
	att.Parent = root
end

local function setRain(on)
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local att = root and root:FindFirstChild("RainAttachment")
		if on and not att and char then
			makeRain(char)
		elseif not on and att then
			att:Destroy()
		end
	end
end

Players.PlayerAdded:Connect(function(pl)
	pl.CharacterAdded:Connect(function(char)
		task.wait(0.5)
		if weatherValue.Value == "Дождь" or weatherValue.Value == "Гроза" then
			makeRain(char)
		end
	end)
end)

local function apply(state)
	weatherValue.Value = state.Name
	local ti = TweenInfo.new(9, Enum.EasingStyle.Sine)
	TweenService:Create(Lighting, ti, { FogEnd = state.FogEnd, Brightness = state.Brightness }):Play()
	if Atmosphere then
		TweenService:Create(Atmosphere, ti, { Density = state.Density }):Play()
	end
	if Clouds then
		TweenService:Create(Clouds, ti, { Cover = state.Cover }):Play()
	end
	setRain(state.Rain)
	print("[Погода] " .. state.Name)
end

-- вспышки молний во время грозы
task.spawn(function()
	while true do
		if weatherValue.Value == "Гроза" then
			Lighting.Brightness = 6
			task.wait(0.08)
			Lighting.Brightness = 1.2
			task.wait(math.random(4, 11))
		else
			task.wait(2)
		end
	end
end)

while true do
	local nextIndex = math.random(1, #STATES)
	if STATES[nextIndex].Name ~= weatherValue.Value then
		apply(STATES[nextIndex])
		task.wait(math.random(150, 320))
	else
		task.wait(30)
	end
end
'''

SWIM_LUA = '''-- Emberfall | Плавание: в глубокой воде персонаж держится на поверхности,
-- под водой тонет медленнее. Монстры глубин — по маркерам SeaMonster_*.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local WATER_Y = -0.6

RunService.Heartbeat:Connect(function()
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if root and hum and hum.Health > 0 then
			local p = root.Position
			if p.Y < WATER_Y then
				local v = root.AssemblyLinearVelocity
				local up = (p.Y < -2.0) and 12 or 4
				root.AssemblyLinearVelocity = Vector3.new(
					v.X * 0.97, math.max(v.Y, up), v.Z * 0.97)
			end
		end
	end
end)

print("[Emberfall] Плавание активно: море глубокое, дно на -35 студов")
'''

TELEPORT_LUA = '''-- Emberfall | Быстрая телепортация для проверки карты (v2).
-- Команды чата: !деревня !лес !древо !лагерь !мороз !озеро !водопад
--   !пустоши !вулкан !топи !берег !порт !рыбаки !маяк !кости !крипта
--   !каньон !трон !обитель !гробница !обзор !сундук
local Players = game:GetService("Players")
local ChatService = game:GetService("Chat")

local SPOTS = {
	{ cmds = {"!деревня", "!village"}, pos = Vector3.new(0, 14, 158),       name = "Пепельная Пристань" },
	{ cmds = {"!лес", "!gloom"},       pos = Vector3.new(-1100, 16, 300),   name = "Глумвуд" },
	{ cmds = {"!древо", "!heart"},     pos = Vector3.new(-1610, 16, 75),    name = "Сердце-Древо" },
	{ cmds = {"!лагерь", "!camp"},     pos = Vector3.new(-1000, 16, 300),   name = "Лагерь разбойников" },
	{ cmds = {"!мороз", "!frost"},     pos = Vector3.new(-1600, 66, -1600), name = "Морозные Пики (арена)" },
	{ cmds = {"!озеро", "!lake"},      pos = Vector3.new(-1150, 24, -1650), name = "Замёрзшее озеро" },
	{ cmds = {"!водопад", "!falls"},   pos = Vector3.new(-1050, 24, -2260), name = "Водопад к морю" },
	{ cmds = {"!пустоши", "!ash"},     pos = Vector3.new(100, 20, -2000),   name = "Пепельные Пустоши (арена)" },
	{ cmds = {"!вулкан", "!volcano"},  pos = Vector3.new(300, 20, -2100),   name = "Вулкан Пепла (паркур)" },
	{ cmds = {"!топи", "!mire"},       pos = Vector3.new(1500, 16, 220),    name = "Топи Мирефен (остров босса)" },
	{ cmds = {"!берег", "!coast"},     pos = Vector3.new(1600, 12, 1700),   name = "Затонувший Берег" },
	{ cmds = {"!порт", "!port"},       pos = Vector3.new(1750, 8, 2560),    name = "Порт «Ржавый Крюк»" },
	{ cmds = {"!рыбаки", "!fish"},     pos = Vector3.new(1364, 12, 2190),   name = "Рыбацкая слобода" },
	{ cmds = {"!маяк", "!beacon"},     pos = Vector3.new(2050, 12, 2000),   name = "Маяк" },
	{ cmds = {"!кости", "!bones"},     pos = Vector3.new(0, 16, 1550),      name = "Костяные Поля (кладбище)" },
	{ cmds = {"!крипта", "!crypt"},    pos = Vector3.new(300, 14, 1885),    name = "Крипта (данж)" },
	{ cmds = {"!каньон", "!deep"},     pos = Vector3.new(-860, 14, 1450),   name = "Вход в Полую Бездну" },
	{ cmds = {"!трон", "!king"},       pos = Vector3.new(-2200, 16, 1850),  name = "Трон Безымянного Короля" },
	{ cmds = {"!обитель", "!hamlet"},  pos = Vector3.new(-1750, 26, -1150), name = "Горная Обитель" },
	{ cmds = {"!гробница", "!tomb"},   pos = Vector3.new(-2200, 26, -1120), name = "Ледяная Гробница (данж)" },
	{ cmds = {"!обзор", "!view"},      pos = Vector3.new(-548, 42, 156),    name = "Круча Дозора (сундук)" },
	{ cmds = {"!сундук", "!chest"},    pos = Vector3.new(2712, 10, 2600),   name = "Остров-спутник (сундук)" },
	{ cmds = {"!тенегрив", "!tenegriv"}, pos = Vector3.new(-1250, 20, 330), name = "Тенегрив (лесная деревня)" },
	{ cmds = {"!хутор", "!farm"},      pos = Vector3.new(-520, 18, 1020),   name = "Хутор Овражный" },
	{ cmds = {"!башня", "!tower"},     pos = Vector3.new(60, 18, 1060),     name = "Сторожевая башня" },
	{ cmds = {"!цитадель", "!citadel"}, pos = Vector3.new(150, 16, -30),    name = "Цитадель Лорд-Магистра" },
	{ cmds = {"!врата", "!gate"},      pos = Vector3.new(0, 14, 660),       name = "Великие Южные Врата" },
	{ cmds = {"!небеса", "!sky"},      pos = Vector3.new(-1000, 26, -1520), name = "Небесная лестница" },
	{ cmds = {"!батарея", "!cannon"},  pos = Vector3.new(1930, 10, 2650),   name = "Береговая батарея" },
	{ cmds = {"!пост", "!outpost"},    pos = Vector3.new(-556, 12, -216),   name = "Форт-пост Запад" },
	{ cmds = {"!водопадр", "!riverfall"}, pos = Vector3.new(-1047, 16, 840), name = "Водопад Западной реки" },
	-- v9: новые земли
	{ cmds = {"!предгорья", "!highlands"}, pos = Vector3.new(-2900, 34, 1900), name = "Предгорья — Каменный Брод" },
	{ cmds = {"!шахта", "!mine"},       pos = Vector3.new(-2750, 34, 2420), name = "Шахта предгорий" },
	{ cmds = {"!архипелаг", "!arch"},   pos = Vector3.new(-1150, 22, -3450), name = "Северный архипелаг" },
	{ cmds = {"!пираты", "!cove"},      pos = Vector3.new(1650, 22, -3280), name = "Пиратская бухта" },
	{ cmds = {"!юг", "!south"},         pos = Vector3.new(-900, 20, 3380), name = "Южные острова — рыбаки" },
	{ cmds = {"!маякблизнец", "!twin"}, pos = Vector3.new(2100, 20, 3280), name = "Маяки-близнецы" },
	{ cmds = {"!ветроград", "!wind"},   pos = Vector3.new(-1500, 40, -1330), name = "Ветроград (Морозные Пики)" },
	{ cmds = {"!дуплино", "!wood"},     pos = Vector3.new(-1850, 22, -320), name = "Деревня лесорубов Дуплино" },
	{ cmds = {"!гнильцы", "!swamp"},    pos = Vector3.new(1750, 20, 700), name = "Деревня на сваях Гнильцы" },
	{ cmds = {"!форт", "!fort"},        pos = Vector3.new(-350, 24, -1480), name = "Форт мародёров" },
	{ cmds = {"!контрабанда", "!smug"}, pos = Vector3.new(1180, 16, 1600), name = "Бухта Контрабанда" },
	-- v11: новые города, чащи и подземелья
	{ cmds = {"!эльдервуд", "!elder"}, pos = Vector3.new(-900, 20, -380), name = "Эльдервуд (город)" },
	{ cmds = {"!роща", "!grove"},     pos = Vector3.new(-1500, 22, -150), name = "Великая Роща" },
	{ cmds = {"!пещеры", "!duplcave"}, pos = Vector3.new(-1950, 18, -780), name = "Пещеры Дупла (данж)" },
	{ cmds = {"!заречье", "!zarech"}, pos = Vector3.new(150, 18, 2500), name = "Заречье (город)" },
	{ cmds = {"!каньонюг", "!veldt"}, pos = Vector3.new(-560, 18, 2600), name = "Красный каньон" },
	{ cmds = {"!шахтакрасн", "!redmine"}, pos = Vector3.new(120, 18, 2680), name = "Шахта Красный Камень (данж)" },
	{ cmds = {"!арканум", "!arcanum"}, pos = Vector3.new(2600, 22, 830), name = "Арканум (город магов)" },
	{ cmds = {"!террасы", "!terraces"}, pos = Vector3.new(3000, 20, 1300), name = "Рисовые террасы" },
	{ cmds = {"!камнегорск", "!kamnegorsk"}, pos = Vector3.new(-3150, 32, 2600), name = "Камнегорск (крепость)" },
	{ cmds = {"!пикветров", "!windpeak"}, pos = Vector3.new(-2550, 240, 2000), name = "Пик Ветров (арена)" },
	{ cmds = {"!забытыешахты", "!oldmine"}, pos = Vector3.new(-2820, 32, 2380), name = "Забытые Шахты (данж)" },
	{ cmds = {"!гавань", "!harbor"},  pos = Vector3.new(1650, 20, -3300), name = "Свободная Гавань (город)" },
	{ cmds = {"!фрегат", "!frigate"}, pos = Vector3.new(1860, 20, -3120), name = "Затонувший Фрегат (данж)" },
	{ cmds = {"!пальмы", "!palm"},    pos = Vector3.new(2100, 18, 3300), name = "Пальмовый Берег (город)" },
	{ cmds = {"!грот", "!grotto"},    pos = Vector3.new(1980, 18, 3420), name = "Коралловый Грот (данж)" },
	{ cmds = {"!кузня", "!forge"},    pos = Vector3.new(220, 22, -2080), name = "Кузня в Жерле (данж)" },
	{ cmds = {"!ашкаран", "!ashkaran"}, pos = Vector3.new(-500, 22, -1900), name = "Аш-Каран (мёртвый город)" },
	{ cmds = {"!храмгнили", "!rottemple"}, pos = Vector3.new(1620, 18, -200), name = "Затонувший Храм Гнили (данж)" },
	{ cmds = {"!змеи", "!wyrm"},      pos = Vector3.new(-2050, 26, -1750), name = "Логово Ледяного Змея (данж)" },
}

Players.PlayerAdded:Connect(function(pl)
	pl.Chatted:Connect(function(msg)
		local text = string.lower(msg)
		for _, spot in ipairs(SPOTS) do
			for _, cmd in ipairs(spot.cmds) do
				if text:sub(1, #cmd) == cmd then
					local char = pl.Character
					local root = char and char:FindFirstChild("HumanoidRootPart")
					if root then
						char:PivotTo(CFrame.new(spot.pos + Vector3.new(0, 4, 0)))
						pcall(function()
							ChatService:Chat(char:FindFirstChild("Head") or root, "→ " .. spot.name, Enum.ChatColor.Blue)
						end)
					end
					return
				end
			end
		end
	end)
end)
'''


def build_lighting():
    begin_item("Lighting", "Lighting")
    p_color3("Ambient", 76, 78, 86)
    p_color3("OutdoorAmbient", 152, 156, 158)
    p_float("Brightness", 3.6)
    p_str("TimeOfDay", "12:00:00")
    p_float("GeographicLatitude", 35)
    p_color3("FogColor", 196, 210, 224)
    p_float("FogStart", 900)
    p_float("FogEnd", 9000)
    p_bool("GlobalShadows", True)
    p_float("EnvironmentDiffuseScale", 0.3)
    p_float("EnvironmentSpecularScale", 0.3)
    p_float("ExposureCompensation", 0.05)
    end_props()
    begin_item("Atmosphere", "Atmosphere")
    p_float("Density", 0.115)
    p_float("Offset", 0.6)
    p_color3("Color", 190, 200, 216)
    p_color3("Decay", 168, 178, 194)
    p_float("Glare", 0.03)
    p_float("Haze", 0.18)
    end_props()
    end_item()
    end_item()


def build_services():
    # ---------------- ReplicatedStorage ----------------
    begin_item("ReplicatedStorage", "ReplicatedStorage")
    end_props()

    folder("Remotes")
    endfolder()

    begin_item("Folder", "EmberfallShared")
    end_props()
    for module_name in ["Config", "GameData", "Net", "Util", "Quests", "NPCData", "Dungeons"]:
        begin_item("ModuleScript", module_name)
        p_pstr("Source", SHARED[module_name])
        end_props()
        end_item()
    end_item()

    end_item()

    # ---------------- ServerScriptService ----------------
    begin_item("ServerScriptService", "ServerScriptService")
    end_props()

    begin_item("Script", "WorldBootstrap")
    p_pstr("Source", BOOTSTRAP_LUA)
    end_props()
    end_item()

    begin_item("Script", "WeatherSystem")
    p_pstr("Source", WEATHER_LUA)
    end_props()
    end_item()

    begin_item("Script", "SwimSystem")
    p_pstr("Source", SWIM_LUA)
    end_props()
    end_item()

    begin_item("Script", "QuickTeleport")
    p_pstr("Source", TELEPORT_LUA)
    end_props()
    end_item()

    begin_item("Folder", "EmberfallServer")
    end_props()
    for module_name in ["PlayerState", "Combat", "MobService", "BossService",
                        "MagicService", "QuestService", "WorldService",
                        "InteractService"]:
        begin_item("ModuleScript", module_name)
        p_pstr("Source", SERVER[module_name])
        end_props()
        end_item()
    end_item()  # Folder EmberfallServer

    begin_item("Script", "EmberfallMain")
    p_pstr("Source", SERVER["Main"])
    end_props()
    end_item()

    end_item()

    # ---------------- StarterPlayer ----------------
    begin_item("StarterPlayer", "StarterPlayer")
    p_float("CameraMaxZoomDistance", 400)
    end_props()

    begin_item("StarterPlayerScripts", "StarterPlayerScripts")
    end_props()
    for module_name in CLIENT_MODULES:
        begin_item("ModuleScript", module_name)
        p_pstr("Source", CLIENT[module_name])
        end_props()
        end_item()

    begin_item("LocalScript", "EmberfallClient")
    p_pstr("Source", CLIENT["ClientMain"])
    end_props()
    end_item()

    end_item()  # StarterPlayerScripts
    end_item()  # StarterPlayer


def main():
    out_name = "Emberfall_Map_v12.rbxlx"

    _lines.append('<?xml version="1.0" encoding="utf-8"?>')
    _lines.append('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" '
                  'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                  'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" '
                  'version="4">')
    _lines.append('\t<External>null</External>')
    _lines.append('\t<External>nil</External>')
    _lines.append('\t<Meta name="ExplicitAutoJoints">true</Meta>')

    # Workspace
    begin_item("Workspace", "Workspace")
    p_bool("StreamingEnabled", False)
    end_props()

    # Terrain с облаками (ими управляет скрипт погоды)
    begin_item("Terrain", "Terrain")
    end_props()
    begin_item("Clouds", "Clouds")
    p_float("Cover", 0.38)
    p_float("Density", 0.55)
    p_color3("Color", 195, 200, 214)
    p_float("Brightness", 0.4)
    p_bool("Enabled", True)
    end_props()
    end_item()
    end_item()

    # точка спавна
    begin_item("SpawnLocation", "SpawnLocation")
    p_bool("Anchored", True)
    p_bool("CanCollide", True)
    p_vec3("size", 16, 1, 16)
    p_cframe("CFrame", (0, 12.5, 158))
    p_color3u8("Color3uint8", 110, 106, 100)
    p_token("Material", MATERIAL_IDS["Cobblestone"])
    p_token("shape", PARTTYPE_IDS["Block"])
    p_float("Transparency", 0)
    p_token("TopSurface", SURFACE_IDS["Smooth"])
    p_token("BottomSurface", SURFACE_IDS["Smooth"])
    p_bool("Neutral", True)
    end_props()
    end_item()

    # ---- ПРОХОД 1: планировка (только рельефные "плоские пятна") ----
    global PLANNING
    PLANNING = True
    build_v12_settlements(None)
    build_sea(None)
    build_village(None)
    build_gloomwood(None)
    build_frostpeak(None)
    build_ashwaste(None)
    build_mirefen(None)
    build_sunken_coast(None)
    build_bonefields(None)
    build_hollow_deep(None)
    build_trade_routes(None)
    build_highlands(None)
    build_archipelago(None)
    build_south_isles(None)
    build_gloomwood_north(None)
    build_south_veldt(None)
    build_terraces(None)
    build_highlands_new(None)
    build_archipelago_new(None)
    build_south_isles_new(None)
    build_ashwaste_new(None)
    build_mirefen_new(None)
    build_frostpeak_new(None)
    build_sealed_peaks(None)
    build_v11_forests(None)
    build_islands(None)
    build_continent(None)
    PLANNING = False
    occ_save()      # v12: план занятых мест для второго прохода

    # ---- ПРОХОД 2: настоящая сборка ----
    occ_save()      # v12: второй проход начинается с плана занятости
    folder("World")
    build_v12_settlements(None)     # v12: сначала города — потом всё остальное
    build_sea(None)
    build_continent(None)
    build_village(None)
    build_gloomwood(None)
    build_frostpeak(None)
    build_ashwaste(None)
    build_mirefen(None)
    build_sunken_coast(None)
    build_bonefields(None)
    build_hollow_deep(None)
    build_trade_routes(None)
    build_highlands(None)
    build_archipelago(None)
    build_south_isles(None)
    build_gloomwood_north(None)
    build_south_veldt(None)
    build_terraces(None)
    build_highlands_new(None)
    build_archipelago_new(None)
    build_south_isles_new(None)
    build_ashwaste_new(None)
    build_mirefen_new(None)
    build_frostpeak_new(None)
    build_sealed_peaks(None)
    build_v11_forests(None)
    build_islands(None)
    endfolder()

    build_game_logic(None)

    end_item()  # Workspace

    build_lighting()
    build_services()

    _lines.append("</roblox>")

    xml = "\n".join(_lines)
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(xml)

    # статистика
    import re
    from collections import Counter
    classes = Counter(re.findall(r'<Item class="([^"]+)"', xml))
    print("Файл: %s (%.1f МБ)" % (out_name, len(xml.encode("utf-8")) / 1e6))
    print("Всего Item: %d" % sum(classes.values()))
    for cls, cnt in classes.most_common():
        print("  %-16s %d" % (cls, cnt))


if __name__ == "__main__":
    main()
