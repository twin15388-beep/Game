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


def folder(name):
    begin_item("Folder", name)
    end_props()


def endfolder():
    end_item()


# ----------------------------------------------------------------------------
# Базовые примитивы
# ----------------------------------------------------------------------------
def part(name, size, pos, yaw=0.0, pitch=0.0, roll=0.0, color=(163, 162, 165),
         material="Plastic", transparency=0.0, cancollide=True, anchored=True,
         shape=None, cls="Part", reflectance=None, light=None, fire=None):
    """light = dict(brightness, range, color, shadows); fire = dict(size, heat, color, secondary)"""
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
    r = rng.uniform(2.5, 6.5) * s
    part("Rock", (r, r, r), (x, y + r * 0.22, z), yaw=rng.uniform(0, 360),
         pitch=rng.uniform(-10, 10), roll=rng.uniform(-10, 10),
         color=col, material=mat)


def mushroom(x, z, y, s=1.0):
    h = rng.uniform(2.5, 4.5) * s
    part("Mushroom_Stem", (h, 1.4 * s, 1.4 * s), (x, y + h / 2, z), roll=90,
         shape="Cylinder", color=(200, 195, 175), material="SmoothPlastic")
    part("Mushroom_Cap", (2.8 * s, 1.6 * s, 2.8 * s), (x, y + h + 0.4, z),
         shape="Ball", color=(150, 60, 190), material="Neon", cancollide=False)


def reed(x, z, y):
    part("Reed", (0.7, rng.uniform(3, 5), 0.7), (x, y + 2, z),
         yaw=rng.uniform(0, 360), pitch=rng.uniform(-8, 8), color=(64, 70, 44),
         material="Grass", cancollide=False)


def crystal(x, z, y, s=1.0, hue="cyan"):
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
    disc("Brazier_Bowl", x, z, y + 1.4, 2.2, 1.4, (45, 45, 50), "Metal")
    part("Brazier_Flame", (1.4, 1.8, 1.4), (x, y + 2.5, z), color=(255, 120, 30),
         material="Neon", cancollide=False, transparency=0.15,
         fire=dict(size=5, heat=7),
         light=dict(brightness=1.6, range=24, color=(255, 140, 50)))


def lamppost(x, z, y):
    part("LampPost", (0.5, 9, 0.5), (x, y + 4.5, z), color=(50, 50, 54),
         material="Metal")
    part("LampPost_Head", (1.3, 1.5, 1.3), (x, y + 9.5, z), color=(255, 190, 110),
         material="Neon", cancollide=False,
         light=dict(brightness=1.4, range=28, color=(255, 180, 100)))


def tombstone(x, z, y):
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
    disc("WaterPool", x, z, y + 0.75, r, 0.7, col, "Water",
         transparency=0.35, cancollide=False)


def lava_pool(x, z, y, r):
    disc("Hazard_Lava", x, z, y + 0.55, r, 1.0, (255, 96, 18), "Neon",
         light=dict(brightness=1.3, range=20, color=(255, 110, 30))
         if rng.random() < 0.3 else None)


# ----------------------------------------------------------------------------
# Постройки
# ----------------------------------------------------------------------------
def house(name, cx, cz, gy, w, d, h, yaw=0.0,
          wall=(176, 168, 150), roof=(70, 50, 38),
          wall_mat="WoodPlanks", roof_mat="WoodPlanks",
          windows=True, chimney=True):
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
    v_cyl("Lighthouse_Base", cx, cz, gy, 14, 20, (200, 192, 175), "Concrete")
    v_cyl("Lighthouse_Mid", cx, cz, gy + 14, 12, 17, (140, 60, 50), "Brick")
    v_cyl("Lighthouse_Top", cx, cz, gy + 26, 10, 15, (200, 192, 175), "Concrete")
    v_cyl("Lighthouse_Lantern", cx, cz, gy + 36, 6, 13, (255, 200, 110), "Neon",
          light=dict(brightness=2.5, range=150, color=(255, 200, 120)))
    part("Lighthouse_Roof", (13, 8, 13), (cx, gy + 44, cz), shape="Ball",
         color=(60, 50, 48), material="Metal", cancollide=False)


def shipwreck(cx, cz, gy):
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


def mega_mesa(x, z, gy, base_w=140, h=110, snow=60):
    """ГОРА: толстые ступени по 6.5 студа (можно запрыгивать), плавный конус."""
    n = max(8, int(h / 6.5))
    tier_h = h / float(n)
    w = base_w
    for i in range(n):
        y = gy + i * tier_h
        t = (y - gy) / float(h)
        if y > snow:
            col, mat = (228, 233, 241), "Snow"
        else:
            g = int(108 + t * 46)
            col, mat = (g, g + 4, g + 12), "Rock"
        part("Peak_Tier%d" % i, (w, tier_h + 0.5, w),
             (x + rng.uniform(-3, 3), y + tier_h / 2, z + rng.uniform(-3, 3)),
             yaw=(i * 7) % 45, color=col, material=mat)
        w = max(9.0, w - (base_w - 12) / n * (0.85 + 0.5 * t))
    part("Peak_Snowcap", (w * 1.6, w * 1.1, w * 1.6),
         (x, gy + h + w * 0.25, z), shape="Ball",
         color=(234, 240, 248), material="Snow", cancollide=False)
    for _ in range(5):
        rock(x + rng.uniform(-base_w / 2, base_w / 2),
             z + rng.uniform(-base_w / 2, base_w / 2), gy,
             rng.uniform(0.9, 1.5), "Rock", (110, 112, 118))


def hill_mound(x, z, gy, r=24, h=12, col=(96, 116, 66)):
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
    part("Farm_Soil", (w, 0.6, d), (x, gy + 0.3, z), yaw=yaw, color=(96, 72, 50),
         material="Ground")
    rows = max(3, int(d / 2))
    for r in range(rows):
        rx, rz = l2w(x, z, yaw, 0, -d / 2 + 1 + r * 2)
        part("Farm_CropRow", (w - 1.6, 1.1, 0.9), (rx, gy + 1.1, rz), yaw=yaw,
             color=rng.choice([(104, 138, 62), (96, 128, 56), (140, 150, 70)]),
             material="Grass", cancollide=False)


def scarecrow(x, z, gy):
    part("Scare_Pole", (0.5, 5, 0.5), (x, gy + 2.5, z), color=(90, 70, 50),
         material="Wood")
    part("Scare_Arms", (3.2, 0.4, 0.4), (x, gy + 3.6, z), color=(90, 70, 50),
         material="Wood", cancollide=False)
    part("Scare_Head", (1.1, 1.1, 1.1), (x, gy + 5.2, z), shape="Ball",
         color=(230, 160, 60), material="Fabric", cancollide=False)
    part("Scare_Hat", (1.6, 0.5, 1.6), (x, gy + 5.9, z), color=(120, 90, 50),
         material="Grass", cancollide=False)


def haystack(x, z, gy):
    part("Haystack", (3.2, 2.6, 3.2), (x, gy + 1.3, z), yaw=rng.uniform(0, 90),
         color=(214, 178, 86), material="Grass")


def cart_wagon(x, z, gy, yaw=0.0):
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
    (-2700, -900), (-2600, -1900), (-2200, -2500), (-1500, -2800),
    (-500, -2850), (500, -2750), (1400, -2600), (2200, -2300),
    (2700, -1700), (2850, -900), (2800, -100), (2900, 700),
    (2750, 1500), (2500, 2200), (1900, 2700), (1000, 2900),
    (0, 2950), (-900, 2800), (-1800, 2500), (-2400, 1900),
    (-2800, 1100), (-2900, 200),
]

ZONE_GROUND = [
    # (x0, z0, x1, z1, цвет, материал) — цвета смешиваются к краям зон
    (-2400, -2400, -800, -1000, (226, 233, 242), "Snow"),    # Морозные Пики
    (-850, -2500, 1050, -1100, (130, 98, 84), "Basalt"),     # Пустоши
    (650, -950, 2350, 1050, (130, 110, 64), "Mud"),          # Топи
    (650, 750, 2450, 2350, (210, 192, 144), "Sand"),         # Берег
    (-950, 750, 950, 2350, (140, 144, 94), "Ground"),        # Костяные поля
    (-2350, -950, -650, 850, (72, 104, 62), "Ground"),       # Глумвуд
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
        fn(x, z, gy)
        out += 1


# ------------------------- растительность ----------------------------------
def tree_nice(x, z, y, s=1.0):
    """Пышное дерево-«помпон»: ствол + 4 сочных шара кроны (как в референсах)."""
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
    part("GrassTuft", (1.4, 1.0, 0.18), (x, y + 0.45, z), yaw=rng.uniform(0, 180),
         color=col or rng.choice([(74, 104, 52), (66, 96, 48), (84, 112, 58)]),
         material="Grass", cancollide=False)


def fern(x, z, y):
    for k in (0, 90):
        part("Fern", (2.0, 1.1, 0.14), (x, y + 0.5, z), yaw=k + rng.uniform(-20, 20),
             pitch=-12, color=(52, 82, 44), material="Grass", cancollide=False)


def flower(x, z, y):
    col = rng.choice([(210, 80, 160), (230, 90, 70), (240, 240, 200), (110, 160, 255)])
    part("Flower_Stem", (0.14, 1.1, 0.14), (x, y + 0.55, z), color=(60, 90, 50),
         material="Grass", cancollide=False)
    part("Flower", (0.45, 0.45, 0.45), (x, y + 1.2, z), shape="Ball", color=col,
         material="Neon", cancollide=False)


def fallen_log(x, z, y):
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
    rock(x, z, y, 0.6, "Rock", (96, 96, 100))
    rock(x + rng.uniform(-2, 2), z + rng.uniform(-2, 2), y, 0.4, "Rock",
         (110, 110, 114))


def ruin_fragment(x, z, y):
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
    """Вулкан с жерлом, лавовым водопадом и паркуром на платформах."""
    w = 210
    y = gy
    hts = [30, 27, 24, 21, 18]
    cols = [(54, 48, 52), (60, 52, 54), (66, 56, 56), (74, 60, 58), (82, 66, 62)]
    for i, hh in enumerate(hts):
        part("Volcano_Tier%d" % i, (w, hh, w),
             (cx + rng.uniform(-6, 6), y + hh / 2, cz + rng.uniform(-6, 6)),
             yaw=rng.uniform(0, 90), color=cols[i], material="Basalt")
        y += hh
        w *= 0.72
    # жерло
    disc("Volcano_Rim", cx, cz, y + 1.5, 32, 3, (48, 42, 46), "Basalt")
    disc("Volcano_Lava", cx, cz, y + 2.6, 20, 1.2, (255, 96, 18), "Neon",
         light=dict(brightness=2.2, range=90, color=(255, 120, 40), shadows=True))
    part("Volcano_Smoke", (0.1, 0.1, 0.1), (cx, y + 8, cz), transparency=1,
         cancollide=False,
         fire=dict(size=14, heat=2, color=(90, 90, 96), secondary=(40, 40, 46)))
    # лавовый водопад по южному склону
    for i, (oy, ln, pitch) in enumerate([(0, 42, 0), (-40, 40, 14), (-76, 38, 26)]):
        part("Volcano_LavaFall", (11, ln, 3),
             (cx, y - 4 + oy - ln / 2 * math.cos(math.radians(pitch)),
              cz + 20 + ln / 2 * math.sin(math.radians(pitch))),
             pitch=pitch, color=(255, 96, 18), material="Neon", cancollide=False,
             light=dict(brightness=1.4, range=30, color=(255, 110, 30))
             if i == 0 else None)
    lava_pool(cx, cz + 92, gy, 26)
    # паркур: деревянные платформы по спирали к жерлу
    import math as _m
    for i in range(9):
        a = 1.2 + i * 0.75
        rr = 95 - i * 6.5
        py = gy + 8 + i * 9.5
        px, pz = cx + _m.sin(a) * rr, cz + _m.cos(a) * rr
        part("Volcano_Plank%d" % i, (6.5, 0.9, 6.5), (px, py, pz), yaw=i * 30,
             color=(74, 58, 44), material="WoodPlanks")
        if i % 3 == 2:
            torch_wall(px, pz + 3, py, 0)
    part("Volcano_Summit", (9, 1, 9), (cx + 14, y - 2, cz + 14), color=(74, 58, 44),
         material="WoodPlanks")
    chest_marker(cx + 14, cz + 14, y - 1.4, "Volcano")


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
    folder("Sea")
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            part("Sea", (2048, 3, 2048), (i * 2048, -1.5, j * 2048),
                 color=(24, 52, 66), material="Water", transparency=0.1,
                 cancollide=False)
            # глубинная вода (объём)
            part("DeepWater", (2048, 26, 2048), (i * 2048, -17, j * 2048),
                 color=(14, 34, 46), material="Water", transparency=0.4,
                 cancollide=False)
            # глубокое дно
            part("Abyss", (2048, 3, 2048), (i * 2048, -35.5, j * 2048),
                 color=(10, 14, 18), material="Basalt")
    endfolder()


def build_continent(parent):
    """Единый материк по полигону: зелёная земля, пляжи, лагуны, отмели."""
    folder("Landmass")
    CELL = 250.0
    beach_cells = []
    shelf_cells = []
    gx = -3000
    while gx < 3000:
        gz = -3000
        while gz < 3000:
            cx, cz = gx + CELL / 2, gz + CELL / 2
            if point_in_poly(cx, cz):
                d = poly_edge_dist(cx, cz)
                if d < 170:
                    col, mat = ground_style(cx, cz)
                    # пляж: песчаная кромка + каменный «фундамент» под водой
                    part("Beach", (CELL, 10, CELL), (cx, -1, cz),
                         color=(198, 182, 142), material="Sand")
                    part("Beach_Cliff", (CELL - 6, 8, CELL - 6), (cx, -9, cz),
                         color=(96, 92, 84), material="Rock")
                    beach_cells.append((cx, cz))
                else:
                    col, mat = ground_style(cx, cz)
                    part("Ground", (CELL, 20, CELL), (cx, -2, cz), color=col,
                         material=mat)
                    if d < 470:
                        shelf_cells.append((cx, cz))
            gz += CELL
        gx += CELL
    # отмели: песчаное дно и лагунная вода вдоль берега
    for (cx, cz) in shelf_cells:
        part("Shelf_Floor", (CELL, 2, CELL), (cx, -6.0, cz), color=(168, 156, 126),
             material="Sand")
        part("Shelf_Water", (CELL, 7.2, CELL), (cx, -2.9, cz), color=(40, 90, 105),
             material="Water", transparency=0.3, cancollide=False)
    # подводная растительность и руины на отмелях
    kelp_n = 0
    for (cx, cz) in shelf_cells:
        if rng.random() < 0.4 and kelp_n < 220:
            for _ in range(rng.randint(1, 3)):
                kelp(cx + rng.uniform(-90, 90), cz + rng.uniform(-90, 90))
            kelp_n += 1
    sunken_ruins(1750, 2620)
    sea_serpent_bones(1200, 2780)
    sunken_boat(2350, 2520)
    # прибрежные валуны на пляжах
    for (cx, cz) in beach_cells:
        if rng.random() < 0.25:
            rock(cx + rng.uniform(-90, 90), cz + rng.uniform(-90, 90), 4.0, 1.2,
                 "Rock", (110, 112, 118))
    endfolder()


def road(x0, z0, x1, z1, top_y, width=9, color=(98, 94, 90), mat="Cobblestone"):
    dx, dz = x1 - x0, z1 - z0
    dist = math.hypot(dx, dz)
    n = max(1, int(dist // 14))
    yaw = math.degrees(math.atan2(dx, dz))
    for i in range(n + 1):
        t = i / float(n)
        part("Road", (width, 0.5, 14), (x0 + dx * t, top_y + 0.25, z0 + dz * t),
             yaw=yaw, color=color, material=mat)


def ramp(cx, cz, base_y, rise, length, width, direction):
    """direction: '+Z','-Z','+X','-X' — куда ведёт подъём."""
    yaw = {"+Z": 0, "-Z": 180, "+X": 90, "-X": -90}[direction]
    part("Ramp", (width, rise, length), (cx, base_y + rise / 2.0, cz), yaw=yaw,
         color=(96, 92, 88), material="Cobblestone", cls="WedgePart")


# ------------------------- ЗОНЫ --------------------------------------------

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
    signpost(8, 146, GY + 0.55, 0, "EMBERFALL v8\nмагия, мобы, боссы, прокачка")

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
    mega_mesa(-860, -380, 14, base_w=120, h=100, snow=90)
    mega_mesa(-880, 470, 14, base_w=130, h=112, snow=90)
    mega_mesa(-480, 760, 8, base_w=115, h=92, snow=120)
    mega_mesa(500, 770, 8, base_w=120, h=96, snow=120)
    mega_mesa(200, -950, 8, base_w=105, h=85, snow=120)
    mega_mesa(-200, -950, 8, base_w=105, h=85, snow=120)

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
    slab("GloomwoodGround", -2300, -700, -700, 800, GY, 6, (72, 104, 62), "Ground")
    plateau_skirt("GloomwoodGround", -2300, -700, -700, 800, GY, (88, 116, 66))
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
    mega_mesa(-1000, -620, GY, base_w=72, h=62, snow=200)
    mega_mesa(-1130, -540, GY, base_w=90, h=80, snow=200)
    mega_mesa(-1320, -590, GY, base_w=76, h=68, snow=200)

    # --- лагерь разбойников ---
    bandit_camp(-1000, 320, GY, yaw=15, name="BanditCamp")

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
    slab("FrostT1", -2300, -2300, -900, -1000, 20, 6, (216, 222, 232), "Snow")
    slab("FrostT2", -2100, -2100, -1100, -1200, 32, 16, (210, 218, 230), "Snow")
    slab("FrostT3", -1900, -1900, -1300, -1400, 46, 28, (168, 196, 222), "Glacier")
    slab("FrostT4", -1750, -1750, -1450, -1550, 62, 42, (222, 228, 238), "Snow")

    ramp(-1100, -1650, 20, 12, 40, 16, "-X")
    ramp(-1300, -1550, 32, 14, 44, 16, "-X")
    ramp(-1600, -1550, 46, 16, 44, 16, "-Z")

    # горы-великаны (взбираются по ступеням-слоям)
    mega_mesa(-2050, -2100, 20, base_w=185, h=145, snow=40)
    mega_mesa(-1150, -2150, 20, base_w=145, h=120, snow=40)

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
    hamlet_excl = [(-1750, -1150, 40), (-1750, -1500, 60)]
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
    signpost(-1712, -1120, 20, -45, "Горная Обитель\n← Ледяная Гробница")
    lamppost(-1735, -1140, 20)
    lamppost(-1765, -1170, 20)

    # Ледяная Гробница — подземелье с боссом Морозным Призраком
    ice_tomb(-1750, -1500, 20, yaw=0)

    # Ледовый паркур к арене Колосса
    parkour_rocks((-1400, -1520), (-1560, -1660), 22, 60, 10,
                  col=(170, 200, 230), tag="Peaks")
    signpost(-1396, -1512, 20, 40, "Восхождение ↑\n(паркур к арене)")

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
    slab("AshGround", -800, -2500, 1000, -1100, GY, 6, (130, 98, 84), "Basalt")
    plateau_skirt("AshGround", -800, -2500, 1000, -1100, GY, (112, 96, 78),
                  mat="Basalt")
    slab("AshCracked", -600, -2300, 800, -1300, GY + 0.2, GY - 1.8, (104, 82, 70),
         "CrackedLava")

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
    mega_mesa(750, -2320, GY, base_w=130, h=108, snow=400)
    mega_mesa(-560, -1220, GY, base_w=105, h=95, snow=400)
    volcano(300, -2250, GY)
    signpost(52, -2130, GY, 150, "Вулкан Пепла ↑\n(паркур к жерлу)")

    # лагерь мародёров
    bandit_camp(520, -1380, GY, yaw=200, tent_cols=((70, 60, 56), (58, 50, 48)),
                banner_col=(180, 60, 30), name="MarauderCamp")

    fortress_ruins(250, -1850, GY)
    boss_arena_circular("AshArena", 100, -2100, GY, r=65, pillar_col=(38, 35, 42),
                        pillar_mat="Basalt", boss_id="Ashlord")
    for i in range(8):
        a = math.pi * 2 * i / 8
        lava_pool(100 + math.sin(a) * 88, -2100 + math.cos(a) * 88, GY, 9)
    endfolder()


def build_mirefen(parent):
    folder("Mirefen")
    GY = 12.0
    slab("MirefenGround", 700, -900, 2300, 1000, GY, 6, (130, 110, 64), "Mud")
    plateau_skirt("MirefenGround", 700, -900, 2300, 1000, GY, (118, 118, 68))
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
    slab("CoastSand", 800, 900, 2400, 2300, GY, 6.4, (200, 184, 142), "Sand")
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
    mega_mesa(1600, 1450, 8.4, base_w=120, h=95, snow=150)
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
    slab("BoneGround", -900, 800, 900, 2300, GY, 6, (140, 144, 94), "Ground")
    plateau_skirt("BoneGround", -900, 800, 900, 2300, GY, (118, 128, 78))
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


def build_game_logic(parent):
    folder("GameLogic")

    folder("ZoneTriggers")
    zone_trigger("Emberfall", -340, -240, 340, 440)
    zone_trigger("Gloomwood", -2320, -720, -680, 820)
    zone_trigger("Frostpeak", -2520, -2520, -680, -820)
    zone_trigger("Ashwaste", -820, -2520, 1020, -1080)
    zone_trigger("Mirefen", 680, -920, 2320, 1020)
    zone_trigger("SunkenCoast", 680, 880, 2420, 2320)
    zone_trigger("Bonefields", -920, 880, 920, 2320)
    zone_trigger("HollowDeep", -2330, 1730, -2070, 1970)
    endfolder()

    folder("MobSpawns")
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
	{ cmds = {"!гробница", "!tomb"},   pos = Vector3.new(-1750, 26, -1460), name = "Ледяная Гробница (данж)" },
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
    for module_name in ["Config", "GameData", "Net", "Util", "Quests", "NPCData"]:
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
    out_name = "Emberfall_Map_v8.rbxlx"

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

    folder("World")
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
