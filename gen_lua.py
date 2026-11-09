# -*- coding: utf-8 -*-
"""АВТОГЕНЕРАЦИЯ. Правь Lua в src/lua/**, затем: python3 tools/build_lua.py"""

SHARED = {}
SHARED["Config"] = """-- Emberfall | Config — все числа баланса и палитра в одном месте.
-- Правка баланса не требует трогать логику.

local Config = {}

Config.Version = "v11"
Config.GameName = "EMBERFALL — Пепел Вечности"

-- ---------------------------- уровень / опыт -------------------------------
Config.MaxLevel = 60
Config.StatPointsPerLevel = 3
Config.StartingStatPoints = 2

function Config.XpForLevel(level)
	-- сколько нужно опыта, чтобы уйти с уровня level
	if level >= Config.MaxLevel then return math.huge end
	return math.floor(40 * (level ^ 1.52) + 45 * level)
end

-- ---------------------------- характеристики ---------------------------------
Config.BaseHealth = 100
Config.BaseMana = 100
Config.BasePower = 10
Config.BaseDefense = 0

Config.HealthPerLevel = 7
Config.ManaPerLevel = 4

Config.Stats = {
	{ id = "Power",    name = "Сила",        desc = "+4% урона за очко",        icon = "⚔" },
	{ id = "Vitality", name = "Живучесть",   desc = "+10 здоровья за очко",     icon = "❤" },
	{ id = "Insight",  name = "Прозрение",   desc = "+8 маны за очко",          icon = "✦" },
	{ id = "Agility",  name = "Ловкость",    desc = "+0.45 скорости за очко",   icon = "➤" },
	{ id = "Ward",     name = "Защита",      desc = "+2 брони за очко",         icon = "⛨" },
}

Config.PowerPerPoint = 0.04
Config.HealthPerPoint = 10
Config.ManaPerPoint = 8
Config.SpeedPerPoint = 0.45
Config.WardPerPoint = 2

-- ---------------------------- движение / выживание ---------------------------
Config.WalkSpeed = 16
Config.SprintSpeed = 25
Config.StaminaMax = 100
Config.StaminaSprintDrain = 14
Config.StaminaJumpCost = 8
Config.StaminaRegen = 18
Config.StaminaRegenDelay = 0.7

Config.ManaRegenPerSec = 4.5
Config.HealthRegenOutOfCombatPerSec = 2.0
Config.OutOfCombatTime = 8

Config.RespawnTime = 5
Config.DeathXpLoss = 0.05        -- доля опыта текущего уровня

-- ---------------------------- стихии -----------------------------------------
Config.Elements = {
	{
		id = "Fire", name = "Огонь", rune = "🔥",
		color = Color3.fromRGB(255, 122, 44),
		desc = "Высокий урон, горение, метеорит. Стихия агрессии.",
	},
	{
		id = "Ice", name = "Лёд", rune = "❄",
		color = Color3.fromRGB(120, 210, 255),
		desc = "Замедление, щит изо льда, ледяная комета.",
	},
	{
		id = "Lightning", name = "Молния", rune = "⚡",
		color = Color3.fromRGB(180, 160, 255),
		desc = "Быстрые удары, рывок-разряд, гроза.",
	},
	{
		id = "Shadow", name = "Тень", rune = "🌑",
		color = Color3.fromRGB(150, 70, 200),
		desc = "Похищение жизни, замедление, Пожирание.",
	},
	{
		id = "Nature", name = "Природа", rune = "🌿",
		color = Color3.fromRGB(120, 220, 120),
		desc = "Лечение, корни, гнев леса.",
	},
	{
		id = "Earth", name = "Земля", rune = "🪨",
		color = Color3.fromRGB(196, 152, 96),
		desc = "Каменные шипы, щит-скала, обвал. Стихия стойкости.",
	},
	{
		id = "Wind", name = "Ветер", rune = "🌀",
		color = Color3.fromRGB(190, 240, 230),
		desc = "Быстрые лезвия, рывок, смерч. Стихия скорости.",
	},
	{
		id = "Blood", name = "Кровь", rune = "🩸",
		color = Color3.fromRGB(200, 50, 70),
		desc = "Похищение жизни, жертва HP за урон, Кровавый пир.",
	},
}

Config.ElementById = {}
for _, e in ipairs(Config.Elements) do
	Config.ElementById[e.id] = e
end

-- ---------------------------- предметы/прочее ---------------------------------
Config.InventorySlots = 24
Config.EquipSlots = { weapon = "Оружие", armor = "Броня", trinket = "Амулет" }
Config.ChestCooldown = 240
Config.MeleeCooldown = 0.45
Config.MeleeRange = 8.5
Config.MeleePower = 12

Config.LogPrefix = "[Emberfall]"

return Config
"""

SHARED["GameData"] = """-- Emberfall | GameData — заклинания, мобы, боссы, предметы, лут.
-- Данные читает и сервер (урон/спавн), и клиент (хотбар, магазин, тултипы).

local GameData = {}

-- ============================================================================
-- ЗАКЛИНАНИЯ
-- kind: "projectile" | "area" | "meteor" | "dash" | "buff" | "heal" | "beam"
-- ============================================================================
GameData.Spells = {
	-- ---------------------------------- ОГОНЬ ---------------------------------
	{
		id = "Fire_Ember", name = "Искра", element = "Fire", icon = "🔥",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 12, cooldown = 1.1,
		damage = 22, speed = 120, radius = 2.2, range = 150, castTime = 0.15,
		desc = "Быстрый огненный снаряд. Дешёвый и надёжный.",
	},
	{
		id = "Fire_Orb", name = "Огненный шар", element = "Fire", icon = "☄",
		kind = "projectile", tier = 2, reqLevel = 6, manaCost = 26, cooldown = 3.2,
		damage = 46, speed = 95, radius = 5.5, range = 170, castTime = 0.35,
		burn = { dps = 8, duration = 3 },
		desc = "Взрывается при попадании, поджигает цель и всех рядом.",
	},
	{
		id = "Fire_Inferno", name = "Инферно", element = "Fire", icon = "💥",
		kind = "area", tier = 2, reqLevel = 10, manaCost = 40, cooldown = 7,
		damage = 52, radius = 22, castTime = 0.5,
		desc = "Волна пламени вокруг мага. Бьёт всех врагов в радиусе 22.",
	},
	{
		id = "Fire_Meteor", name = "Метеор", element = "Fire", icon = "🌋",
		kind = "meteor", tier = 3, reqLevel = 20, manaCost = 65, cooldown = 13,
		damage = 130, radius = 16, range = 200, fallTime = 0.85, castTime = 0.6,
		desc = "Призывает метеор в точку прицела. Огромный урон, долгий откат.",
	},
	-- ---------------------------------- ЛЁД -----------------------------------
	{
		id = "Ice_Shard", name = "Осколок льда", element = "Ice", icon = "❄",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 11, cooldown = 1.0,
		damage = 19, speed = 135, radius = 2.0, range = 160, castTime = 0.12,
		slow = { mult = 0.75, duration = 1.6 },
		desc = "Быстрый осколок, замедляет цель на 25%.",
	},
	{
		id = "Ice_Nova", name = "Ледяная новая", element = "Ice", icon = "🧊",
		kind = "area", tier = 2, reqLevel = 7, manaCost = 35, cooldown = 6,
		damage = 38, radius = 20, castTime = 0.45,
		slow = { mult = 0.5, duration = 3.5 },
		desc = "Взрыв холода: урон и сильное замедление вокруг.",
	},
	{
		id = "Ice_Shield", name = "Ледяной панцирь", element = "Ice", icon = "🛡",
		kind = "buff", tier = 2, reqLevel = 12, manaCost = 30, cooldown = 12,
		buffType = "armor", buffValue = 45, duration = 9, castTime = 0.2,
		desc = "+45 брони на 9 секунд. Лучший выживающий бафф.",
	},
	{
		id = "Ice_Comet", name = "Ледяная комета", element = "Ice", icon = "🌠",
		kind = "meteor", tier = 3, reqLevel = 22, manaCost = 60, cooldown = 12,
		damage = 105, radius = 15, range = 200, fallTime = 0.9, castTime = 0.55,
		slow = { mult = 0.4, duration = 4 },
		desc = "Комета льда с неба. Урон + глубокое замедление.",
	},
	-- --------------------------------- МОЛНИЯ ---------------------------------
	{
		id = "Lightning_Spark", name = "Разряд", element = "Lightning", icon = "⚡",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 13, cooldown = 1.2,
		damage = 24, speed = 170, radius = 2.0, range = 165, castTime = 0.1,
		desc = "Мгновенный электрический снаряд — самый быстрый в игре.",
	},
	{
		id = "Lightning_Dash", name = "Громовой рывок", element = "Lightning", icon = "💨",
		kind = "dash", tier = 1, reqLevel = 5, manaCost = 20, cooldown = 5,
		damage = 26, distance = 34, radius = 7, castTime = 0,
		desc = "Рывок вперёд с уроном всем, кого задел.",
	},
	{
		id = "Lightning_Storm", name = "Гроза", element = "Lightning", icon = "🌩",
		kind = "storm", tier = 2, reqLevel = 14, manaCost = 55, cooldown = 11,
		damage = 30, radius = 24, range = 120, strikes = 6, duration = 3.0, castTime = 0.5,
		desc = "6 ударов молний по области за 3 секунды.",
	},
	{
		id = "Lightning_Chain", name = "Цепь молний", element = "Lightning", icon = "🔗",
		kind = "chain", tier = 3, reqLevel = 24, manaCost = 58, cooldown = 10,
		damage = 78, radius = 45, chainTargets = 3, range = 160, castTime = 0.4,
		desc = "Прыгает по 3 врагам с падающим уроном.",
	},
	-- --------------------------------- ТЕНЬ -----------------------------------
	{
		id = "Shadow_Bolt", name = "Теневой болт", element = "Shadow", icon = "🌑",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 12, cooldown = 1.1,
		damage = 21, speed = 110, radius = 2.4, range = 150, castTime = 0.2,
		lifesteal = 0.35,
		desc = "Крадёт 35% нанесённого урона как здоровье.",
	},
	{
		id = "Shadow_Veil", name = "Покров тьмы", element = "Shadow", icon = "🌫",
		kind = "buff", tier = 1, reqLevel = 8, manaCost = 25, cooldown = 10,
		buffType = "speed", buffValue = 8, duration = 6, castTime = 0.15,
		desc = "+8 скорости на 6 секунд. Убежать или догнать.",
	},
	{
		id = "Shadow_Devour", name = "Пожирание", element = "Shadow", icon = "🩸",
		kind = "area", tier = 2, reqLevel = 16, manaCost = 45, cooldown = 9,
		damage = 60, radius = 18, castTime = 0.55, lifesteal = 0.5,
		desc = "Вытягивает жизнь из всех вокруг и лечит вас на половину.",
	},
	{
		id = "Shadow_Abyss", name = "Взгляд Бездны", element = "Shadow", icon = "👁",
		kind = "meteor", tier = 3, reqLevel = 28, manaCost = 70, cooldown = 15,
		damage = 120, radius = 17, range = 210, fallTime = 0.8, castTime = 0.6,
		slow = { mult = 0.45, duration = 3 }, lifesteal = 0.25,
		desc = "Разлом тьмы в точке прицела, ослабляет и лечит.",
	},
	-- -------------------------------- ПРИРОДА ---------------------------------
	{
		id = "Nature_Thorn", name = "Шип", element = "Nature", icon = "🌿",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 10, cooldown = 1.0,
		damage = 18, speed = 115, radius = 2.2, range = 150, castTime = 0.15,
		desc = "Дешёвый снаряд. Самый экономный по мане.",
	},
	{
		id = "Nature_Bloom", name = "Цветение", element = "Nature", icon = "💚",
		kind = "heal", tier = 1, reqLevel = 6, manaCost = 30, cooldown = 9,
		healAmount = 55, castTime = 0.4,
		desc = "Мгновенно восстанавливает 55 здоровья.",
	},
	{
		id = "Nature_Roots", name = "Корни", element = "Nature", icon = "🌱",
		kind = "area", tier = 2, reqLevel = 12, manaCost = 32, cooldown = 7,
		damage = 28, radius = 20, castTime = 0.4,
		slow = { mult = 0.35, duration = 4 },
		desc = "Опутывает врагов: сильное замедление до 4 секунд.",
	},
	{
		id = "Nature_Wrath", name = "Гнев леса", element = "Nature", icon = "🌳",
		kind = "meteor", tier = 3, reqLevel = 26, manaCost = 62, cooldown = 13,
		damage = 112, radius = 18, range = 200, fallTime = 0.9, castTime = 0.55,
		desc = "Древесный кулак с неба. Урон по площади.",
	},
	-- ---------------------------------- ЗЕМЛЯ ---------------------------------
	{
		id = "Earth_Stone", name = "Каменный шип", element = "Earth", icon = "🪨",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 12, cooldown = 1.25,
		damage = 25, speed = 105, radius = 2.6, range = 145, castTime = 0.18,
		desc = "Тяжёлый камень. Медленнее огня, но бьёт ощутимо.",
	},
	{
		id = "Earth_Wall", name = "Каменная кожа", element = "Earth", icon = "🧱",
		kind = "buff", tier = 1, reqLevel = 5, manaCost = 24, cooldown = 9,
		buffType = "armor", buffValue = 28, duration = 8, castTime = 0.2,
		desc = "+28 брони на 8 секунд.",
	},
	{
		id = "Earth_Quake", name = "Землетрясение", element = "Earth", icon = "⛰",
		kind = "area", tier = 2, reqLevel = 11, manaCost = 38, cooldown = 7,
		damage = 48, radius = 22, castTime = 0.5,
		slow = { mult = 0.55, duration = 2.5 },
		desc = "Волна земли: урон и замедление вокруг.",
	},
	{
		id = "Earth_Colossus", name = "Поступь колосса", element = "Earth", icon = "🗿",
		kind = "meteor", tier = 3, reqLevel = 22, manaCost = 66, cooldown = 14,
		damage = 140, radius = 19, range = 190, fallTime = 0.95, castTime = 0.6,
		desc = "Гигантская скала с неба. Сокрушительный удар по площади.",
	},
	-- ---------------------------------- ВЕТЕР ---------------------------------
	{
		id = "Wind_Blade", name = "Лезвие ветра", element = "Wind", icon = "🌀",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 10, cooldown = 0.9,
		damage = 17, speed = 160, radius = 1.9, range = 175, castTime = 0.1,
		desc = "Самый быстрый снаряд в игре — почти не промахивается.",
	},
	{
		id = "Wind_Dash", name = "Порыв", element = "Wind", icon = "💨",
		kind = "dash", tier = 1, reqLevel = 4, manaCost = 16, cooldown = 4,
		damage = 22, distance = 40, radius = 6, castTime = 0,
		desc = "Рывок с уроном всем на пути.",
	},
	{
		id = "Wind_Cyclone", name = "Смерч", element = "Wind", icon = "🌪",
		kind = "storm", tier = 2, reqLevel = 13, manaCost = 50, cooldown = 10,
		damage = 26, radius = 22, range = 130, strikes = 7, duration = 3.2, castTime = 0.45,
		desc = "7 вихрей по области за 3 секунды.",
	},
	{
		id = "Wind_Storm", name = "Буря клинков", element = "Wind", icon = "🌬",
		kind = "chain", tier = 3, reqLevel = 23, manaCost = 54, cooldown = 9,
		damage = 70, radius = 40, chainTargets = 4, range = 155, castTime = 0.35,
		desc = "Прыгает по 4 врагам.",
	},
	-- ---------------------------------- КРОВЬ ---------------------------------
	{
		id = "Blood_Drain", name = "Кровавый струй", element = "Blood", icon = "🩸",
		kind = "projectile", tier = 1, reqLevel = 1, manaCost = 13, cooldown = 1.2,
		damage = 20, speed = 115, radius = 2.2, range = 150, castTime = 0.2,
		lifesteal = 0.5,
		desc = "Крадёт 50% урона как здоровье.",
	},
	{
		id = "Blood_Sacrifice", name = "Жертвенная ярость", element = "Blood", icon = "🖤",
		kind = "buff", tier = 2, reqLevel = 9, manaCost = 20, cooldown = 12,
		buffType = "power", buffValue = 0.35, duration = 8, castTime = 0.25,
		desc = "+35% урона на 8 секунд. Цена — риск.",
	},
	{
		id = "Blood_Feast", name = "Кровавый пир", element = "Blood", icon = "🫀",
		kind = "area", tier = 2, reqLevel = 17, manaCost = 44, cooldown = 9,
		damage = 56, radius = 19, castTime = 0.5, lifesteal = 0.7,
		desc = "Вытягивает жизнь из всех вокруг, лечит на 70% урона.",
	},
	{
		id = "Blood_Exsanguinate", name = "Обескровливание", element = "Blood", icon = "💀",
		kind = "meteor", tier = 3, reqLevel = 27, manaCost = 68, cooldown = 14,
		damage = 118, radius = 16, range = 195, fallTime = 0.85, castTime = 0.55,
		lifesteal = 0.4,
		desc = "Кровавый разлом: урон по площади и лечение.",
	},
}

GameData.SpellById = {}
for _, s in ipairs(GameData.Spells) do
	GameData.SpellById[s.id] = s
end

function GameData.SpellsForElement(element)
	local out = {}
	for _, s in ipairs(GameData.Spells) do
		if s.element == element then table.insert(out, s) end
	end
	return out
end

-- ============================================================================
-- ПРЕДМЕТЫ
-- rarity: common / uncommon / rare / epic / legendary
-- ============================================================================
GameData.Rarities = {
	common    = { name = "Обычный",    color = Color3.fromRGB(200, 200, 200) },
	uncommon  = { name = "Необычный",  color = Color3.fromRGB(120, 220, 120) },
	rare      = { name = "Редкий",     color = Color3.fromRGB(90, 160, 255) },
	epic      = { name = "Эпический",  color = Color3.fromRGB(190, 120, 255) },
	legendary = { name = "Легендарный", color = Color3.fromRGB(255, 186, 70) },
}

GameData.Items = {
	-- ------------------------------ ОРУЖИЕ -----------------------------------
	{ id = "W_Stick",       name = "Дубовая палка",       type = "weapon", rarity = "common",    reqLevel = 1,  damage = 6,  speed = 1.15, price = 0,   desc = "С этого всё начинается." },
	{ id = "W_ShortSword",  name = "Короткий меч",        type = "weapon", rarity = "common",    reqLevel = 1,  damage = 12, speed = 1.0,  price = 90,  desc = "Надёжная сталь пристани." },
	{ id = "W_Hatchet",     name = "Топор лесоруба",      type = "weapon", rarity = "common",    reqLevel = 4,  damage = 16, speed = 1.2,  price = 150, desc = "Тяжёлый, но бьёт больно." },
	{ id = "W_Sabre",       name = "Глумвудская сабля",   type = "weapon", rarity = "uncommon",  reqLevel = 8,  damage = 24, speed = 0.9,  price = 320, desc = "Заточена на тенях." },
	{ id = "W_FrostBlade",  name = "Морозный клинок",     type = "weapon", rarity = "rare",      reqLevel = 14, damage = 34, speed = 0.85, price = 700, desc = "Обжигает холодом даже рукоять." },
	{ id = "W_AshCleaver",  name = "Пепельный тесак",     type = "weapon", rarity = "rare",      reqLevel = 20, damage = 46, speed = 1.05, price = 1100, desc = "Пахнет вулканом." },
	{ id = "W_BoneScythe",  name = "Костяная коса",       type = "weapon", rarity = "epic",      reqLevel = 28, damage = 62, speed = 1.1,  price = 1900, desc = "Жнёт не только траву." },
	{ id = "W_VoidEdge",    name = "Клинок Бездны",       type = "weapon", rarity = "legendary", reqLevel = 40, damage = 88, speed = 0.8,  price = 0,   desc = "Только с Безымянного Короля." },

	-- ------------------------------ БРОНЯ ------------------------------------
	{ id = "A_Rags",        name = "Тряпьё",              type = "armor", rarity = "common",    reqLevel = 1,  armor = 4,  price = 0,   desc = "Хоть что-то." },
	{ id = "A_Leather",     name = "Кожаный доспех",      type = "armor", rarity = "common",    reqLevel = 1,  armor = 10, price = 110, desc = "Дёшево и сердито." },
	{ id = "A_Chain",       name = "Кольчуга",            type = "armor", rarity = "uncommon",  reqLevel = 7,  armor = 20, price = 380, desc = "Кольцо к кольцу." },
	{ id = "A_FrostPlate",  name = "Морозная броня",      type = "armor", rarity = "rare",      reqLevel = 14, armor = 34, price = 820, desc = "Лёд держит форму камня." },
	{ id = "A_AshPlate",    name = "Пепельные латы",      type = "armor", rarity = "rare",      reqLevel = 22, armor = 48, price = 1350, desc = "Не плавится в лаве." },
	{ id = "A_BoneMail",    name = "Костяная кольчуга",   type = "armor", rarity = "epic",      reqLevel = 30, armor = 66, price = 2200, desc = "Щёлкает при ходьбе." },
	{ id = "A_VoidShroud",  name = "Саван Бездны",        type = "armor", rarity = "legendary", reqLevel = 42, armor = 95, price = 0,   desc = "Тьма поглощает удары." },

	-- ------------------------------ АМУЛЕТЫ ----------------------------------
	{ id = "T_EmberCharm",  name = "Уголёк-оберег",       type = "trinket", rarity = "common",    reqLevel = 2,  manaBonus = 10, price = 140, desc = "+10 маны." },
	{ id = "T_SwiftCharm",  name = "Оберег скорости",     type = "trinket", rarity = "uncommon",  reqLevel = 9,  speedBonus = 2,  price = 420, desc = "+2 скорости." },
	{ id = "T_FocusCharm",  name = "Амулет сосредоточения", type = "trinket", rarity = "rare",    reqLevel = 18, manaBonus = 35, cooldownBonus = 0.08, price = 900, desc = "+35 маны, -8% откатов." },
	{ id = "T_BloodCharm",  name = "Кровавый амулет",     type = "trinket", rarity = "epic",      reqLevel = 26, lifesteal = 0.08, healthBonus = 40, price = 1800, desc = "+8% похищения жизни." },

	-- ------------------------------ РАСХОДНИКИ --------------------------------
	{ id = "C_HealthPotion", name = "Зелье здоровья",     type = "consumable", rarity = "common", price = 45,  stack = 20, heal = 60,  desc = "Восстанавливает 60 здоровья." },
	{ id = "C_ManaPotion",   name = "Зелье маны",         type = "consumable", rarity = "common", price = 50,  stack = 20, mana = 60,  desc = "Восстанавливает 60 маны." },
	{ id = "C_Elixir",       name = "Эликсир силы",       type = "consumable", rarity = "rare",   price = 260, stack = 10, buffPower = 0.25, buffDuration = 25, desc = "+25% урона на 25 секунд." },
	{ id = "C_Bread",        name = "Хлеб пристани",      type = "consumable", rarity = "common", price = 12,  stack = 30, heal = 25,  desc = "Быстрый перекус." },

	-- ------------------------------ МАТЕРИАЛЫ --------------------------------
	{ id = "M_Pelt",        name = "Шкура",               type = "material", rarity = "common", price = 18, desc = "Сгодится кузнецу." },
	{ id = "M_Fang",        name = "Клык",                type = "material", rarity = "common", price = 26, desc = "Острый." },
	{ id = "M_Ore",         name = "Руда",                type = "material", rarity = "uncommon", price = 40, desc = "Железо для ковки." },
	{ id = "M_IceShard",    name = "Ледяной осколок",     type = "material", rarity = "uncommon", price = 55, desc = "Не тает." },
	{ id = "M_AshEssence",  name = "Пепельная эссенция",  type = "material", rarity = "rare", price = 90, desc = "Тёплая на ощупь." },
	{ id = "M_BoneDust",    name = "Костяная пыль",       type = "material", rarity = "rare", price = 85, desc = "Материал для ритуалов." },
	{ id = "M_VoidShard",   name = "Осколок Бездны",      type = "material", rarity = "epic", price = 220, desc = "Смотрит в ответ." },
	{ id = "M_Coral",       name = "Коралл",              type = "material", rarity = "uncommon", price = 60, desc = "Хрустит под ногами." },
	{ id = "M_EmberStone",  name = "Пепельный камень",    type = "material", rarity = "rare", price = 100, desc = "Ещё тёплый." },
}

GameData.ItemById = {}
for _, it in ipairs(GameData.Items) do
	GameData.ItemById[it.id] = it
end

function GameData.ItemsOfType(t)
	local out = {}
	for _, it in ipairs(GameData.Items) do
		if it.type == t then table.insert(out, it) end
	end
	return out
end

-- ============================================================================
-- МОБЫ
-- model: "humanoid" (гуманоидная стойка), "beast" (четвероногое), "golem", "floating"
-- ============================================================================
GameData.Mobs = {
	-- ГЛУМВУД (10-20)
	{ id = "ShadowWolf",  name = "Теневой волк",   zone = "Gloomwood", level = 10, health = 90,  damage = 9,  speed = 17, xp = 32,
	  model = "beast", color = Color3.fromRGB(70, 66, 92), scale = 1.0, aggro = 55, attackCooldown = 1.4,
	  loot = { { item = "M_Pelt", chance = 0.55, min = 1, max = 2 }, { item = "M_Fang", chance = 0.3 } } },
	{ id = "GloomGoblin", name = "Глумвудский гоблин", zone = "Gloomwood", level = 11, health = 110, damage = 11, speed = 15, xp = 38,
	  model = "humanoid", color = Color3.fromRGB(96, 130, 78), scale = 0.85, aggro = 50, attackCooldown = 1.5,
	  loot = { { item = "M_Pelt", chance = 0.35 }, { item = "C_Bread", chance = 0.2 }, { item = "M_Ore", chance = 0.18 } } },
	{ id = "Bandit",      name = "Разбойник",      zone = "Gloomwood", level = 14, health = 165, damage = 15, speed = 15, xp = 60,
	  model = "humanoid", color = Color3.fromRGB(118, 92, 70), scale = 1.0, aggro = 60, attackCooldown = 1.3,
	  loot = { { item = "W_ShortSword", chance = 0.08 }, { item = "C_HealthPotion", chance = 0.25 }, { item = "M_Ore", chance = 0.3 } } },
	{ id = "ForestHorror", name = "Лесной ужас",   zone = "Gloomwood", level = 18, health = 420, damage = 24, speed = 13, xp = 210, elite = true,
	  model = "golem", color = Color3.fromRGB(58, 82, 52), scale = 1.5, aggro = 70, attackCooldown = 2.2,
	  loot = { { item = "W_Sabre", chance = 0.3 }, { item = "A_Chain", chance = 0.25 }, { item = "M_Pelt", chance = 1, min = 2, max = 4 } } },

	-- ЗАТОНУВШИЙ БЕРЕГ (15-25)
	{ id = "Drowned",     name = "Утопленник",     zone = "SunkenCoast", level = 16, health = 150, damage = 14, speed = 13, xp = 58,
	  model = "humanoid", color = Color3.fromRGB(78, 112, 104), scale = 1.0, aggro = 55, attackCooldown = 1.6,
	  loot = { { item = "C_HealthPotion", chance = 0.2 }, { item = "M_Ore", chance = 0.25 } } },
	{ id = "PirateDead",  name = "Пират-мертвец",  zone = "SunkenCoast", level = 20, health = 210, damage = 19, speed = 15, xp = 88,
	  model = "humanoid", color = Color3.fromRGB(96, 74, 62), scale = 1.0, aggro = 60, attackCooldown = 1.4,
	  loot = { { item = "W_Hatchet", chance = 0.12 }, { item = "C_ManaPotion", chance = 0.2 }, { item = "M_Ore", chance = 0.3 } } },
	{ id = "PirateGhost", name = "Призрак корсара", zone = "SunkenCoast", level = 22, health = 180, damage = 22, speed = 14, xp = 110,
	  model = "floating", color = Color3.fromRGB(140, 200, 210), scale = 1.0, aggro = 70, attackCooldown = 2.0, ranged = 70,
	  loot = { { item = "T_EmberCharm", chance = 0.12 }, { item = "M_IceShard", chance = 0.2 } } },

	-- МОРОЗНЫЕ ПИКИ (20-35)
	{ id = "FrostWolf",   name = "Морозный волк",  zone = "Frostpeak", level = 22, health = 230, damage = 21, speed = 18, xp = 115,
	  model = "beast", color = Color3.fromRGB(200, 220, 235), scale = 1.1, aggro = 60, attackCooldown = 1.3,
	  loot = { { item = "M_Pelt", chance = 0.8, min = 1, max = 3 }, { item = "M_IceShard", chance = 0.3 } } },
	{ id = "SnowGolem",   name = "Снежный голем",  zone = "Frostpeak", level = 26, health = 480, damage = 28, speed = 10, xp = 190,
	  model = "golem", color = Color3.fromRGB(226, 236, 246), scale = 1.4, aggro = 55, attackCooldown = 2.4,
	  loot = { { item = "M_IceShard", chance = 0.75, min = 1, max = 3 }, { item = "A_FrostPlate", chance = 0.08 } } },
	{ id = "FrostRenegade", name = "Отступник-охотник", zone = "Frostpeak", level = 24, health = 280, damage = 24, speed = 15, xp = 150,
	  model = "humanoid", color = Color3.fromRGB(88, 96, 120), scale = 1.05, aggro = 70, attackCooldown = 1.5, ranged = 65,
	  loot = { { item = "W_FrostBlade", chance = 0.1 }, { item = "C_ManaPotion", chance = 0.3 } } },

	-- ТОПИ МИРЕФЕН (25-40)
	{ id = "BogLurker",   name = "Болотный гад",   zone = "Mirefen", level = 26, health = 260, damage = 24, speed = 14, xp = 135,
	  model = "beast", color = Color3.fromRGB(86, 104, 58), scale = 1.2, aggro = 55, attackCooldown = 1.5,
	  loot = { { item = "M_Pelt", chance = 0.6 }, { item = "C_Bread", chance = 0.3 } } },
	{ id = "MireZombie",  name = "Трясинный зомби", zone = "Mirefen", level = 30, health = 330, damage = 28, speed = 11, xp = 165,
	  model = "humanoid", color = Color3.fromRGB(102, 118, 74), scale = 1.0, aggro = 50, attackCooldown = 1.9,
	  loot = { { item = "M_BoneDust", chance = 0.3 }, { item = "C_HealthPotion", chance = 0.25 } } },
	{ id = "SporeShaman", name = "Грибной шаман",  zone = "Mirefen", level = 32, health = 240, damage = 30, speed = 13, xp = 180,
	  model = "humanoid", color = Color3.fromRGB(150, 120, 170), scale = 1.0, aggro = 75, attackCooldown = 2.2, ranged = 75,
	  loot = { { item = "C_ManaPotion", chance = 0.4 }, { item = "M_BoneDust", chance = 0.2 }, { item = "T_SwiftCharm", chance = 0.07 } } },

	-- ПЕПЕЛЬНЫЕ ПУСТОШИ (35-50)
	{ id = "AshHound",    name = "Пепельный пёс",  zone = "Ashwaste", level = 34, health = 320, damage = 30, speed = 19, xp = 200,
	  model = "beast", color = Color3.fromRGB(96, 72, 62), scale = 1.1, aggro = 65, attackCooldown = 1.2,
	  loot = { { item = "M_Fang", chance = 0.7, min = 1, max = 2 }, { item = "M_AshEssence", chance = 0.25 } } },
	{ id = "Marauder",    name = "Мародёр пустошей", zone = "Ashwaste", level = 38, health = 420, damage = 36, speed = 15, xp = 260,
	  model = "humanoid", color = Color3.fromRGB(84, 60, 52), scale = 1.05, aggro = 65, attackCooldown = 1.4,
	  loot = { { item = "W_AshCleaver", chance = 0.09 }, { item = "C_Elixir", chance = 0.12 }, { item = "M_Ore", chance = 0.35 } } },
	{ id = "LavaElemental", name = "Лавовый элементаль", zone = "Ashwaste", level = 42, health = 620, damage = 44, speed = 12, xp = 380, elite = true,
	  model = "golem", color = Color3.fromRGB(210, 92, 40), scale = 1.35, aggro = 60, attackCooldown = 2.1, glow = true,
	  loot = { { item = "M_AshEssence", chance = 1, min = 1, max = 3 }, { item = "A_AshPlate", chance = 0.12 }, { item = "C_Elixir", chance = 0.2 } } },

	-- КОСТЯНЫЕ ПОЛЯ (30-45)
	{ id = "Skeleton",    name = "Скелет",         zone = "Bonefields", level = 31, health = 300, damage = 27, speed = 13, xp = 170,
	  model = "humanoid", color = Color3.fromRGB(214, 208, 186), scale = 1.0, aggro = 55, attackCooldown = 1.5,
	  loot = { { item = "M_BoneDust", chance = 0.5, min = 1, max = 2 }, { item = "M_Ore", chance = 0.15 } } },
	{ id = "SkeletonArcher", name = "Скелет-лучник", zone = "Bonefields", level = 33, health = 240, damage = 29, speed = 12, xp = 185,
	  model = "humanoid", color = Color3.fromRGB(198, 192, 172), scale = 1.0, aggro = 80, attackCooldown = 2.0, ranged = 80,
	  loot = { { item = "M_BoneDust", chance = 0.45 }, { item = "C_HealthPotion", chance = 0.2 } } },
	{ id = "Cultist",     name = "Культист",       zone = "Bonefields", level = 36, health = 380, damage = 34, speed = 14, xp = 240,
	  model = "humanoid", color = Color3.fromRGB(120, 60, 140), scale = 1.0, aggro = 70, attackCooldown = 1.8, ranged = 70,
	  loot = { { item = "T_FocusCharm", chance = 0.06 }, { item = "C_ManaPotion", chance = 0.35 }, { item = "M_BoneDust", chance = 0.3 } } },
	{ id = "BoneGuardian", name = "Костяной страж", zone = "Bonefields", level = 40, health = 720, damage = 46, speed = 12, xp = 430, elite = true,
	  model = "golem", color = Color3.fromRGB(226, 220, 198), scale = 1.45, aggro = 60, attackCooldown = 2.3,
	  loot = { { item = "W_BoneScythe", chance = 0.12 }, { item = "A_BoneMail", chance = 0.1 }, { item = "M_BoneDust", chance = 1, min = 2, max = 4 } } },

	-- ПРЕДГОРЬЯ (26-34)
	{ id = "RockTroll", name = "Каменный тролль", zone = "Highlands", level = 28, health = 520, damage = 30, speed = 12, xp = 210, elite = true,
	  model = "golem", color = Color3.fromRGB(126, 116, 100), scale = 1.45, aggro = 60, attackCooldown = 2.1,
	  loot = { { item = "M_Ore", chance = 0.8, min = 1, max = 3 }, { item = "A_Chain", chance = 0.08 } } },
	{ id = "MinerGhoul", name = "Шахтный гуль", zone = "Highlands", level = 26, health = 300, damage = 26, speed = 14, xp = 160,
	  model = "humanoid", color = Color3.fromRGB(110, 106, 92), scale = 1.0, aggro = 55, attackCooldown = 1.6,
	  loot = { { item = "M_Ore", chance = 0.5 }, { item = "C_HealthPotion", chance = 0.2 } } },
	{ id = "Highwayman", name = "Горный разбойник", zone = "Highlands", level = 30, health = 380, damage = 32, speed = 15, xp = 220,
	  model = "humanoid", color = Color3.fromRGB(98, 76, 58), scale = 1.0, aggro = 70, attackCooldown = 1.4, ranged = 65,
	  loot = { { item = "C_Elixir", chance = 0.1 }, { item = "W_Hatchet", chance = 0.1 }, { item = "M_Ore", chance = 0.4 } } },

	-- АРХИПЕЛАГ (28-40)
	{ id = "SeaWraith", name = "Морской призрак", zone = "Archipelago", level = 32, health = 360, damage = 34, speed = 15, xp = 240,
	  model = "floating", color = Color3.fromRGB(120, 180, 200), scale = 1.1, aggro = 70, attackCooldown = 1.9, ranged = 75,
	  loot = { { item = "M_IceShard", chance = 0.4 }, { item = "C_ManaPotion", chance = 0.3 } } },
	{ id = "PirateLord", name = "Пират-капитан", zone = "Archipelago", level = 36, health = 620, damage = 40, speed = 15, xp = 330, elite = true,
	  model = "humanoid", color = Color3.fromRGB(120, 70, 60), scale = 1.2, aggro = 70, attackCooldown = 1.6,
	  loot = { { item = "W_Sabre", chance = 0.2 }, { item = "C_Elixir", chance = 0.25 }, { item = "T_SwiftCharm", chance = 0.1 } } },
	{ id = "FrostCrab", name = "Морозный краб", zone = "Archipelago", level = 29, health = 340, damage = 28, speed = 13, xp = 190,
	  model = "beast", color = Color3.fromRGB(190, 210, 220), scale = 1.2, aggro = 50, attackCooldown = 1.7,
	  loot = { { item = "M_Pelt", chance = 0.5 }, { item = "M_IceShard", chance = 0.25 } } },

	-- ЮЖНЫЕ ОСТРОВА (22-32)
	{ id = "CoralGolem", name = "Коралловый голем", zone = "SouthIsles", level = 24, health = 420, damage = 24, speed = 11, xp = 170,
	  model = "golem", color = Color3.fromRGB(210, 140, 150), scale = 1.3, aggro = 55, attackCooldown = 2.0,
	  loot = { { item = "M_BoneDust", chance = 0.4 }, { item = "C_HealthPotion", chance = 0.3 } } },
	{ id = "BeachRaider", name = "Береговой налётчик", zone = "SouthIsles", level = 28, health = 320, damage = 28, speed = 16, xp = 200,
	  model = "humanoid", color = Color3.fromRGB(100, 84, 66), scale = 1.0, aggro = 65, attackCooldown = 1.5,
	  loot = { { item = "C_Elixir", chance = 0.08 }, { item = "M_Ore", chance = 0.35 } } },

	-- ПОЛАЯ БЕЗДНА (50+)
	{ id = "VoidStalker", name = "Теневой страж",  zone = "HollowDeep", level = 52, health = 900, damage = 58, speed = 16, xp = 620, elite = true,
	  model = "floating", color = Color3.fromRGB(66, 40, 96), scale = 1.2, aggro = 75, attackCooldown = 1.6, glow = true,
	  loot = { { item = "M_VoidShard", chance = 0.5 }, { item = "C_Elixir", chance = 0.3 } } },
	{ id = "CrystalGolem", name = "Кристальный голем", zone = "HollowDeep", level = 54, health = 1200, damage = 64, speed = 10, xp = 780, elite = true,
	  model = "golem", color = Color3.fromRGB(120, 90, 200), scale = 1.6, aggro = 55, attackCooldown = 2.5, glow = true,
	  loot = { { item = "M_VoidShard", chance = 0.8, min = 1, max = 2 }, { item = "A_VoidShroud", chance = 0.06 } } },

	-- ===== v11: обитатели новых подземелий =====
	{ id = "MineGhoulBoss", name = "Шахтный вурдалак", zone = "Highlands", level = 38, health = 620, damage = 40, speed = 14, xp = 380, elite = true,
	  model = "humanoid", color = Color3.fromRGB(96, 88, 76), scale = 1.2, aggro = 70, attackCooldown = 1.5,
	  loot = { { item = "M_Ore", chance = 0.9, min = 2, max = 4 }, { item = "C_Elixir", chance = 0.2 } } },
	{ id = "BogHydraSpawn", name = "Болотный выродок", zone = "Mirefen", level = 42, health = 760, damage = 48, speed = 12, xp = 460, elite = true,
	  model = "beast", color = Color3.fromRGB(78, 112, 66), scale = 1.4, aggro = 65, attackCooldown = 1.8, glow = true,
	  loot = { { item = "M_BoneDust", chance = 0.7, min = 1, max = 3 }, { item = "C_Elixir", chance = 0.25 } } },
	{ id = "ForgeSlave", name = "Пленный кузнец", zone = "Ashwaste", level = 46, health = 980, damage = 56, speed = 13, xp = 560, elite = true,
	  model = "humanoid", color = Color3.fromRGB(160, 70, 40), scale = 1.3, aggro = 70, attackCooldown = 1.6, glow = true,
	  loot = { { item = "M_AshEssence", chance = 0.8, min = 1, max = 3 }, { item = "M_EmberStone", chance = 0.3 } } },
	{ id = "DrownedSailor", name = "Утонувший матрос", zone = "Archipelago", level = 34, health = 480, damage = 34, speed = 13, xp = 300, elite = true,
	  model = "humanoid", color = Color3.fromRGB(70, 96, 108), scale = 1.1, aggro = 65, attackCooldown = 1.6,
	  loot = { { item = "M_Coral", chance = 0.5 }, { item = "C_HealthPotion", chance = 0.3 } } },
	{ id = "CoralSentinel", name = "Коралловый страж", zone = "SouthIsles", level = 30, health = 520, damage = 32, speed = 11, xp = 320, elite = true,
	  model = "golem", color = Color3.fromRGB(220, 150, 170), scale = 1.4, aggro = 60, attackCooldown = 2.0,
	  loot = { { item = "M_Coral", chance = 0.8, min = 1, max = 2 }, { item = "C_ManaPotion", chance = 0.4 } } },
	{ id = "BoneScribe", name = "Костяной писарь", zone = "Bonefields", level = 36, health = 560, damage = 44, speed = 14, xp = 360, elite = true,
	  model = "floating", color = Color3.fromRGB(196, 186, 150), scale = 1.2, aggro = 70, attackCooldown = 1.7,
	  loot = { { item = "M_BoneDust", chance = 0.9, min = 2, max = 4 }, { item = "C_ManaPotion", chance = 0.35 } } },
}

GameData.MobById = {}
for _, m in ipairs(GameData.Mobs) do
	GameData.MobById[m.id] = m
end

function GameData.MobsInZone(zone)
	local out = {}
	for _, m in ipairs(GameData.Mobs) do
		if m.zone == zone then table.insert(out, m) end
	end
	return out
end

-- ============================================================================
-- БОССЫ
-- phases: { at = 0.6 (доля HP), abilities = {...} }
-- ============================================================================
GameData.Bosses = {
	{
		id = "FrostWraith", name = "Ледяной Призрак", title = "Страж Ледяной Гробницы",
		level = 30, health = 3200, damage = 42, speed = 13, xp = 1400,
		model = "floating", color = Color3.fromRGB(150, 216, 255), scale = 2.0, glow = true,
		arenaRadius = 48, respawn = 150,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley" } },
			{ at = 0.55, abilities = { "Slam", "Volley", "FrostNova" } },
			{ at = 0.25, abilities = { "Slam", "FrostNova", "Summon" }, enrage = 0.35 },
		},
		loot = { { item = "W_FrostBlade", chance = 0.6 }, { item = "A_FrostPlate", chance = 0.6 },
		         { item = "M_IceShard", chance = 1, min = 3, max = 6 }, { item = "C_ManaPotion", chance = 1, min = 2, max = 3 } },
	},
	{
		id = "FrostColossus", name = "Ледяной Колосс", title = "Титан Морозных Пиков",
		level = 35, health = 5200, damage = 55, speed = 11, xp = 2600,
		model = "golem", color = Color3.fromRGB(200, 232, 255), scale = 2.6, glow = true,
		arenaRadius = 77, respawn = 180,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley" } },
			{ at = 0.6, abilities = { "Slam", "FrostNova", "Summon" } },
			{ at = 0.3, abilities = { "Slam", "FrostNova", "Meteor" }, enrage = 0.4 },
		},
		loot = { { item = "A_FrostPlate", chance = 0.75 }, { item = "T_FocusCharm", chance = 0.4 },
		         { item = "M_IceShard", chance = 1, min = 4, max = 8 }, { item = "C_Elixir", chance = 0.8 } },
	},
	{
		id = "SwampMother", name = "Мать Болот", title = "Хозяйка Топей",
		level = 40, health = 6800, damage = 62, speed = 12, xp = 3600,
		model = "golem", color = Color3.fromRGB(96, 132, 80), scale = 2.3,
		arenaRadius = 100, respawn = 180,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Summon" } },
			{ at = 0.55, abilities = { "Slam", "PoisonNova", "Summon" } },
			{ at = 0.25, abilities = { "PoisonNova", "Volley", "Summon" }, enrage = 0.3 },
		},
		loot = { { item = "W_AshCleaver", chance = 0.5 }, { item = "A_AshPlate", chance = 0.55 },
		         { item = "C_Elixir", chance = 1, min = 1, max = 2 }, { item = "M_BoneDust", chance = 1, min = 3, max = 6 } },
	},
	{
		id = "CryptWraith", name = "Склепный Призрак", title = "Первый мертвец Костяных Полей",
		level = 45, health = 7600, damage = 70, speed = 14, xp = 4200,
		model = "floating", color = Color3.fromRGB(180, 170, 220), scale = 2.0, glow = true,
		arenaRadius = 62, respawn = 200,
		phases = {
			{ at = 1.0, abilities = { "Volley", "Summon" } },
			{ at = 0.6, abilities = { "Volley", "Slam", "Meteor" } },
			{ at = 0.3, abilities = { "Meteor", "FrostNova", "Summon" }, enrage = 0.4 },
		},
		loot = { { item = "W_BoneScythe", chance = 0.7 }, { item = "A_BoneMail", chance = 0.6 },
		         { item = "T_BloodCharm", chance = 0.4 }, { item = "M_BoneDust", chance = 1, min = 5, max = 9 } },
	},
	{
		id = "Ashlord", name = "Пепельный Владыка", title = "Повелитель Пустошей",
		level = 50, health = 9500, damage = 82, speed = 13, xp = 6200,
		model = "humanoid", color = Color3.fromRGB(180, 60, 30), scale = 2.2, glow = true,
		arenaRadius = 87, respawn = 220,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley" } },
			{ at = 0.65, abilities = { "Slam", "Meteor", "Summon" } },
			{ at = 0.35, abilities = { "Meteor", "FrostNova", "Volley", "Summon" }, enrage = 0.5 },
		},
		loot = { { item = "W_AshCleaver", chance = 0.8 }, { item = "A_AshPlate", chance = 0.75 },
		         { item = "C_Elixir", chance = 1, min = 2, max = 3 }, { item = "M_AshEssence", chance = 1, min = 5, max = 10 } },
	},
	{
		id = "NamelessKing", name = "Безымянный Король", title = "Тот, Кого Забыли",
		level = 60, health = 16000, damage = 110, speed = 14, xp = 12000,
		model = "humanoid", color = Color3.fromRGB(90, 60, 140), scale = 2.4, glow = true,
		arenaRadius = 105, respawn = 300,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley", "Summon" } },
			{ at = 0.7, abilities = { "Slam", "Meteor", "Summon" } },
			{ at = 0.4, abilities = { "Meteor", "FrostNova", "Volley", "Summon" }, enrage = 0.4 },
			{ at = 0.15, abilities = { "Meteor", "FrostNova", "Volley", "Summon" }, enrage = 0.7 },
		},
		loot = { { item = "W_VoidEdge", chance = 0.5 }, { item = "A_VoidShroud", chance = 0.5 },
		         { item = "T_BloodCharm", chance = 0.8 }, { item = "M_VoidShard", chance = 1, min = 3, max = 6 } },
	},
	{
		id = "MarrowTyrant", name = "Костяной Тиран", title = "Хозяин Оссуарии",
		level = 42, health = 7200, damage = 66, speed = 13, xp = 3900,
		model = "golem", color = Color3.fromRGB(206, 196, 160), scale = 2.2, glow = true,
		arenaRadius = 58, respawn = 200,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Summon" } },
			{ at = 0.6, abilities = { "Slam", "Volley", "Summon" } },
			{ at = 0.3, abilities = { "Volley", "Meteor", "Summon" }, enrage = 0.4 },
		},
		loot = { { item = "W_BoneScythe", chance = 0.6 }, { item = "A_BoneMail", chance = 0.55 },
		         { item = "M_BoneDust", chance = 1, min = 6, max = 10 } },
	},
	{
		id = "StoneWarden", name = "Каменный Страж", title = "Тюремщик Забытых Шахт",
		level = 44, health = 8600, damage = 72, speed = 10, xp = 4400,
		model = "golem", color = Color3.fromRGB(120, 118, 110), scale = 2.8, glow = true,
		arenaRadius = 52, respawn = 210,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley" } },
			{ at = 0.55, abilities = { "Slam", "Meteor" } },
			{ at = 0.25, abilities = { "Meteor", "Slam", "Summon" }, enrage = 0.5 },
		},
		loot = { { item = "W_AshCleaver", chance = 0.5 }, { item = "A_Chain", chance = 0.6 },
		         { item = "M_Ore", chance = 1, min = 6, max = 12 }, { item = "M_EmberStone", chance = 0.5 } },
	},
	{
		id = "BogHydra", name = "Болотная Гидра", title = "Утроба Затонувшего Храма",
		level = 46, health = 9800, damage = 78, speed = 12, xp = 5100,
		model = "beast", color = Color3.fromRGB(86, 128, 72), scale = 2.5, glow = true,
		arenaRadius = 64, respawn = 220,
		phases = {
			{ at = 1.0, abilities = { "Slam", "PoisonNova" } },
			{ at = 0.6, abilities = { "PoisonNova", "Volley", "Summon" } },
			{ at = 0.3, abilities = { "PoisonNova", "Meteor", "Summon" }, enrage = 0.45 },
		},
		loot = { { item = "A_AshPlate", chance = 0.55 }, { item = "T_BloodCharm", chance = 0.45 },
		         { item = "M_BoneDust", chance = 1, min = 5, max = 9 } },
	},
	{
		id = "VolcanoForge", name = "Владыка Кузни", title = "Кузнец в Жерле",
		level = 52, health = 11500, damage = 88, speed = 12, xp = 6600,
		model = "humanoid", color = Color3.fromRGB(232, 96, 32), scale = 2.3, glow = true,
		arenaRadius = 66, respawn = 230,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Meteor" } },
			{ at = 0.6, abilities = { "Slam", "Meteor", "Volley" } },
			{ at = 0.3, abilities = { "Meteor", "Meteor", "Summon" }, enrage = 0.55 },
		},
		loot = { { item = "W_AshCleaver", chance = 0.7 }, { item = "A_AshPlate", chance = 0.7 },
		         { item = "M_EmberStone", chance = 1, min = 4, max = 8 } },
	},
	{
		id = "PirateAdmiral", name = "Адмирал-Мертвец", title = "Капитан Затонувшего Фрегата",
		level = 48, health = 9200, damage = 80, speed = 15, xp = 5800,
		model = "humanoid", color = Color3.fromRGB(64, 92, 118), scale = 2.1, glow = true,
		arenaRadius = 60, respawn = 220,
		phases = {
			{ at = 1.0, abilities = { "Slam", "Volley" } },
			{ at = 0.6, abilities = { "Volley", "Slam", "Summon" } },
			{ at = 0.25, abilities = { "Volley", "Meteor", "Summon" }, enrage = 0.5 },
		},
		loot = { { item = "W_Sabre", chance = 0.6 }, { item = "A_VoidShroud", chance = 0.3 },
		         { item = "M_Coral", chance = 1, min = 4, max = 8 } },
	},
	{
		id = "WindArchon", name = "Ветряной Архипастырь", title = "Хозяин Пика Ветров",
		level = 56, health = 13200, damage = 96, speed = 16, xp = 7600,
		model = "floating", color = Color3.fromRGB(198, 226, 240), scale = 2.2, glow = true,
		arenaRadius = 62, respawn = 240,
		phases = {
			{ at = 1.0, abilities = { "Volley", "Slam" } },
			{ at = 0.65, abilities = { "Volley", "FrostNova", "Summon" } },
			{ at = 0.3, abilities = { "FrostNova", "Meteor", "Volley" }, enrage = 0.5 },
		},
		loot = { { item = "W_FrostBlade", chance = 0.5 }, { item = "T_SwiftCharm", chance = 0.6 },
		         { item = "M_IceShard", chance = 1, min = 6, max = 10 } },
	},
	{
		id = "CoralQueen", name = "Коралловая Королева", title = "Мать Отмелей",
		level = 38, health = 6400, damage = 60, speed = 12, xp = 3400,
		model = "floating", color = Color3.fromRGB(236, 150, 178), scale = 2.0, glow = true,
		arenaRadius = 54, respawn = 190,
		phases = {
			{ at = 1.0, abilities = { "Volley", "Summon" } },
			{ at = 0.55, abilities = { "Volley", "FrostNova", "Summon" } },
			{ at = 0.25, abilities = { "FrostNova", "Slam", "Summon" }, enrage = 0.4 },
		},
		loot = { { item = "T_FocusCharm", chance = 0.5 }, { item = "A_FrostPlate", chance = 0.4 },
		         { item = "M_Coral", chance = 1, min = 5, max = 9 } },
	},
	{
		id = "GlacierWyrm", name = "Ледяной Змей", title = "Древний Холод",
		level = 58, health = 15000, damage = 104, speed = 15, xp = 9000,
		model = "beast", color = Color3.fromRGB(176, 216, 246), scale = 2.7, glow = true,
		arenaRadius = 70, respawn = 260,
		phases = {
			{ at = 1.0, abilities = { "Slam", "FrostNova" } },
			{ at = 0.7, abilities = { "FrostNova", "Volley", "Summon" } },
			{ at = 0.4, abilities = { "FrostNova", "Meteor", "Slam" } },
			{ at = 0.15, abilities = { "Meteor", "FrostNova", "Volley", "Summon" }, enrage = 0.6 },
		},
		loot = { { item = "W_FrostBlade", chance = 0.75 }, { item = "A_FrostPlate", chance = 0.7 },
		         { item = "T_FocusCharm", chance = 0.5 }, { item = "M_IceShard", chance = 1, min = 8, max = 14 } },
	},
}

-- «Печати призыва»: босса можно вызвать в его зоне, даже если арена пуста
GameData.BossSummons = {
	{ id = "FrostWraith",  seal = "P_FrostWraith",  mats = { { item = "M_IceShard", count = 4 } } },
	{ id = "FrostColossus", seal = "P_FrostColossus", mats = { { item = "M_IceShard", count = 6 }, { item = "M_Ore", count = 4 } } },
	{ id = "SwampMother",  seal = "P_SwampMother",  mats = { { item = "M_BoneDust", count = 5 }, { item = "M_Pelt", count = 3 } } },
	{ id = "CryptWraith",  seal = "P_CryptWraith",  mats = { { item = "M_BoneDust", count = 6 }, { item = "M_AshEssence", count = 3 } } },
	{ id = "Ashlord",      seal = "P_Ashlord",      mats = { { item = "M_AshEssence", count = 6 }, { item = "M_EmberStone", count = 4 } } },
	{ id = "NamelessKing", seal = "P_NamelessKing", mats = { { item = "M_VoidShard", count = 5 }, { item = "M_BoneDust", count = 8 } } },
	{ id = "MarrowTyrant",  seal = "P_MarrowTyrant",  mats = { { item = "M_BoneDust", count = 8 }, { item = "M_VoidShard", count = 2 } } },
	{ id = "StoneWarden",   seal = "P_StoneWarden",   mats = { { item = "M_Ore", count = 8 }, { item = "M_EmberStone", count = 3 } } },
	{ id = "BogHydra",      seal = "P_BogHydra",      mats = { { item = "M_BoneDust", count = 6 }, { item = "M_Pelt", count = 5 } } },
	{ id = "VolcanoForge",  seal = "P_VolcanoForge",  mats = { { item = "M_EmberStone", count = 6 }, { item = "M_AshEssence", count = 5 } } },
	{ id = "PirateAdmiral", seal = "P_PirateAdmiral", mats = { { item = "M_Coral", count = 6 }, { item = "M_Ore", count = 4 } } },
	{ id = "WindArchon",    seal = "P_WindArchon",    mats = { { item = "M_IceShard", count = 7 }, { item = "M_Ore", count = 5 } } },
	{ id = "CoralQueen",    seal = "P_CoralQueen",    mats = { { item = "M_Coral", count = 8 }, { item = "C_ManaPotion", count = 3 } } },
	{ id = "GlacierWyrm",   seal = "P_GlacierWyrm",   mats = { { item = "M_IceShard", count = 10 }, { item = "M_VoidShard", count = 4 } } },
}

GameData.BossById = {}
for _, b in ipairs(GameData.Bosses) do
	GameData.BossById[b.id] = b
end

-- ============================================================================
-- ЛАВКА И КУЗНЕЦ (ассортимент по уровням)
-- ============================================================================
GameData.ShopStock = {
	"W_ShortSword", "W_Hatchet", "W_Sabre", "W_FrostBlade", "W_AshCleaver",
	"A_Leather", "A_Chain", "A_FrostPlate", "A_AshPlate",
	"T_EmberCharm", "T_SwiftCharm", "T_FocusCharm",
	"C_HealthPotion", "C_ManaPotion", "C_Elixir", "C_Bread",
}

-- что скупает торговец (материалы)
GameData.SellableTypes = { material = 1.0, consumable = 0.4, weapon = 0.35, armor = 0.35, trinket = 0.4 }

return GameData
"""

SHARED["Net"] = """-- Emberfall | Net — имена Remote-объектов (сервер и клиент читают отсюда).
local Net = {}

Net.FolderName = "Remotes"

-- Client -> Server
Net.Req = {
	UseSpell = "Req_UseSpell",       -- (spellId)
	Melee = "Req_Melee",             -- ()
	Equip = "Req_Equip",             -- (itemUid)
	Unequip = "Req_Unequip",         -- (slotType)
	UseItem = "Req_UseItem",         -- (itemUid)
	SpendStat = "Req_SpendStat",     -- (statId)
	LearnSpell = "Req_LearnSpell",   -- (spellId)
	ChooseElement = "Req_ChooseElement", -- (elementId)
	ShopBuy = "Req_ShopBuy",         -- (itemId)
	ShopSell = "Req_ShopSell",       -- (itemUid)
	QuestAccept = "Req_QuestAccept", -- (questId)
	QuestClaim = "Req_QuestClaim",   -- (questId)
	QuestAbandon = "Req_QuestAbandon", -- (questId)
	Dialog = "Req_Dialog",           -- (npcMarkerName)
	Respawn = "Req_Respawn",         -- ()
	Ping = "Req_Ping",               -- (clientTime)
	Interact = "Req_Interact",       -- (targetInstance)
	Heal = "Req_Heal",               -- (): лечение у лекаря
	BossSummon = "Req_BossSummon",   -- (bossId): крафт «Печати призыва»
}

-- Server -> Client
Net.Rep = {
	Snapshot = "Rep_Snapshot",       -- полное состояние игрока (при входе/смерти/уровне)
	Vitals = "Rep_Vitals",           -- hp/mana/stamina/xp/level/coins
	Inventory = "Rep_Inventory",     -- предметы + экипировка
	Spells = "Rep_Spells",           -- известные заклинания + выбранный хотбар
	Stats = "Rep_Stats",             -- очки характеристик
	Quests = "Rep_Quests",           -- журнал квестов
	Notify = "Rep_Notify",           -- всплывающие сообщения
	CastFail = "Rep_CastFail",       -- почему не скастовалось
	ZoneChanged = "Rep_ZoneChanged", -- вошёл в новую зону
	DialogOpen = "Rep_Dialog",       -- данные окна диалога NPC
	ShopOpen = "Rep_Shop",           -- ассортимент лавки
	DamageNumber = "Rep_Damage",     -- цифры урона над целями
	BossBar = "Rep_BossBar",         -- полоса здоровья босса
	BossEvent = "Rep_BossEvent",     -- анонсы/фазы/смерть босса
	LevelUp = "Rep_LevelUp",         -- эффект повышения уровня
	CastFx = "Rep_CastFx",           -- визуал каста (лучи, вспышки)
	ElementPick = "Rep_ElementPick", -- предложение выбрать стихию
	CombatState = "Rep_Combat",      -- в бою / вне боя
}

function Net.Get(req, folder)
	return folder:FindFirstChild(req)
end

return Net
"""

SHARED["Util"] = """-- Emberfall | Util — мелкие помощники, общие для сервера и клиента.

local Util = {}

function Util.round(n, digits)
	digits = digits or 0
	local m = 10 ^ digits
	return math.floor(n * m + 0.5) / m
end

function Util.clamp(v, lo, hi)
	if v < lo then return lo end
	if v > hi then return hi end
	return v
end

function Util.lerp(a, b, t)
	return a + (b - a) * t
end

function Util.pick(rng, list)
	if #list == 0 then return nil end
	return list[rng:NextInteger(1, #list)]
end

function Util.weighted(rng, entries, key)
	-- entries: { {weight=3, ...}, ... } или {[id]=weight}
	key = key or "weight"
	local total = 0
	for _, e in ipairs(entries) do
		total = total + (e[key] or 1)
	end
	if total <= 0 then return entries[1] end
	local roll = rng:NextNumber() * total
	local acc = 0
	for _, e in ipairs(entries) do
		acc = acc + (e[key] or 1)
		if roll <= acc then return e end
	end
	return entries[#entries]
end

-- Форматирование чисел с разделителями тысяч: 12345 -> "12 345"
function Util.fmtNum(n)
	local s = tostring(math.floor(n + 0.5))
	local out = s:reverse():gsub("(%d%d%d)", "%1 "):reverse()
	return (out:gsub("^%s+", ""))
end

function Util.fmtTime(sec)
	sec = math.max(0, math.floor(sec))
	local m = math.floor(sec / 60)
	local s = sec % 60
	if m <= 0 then return s .. "с" end
	return m .. ":" .. string.format("%02d", s)
end

function Util.inBox(pos, center, halfSize)
	return math.abs(pos.X - center.X) <= halfSize.X
		and math.abs(pos.Y - center.Y) <= halfSize.Y
		and math.abs(pos.Z - center.Z) <= halfSize.Z
end

function Util.horizontalDist(a, b)
	return math.sqrt((a.X - b.X) ^ 2 + (a.Z - b.Z) ^ 2)
end

-- Сортировка списка игроков по близости к точке
function Util.sortedByDistance(list, pos)
	local copy = {}
	for i, v in ipairs(list) do copy[i] = v end
	table.sort(copy, function(a, b)
		return (a - pos).Magnitude < (b - pos).Magnitude
	end)
	return copy
end

return Util
"""

SHARED["Quests"] = """-- Emberfall | Quests — цепочки заданий.
-- objective: kill / boss / collect / visit / level
local Quests = {}

Quests.List = {
	-- ========================= ПЕПЕЛЬНАЯ ПРИСТАНЬ (хаб) =====================
	{
		id = "Q_FirstSteps", name = "Первые шаги", giver = "QuestKeeper", minLevel = 1,
		desc = "Хранитель знаний хочет убедиться, что ты выживешь за стенами. Убей 5 тварей в любой зоне.",
		objectives = { { type = "killZone", target = "any", count = 5, text = "Убить тварей" } },
		rewards = { xp = 180, coins = 60, items = { { id = "C_HealthPotion", count = 3 } } },
	},
	{
		id = "Q_WelcomeGift", name = "Дар пристани", giver = "Merchant", minLevel = 1,
		desc = "Торговец ищет шкуры для пошива. Принеси 4 шкуры из Глумвуда.",
		objectives = { { type = "collect", target = "M_Pelt", count = 4, text = "Собрать шкур" } },
		rewards = { xp = 220, coins = 120, items = { { id = "W_ShortSword", count = 1 } } },
	},
	{
		id = "Q_FirstSpell", name = "Первый ритуал", giver = "QuestKeeper", minLevel = 2,
		prereq = { "Q_FirstSteps" },
		desc = "Пора выбрать стихию. Подойди к алтарю у площади и коснись его.",
		objectives = { { type = "flag", target = "choseElement", count = 1, text = "Выбрать стихию" } },
		rewards = { xp = 260, coins = 80, items = { { id = "C_ManaPotion", count = 3 } } },
	},
	{
		id = "Q_BlacksmithOre", name = "Кузнецу нужна руда", giver = "Blacksmith", minLevel = 4,
		desc = "Кузнец Гарм просит 6 кусков руды. Руду роняют гоблины и разбойники.",
		objectives = { { type = "collect", target = "M_Ore", count = 6, text = "Собрать руды" } },
		rewards = { xp = 420, coins = 200, items = { { id = "A_Chain", count = 1 } } },
	},
	{
		id = "Q_GateGuard", name = "Стража ворот", giver = "GateCaptain", minLevel = 6,
		desc = "Капрал просит проредить разбойников у западного тракта: убей 6 разбойников.",
		objectives = { { type = "kill", target = "Bandit", count = 6, text = "Убить разбойников" } },
		rewards = { xp = 650, coins = 260, items = { { id = "W_Sabre", count = 1 } } },
	},

	-- ============================== ГЛУМВУД ==================================
	{
		id = "Q_Wolves", name = "Волчья напасть", giver = "Herbalist", minLevel = 8,
		desc = "Травница Тенегрива: теневые волки рвут скот. Убей 8 теневых волков.",
		objectives = { { type = "kill", target = "ShadowWolf", count = 8, text = "Убить теневых волков" } },
		rewards = { xp = 800, coins = 300, items = { { id = "C_HealthPotion", count = 5 }, { id = "T_EmberCharm", count = 1 } } },
	},
	{
		id = "Q_ForestHorror", name = "Ужас чащи", giver = "Hunter", minLevel = 14,
		desc = "Охотник видел нечто огромное между деревьями. Убей Лесного ужаса.",
		objectives = { { type = "kill", target = "ForestHorror", count = 1, text = "Убить Лесного ужаса" } },
		rewards = { xp = 1200, coins = 450, items = { { id = "T_SwiftCharm", count = 1 } } },
	},
	{
		id = "Q_GloomTrial", name = "Испытание Глумвуда", giver = "QuestKeeper", minLevel = 12,
		prereq = { "Q_FirstSpell" },
		desc = "Испытание леса: убей 10 любых тварей Глумвуда и вернись.",
		objectives = { { type = "killZone", target = "Gloomwood", count = 10, text = "Убить в Глумвуде" } },
		rewards = { xp = 1400, coins = 500, items = { { id = "A_Chain", count = 1 } } },
	},

	-- ============================ МОРОЗНЫЕ ПИКИ ==============================
	{
		id = "Q_FrozenPass", name = "Мёрзлый перевал", giver = "Farmer", minLevel = 20,
		desc = "Фермер с хутора слышал вой с перевала. Убей 8 морозных волков.",
		objectives = { { type = "kill", target = "FrostWolf", count = 8, text = "Убить морозных волков" } },
		rewards = { xp = 2100, coins = 700, items = { { id = "C_ManaPotion", count = 5 } } },
	},
	{
		id = "Q_BossFrost", name = "Страж гробницы", giver = "QuestKeeper", minLevel = 26,
		prereq = { "Q_FrozenPass" },
		desc = "Ледяной Призрак стережёт древнюю гробницу. Уничтожь его.",
		objectives = { { type = "boss", target = "FrostWraith", count = 1, text = "Победить Ледяного Призрака" } },
		rewards = { xp = 4000, coins = 1500, items = { { id = "W_FrostBlade", count = 1 }, { id = "C_Elixir", count = 2 } }, statPoints = 1 },
	},
	{
		id = "Q_Colossus", name = "Колосс пробудился", giver = "QuestKeeper", minLevel = 32,
		prereq = { "Q_BossFrost" },
		desc = "На арене Морозных Пиков стоит Ледяной Колосс. Сокруши титана.",
		objectives = { { type = "boss", target = "FrostColossus", count = 1, text = "Победить Ледяного Колосса" } },
		rewards = { xp = 7000, coins = 2600, items = { { id = "A_FrostPlate", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ЗАТОНУВШИЙ БЕРЕГ ===========================
	{
		id = "Q_DrownedFleet", name = "Затонувший флот", giver = "Portmaster", minLevel = 16,
		desc = "Портмейстер: утопленники лезут на причалы. Убей 10 утопленников.",
		objectives = { { type = "kill", target = "Drowned", count = 10, text = "Убить утопленников" } },
		rewards = { xp = 1600, coins = 600, items = { { id = "C_HealthPotion", count = 6 } } },
	},
	{
		id = "Q_PirateGold", name = "Проклятое золото", giver = "Fishmonger", minLevel = 18,
		desc = "Рыботорговец нашёл монету с проклятием. Убей 6 пиратов-мертвецов.",
		objectives = { { type = "kill", target = "PirateDead", count = 6, text = "Убить пиратов-мертвецов" } },
		rewards = { xp = 1800, coins = 800, items = { { id = "T_SwiftCharm", count = 1 } } },
	},

	-- ============================ ТОПИ МИРЕФЕН ===============================
	{
		id = "Q_MireHerbs", name = "Болотные травы", giver = "Herbalist", minLevel = 24,
		desc = "Травнице нужны костяная пыль и эссенции. Принеси 5 костяной пыли.",
		objectives = { { type = "collect", target = "M_BoneDust", count = 5, text = "Собрать костяной пыли" } },
		rewards = { xp = 2600, coins = 900, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_SwampMother", name = "Мать Болот", giver = "QuestKeeper", minLevel = 34,
		desc = "Остров в Топях Мирефен — логово Матери Болот. Убей её.",
		objectives = { { type = "boss", target = "SwampMother", count = 1, text = "Победить Мать Болот" } },
		rewards = { xp = 9000, coins = 3200, items = { { id = "T_FocusCharm", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ПЕПЕЛЬНЫЕ ПУСТОШИ ==========================
	{
		id = "Q_AshCull", name = "Пепельная чистка", giver = "GateCaptain", minLevel = 36,
		desc = "Пустоши кишат пепельными псами. Убей 12.",
		objectives = { { type = "kill", target = "AshHound", count = 12, text = "Убить пепельных псов" } },
		rewards = { xp = 5200, coins = 1800, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_Ashlord", name = "Владыка Пепла", giver = "QuestKeeper", minLevel = 42,
		prereq = { "Q_Colossus" },
		desc = "Пепельный Владыка ждёт на арене Пустошей. Положи конец его власти.",
		objectives = { { type = "boss", target = "Ashlord", count = 1, text = "Победить Пепельного Владыку" } },
		rewards = { xp = 14000, coins = 5000, items = { { id = "W_AshCleaver", count = 1 }, { id = "A_AshPlate", count = 1 } }, statPoints = 1 },
	},

	-- ============================ КОСТЯНЫЕ ПОЛЯ ==============================
	{
		id = "Q_BoneTide", name = "Костяной прилив", giver = "Healer", minLevel = 30,
		desc = "Лекарь пристани: нежить поднимается волнами. Убей 12 скелетов.",
		objectives = { { type = "kill", target = "Skeleton", count = 12, text = "Убить скелетов" } },
		rewards = { xp = 4800, coins = 1600, items = { { id = "C_HealthPotion", count = 8 } } },
	},
	{
		id = "Q_Cult", name = "Тайный культ", giver = "GateCaptain", minLevel = 38,
		desc = "Культисты собираются у кладбища. Убей 8 культистов и их вожаков.",
		objectives = { { type = "kill", target = "Cultist", count = 8, text = "Убить культистов" } },
		rewards = { xp = 6000, coins = 2200, items = { { id = "T_BloodCharm", count = 1 } } },
	},
	{
		id = "Q_CryptWraith", name = "Склепный призрак", giver = "QuestKeeper", minLevel = 44,
		prereq = { "Q_BoneTide" },
		desc = "В крипте Костяных Полей заперт Склепный Призрак. Открой склеп и уничтожь его.",
		objectives = { { type = "boss", target = "CryptWraith", count = 1, text = "Победить Склепного Призрака" } },
		rewards = { xp = 16000, coins = 5600, items = { { id = "W_BoneScythe", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ПРЕДГОРЬЯ ==================================
	{
		id = "Q_Trolls", name = "Тролльи тропы", giver = "Highlander", minLevel = 27,
		desc = "Горец Бран: каменные тролли раздавили торговый караван. Убей 5 троллей.",
		objectives = { { type = "kill", target = "RockTroll", count = 5, text = "Убить каменных троллей" } },
		rewards = { xp = 3600, coins = 1200, items = { { id = "A_AshPlate", count = 1 } } },
	},
	{
		id = "Q_MineShadows", name = "Тени шахты", giver = "Miner", minLevel = 25,
		desc = "Шахтёр Гром: из забоя лезут гули. Убей 10 шахтных гулей.",
		objectives = { { type = "kill", target = "MinerGhoul", count = 10, text = "Убить шахтных гулей" } },
		rewards = { xp = 3200, coins = 1100, items = { { id = "M_Ore", count = 8 } } },
	},
	{
		id = "Q_Highway", name = "Горный тракт", giver = "Highlander", minLevel = 30,
		desc = "Горные разбойники грабят предгорья. Убей 8.",
		objectives = { { type = "kill", target = "Highwayman", count = 8, text = "Убить горных разбойников" } },
		rewards = { xp = 4200, coins = 1500, items = { { id = "C_Elixir", count = 2 } } },
	},

	-- ============================ АРХИПЕЛАГ ==================================
	{
		id = "Q_PiratesBane", name = "Гибель пиратов", giver = "Pirate", minLevel = 32,
		desc = "Кровавый Джо хочет покоя: убей 8 пиратов-капитанов.",
		objectives = { { type = "kill", target = "PirateLord", count = 8, text = "Убить пиратских капитанов" } },
		rewards = { xp = 6000, coins = 2200, items = { { id = "T_BloodCharm", count = 1 } } },
	},
	{
		id = "Q_SeaWraiths", name = "Призраки архипелага", giver = "Pirate", minLevel = 30,
		desc = "Морские призраки не дают рыбачить. Убей 10.",
		objectives = { { type = "kill", target = "SeaWraith", count = 10, text = "Убить морских призраков" } },
		rewards = { xp = 5200, coins = 1900, items = { { id = "C_ManaPotion", count = 6 } } },
	},

	-- ============================ ЮЖНЫЕ ОСТРОВА ==============================
	{
		id = "Q_Coral", name = "Коралловый риф", giver = "Fishmonger", minLevel = 22,
		desc = "Рыбак просит кораллы: принеси 4.",
		objectives = { { type = "collect", target = "M_Coral", count = 4, text = "Собрать кораллы" } },
		rewards = { xp = 2600, coins = 900, items = { { id = "T_SwiftCharm", count = 1 } } },
	},
	{
		id = "Q_BeachRaiders", name = "Налётчики", giver = "Farmer", minLevel = 24,
		desc = "Береговые налётчики жгут дома. Убей 8.",
		objectives = { { type = "kill", target = "BeachRaider", count = 8, text = "Убить налётчиков" } },
		rewards = { xp = 3000, coins = 1000, items = { { id = "C_HealthPotion", count = 6 } } },
	},
	{
		id = "Q_FrostWind", name = "Ветроград", giver = "Villager", minLevel = 28,
		desc = "Житель Ветрограда просит зачистить морозных волков у стен.",
		objectives = { { type = "kill", target = "FrostWolf", count = 12, text = "Убить морозных волков" } },
		rewards = { xp = 4600, coins = 1600, items = { { id = "A_FrostPlate", count = 1 } } },
	},

	-- ============================ ПОЛАЯ БЕЗДНА ===============================
	{
		id = "Q_VoidShards", name = "Осколки Бездны", giver = "QuestKeeper", minLevel = 48,
		desc = "Бездна смотрит в ответ. Принеси 3 осколка Бездны из каньона.",
		objectives = { { type = "collect", target = "M_VoidShard", count = 3, text = "Собрать осколки Бездны" } },
		rewards = { xp = 18000, coins = 6000, items = { { id = "C_Elixir", count = 3 } } },
	},
	{
		id = "Q_NamelessKing", name = "Безымянный Король", giver = "QuestKeeper", minLevel = 52,
		prereq = { "Q_Ashlord" },
		desc = "Финальная цель: трон в глубине каньона. Победи Безымянного Короля.",
		objectives = { { type = "boss", target = "NamelessKing", count = 1, text = "Победить Безымянного Короля" } },
		rewards = { xp = 40000, coins = 15000, items = { { id = "W_VoidEdge", count = 1 }, { id = "A_VoidShroud", count = 1 } }, statPoints = 3 },
	},

	-- ==================== v11: НОВЫЕ ЗЕМЛИ И ПОДЗЕМЕЛЬЯ ====================
	{
		id = "Q_GreatGrove", name = "Великая Роща", giver = "Woodcutter", minLevel = 10,
		desc = "Лесоруб Хват просит очистить рощу от падали, которую подняли пещерные твари. Убей 8 тварей Глумвуда.",
		objectives = { { type = "killZone", target = "Gloomwood", count = 8, text = "Убить в Глумвуде" } },
		rewards = { xp = 1500, coins = 420, items = { { id = "M_Ore", count = 4 } } },
	},
	{
		id = "Q_DuplinoCave", name = "Пещеры Дупла", giver = "Woodcutter", minLevel = 12,
		prereq = { "Q_GreatGrove" },
		desc = "Спустись в Пещеры Дупла под пилорамой и вычисти первые залы. Убей 6 гоблинов.",
		objectives = { { type = "kill", target = "GloomGoblin", count = 6, text = "Убить гоблинов" } },
		rewards = { xp = 1900, coins = 520, items = { { id = "A_Chain", count = 1 }, { id = "C_HealthPotion", count = 3 } } },
	},
	{
		id = "Q_CanyonShade", name = "Тени Красного каньона", giver = "RiceFarmer", minLevel = 28,
		desc = "Крестьянин Тэру: с каньона приходят тени. Убей 10 любых тварей на южном вельде.",
		objectives = { { type = "killZone", target = "Bonefields", count = 10, text = "Убить на вельде" } },
		rewards = { xp = 4200, coins = 900, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_MarrowTyrant", name = "Оссуария", giver = "Prospector", minLevel = 34,
		desc = "Старатель Гриб: в Шахте Красный Камень сидит Костяной Тиран. Очисти её.",
		objectives = { { type = "boss", target = "MarrowTyrant", count = 1, text = "Победить Костяного Тирана" } },
		rewards = { xp = 9000, coins = 2200, items = { { id = "W_BoneScythe", count = 1 } } },
	},
	{
		id = "Q_ArcanumSteps", name = "Ступени Арканума", giver = "Archmage", minLevel = 22,
		desc = "Селена Звёздная: чтобы учиться дальше, докажи силу. Убей 12 тварей на восточных землях.",
		objectives = { { type = "killZone", target = "SunkenCoast", count = 12, text = "Убить на востоке" } },
		rewards = { xp = 3400, coins = 800, items = { { id = "C_ManaPotion", count = 4 } } },
	},
	{
		id = "Q_TowerClimb", name = "На вершину башни", giver = "Archmage", minLevel = 26,
		prereq = { "Q_ArcanumSteps" },
		desc = "Поднимись по летающим платформам к вершине башни Арканума и забери гримуар.",
		objectives = { { type = "collect", target = "T_FocusCharm", count = 1, text = "Найти фокус-амулет" } },
		rewards = { xp = 4600, coins = 1100, items = { { id = "T_FocusCharm", count = 1 } }, statPoints = 1 },
	},
	{
		id = "Q_OldMine", name = "Забытые Шахты", giver = "MineOverseer", minLevel = 36,
		desc = "Горный мастер: шахты закрыли сорок лет назад, а Страж всё ходит. Убей Каменного Стража.",
		objectives = { { type = "boss", target = "StoneWarden", count = 1, text = "Победить Каменного Стража" } },
		rewards = { xp = 10000, coins = 2600, items = { { id = "A_Chain", count = 1 }, { id = "M_Ore", count = 8 } } },
	},
	{
		id = "Q_WindPeak", name = "Пик Ветров", giver = "MineOverseer", minLevel = 42,
		prereq = { "Q_OldMine" },
		desc = "Поднимись на Пик Ветров и выстои против Архипастыря. Это проверка на выносливость.",
		objectives = { { type = "boss", target = "WindArchon", count = 1, text = "Победить Архипастыря" } },
		rewards = { xp = 14000, coins = 3200, items = { { id = "T_SwiftCharm", count = 1 } }, statPoints = 1 },
	},
	{
		id = "Q_DrownedShip", name = "Затонувший фрегат", giver = "PirateCaptain", minLevel = 30,
		desc = "Рыжая Мора: мой фрегат лежит у Гавани, а адмирал всё командует. Разберись с ним.",
		objectives = { { type = "boss", target = "PirateAdmiral", count = 1, text = "Победить Адмирала-Мертвеца" } },
		rewards = { xp = 7200, coins = 1900, items = { { id = "W_Sabre", count = 1 } } },
	},
	{
		id = "Q_CoralChildren", name = "Дети Пальмового Берега", giver = "Islander", minLevel = 26,
		desc = "Каи: Коралловая Королева забрала наших детей в грот. Освободи их.",
		objectives = { { type = "boss", target = "CoralQueen", count = 1, text = "Победить Коралловую Королеву" } },
		rewards = { xp = 6000, coins = 1500, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_Forge", name = "Кузня в Жерле", giver = "AshenSmith", minLevel = 44,
		desc = "Горн: Владыка Кузни держит вечный огонь. Забери его — и я выкую тебе оружие.",
		objectives = { { type = "boss", target = "VolcanoForge", count = 1, text = "Победить Владыку Кузни" } },
		rewards = { xp = 12000, coins = 3000, items = { { id = "W_AshCleaver", count = 1 }, { id = "M_EmberStone", count = 4 } } },
	},
	{
		id = "Q_RotTemple", name = "Служба в затопленном храме", giver = "BogPriest", minLevel = 38,
		desc = "Отец Мох: Гидра выросла из наших молитв. Прекрати это.",
		objectives = { { type = "boss", target = "BogHydra", count = 1, text = "Победить Болотную Гидру" } },
		rewards = { xp = 9500, coins = 2400, items = { { id = "A_BoneMail", count = 1 } } },
	},
	{
		id = "Q_WyrmLair", name = "Логово Змея", giver = "IceScholar", minLevel = 50,
		desc = "Ивар: Змей спит в леднике. Каждая его чешуйка — зима. Разбуди и победи.",
		objectives = { { type = "boss", target = "GlacierWyrm", count = 1, text = "Победить Ледяного Змея" } },
		rewards = { xp = 22000, coins = 5200, items = { { id = "A_FrostPlate", count = 1 } }, statPoints = 2 },
	},
	{
		id = "Q_Kamnegorsk", name = "Крепость горняков", giver = "MineOverseer", minLevel = 32,
		desc = "Помоги Камнегорску: прореди горных тварей, чтобы караваны шли безопасно.",
		objectives = { { type = "killZone", target = "Highlands", count = 12, text = "Убить в Предгорьях" } },
		rewards = { xp = 5600, coins = 1400, items = { { id = "M_Ore", count = 6 } } },
	},
}

Quests.ById = {}
for _, q in ipairs(Quests.List) do
	Quests.ById[q.id] = q
end

function Quests.forNpc(npcKey)
	local out = {}
	for _, q in ipairs(Quests.List) do
		if q.giver == npcKey then table.insert(out, q) end
	end
	return out
end

return Quests
"""

SHARED["NPCData"] = """-- Emberfall | NPCData — кто стоит на маркерах NPC_* и что говорит.
local NPCData = {}

-- assistant: подсказки новичку
NPCData.List = {
	{
		key = "QuestKeeper", name = "Хранитель Знаний", title = "Элдрин", color = Color3.fromRGB(120, 90, 200),
		lines = {
			"Ты пришёл вовремя. Мир трещит по швам.",
			"Выбери стихию у алтаря на площади — без магии ты просто мясо.",
			"Бери задания: опыт, монеты, снаряжение. Всё пригодится.",
		},
		role = "quests",
	},
	{
		key = "Merchant", name = "Торговец", title = "Бор", color = Color3.fromRGB(200, 160, 70),
		lines = {
			"Покупаю шкуры, руду, всё что блестит.",
			"Зелья не бесплатные, но жизнь дороже.",
		},
		role = "shop",
	},
	{
		key = "Blacksmith", name = "Кузнец", title = "Гарм", color = Color3.fromRGB(150, 120, 100),
		lines = {
			"Сталь — единственное, чему я верю.",
			"Принеси руду — скуём что-нибудь стоящее.",
		},
		role = "shop",
	},
	{
		key = "Healer", name = "Лекарь", title = "Мирра", color = Color3.fromRGB(120, 220, 160),
		lines = {
			"Раны затянутся, шрамы останутся.",
			"Не умирай слишком часто — опыт теряется.",
		},
		role = "heal",
	},
	{
		key = "GateCaptain", name = "Капрал стражи", title = "Дорн", color = Color3.fromRGB(150, 150, 170),
		lines = {
			"За воротами не прогулка, а война.",
			"Держись дорог — в чаще тебя сожрут.",
		},
		role = "quests",
	},
	{
		key = "Herbalist", name = "Травница", title = "Сайра", color = Color3.fromRGB(120, 200, 110),
		lines = {
			"Теневые волки рвут наших овец. Помоги — отблагодарю.",
			"Болотные грибы светятся, но они не добрые.",
		},
		role = "quests",
	},
	{
		key = "Hunter", name = "Охотник", title = "Кайл", color = Color3.fromRGB(140, 110, 80),
		lines = {
			"В чаще что-то ходит. Большое.",
			"Убей его — и я поверю, что ты не просто мальчишка с палкой.",
		},
		role = "quests",
	},
	{
		key = "Farmer", name = "Фермер", title = "Хэм", color = Color3.fromRGB(180, 150, 90),
		lines = {
			"Волки с перевала воют всю ночь.",
			"Хутор держится, но не долго.",
		},
		role = "quests",
	},
	{
		key = "Portmaster", name = "Портмейстер", title = "Сэл", color = Color3.fromRGB(90, 160, 200),
		lines = {
			"Утопленники лезут на причалы каждую ночь.",
			"Море забирает всех. И возвращает не такими.",
		},
		role = "quests",
	},
	{
		key = "Miner", name = "Шахтёр", title = "Гром", color = Color3.fromRGB(160, 140, 110),
		lines = {
			"В шахте что-то завелось. Гули, не иначе.",
			"Руда тут богатая — если выживешь.",
		},
		role = "quests",
	},
	{
		key = "Highlander", name = "Горец", title = "Бран", color = Color3.fromRGB(140, 120, 96),
		lines = {
			"Предгорья — край суровый. Тролли топчут наши тропы.",
			"Возьми заказ, если не боишься камня.",
		},
		role = "quests",
	},
	{
		key = "Pirate", name = "Старый пират", title = "Кровавый Джо", color = Color3.fromRGB(150, 90, 80),
		lines = {
			"Тут был мой корабль. Был.",
			"Морские призраки не дают уплыть.",
		},
		role = "quests",
	},
	{
		key = "Villager", name = "Житель Ветрограда", title = "Эйнар", color = Color3.fromRGB(200, 200, 210),
		lines = {
			"Северные охотники держат оборону, но силы кончаются.",
			"Помоги — и Ветроград запомнит тебя.",
		},
		role = "quests",
	},
	{
		key = "Mogilshik", name = "Могильщик", title = "Сумрачный Том", color = Color3.fromRGB(120, 118, 100),
		lines = {
			"Копаю глубже, чем они встают.",
			"Нежить лезет из земли каждую ночь.",
		},
		role = "quests",
	},
	{
		key = "Fishmonger", name = "Рыботорговец", title = "Нэд", color = Color3.fromRGB(110, 180, 190),
		lines = {
			"Монета была тёплой. Потом стало холодно.",
			"Пираты-мертвецы ходят по берегу. Не ходи туда ночью.",
		},
		role = "quests",
	},
	-- ===== v11: новые города и подземелья =====
	{
		key = "Woodcutter", name = "Лесоруб", title = "Дубовый Хват", color = Color3.fromRGB(150, 116, 80),
		lines = {
			"Дуплино живёт лесом — и умирает вместе с ним.",
			"В Пещерах Дупла что-то грызёт корни. Спустись и проверь.",
			"Пилорама за площадью, там и вход вниз.",
		},
		role = "quests",
	},
	{
		key = "Archmage", name = "Архимаг", title = "Селена Звёздная", color = Color3.fromRGB(150, 140, 230),
		lines = {
			"Арканум стоит на костях семи стихий. Тебе не понять — пока.",
			"Учись у башни: каждая ступень даёт новое заклинание.",
			"Мой ученик ушёл в рисовые террасы и не вернулся.",
		},
		role = "quests",
	},
	{
		key = "RiceFarmer", name = "Крестьянин", title = "Тэру", color = Color3.fromRGB(226, 200, 130),
		lines = {
			"Террасы держат воду, вода держит нас.",
			"По ночам с каньона приходят тени и топчут посевы.",
		},
		role = "quests",
	},
	{
		key = "MineOverseer", name = "Горный мастер", title = "Скала", color = Color3.fromRGB(160, 150, 130),
		lines = {
			"Камнегорск — не город, а крепость над шахтами.",
			"Забытые Шахты закрыли сорок лет назад. Каменный Страж не спит.",
		},
		role = "quests",
	},
	{
		key = "PirateCaptain", name = "Капитан вольных", title = "Рыжая Мора", color = Color3.fromRGB(220, 120, 90),
		lines = {
			"В Свободной Гавани нет королей — только доли.",
			"Мой старый фрегат затонул вместе с адмиралом. Его команда до сих пор ходит по палубе.",
		},
		role = "quests",
	},
	{
		key = "Islander", name = "Островитянин", title = "Каи", color = Color3.fromRGB(200, 226, 190),
		lines = {
			"Пальмовый Берег — последнее тёплое место на карте.",
			"Коралловая Королева забрала наших детей в грот. Верни их.",
		},
		role = "quests",
	},
	{
		key = "AshenSmith", name = "Пепельный кузнец", title = "Горн", color = Color3.fromRGB(210, 110, 60),
		lines = {
			"Кузня в Жерле не остыла ни на день.",
			"Владыка Кузни держит там вечный огонь. Забери его.",
		},
		role = "shop",
	},
	{
		key = "BogPriest", name = "Жрец гнили", title = "Отец Мох", color = Color3.fromRGB(130, 160, 100),
		lines = {
			"Храм затонул, но служба идёт.",
			"Гидра выросла из наших молитв. Это наша вина.",
		},
		role = "quests",
	},
	{
		key = "IceScholar", name = "Ледяной книжник", title = "Ивар", color = Color3.fromRGB(170, 210, 236),
		lines = {
			"Змей спит в леднике дольше, чем существует наш мир.",
			"Каждая его чешуйка — отдельная зима.",
		},
		role = "quests",
	},
	{
		key = "Prospector", name = "Старатель", title = "Гриб", color = Color3.fromRGB(200, 160, 110),
		lines = {
			"Красный камень в каньоне мягче золота, но дороже.",
			"В Шахте Красный Камень сидит Костяной Тиран. Не для слабаков.",
		},
		role = "shop",
	},
}

NPCData.ByKey = {}
for _, n in ipairs(NPCData.List) do
	NPCData.ByKey[n.key] = n
end

return NPCData
"""

SHARED["Dungeons"] = """-- Emberfall | Dungeons — соответствие данжей и их обитателей зонам.
-- Нужно, чтобы мобы в данже подходили по уровню, а не брались из общего списка.
local Dungeons = {}

-- dungeon -> зона (по ней ищем мобов для волн)
Dungeons.OfBoss = {
	FrostWraith      = "Frostpeak",
	FrostColossus    = "Frostpeak",
	SwampMother      = "Mirefen",
	CryptWraith      = "Bonefields",
	Ashlord          = "Ashwaste",
	NamelessKing     = "HollowDeep",
	-- v11: новые подземелья
	MarrowTyrant     = "Bonefields",
	StoneWarden      = "Highlands",
	BogHydra         = "Mirefen",
	VolcanoForge     = "Ashwaste",
	PirateAdmiral    = "Archipelago",
	WindArchon       = "Frostpeak",
	CoralQueen       = "SouthIsles",
	GlacierWyrm      = "Frostpeak",
}

-- Подписи входов в данжи (для указателей и UI)
Dungeons.Titles = {
	FrostWraith   = "Ледяная Гробница",
	FrostColossus = "Арена Ледяного Колосса",
	SwampMother   = "Топь Матери Болот",
	CryptWraith   = "Крипта Костяных Полей",
	Ashlord       = "Арена Пепельного Владыки",
	NamelessKing  = "Трон Безымянного Короля",
	MarrowTyrant  = "Костяная Оссуария",
	StoneWarden   = "Забытые Шахты Предгорий",
	BogHydra      = "Затонувший Храм Гнили",
	VolcanoForge  = "Кузня в Жерле",
	PirateAdmiral = "Затонувший Фрегат",
	WindArchon    = "Пик Ветров",
	CoralQueen    = "Коралловый Грот",
	GlacierWyrm   = "Логово Ледяного Змея",
}

return Dungeons
"""

SERVER = {}
SERVER["PlayerState"] = """-- Emberfall | PlayerState — уровень, статы, инвентарь, экипировка, заклинания.
-- Всё, что нужно хранить про игрока и пересчитывать при изменениях.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local PlayerState = {}

local states = {}
local uidCounter = 0

local function newUid()
	uidCounter = uidCounter + 1
	return "it" .. uidCounter
end

PlayerState.newUid = newUid

local function defaultStats()
	local t = {}
	for _, s in ipairs(Config.Stats) do t[s.id] = 0 end
	return t
end

function PlayerState.new(player)
	local st = {
		player = player,
		userId = player.UserId,

		level = 1,
		xp = 0,
		statPoints = Config.StartingStatPoints,
		stats = defaultStats(),

		element = nil,
		spells = {},          -- [spellId] = true
		hotbar = {},          -- [1..6] = spellId

		coins = 120,
		inventory = {},       -- [uid] = {id=..., count=...}
		equip = {},           -- [slotType] = uid

		quests = {},          -- [questId] = {state="active"|"ready"|"done", counters={}}
		questsDone = {},

		hp = 100,
		mana = 100,
		stamina = Config.StaminaMax,
		cooldowns = {},       -- [key] = os.clock() доступен с
		lastCombat = 0,
		lastMelee = 0,
		lastChest = {},       -- [tag] = os.clock()
		zone = "Emberfall",
		buffs = {},           -- активные баффы { {type=, value=, until=} }
		data = {},            -- произвольные флаги квестов/мира

		stats_cache = {},
	}
	states[player.UserId] = st
	return st
end

function PlayerState.get(player)
	return states[player.UserId]
end

function PlayerState.getByUserId(id)
	return states[id]
end

function PlayerState.all()
	return states
end

function PlayerState.remove(player)
	states[player.UserId] = nil
end

-- ============================================================================
-- Производные величины
-- ============================================================================
local function equippedItem(st, slot)
	local uid = st.equip[slot]
	if not uid then return nil end
	local it = st.inventory[uid]
	if not it then return nil end
	return GameData.ItemById[it.id]
end

function PlayerState.equippedItem(st, slot)
	return equippedItem(st, slot)
end

function PlayerState.activeBuffValue(st, buffType, now)
	local total = 0
	for _, b in ipairs(st.buffs) do
		if b.type == buffType and (b.expires or 0) > now then
			total = total + b.value
		end
	end
	return total
end

function PlayerState.recompute(st, character)
	local now = os.clock()
	local weapon = equippedItem(st, "weapon")
	local armor = equippedItem(st, "armor")
	local trinket = equippedItem(st, "trinket")

	local maxHealth = Config.BaseHealth
		+ (st.level - 1) * Config.HealthPerLevel
		+ st.stats.Vitality * Config.HealthPerPoint
		+ (trinket and trinket.healthBonus or 0)

	local maxMana = Config.BaseMana
		+ (st.level - 1) * Config.ManaPerLevel
		+ st.stats.Insight * Config.ManaPerPoint
		+ (trinket and trinket.manaBonus or 0)

	local powerMult = 1 + st.stats.Power * Config.PowerPerPoint
		+ PlayerState.activeBuffValue(st, "power", now)

	local armorTotal = st.stats.Ward * Config.WardPerPoint
		+ (armor and armor.armor or 0)
		+ PlayerState.activeBuffValue(st, "armor", now)

	local speed = Config.WalkSpeed
		+ st.stats.Agility * Config.SpeedPerPoint
		+ (trinket and trinket.speedBonus or 0)
		+ PlayerState.activeBuffValue(st, "speed", now)

	local cdMult = math.max(0.5, 1 - ((trinket and trinket.cooldownBonus) or 0))
	local lifesteal = (trinket and trinket.lifesteal) or 0

	st.stats_cache = {
		maxHealth = maxHealth,
		maxMana = maxMana,
		powerMult = powerMult,
		armor = armorTotal,
		speed = math.min(speed, 34),
		cdMult = cdMult,
		lifesteal = lifesteal,
		weaponDamage = weapon and weapon.damage or 4,
		weaponSpeed = weapon and weapon.speed or 1.0,
	}

	if character then
		local hum = character:FindFirstChildOfClass("Humanoid")
		if hum then
			local ratio = 1
			if hum.MaxHealth > 0 then
				ratio = hum.Health / hum.MaxHealth
			end
			hum.MaxHealth = maxHealth
			hum.Health = math.clamp(maxHealth * ratio, 1, maxHealth)
			hum.WalkSpeed = st.stats_cache.speed
			hum:SetAttribute("EmberSpeed", st.stats_cache.speed)
		end
	end

	st.hp = math.min(st.hp <= 0 and maxHealth or st.hp, maxHealth)
	st.mana = math.min(st.mana, maxMana)
	return st.stats_cache
end

function PlayerState.cache(st)
	return st.stats_cache
end

-- ============================================================================
-- Опыт и уровни
-- ============================================================================
-- Возвращает список повышений уровня (обычно 0 или 1)
function PlayerState.addXp(st, amount)
	local ups = 0
	local notifyLevels = {}
	st.xp = st.xp + amount
	while st.level < Config.MaxLevel do
		local need = Config.XpForLevel(st.level)
		if st.xp < need then break end
		st.xp = st.xp - need
		st.level = st.level + 1
		st.statPoints = st.statPoints + Config.StatPointsPerLevel
		ups = ups + 1
		table.insert(notifyLevels, st.level)
		if ups > 40 then break end
	end
	if st.level >= Config.MaxLevel then
		st.xp = math.min(st.xp, Config.XpForLevel(Config.MaxLevel - 1))
	end
	return notifyLevels
end

function PlayerState.xpToNext(st)
	if st.level >= Config.MaxLevel then return 0 end
	return Config.XpForLevel(st.level)
end

-- ============================================================================
-- Инвентарь
-- ============================================================================
function PlayerState.addItem(st, itemId, count)
	local def = GameData.ItemById[itemId]
	if not def then return nil, "нет такого предмета" end
	count = count or 1

	-- расходники/материалы складываем в стопку
	if def.type == "consumable" or def.type == "material" then
		for uid, inv in pairs(st.inventory) do
			if inv.id == itemId and (inv.count or 1) < (def.stack or 99) then
				inv.count = (inv.count or 1) + count
				return uid
			end
		end
	end

	local total = 0
	for _ in pairs(st.inventory) do total = total + 1 end
	if total >= Config.InventorySlots then return nil, "рюкзак полон" end

	local uid = newUid()
	st.inventory[uid] = { id = itemId, count = count }
	return uid
end

function PlayerState.removeItem(st, uid, count)
	local inv = st.inventory[uid]
	if not inv then return false, "нет предмета" end
	count = count or 1
	inv.count = (inv.count or 1) - count
	if inv.count <= 0 then
		for slot, equippedUid in pairs(st.equip) do
			if equippedUid == uid then st.equip[slot] = nil end
		end
		st.inventory[uid] = nil
	end
	return true
end

function PlayerState.countOf(st, itemId)
	local n = 0
	for _, inv in pairs(st.inventory) do
		if inv.id == itemId then n = n + (inv.count or 1) end
	end
	return n
end

function PlayerState.findStack(st, itemId)
	for uid, inv in pairs(st.inventory) do
		if inv.id == itemId then return uid end
	end
	return nil
end

-- ============================================================================
-- Сеть
-- ============================================================================
local function remote(name, folder)
	return folder and folder:FindFirstChild(name)
end

function PlayerState.sendVitals(st, remotes)
	local r = remote(Net.Rep.Vitals, remotes)
	if not r then return end
	local c = st.stats_cache
	r:FireClient(st.player, {
		hp = math.floor(st.hp + 0.5),
		maxHp = math.floor(c.maxHealth + 0.5),
		mana = math.floor(st.mana + 0.5),
		maxMana = math.floor(c.maxMana + 0.5),
		stamina = math.floor(st.stamina + 0.5),
		maxStamina = Config.StaminaMax,
		level = st.level,
		xp = math.floor(st.xp),
		xpNeed = PlayerState.xpToNext(st),
		coins = st.coins,
		power = c.weaponDamage,
		armor = math.floor(c.armor + 0.5),
	})
end

function PlayerState.serializeInventory(st)
	local inv = {}
	for uid, it in pairs(st.inventory) do
		table.insert(inv, { uid = uid, id = it.id, count = it.count or 1 })
	end
	return { items = inv, equip = st.equip }
end

function PlayerState.sendInventory(st, remotes)
	local r = remote(Net.Rep.Inventory, remotes)
	if r then r:FireClient(st.player, PlayerState.serializeInventory(st)) end
end

function PlayerState.sendSpells(st, remotes)
	local r = remote(Net.Rep.Spells, remotes)
	if r then
		r:FireClient(st.player, { spells = st.spells, hotbar = st.hotbar, element = st.element })
	end
end

function PlayerState.sendStats(st, remotes)
	local r = remote(Net.Rep.Stats, remotes)
	if r then
		r:FireClient(st.player, { level = st.level, points = st.statPoints, stats = st.stats })
	end
end

function PlayerState.notify(st, remotes, text, kind)
	local r = remote(Net.Rep.Notify, remotes)
	if r then r:FireClient(st.player, { text = text, kind = kind or "info" }) end
end

return PlayerState
"""

SERVER["Combat"] = """-- Emberfall | Combat — единая точка нанесения урона, смерти, лута и опыта.
-- Все системы (мобы, боссы, заклинания, ближний бой) бьют через этот модуль.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local Combat = {}

local remotes            -- Remotes (заполняется снаружи)
local PlayerState        -- модуль состояния
local hooks = { onMobKilled = {}, onBossKilled = {}, onPlayerDied = {} }

function Combat.setup(deps)
	remotes = deps.remotes
	PlayerState = deps.playerState
end

function Combat.onMobKilled(fn) table.insert(hooks.onMobKilled, fn) end
function Combat.onBossKilled(fn) table.insert(hooks.onBossKilled, fn) end
function Combat.onPlayerDied(fn) table.insert(hooks.onPlayerDied, fn) end

-- ============================================================================
-- Служебное
-- ============================================================================
local function fireRep(name, player, ...)
	local r = remotes and remotes:FindFirstChild(name)
	if r then r:FireClient(player, ...) end
end

function Combat.broadcast(name, ...)
	local r = remotes and remotes:FindFirstChild(name)
	if r then r:FireAllClients(...) end
end

function Combat.damageNumber(pos, amount, kind)
	if not remotes then return end
	local r = remotes:FindFirstChild(Net.Rep.DamageNumber)
	if r then
		r:FireAllClients({ pos = pos, amount = math.floor(amount + 0.5), kind = kind or "normal" })
	end
end

-- ============================================================================
-- Урон по мобу / боссу
-- ============================================================================
local function rollCrit(chance)
	return math.random() < (chance or 0.1)
end

-- opts: { crit = bool, lifesteal = n, silent = bool, kind = "spell"|"melee" }
function Combat.damageMob(mob, amount, st, opts)
	if not mob or mob.dead then return 0 end
	opts = opts or {}

	local dmg = amount
	local crit = opts.crit
	if crit == nil then crit = rollCrit(0.1) end
	if crit then dmg = dmg * 1.6 end

	-- защита моба: чем выше уровень, тем меньше входящий урон от низкоуровневого героя
	if st then
		local lvlGap = (mob.def.level or 1) - st.level
		if lvlGap > 8 then
			dmg = dmg * math.max(0.45, 1 - (lvlGap - 8) * 0.03)
		end
	end

	dmg = math.max(1, dmg)
	mob.health = mob.health - dmg

	if not opts.silent then
		local head = mob.parts and mob.parts.head
		Combat.damageNumber(head and head.Position or mob.root.Position, dmg, crit and "crit" or (opts.kind or "normal"))
	end

	-- похищение жизни
	if st and opts.lifesteal and opts.lifesteal > 0 then
		local heal = dmg * opts.lifesteal
		Combat.healPlayer(st, heal, true)
	end

	if mob.health <= 0 then
		Combat.killMob(mob, st)
	else
		mob.onDamaged(dmg, st)
	end
	return dmg
end

-- ============================================================================
-- Смерть моба: лут, опыт, квесты
-- ============================================================================
function Combat.killMob(mob, st)
	if mob.dead then return end
	mob.dead = true

	local def = mob.def
	if def.isBoss then
		Combat.broadcast(Net.Rep.BossEvent, {
			event = "died", id = def.id, name = def.name,
		})
		Combat.broadcast(Net.Rep.BossBar, { visible = false })
		for _, fn in ipairs(hooks.onBossKilled) do fn(def, st) end
		if mob.onDeath then mob.onDeath() end
	else
		for _, fn in ipairs(hooks.onMobKilled) do fn(def, st, mob) end
	end

	-- опыт всем, кто рядом участвовал
	local xp = def.xp or 0
	if st and st.player and st.player.Parent then
		Combat.giveXp(st, xp)
	elseif mob.lastAttacker then
		local pst = PlayerState.get(mob.lastAttacker)
		if pst then Combat.giveXp(pst, xp) end
	end

	-- лут
	if st and st.player and st.player.Parent then
		Combat.dropLoot(def, st.player, mob.root.Position)
	end
end

function Combat.giveXp(st, amount)
	if not st or amount <= 0 then return end
	local before = st.level
	local ups = PlayerState.addXp(st, amount)
	local c = PlayerState.cache(st)

	if #ups > 0 then
		local character = st.player.Character
		if character then
			PlayerState.recompute(st, character)
			local hum = character:FindFirstChildOfClass("Humanoid")
			if hum then hum.Health = hum.MaxHealth end
		end
		st.hp = c.maxHealth or st.hp
		st.mana = c.maxMana or st.mana

		fireRep(Net.Rep.LevelUp, st.player, { level = st.level, from = before, points = st.statPoints })
		PlayerState.notify(st, remotes, "Уровень " .. st.level .. "! +" .. Config.StatPointsPerLevel .. " очка характеристик", "level")
		PlayerState.sendStats(st, remotes)
		-- открыть новые заклинания стихии
		if st.element then
			for _, sp in ipairs(GameData.SpellsForElement(st.element)) do
				if sp.reqLevel <= st.level and not st.spells[sp.id] and sp.reqLevel == st.level then
					st.spells[sp.id] = true
					local slot = Combat.firstFreeSlot(st)
					if slot then st.hotbar[slot] = sp.id end
					PlayerState.notify(st, remotes, "Новое заклинание: " .. sp.name .. "!", "spell")
				end
			end
			PlayerState.sendSpells(st, remotes)
		end
	else
		-- тихое обновление опыта
		fireRep(Net.Rep.Vitals, st.player, nil)  -- сигнал перерисовать
	end
	PlayerState.sendVitals(st, remotes)
end

function Combat.firstFreeSlot(st)
	for i = 1, 6 do
		if not st.hotbar[i] then return i end
	end
	return nil
end

-- ============================================================================
-- Лут
-- ============================================================================
function Combat.rollLoot(def, luck)
	local drops = {}
	for _, entry in ipairs(def.loot or {}) do
		local chance = entry.chance or 0.5
		if math.random() < chance then
			local minN = entry.min or 1
			local maxN = entry.max or minN
			local n = math.random(minN, maxN)
			table.insert(drops, { item = entry.item, count = n })
		end
	end
	return drops
end

function Combat.dropLoot(def, player, pos)
	local st = PlayerState.get(player)
	if not st then return end
	local drops = Combat.rollLoot(def)
	if #drops == 0 then return end

	for _, d in ipairs(drops) do
		local uid, err = PlayerState.addItem(st, d.item, d.count)
		local idef = GameData.ItemById[d.item]
		if uid and idef then
			local rar = GameData.Rarities[idef.rarity] or GameData.Rarities.common
			PlayerState.notify(st, remotes, "+ " .. idef.name .. (d.count > 1 and (" x" .. d.count) or ""), "loot_" .. idef.rarity)
		elseif err then
			PlayerState.notify(st, remotes, "Рюкзак полон — " .. (idef and idef.name or d.item) .. " потерян", "warn")
		end
	end
	PlayerState.sendInventory(st, remotes)
end

-- ============================================================================
-- Урон по игроку
-- ============================================================================
function Combat.damagePlayer(st, amount, source, opts)
	if not st or not st.player.Parent then return 0 end
	opts = opts or {}
	local character = st.player.Character
	if not character then return 0 end
	local hum = character:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return 0 end

	local c = PlayerState.cache(st)
	local dmg = amount
	if not opts.trueDamage then
		local armor = c.armor or 0
		dmg = dmg * (100 / (100 + armor))
	end
	dmg = math.max(1, dmg)

	st.hp = st.hp - dmg
	st.lastCombat = os.clock()
	hum.Health = math.clamp(st.hp, 0, hum.MaxHealth)

	local head = character:FindFirstChild("Head")
	Combat.damageNumber(head and head.Position or character:GetPivot().Position, dmg, "player")

	PlayerState.sendVitals(st, remotes)
	fireRep(Net.Rep.CombatState, st.player, true)

	if st.hp <= 0 then
		Combat.killPlayer(st, source)
	end
	return dmg
end

function Combat.healPlayer(st, amount, silent)
	if not st then return end
	local character = st.player.Character
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return end
	local before = st.hp
	st.hp = math.min(st.hp + amount, hum.MaxHealth)
	hum.Health = st.hp
	if not silent then
		local head = character:FindFirstChild("Head")
		Combat.damageNumber(head and head.Position or character:GetPivot().Position, amount, "heal")
	end
	PlayerState.sendVitals(st, remotes)
	return st.hp - before
end

function Combat.restoreMana(st, amount)
	local c = PlayerState.cache(st)
	st.mana = math.min(st.mana + amount, c.maxMana or 100)
	PlayerState.sendVitals(st, remotes)
end

function Combat.killPlayer(st, source)
	if st.dead then return end
	st.dead = true
	st.hp = 0
	st.lastCombat = os.clock()
	local character = st.player.Character
	if character then
		local hum = character:FindFirstChildOfClass("Humanoid")
		if hum then hum.Health = 0 end
	end
	-- штраф опыта
	local loss = math.floor(st.xp * Config.DeathXpLoss)
	st.xp = math.max(0, st.xp - loss)
	if loss > 0 then
		PlayerState.notify(st, remotes, "Вы погибли. Потеряно " .. loss .. " опыта", "bad")
	else
		PlayerState.notify(st, remotes, "Вы погибли", "bad")
	end
	for _, fn in ipairs(hooks.onPlayerDied) do fn(st, source) end
	PlayerState.sendVitals(st, remotes)
end

return Combat
"""

SERVER["MobService"] = """-- Emberfall | MobService — спавн мобов по маркерам GameLogic/MobSpawns,
-- погоня, атаки (ближние и дальние), респавн, привязка к земле.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local MobService = {}

local deps               -- { remotes, playerState, combat }
local mobFolder
local mobs = {}          -- массив активных мобов
local spawnPoints = {}   -- { marker, zone, x, y, z, respawnAt, mobId }
local activeRadius = 260
local maxActive = 42
local templateCache = {}

-- зоны-«лагеря» в маркерах -> конкретные мобы
local CAMP_MOB = {
	Bandits  = "Bandit",
	Hunters  = "FrostRenegade",
	Marauders = "Marauder",
	Cult     = "Cultist",
	Fishers  = "Drowned",
	-- v11: новые лагеря
	VeldtRaiders  = "Bandit",
	CanyonBandits = "SkeletonArcher",
	RidgePoachers = "Highwayman",
	ForestCutters = "GloomGoblin",
	DuneWreckers  = "BeachRaider",
}

function MobService.setup(d)
	deps = d
	mobFolder = Instance.new("Folder")
	mobFolder.Name = "EmberfallMobs"
	mobFolder.Parent = Workspace
end

-- ============================================================================
-- МОДЕЛЬ МОБА
-- ============================================================================
local function part(name, size, color, material, shape, transparency)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Shape = shape or Enum.PartType.Block
	p.Transparency = transparency or 0
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	return p
end

local function eyePair(parent, head, def, scale)
	local eyeColor = def.glow and Color3.fromRGB(255, 240, 140) or Color3.fromRGB(255, 90, 60)
	for _, sx in ipairs({ -1, 1 }) do
		local e = part("Eye", Vector3.new(0.28, 0.22, 0.14) * scale, eyeColor, Enum.Material.Neon)
		e.CFrame = head.CFrame * CFrame.new(sx * 0.3 * scale, 0.12 * scale, -0.46 * scale)
		e.Parent = parent
		local w = Instance.new("WeldConstraint")
		w.Part0 = head
		w.Part1 = e
		w.Parent = e
		e.Anchored = false
	end
end

local function buildModel(def)
	-- возвращает Model с якорным корнем; остальные части приварены
	local scale = def.scale or 1
	local model = Instance.new("Model")
	model.Name = def.name

	local col = def.color or Color3.fromRGB(120, 120, 120)
	local mat = Enum.Material.SmoothPlastic
	if def.model == "golem" then mat = Enum.Material.Slate end
	if def.model == "floating" then mat = Enum.Material.Neon end
	if def.model == "beast" then mat = Enum.Material.Fabric end

	local root = part("Root", Vector3.new(2, 2, 2) * scale, col, mat, Enum.PartType.Block, 1)
	root.CanQuery = false
	root.Parent = model
	model.PrimaryPart = root

	-- вспомогательная функция приварки
	local function weld(child, offset, rot)
		local w = Instance.new("WeldConstraint")
		w.Part0 = root
		w.Part1 = child
		w.Parent = child
		child.Anchored = false
		child.CFrame = root.CFrame * offset * (rot or CFrame.new())
		return child
	end

	local parts = { root = root }
	local torsoSize, headSize, limbSize

	if def.model == "beast" then
		torsoSize = Vector3.new(1.8, 1.5, 4.2) * scale
		headSize = Vector3.new(1.5, 1.4, 1.9) * scale
		limbSize = Vector3.new(0.5, 2.0, 0.5) * scale
	elseif def.model == "floating" then
		torsoSize = Vector3.new(2.0, 2.6, 1.3) * scale
		headSize = Vector3.new(1.5, 1.5, 1.5) * scale
		limbSize = Vector3.new(0.5, 2.2, 0.5) * scale
	elseif def.model == "golem" then
		torsoSize = Vector3.new(3.2, 3.2, 2.2) * scale
		headSize = Vector3.new(1.6, 1.5, 1.5) * scale
		limbSize = Vector3.new(1.1, 2.8, 1.1) * scale
	else
		torsoSize = Vector3.new(2.0, 2.2, 1.1) * scale
		headSize = Vector3.new(1.3, 1.3, 1.3) * scale
		limbSize = Vector3.new(0.55, 2.0, 0.55) * scale
	end

	local torso = part("Torso", torsoSize, col, mat)
	torso.Parent = model
	weld(torso, CFrame.new(0, def.model == "beast" and 0.2 * scale or 0, 0))
	parts.torso = torso

	local head = part("Head", headSize, col, mat)
	head.Parent = model
	local headY = (torsoSize.Y / 2 + headSize.Y / 2 + 0.1) * (def.model == "beast" and 0.35 or 1)
	local headZ = def.model == "beast" and (-torsoSize.Z / 2 - headSize.Z / 2 + 0.6 * scale) or 0
	weld(head, CFrame.new(0, headY, headZ))
	parts.head = head
	eyePair(model, head, def, scale)

	-- конечности (для вида; анимация — покачивание)
	local limbOffsets
	if def.model == "beast" then
		limbOffsets = {
			{ -torsoSize.X / 2 + 0.1, -torsoSize.Y / 2, -torsoSize.Z / 3 },
			{ torsoSize.X / 2 - 0.1, -torsoSize.Y / 2, -torsoSize.Z / 3 },
			{ -torsoSize.X / 2 + 0.1, -torsoSize.Y / 2, torsoSize.Z / 3 },
			{ torsoSize.X / 2 - 0.1, -torsoSize.Y / 2, torsoSize.Z / 3 },
		}
	else
		limbOffsets = {
			{ -torsoSize.X / 2 - limbSize.X / 2, -0.1 * scale, 0 },
			{ torsoSize.X / 2 + limbSize.X / 2, -0.1 * scale, 0 },
		}
	end

	parts.limbs = {}
	for i, o in ipairs(limbOffsets) do
		local l = part("Limb" .. i, limbSize, col, mat)
		l.Parent = model
		weld(l, CFrame.new(table.unpack(o)) * CFrame.new(0, -limbSize.Y / 2, 0))
		parts.limbs[i] = l
	end

	-- аура/свечение
	if def.glow then
		local light = Instance.new("PointLight")
		light.Color = col
		light.Brightness = 1.4
		light.Range = 18 * scale
		light.Parent = torso
	end

	-- полоска здоровья над головой (BillboardGui)
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "HpBar"
	billboard.Size = UDim2.new(0, 90 * math.min(scale, 1.6), 0, 14)
	billboard.StudsOffset = Vector3.new(0, headSize.Y + 1.2, 0)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 140
	billboard.Parent = head

	local bg = Instance.new("Frame")
	bg.Size = UDim2.new(1, 0, 1, 0)
	bg.BackgroundColor3 = Color3.fromRGB(20, 20, 22)
	bg.BackgroundTransparency = 0.35
	bg.BorderSizePixel = 0
	bg.Parent = billboard

	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.new(1, 0, 1, 0)
	fill.BackgroundColor3 = Color3.fromRGB(200, 60, 60)
	fill.BorderSizePixel = 0
	fill.Parent = bg

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = def.name .. "  ур." .. tostring(def.level)
	label.TextColor3 = Color3.fromRGB(255, 255, 255)
	label.TextStrokeTransparency = 0.4
	label.TextScaled = true
	label.Font = Enum.Font.GothamBold
	label.Parent = bg

	return model, parts
end

-- ============================================================================
-- ЗЕМЛЯ
-- ============================================================================
local groundParams
local function ensureParams()
	groundParams = RaycastParams.new()
	groundParams.FilterType = Enum.RaycastFilterType.Exclude
	local ignore = { mobFolder }
	local gl = Workspace:FindFirstChild("GameLogic")
	if gl then table.insert(ignore, gl) end
	for _, name in ipairs({ "EmberfallFx", "EmberfallWorld" }) do
		local f = Workspace:FindFirstChild(name)
		if f then table.insert(ignore, f) end
	end
	groundParams.FilterDescendantsInstances = ignore
	groundParams.IgnoreWater = true
	return groundParams
end

function MobService.groundY(pos)
	local params = ensureParams()
	local origin = Vector3.new(pos.X, pos.Y + 220, pos.Z)
	local result = Workspace:Raycast(origin, Vector3.new(0, -600, 0), params)
	if result then
		return result.Position.Y
	end
	return nil
end

-- ============================================================================
-- СОЗДАНИЕ МОБА
-- ============================================================================
local function nearestPlayer(position, maxDist)
	local best, bestD = nil, maxDist or 1e9
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if root and hum and hum.Health > 0 then
			local d = (root.Position - position).Magnitude
			if d < bestD then best, bestD = pl, d end
		end
	end
	return best, bestD
end

local function shootProjectile(fromPos, targetPlayer, def, damage)
	local char = targetPlayer.Character
	local torso = char and (char:FindFirstChild("HumanoidRootPart") or char:FindFirstChild("Torso"))
	if not torso then return end

	local col = def.color or Color3.fromRGB(200, 100, 255)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(0.9, 0.9, 0.9)
	p.Color = col
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Parent = deps.fxFolder
	p.Position = fromPos

	local start = fromPos
	local target = torso.Position
	local dist = (target - start).Magnitude
	local speed = 70
	local t = dist / speed

	local TweenService = game:GetService("TweenService")
	local tw = TweenService:Create(p, TweenInfo.new(t, Enum.EasingStyle.Linear), { CFrame = CFrame.new(target) })
	tw:Play()
	tw.Completed:Connect(function()
		p:Destroy()
		-- урон, если игрок ещё жив и близко
		local st = deps.playerState.get(targetPlayer)
		if st and st.player.Character then
			local r = st.player.Character:FindFirstChild("HumanoidRootPart")
			if r and (r.Position - target).Magnitude < 14 then
				deps.combat.damagePlayer(st, damage, def.name)
			end
		end
	end)
end

function MobService.spawnMob(def, position)
	local model, parts = buildModel(def)
	model.Parent = mobFolder

	local mob = {
		model = model,
		parts = parts,
		root = parts.root,
		def = def,
		health = def.health,
		maxHealth = def.health,
		dead = false,
		lastAttack = 0,
		lastGroundCheck = 0,
		groundY = position.Y,
		pos = position,
		yaw = math.random() * math.pi * 2,
		speedMult = 1,
		home = position,
		walkPhase = math.random() * 10,
		aggroOn = nil,
	}

	-- обработчик полоски здоровья
	local fill = parts.head:FindFirstChild("HpBar") and parts.head.HpBar:FindFirstChild("Frame"):FindFirstChild("Fill")
	local baseColor = Color3.fromRGB(200, 60, 60)
	mob.setBar = function()
		if not fill then return end
		local ratio = math.clamp(mob.health / mob.maxHealth, 0, 1)
		fill.Size = UDim2.new(ratio, 0, 1, 0)
		if def.isBoss then
			fill.BackgroundColor3 = Color3.fromRGB(180, 40, 220)
		elseif def.elite then
			fill.BackgroundColor3 = Color3.fromRGB(240, 170, 50)
		else
			fill.BackgroundColor3 = baseColor
		end
	end
	mob.setBar()

	mob.onDamaged = function()
		mob.setBar()
		if not mob.aggroOn then
			local pl = nearestPlayer(mob.pos, 90)
			if pl then mob.aggroOn = pl end
		end
	end

	mob.onDeath = function()
		-- эффект смерти
		local root = mob.root
		local burst = Instance.new("Part")
		burst.Shape = Enum.PartType.Ball
		burst.Size = Vector3.new(1, 1, 1)
		burst.Color = def.color or Color3.fromRGB(150, 150, 150)
		burst.Material = Enum.Material.Neon
		burst.Anchored = true
		burst.CanCollide = false
		burst.CanQuery = false
		burst.Position = root.Position
		burst.Parent = deps.fxFolder
		local T = game:GetService("TweenService")
		local tw = T:Create(burst, TweenInfo.new(0.45, Enum.EasingStyle.Quad), {
			Size = Vector3.new(9, 9, 9), Transparency = 1,
		})
		tw:Play()
		tw.Completed:Connect(function() burst:Destroy() end)
		model:Destroy()
	end

	mob.root.CFrame = CFrame.new(position) * CFrame.Angles(0, mob.yaw, 0)
	table.insert(mobs, mob)
	return mob
end

-- ============================================================================
-- ИИ
-- ============================================================================
local function updateMob(mob, dt, now)
	if mob.dead then return end
	local root = mob.root
	if not root or not root.Parent then mob.dead = true return end

	local myPos = root.Position
	-- земля
	if now - mob.lastGroundCheck > 0.35 then
		mob.lastGroundCheck = now
		local gy = MobService.groundY(myPos)
		if gy then mob.groundY = gy end
	end

	local target = mob.aggroOn
	if target and (not target.Parent or not target.Character) then target = nil; mob.aggroOn = nil end
	if target then
		local char = target.Character
		local tr = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if not tr or not hum or hum.Health <= 0 then
			mob.aggroOn = nil
			target = nil
		end
	end

	if not target then
		local pl, d = nearestPlayer(myPos, mob.def.aggro or 55)
		if pl then
			mob.aggroOn = pl
			target = pl
		end
	end

	local moveTo = nil
	local attackRange = mob.def.ranged and (mob.def.ranged - 8) or 6.5

	if target then
		local tr = target.Character.HumanoidRootPart
		local toPlayer = tr.Position - myPos
		local dist = toPlayer.Magnitude
		local dir = Vector3.new(toPlayer.X, 0, toPlayer.Z).Unit

		if dist > attackRange then
			moveTo = myPos + dir * math.min(dist - attackRange + 1, 8)
			mob.yaw = math.atan2(dir.X, dir.Z)
		else
			mob.yaw = math.atan2(toPlayer.X, toPlayer.Z)
			if now - mob.lastAttack > (mob.def.attackCooldown or 1.5) then
				mob.lastAttack = now
				local st = deps.playerState.get(target)
				if st then
					if mob.def.ranged then
						shootProjectile(myPos + Vector3.new(0, 2, 0), target, mob.def, mob.def.damage)
					else
						deps.combat.damagePlayer(st, mob.def.damage, mob.def.name)
					end
				end
			end
		end
	elseif (myPos - mob.home).Magnitude > 45 then
		-- возврат домой
		local dir = (mob.home - myPos)
		dir = Vector3.new(dir.X, 0, dir.Z).Unit
		moveTo = myPos + dir * 6
		mob.yaw = math.atan2(dir.X, dir.Z)
	end

	local newPos = myPos
	if moveTo then
		local speed = (mob.def.speed or 14) * (mob.speedMult or 1) * (mob.enraged and 1.25 or 1)
		local step = Vector3.new(moveTo.X - myPos.X, 0, moveTo.Z - myPos.Z)
		if step.Magnitude > 0.05 then
			step = step.Unit * math.min(speed * dt, step.Magnitude)
			newPos = myPos + step
			mob.walkPhase = mob.walkPhase + dt * 9
		end
	end

	-- держим на земле + покачивание при ходьбе
	local bob = math.sin(mob.walkPhase) * 0.18
	local y = (mob.groundY or myPos.Y) + (mob.def.model == "floating" and 3.2 or 2.2)
	if mob.def.model == "floating" then
		y = y + math.sin(now * 1.6 + mob.walkPhase) * 0.5
	else
		y = y + bob
	end

	local tilt = moveTo and math.sin(mob.walkPhase) * 0.06 or 0
	root.CFrame = CFrame.new(newPos.X, y, newPos.Z) * CFrame.Angles(tilt, mob.yaw, 0)
	mob.pos = root.Position
end

-- ============================================================================
-- СПАВН-ПОИНТЫ
-- ============================================================================
local function chooseMobForZone(zone, rng)
	local explicit = CAMP_MOB[zone]
	if explicit then return GameData.MobById[explicit] end
	local list = GameData.MobsInZone(zone)
	if #list == 0 then return nil end
	return list[rng:NextInteger(1, #list)]
end

function MobService.start()
	local gl = Workspace:FindFirstChild("GameLogic")
	local spawnsFolder = gl and gl:FindFirstChild("MobSpawns")
	if not spawnsFolder then
		warn("[Emberfall] MobSpawns не найдены")
		return
	end

	local rng = Random.new(os.time())
	local count = 0
	for _, marker in ipairs(spawnsFolder:GetChildren()) do
		if marker:IsA("BasePart") and marker.Name:match("^MobSpawn_") then
			local zone = marker.Name:match("^MobSpawn_([^_]+)_")
			local def = chooseMobForZone(zone, rng)
			if def then
				table.insert(spawnPoints, {
					def = def,
					pos = marker.Position,
					marker = marker,
					respawnAt = 0,
					mob = nil,
					zone = zone,
				})
				count = count + 1
			end
		end
	end
	print(("[Emberfall] Точек спавна мобов: %d"):format(count))
end

-- активность: спавним точки рядом с игроками, убираем далёких
local function manageSpawns(now)
	local players = Players:GetPlayers()
	if #players == 0 then return end

	local activeCount = 0
	for _, m in ipairs(mobs) do
		if not m.dead then activeCount = activeCount + 1 end
	end

	for _, sp in ipairs(spawnPoints) do
		local near = false
		for _, pl in ipairs(players) do
			local char = pl.Character
			local root = char and char:FindFirstChild("HumanoidRootPart")
			if root and (root.Position - sp.pos).Magnitude < activeRadius then
				near = true
				break
			end
		end

		if sp.mob and sp.mob.dead then
			sp.mob = nil
			sp.respawnAt = now + 14 + math.random() * 12
		elseif sp.mob and not near then
			-- далеко: убираем, чтобы не жечь ресурсы
			if sp.mob.model then sp.mob.model:Destroy() end
			sp.mob.dead = true
			sp.mob = nil
			sp.respawnAt = now + 1
		end

		if not sp.mob and near and now >= sp.respawnAt and activeCount < maxActive then
			local gy = MobService.groundY(sp.pos)
			local pos = Vector3.new(sp.pos.X, (gy or sp.pos.Y - 1), sp.pos.Z)
			sp.mob = MobService.spawnMob(sp.def, pos)
			activeCount = activeCount + 1
		end
	end

	-- чистка мёртвых
	for i = #mobs, 1, -1 do
		local m = mobs[i]
		if m.dead or not m.model.Parent then table.remove(mobs, i) end
	end
end

-- ============================================================================
-- ПУБЛИЧНЫЙ API
-- ============================================================================
function MobService.getMobsNear(pos, radius)
	local out = {}
	for _, m in ipairs(mobs) do
		if not m.dead and m.root and m.root.Parent then
			if (m.root.Position - pos).Magnitude <= radius then
				table.insert(out, m)
			end
		end
	end
	return out
end

-- доступ для автотестов
function MobService.spawnPointsForTest()
	return spawnPoints
end

function MobService.allMobs()
	return mobs
end

function MobService.startLoop()
	local acc = 0
	local manageAcc = 0
	RunService.Heartbeat:Connect(function(dt)
		local now = os.clock()
		acc = acc + dt
		manageAcc = manageAcc + dt
		if manageAcc > 1.0 then
			manageAcc = 0
			manageSpawns(now)
		end
		for _, m in ipairs(mobs) do
			-- LOD: далёкие мобы думают реже
			local pl = Players:GetPlayers()[1]
			updateMob(m, dt, now)
		end
	end)
end

return MobService
"""

SERVER["BossService"] = """-- Emberfall | BossService — боссы на аренах: спавн по входу в ArenaTrigger_*,
-- фазы, способности, полоса HP, анонсы, респавн, лут.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local BossService = {}

local deps
local arenas = {}   -- { def, center, radius, marker, boss, respawnAt }
local activeBoss = nil

local function broadcast(name, ...)
	local r = deps.remotes:FindFirstChild(name)
	if r then r:FireAllClients(...) end
end

local function ringEffect(pos, color, radius, duration)
	local ring = Instance.new("Part")
	ring.Shape = Enum.PartType.Cylinder
	ring.Size = Vector3.new(0.4, radius * 2, radius * 2)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	ring.Color = color
	ring.Material = Enum.Material.Neon
	ring.Transparency = 0.35
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.Parent = deps.fxFolder
	local tw = TweenService:Create(ring, TweenInfo.new(duration or 0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Transparency = 1, Size = Vector3.new(0.4, radius * 3, radius * 3),
	})
	tw:Play()
	tw.Completed:Connect(function() ring:Destroy() end)
	return ring
end

local function damageCircle(center, radius, damage, bossDef, opts)
	opts = opts or {}
	ringEffect(center, opts.color or (bossDef.color or Color3.fromRGB(200, 80, 80)), radius, opts.ringTime or 0.45)
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if root then
			local d = (root.Position - center)
			if Vector3.new(d.X, 0, d.Z).Magnitude <= radius then
				local st = deps.playerState.get(pl)
				if st then
					deps.combat.damagePlayer(st, damage, bossDef.name)
					if opts.slow then
						table.insert(st.buffs, { type = "speed", value = -6, expires = os.clock() + opts.slow })
					end
				end
			end
		end
	end
end

local function meteorStrike(bossDef, targetPos, damage, radius, color)
	-- предупреждение на земле
	local warn = Instance.new("Part")
	warn.Shape = Enum.PartType.Cylinder
	warn.Size = Vector3.new(0.3, radius * 2, radius * 2)
	warn.CFrame = CFrame.new(targetPos) * CFrame.Angles(0, 0, math.rad(90))
	warn.Color = color
	warn.Material = Enum.Material.Neon
	warn.Transparency = 0.55
	warn.Anchored = true
	warn.CanCollide = false
	warn.CanQuery = false
	warn.Parent = deps.fxFolder

	local fall = Instance.new("Part")
	fall.Shape = Enum.PartType.Ball
	fall.Size = Vector3.new(radius * 0.9, radius * 0.9, radius * 0.9)
	fall.Color = color
	fall.Material = Enum.Material.Neon
	fall.Anchored = true
	fall.CanCollide = false
	fall.CanQuery = false
	fall.Position = targetPos + Vector3.new(0, 160, 0)
	fall.Parent = deps.fxFolder

	local tw = TweenService:Create(fall, TweenInfo.new(0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		Position = targetPos,
	})
	tw:Play()
	tw.Completed:Connect(function()
		fall:Destroy()
		warn:Destroy()
		damageCircle(targetPos, radius, damage, bossDef, { color = color, ringTime = 0.6 })
	end)
end

-- ============================================================================
-- СПОСОБНОСТИ
-- ============================================================================
local function abilityVolley(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Залп" })
	local targets = {}
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local r = char and char:FindFirstChild("HumanoidRootPart")
		if r and (r.Position - root.Position).Magnitude < 180 then
			table.insert(targets, pl)
		end
	end
	for i, pl in ipairs(targets) do
		task.delay(i * 0.12, function()
			if boss.dead or not root.Parent then return end
			local char = pl.Character
			local tr = char and char:FindFirstChild("HumanoidRootPart")
			if not tr then return end
			local proj = Instance.new("Part")
			proj.Shape = Enum.PartType.Ball
			proj.Size = Vector3.new(1.6, 1.6, 1.6)
			proj.Color = def.color or Color3.fromRGB(200, 100, 255)
			proj.Material = Enum.Material.Neon
			proj.Anchored = true
			proj.CanCollide = false
			proj.CanQuery = false
			proj.Position = root.Position + Vector3.new(0, 4, 0)
			proj.Parent = deps.fxFolder
			local targetPos = tr.Position
			local dist = (targetPos - proj.Position).Magnitude
			local tw = TweenService:Create(proj, TweenInfo.new(dist / 70, Enum.EasingStyle.Linear), {
				Position = targetPos,
			})
			tw:Play()
			tw.Completed:Connect(function()
				proj:Destroy()
				local st = deps.playerState.get(pl)
				local c = pl.Character
				local rr = c and c:FindFirstChild("HumanoidRootPart")
				if st and rr and (rr.Position - targetPos).Magnitude < 12 then
					deps.combat.damagePlayer(st, def.damage * 0.55, def.name)
				end
			end)
		end)
	end
end

local function abilitySlam(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Сокрушающий удар" })
	task.wait(0.55)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 22, def.damage * 0.8, def, { slow = 0 })
	-- тряска: толкаем игроков
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		if rr and (rr.Position - root.Position).Magnitude < 26 then
			local dir = (rr.Position - root.Position).Unit
			rr.AssemblyLinearVelocity = dir * 55 + Vector3.new(0, 26, 0)
		end
	end
end

local function abilityFrostNova(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Ледяная новая" })
	task.wait(0.4)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 34, def.damage * 0.7, def, {
		color = Color3.fromRGB(150, 220, 255), slow = 4, ringTime = 0.7,
	})
end

local function abilityPoisonNova(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Ядовитая волна" })
	task.wait(0.4)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 30, def.damage * 0.5, def, {
		color = Color3.fromRGB(120, 200, 80), ringTime = 0.8,
	})
	-- отравление: тикающий урон
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		if rr and (rr.Position - root.Position).Magnitude < 34 then
			local st = deps.playerState.get(pl)
			if st then
				task.spawn(function()
					for i = 1, 4 do
						task.wait(1)
						if st.hp <= 0 then break end
						deps.combat.damagePlayer(st, def.damage * 0.14, def.name, { trueDamage = true })
					end
				end)
			end
		end
	end
end

local function abilityMeteor(boss, def)
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Метеоритный дождь" })
	local players = Players:GetPlayers()
	for i = 1, 3 do
		task.delay((i - 1) * 0.5, function()
			if boss.dead then return end
			-- цель: случайный игрок, либо случайная точка рядом с боссом
			local pl = players[math.random(1, math.max(1, #players))]
			local char = pl and pl.Character
			local rr = char and char:FindFirstChild("HumanoidRootPart")
			local targetPos
			if rr and (rr.Position - boss.root.Position).Magnitude < 200 then
				targetPos = rr.Position
			else
				targetPos = boss.root.Position + Vector3.new(math.random(-25, 25), 0, math.random(-25, 25))
			end
			local gy = deps.mobService.groundY(targetPos)
			targetPos = Vector3.new(targetPos.X, gy or targetPos.Y, targetPos.Z)
			meteorStrike(def, targetPos, def.damage * 0.85, 14, def.color or Color3.fromRGB(255, 120, 40))
		end)
	end
end

local function abilitySummon(boss, def)
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Зов слуг" })
	-- зона берётся из таблицы данжей (Dungeons.OfBoss), чтобы слуги были «свои»
	local Dungeons = require(Shared:WaitForChild("Dungeons"))
	local zone = Dungeons.OfBoss[def.id] or "Bonefields"
	local list = GameData.MobsInZone(zone)
	if #list == 0 then return end
	for i = 1, 2 do
		task.delay(i * 0.25, function()
			if boss.dead then return end
			local angle = math.random() * math.pi * 2
			local off = Vector3.new(math.cos(angle) * 12, 0, math.sin(angle) * 12)
			local def2 = list[math.random(1, #list)]
			local gy = deps.mobService.groundY(boss.root.Position + off)
			local m = deps.mobService.spawnMob(def2, Vector3.new(
				boss.root.Position.X + off.X, gy or boss.root.Position.Y, boss.root.Position.Z + off.Z))
			-- слуги босса агрессивны сразу
			for _, pl in ipairs(Players:GetPlayers()) do
				local rr = pl.Character and pl.Character:FindFirstChild("HumanoidRootPart")
				if rr and (rr.Position - m.root.Position).Magnitude < 90 then
					m.aggroOn = pl
					break
				end
			end
		end)
	end
end

local ABILITIES = {
	Volley = abilityVolley,
	Slam = abilitySlam,
	FrostNova = abilityFrostNova,
	PoisonNova = abilityPoisonNova,
	Meteor = abilityMeteor,
	Summon = abilitySummon,
}

-- ============================================================================
-- ФАЗЫ / БОЙ
-- ============================================================================
local function currentPhase(boss)
	local ratio = boss.health / boss.maxHealth
	local phase = boss.def.phases[1]
	for _, p in ipairs(boss.def.phases) do
		if ratio <= p.at then phase = p end
	end
	return phase
end

local function bossThink(boss, def, now)
	if boss.dead then return end
	local root = boss.root
	if not root or not root.Parent then boss.dead = true return end

	-- фаза
	local phase = currentPhase(boss)
	if boss.phase ~= phase then
		if boss.phase ~= nil then
			broadcast(Net.Rep.BossEvent, {
				event = "phase", id = def.id, name = def.name,
				text = "Фаза " .. (phase == def.phases[#def.phases] and "финальная" or "изменилась") .. "!",
			})
		end
		boss.phase = phase
		if phase.enrage then
			boss.enraged = true
		end
	end

	local phaseAbilities = phase.abilities or { "Slam" }

	-- движение к ближайшему игроку
	local bestPl, bestD = nil, 1e9
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if rr and hum and hum.Health > 0 then
			local d = (rr.Position - root.Position).Magnitude
			if d < bestD then bestPl, bestD = pl, d end
		end
	end

	if not bestPl then
		boss.idleTime = (boss.idleTime or 0) + 0.1
		boss.lastAttack = now
		return
	end

	local tr = bestPl.Character.HumanoidRootPart
	local toP = tr.Position - root.Position
	local dist = toP.Magnitude
	local dir = Vector3.new(toP.X, 0, toP.Z).Unit

	-- смотрим на игрока
	boss.yaw = math.atan2(toP.X, toP.Z)

	-- подходим, если далеко
	if dist > 16 then
		local speed = (def.baseSpeed or def.speed or 12) * (boss.enraged and 1.35 or 1)
		local step = dir * math.min(speed * 0.1, dist - 16)
		local newPos = root.Position + step
		local gy = deps.mobService.groundY(newPos)
		local y = (gy or root.Position.Y) + 4
		if def.model == "floating" then y = y + 1 end
		root.CFrame = CFrame.new(newPos.X, y, newPos.Z) * CFrame.Angles(0, boss.yaw, 0)
	end

	-- атака
	if now - boss.lastAttack > (boss.attackInterval or 3.2) then
		boss.lastAttack = now
		local abilityName = phaseAbilities[math.random(1, #phaseAbilities)]
		local fn = ABILITIES[abilityName]
		if fn then
			task.spawn(function()
				local ok, err = pcall(fn, boss, def)
				if not ok then warn("[Emberfall] Босс-способность ошибка: " .. tostring(err)) end
			end)
		end
		boss.attackInterval = 2.6 + math.random() * 1.6
	end

	-- ближняя атака вплотную
	if dist < 12 and now - (boss.lastMelee or 0) > 2.0 then
		boss.lastMelee = now
		local st = deps.playerState.get(bestPl)
		if st then deps.combat.damagePlayer(st, def.damage * 0.5, def.name) end
	end
end

-- ============================================================================
-- СПАВН / СМЕРТЬ
-- ============================================================================
local function applyBossBar()
	if worldBoss and not worldBoss.dead and worldBoss.root and worldBoss.root.Parent then
		-- мировой босс перекрывает аренного, если игрок рядом
		for _, pl in ipairs(Players:GetPlayers()) do
			local rr = pl.Character and pl.Character:FindFirstChild("HumanoidRootPart")
			if rr and (rr.Position - worldBoss.root.Position).Magnitude < 320 then
				broadcast(Net.Rep.BossBar, {
					visible = true, name = worldBoss.def.name, title = worldBoss.def.title,
					level = worldBoss.def.level, hp = worldBoss.health,
					maxHp = worldBoss.maxHealth, phase = 1,
				})
				return
			end
		end
	end
	if not activeBoss or activeBoss.dead then
		broadcast(Net.Rep.BossBar, { visible = false })
		return
	end
	local b = activeBoss
	broadcast(Net.Rep.BossBar, {
		visible = true,
		name = b.def.name,
		title = b.def.title,
		level = b.def.level,
		hp = b.health,
		maxHp = b.maxHealth,
		phase = b.phase and b.phase.at or 1.0,
	})
end

local function spawnBoss(arena, now)
	local def = arena.def
	local markerPos = arena.marker.Position
	local gy = deps.mobService.groundY(markerPos) or markerPos.Y
	local pos = Vector3.new(markerPos.X, gy, markerPos.Z)

	broadcast(Net.Rep.BossEvent, {
		event = "appear", id = def.id, name = def.name, title = def.title, level = def.level,
	})
	broadcast(Net.Rep.BossBar, { visible = true, name = def.name, title = def.title,
		level = def.level, hp = def.health, maxHp = def.health, phase = 1 })

	local defCopy = {}
	for k, v in pairs(def) do defCopy[k] = v end
	defCopy.isBoss = true
	defCopy.baseSpeed = def.speed

	local mob = deps.mobService.spawnMob(defCopy, pos)
	-- боссу увеличиваем полоску (BillboardGui уже есть) — полоса сверху экрана важнее
	mob.isBoss = true
	mob.attackInterval = 3.0
	mob.lastAttack = now

	-- перехватываем onDamaged для полосы
	local origDamaged = mob.onDamaged
	mob.onDamaged = function(dmg, st)
		origDamaged(dmg, st)
		if st then mob.lastAttackerPlayer = st.player end
		applyBossBar()
	end

	mob.onDeath = function()
		-- эффект
		ringEffect(mob.root.Position, def.color or Color3.fromRGB(200, 120, 255), 40, 1.2)
		for i = 1, 6 do
			task.delay(i * 0.15, function()
				local p = mob.root.Position + Vector3.new(math.random(-20, 20), math.random(2, 18), math.random(-20, 20))
				ringEffect(p, def.color or Color3.fromRGB(200, 120, 255), math.random(4, 12), 0.6)
			end)
		end
		mob.model:Destroy()
		activeBoss = nil
		arena.mob = nil
		arena.respawnAt = now + (def.respawn or 180)
		applyBossBar()
	end

	arena.mob = mob
	activeBoss = mob
	return mob
end



-- ============================================================================
-- МИРОВОЙ БОСС: «Пепельный Странник» — появляется сам, раз в ~12 минут
-- ============================================================================
local worldBoss = nil

local WORLD_BOSS_DEF = {
	id = "EmberWanderer", name = "Пепельный Странник", title = "Вестник Конца",
	level = 45, health = 11000, damage = 88, speed = 15, xp = 9000,
	model = "humanoid", color = Color3.fromRGB(220, 90, 40), scale = 2.1, glow = true,
	arenaRadius = 90, respawn = 600, isWorldBoss = true,
	phases = {
		{ at = 1.0, abilities = { "Slam", "Volley" } },
		{ at = 0.6, abilities = { "Slam", "Meteor", "Summon" } },
		{ at = 0.25, abilities = { "Meteor", "FrostNova", "Volley", "Summon" }, enrage = 0.5 },
	},
	loot = { { item = "W_AshCleaver", chance = 0.9 }, { item = "C_Elixir", chance = 1, min = 2, max = 4 },
	         { item = "M_AshEssence", chance = 1, min = 6, max = 10 },
	         { item = "T_BloodCharm", chance = 0.5 } },
}

local function spawnWorldBoss()
	local pl = Players:GetPlayers()[math.random(1, #Players:GetPlayers())]
	local char = pl and pl.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local angle = math.random() * math.pi * 2
	local dist = math.random(70, 110)
	local pos = root.Position + Vector3.new(math.cos(angle) * dist, 0, math.sin(angle) * dist)
	local gy = deps.mobService.groundY(pos)
	pos = Vector3.new(pos.X, gy or pos.Y, pos.Z)

	deps.combat.broadcast(Net.Rep.BossEvent, {
		event = "world", id = WORLD_BOSS_DEF.id, name = WORLD_BOSS_DEF.name,
		title = WORLD_BOSS_DEF.title, level = WORLD_BOSS_DEF.level,
	})
	deps.combat.broadcast(Net.Rep.Notify, {
		text = "МИРОВОЙ БОСС: " .. WORLD_BOSS_DEF.name .. " появился рядом с " .. pl.DisplayName .. "!",
		kind = "boss",
	})

	local defCopy = {}
	for k, v in pairs(WORLD_BOSS_DEF) do defCopy[k] = v end
	defCopy.baseSpeed = WORLD_BOSS_DEF.speed
	defCopy.isBoss = true

	local mob = deps.mobService.spawnMob(defCopy, pos)
	mob.isBoss = true
	mob.attackInterval = 2.6
	mob.lastAttack = os.clock()
	local origDamaged = mob.onDamaged
	mob.onDamaged = function(dmg, st)
		origDamaged(dmg, st)
		applyBossBar()
	end
	mob.onDeath = function()
		mob.model:Destroy()
		if worldBoss == mob then worldBoss = nil end
		applyBossBar()
	end
	worldBoss = mob
	applyBossBar()
	return mob
end

-- ============================================================================
-- СБОРКА АРЕН
-- ============================================================================
function BossService.setup(d)
	deps = d
	-- маркеры разложены по папкам биомов внутри Workspace.World
	local bossMarkers = {}
	local arenaMarkers = {}
	for _, inst in ipairs(Workspace:GetDescendants()) do
		if inst:IsA("BasePart") then
			if inst.Name:match("^BossSpawn_") then
				table.insert(bossMarkers, inst)
			elseif inst.Name:match("^ArenaTrigger_") then
				table.insert(arenaMarkers, inst)
			end
		end
	end

	if true then
		for _, marker in ipairs(bossMarkers) do
			do
				local bossId = marker.Name:match("^BossSpawn_(.+)$")
				local def = bossId and GameData.BossById[bossId]
				if def then
					table.insert(arenas, {
						def = def, marker = marker,
						center = marker.Position,
						radius = def.arenaRadius or 70,
						respawnAt = 0, mob = nil,
					})
				end
			end
		end
	end

	if true then
		for _, marker in ipairs(arenaMarkers) do
			do
				local bossId = marker.Name:match("^ArenaTrigger_(.+)$")
				local def = bossId and GameData.BossById[bossId]
				if def then
					local exists = false
					for _, a in ipairs(arenas) do
						if a.def.id == def.id then exists = true end
					end
					if not exists then
						table.insert(arenas, {
							def = def, marker = marker, center = marker.Position,
							radius = def.arenaRadius or 70, respawnAt = 0, mob = nil,
						})
					else
						-- уточняем радиус из маркера арены (Size.Y = r*2)
						for _, a in ipairs(arenas) do
							if a.def.id == def.id then
								a.arenaMarker = marker
								a.arenaRadius = math.floor(marker.Size.Y / 2)
								a.center = marker.Position
							end
						end
					end
				end
			end
		end
	end
	print(("[Emberfall] Арен с боссами: %d"):format(#arenas))
end

function BossService.startLoop()
	local barAcc = 0
	local worldAcc = 0
	local arenaAcc = 0
	RunService.Heartbeat:Connect(function(dt)
		local now = os.clock()
		arenaAcc = arenaAcc + dt
		barAcc = barAcc + dt

		if barAcc > 0.25 then
			barAcc = 0
			applyBossBar()
			if activeBoss and not activeBoss.dead then
				bossThink(activeBoss, activeBoss.def, now)
			end
		end

		-- мировой босс: раз в 12 минут появляется у случайного игрока
		worldAcc = worldAcc + dt
		if worldAcc > 720 and #Players:GetPlayers() > 0 and not worldBoss then
			worldAcc = 0
			spawnWorldBoss()
		end
		if worldBoss and (worldBoss.dead or not worldBoss.root.Parent) then
			if worldBoss and worldBoss.dead then
				worldBoss = nil
				applyBossBar()
			end
		end

		if arenaAcc > 0.5 then
			arenaAcc = 0
			-- проверяем вход на арену
			for _, arena in ipairs(arenas) do
				if not arena.mob and now >= arena.respawnAt then
					local center = arena.arenaMarker and arena.arenaMarker.Position or arena.center
					local r = arena.arenaRadius or arena.radius
					for _, pl in ipairs(Players:GetPlayers()) do
						local char = pl.Character
						local rr = char and char:FindFirstChild("HumanoidRootPart")
						local hum = char and char:FindFirstChildOfClass("Humanoid")
						if rr and hum and hum.Health > 0 then
							local d = rr.Position - center
							if Vector3.new(d.X, 0, d.Z).Magnitude <= r then
								spawnBoss(arena, now)
								break
							end
						end
					end
				end
			end
			-- убрать мёртвого активного босса
			if activeBoss and (activeBoss.dead or not activeBoss.root.Parent) then
				activeBoss = nil
				applyBossBar()
			end
		end
	end)
end

-- доступ для автотестов
function BossService.arenasForTest()
	return arenas
end

-- Секретный босс по «Печати призыва»: печать требует 6 мин отката,
-- призывает любого босса в его биоме (даже на 1 игрока).
function BossService.summonBoss(st, bossId)
	local def = GameData.BossById[bossId]
	if not def then return false, "нет такого босса" end
	if def.isWorldBoss then return false, "мирового босса нельзя призвать печатью" end
	local now = os.clock()
	st.data.bossSummonAt = st.data.bossSummonAt or 0
	if now - st.data.bossSummonAt < 360 then
		return false, "Печать ещё не восстановилась (" .. math.ceil(360 - (now - st.data.bossSummonAt)) .. "с)"
	end

	-- ищем свободную арену этого босса
	local arena = nil
	for _, a in ipairs(arenas) do
		if a.def.id == bossId and not a.mob then arena = a break end
	end
	if not arena then
		return false, "арена этого босса занята"
	end
	st.data.bossSummonAt = now
	spawnBoss(arena, now)
	deps.combat.broadcast(Net.Rep.BossEvent, {
		event = "summon", id = def.id, name = def.name,
		by = st.player.DisplayName,
	})
	return true
end

function BossService.getActiveBoss()
	return activeBoss
end

return BossService
"""

SERVER["MagicService"] = """-- Emberfall | MagicService — каст заклинаний, снаряды, зоны, снаряд-визуал.
-- Клиент шлёт только id заклинания; сервер проверяет всё остальное.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local MagicService = {}

local deps
local projectileFolder

function MagicService.setup(d)
	deps = d
	projectileFolder = Instance.new("Folder")
	projectileFolder.Name = "EmberfallProjectiles"
	projectileFolder.Parent = deps.fxFolder
end

local function notifyFail(st, reason)
	local r = deps.remotes:FindFirstChild(Net.Rep.CastFail)
	if r then r:FireClient(st.player, { reason = reason }) end
end

local function elementColor(spell)
	local el = Config.ElementById[spell.element]
	return el and el.color or Color3.fromRGB(200, 200, 255)
end

local function makeProjectileVisual(pos, spell, size)
	local color = elementColor(spell)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(size, size, size)
	p.Color = color
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Position = pos
	p.Parent = projectileFolder
	Debris:AddItem(p, 5)

	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 2
	light.Range = 18
	light.Parent = p

	local trail = Instance.new("Trail")
	trail.Color = ColorSequence.new(color)
	trail.Lifetime = 0.28
	trail.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
	trail.WidthScale = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0) })
	trail.Attachment0 = Instance.new("Attachment")
	trail.Attachment0.Parent = p
	trail.Attachment1 = Instance.new("Attachment")
	trail.Attachment1.Parent = p
	trail.Parent = p

	return p
end

-- визуальная вспышка
local function burst(pos, color, radius, duration)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(1, 1, 1)
	p.Color = color
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Position = pos
	p.Parent = projectileFolder
	local tw = TweenService:Create(p, TweenInfo.new(duration or 0.35, Enum.EasingStyle.Quad), {
		Size = Vector3.new(radius * 2, radius * 2, radius * 2), Transparency = 1,
	})
	tw:Play()
	tw.Completed:Connect(function() p:Destroy() end)
end

-- ============================================================================
-- ОБЩИЕ ПРОВЕРКИ
-- ============================================================================
local function validateCast(st, spellId)
	local spell = GameData.SpellById[spellId]
	if not spell then return nil, "нет такого заклинания" end
	if not st.spells[spellId] then return nil, "заклинание не изучено" end
	if st.level < (spell.reqLevel or 1) then return nil, "нужен уровень " .. spell.reqLevel end

	local c = deps.playerState.cache(st)
	local manaCost = spell.manaCost or 10
	if st.mana < manaCost then return nil, "не хватает маны" end

	local now = os.clock()
	local ready = st.cooldowns[spellId] or 0
	if now < ready then return nil, "откат ещё " .. math.ceil(ready - now) .. "с" end

	local character = st.player.Character
	if not character then return nil, "нет персонажа" end
	local hum = character:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return nil, "нет персонажа" end
	return spell, nil
end

local function applyCooldown(st, spell)
	local c = deps.playerState.cache(st)
	local cd = (spell.cooldown or 1) * (c.cdMult or 1)
	st.cooldowns[spell.id] = os.clock() + cd
end

local function aimPoint(st)
	-- точка прицела клиента: смотрим на mouse.Hit через ремоут клиента
	return st.aimPoint or nil
end

-- ============================================================================
-- НАНЕСЕНИЕ УРОНА ПО ОБЛАСТИ
-- ============================================================================
local function damageMobsInRadius(st, center, radius, spell, opts)
	opts = opts or {}
	local power = deps.playerState.cache(st).powerMult or 1
	local dmg = (spell.damage or 0) * power
	if opts.damageMult then dmg = dmg * opts.damageMult end

	local hitAny = false
	for _, mob in ipairs(deps.mobService.getMobsNear(center, radius)) do
		local d = (mob.root.Position - center).Magnitude
		if d <= radius then
			local falloff = opts.noFalloff and 1 or math.clamp(1 - (d / radius) * 0.45, 0.55, 1)
			deps.combat.damageMob(mob, dmg * falloff, st, {
				lifesteal = spell.lifesteal, kind = "spell",
			})
			if spell.slow then
				-- замедление моба: множитель живёт на самом мобе, не на общем def
				mob.speedMult = spell.slow.mult
				mob.slowToken = (mob.slowToken or 0) + 1
				local token = mob.slowToken
				task.delay(spell.slow.duration, function()
					if mob.slowToken == token then mob.speedMult = 1 end
				end)
			end
			hitAny = true
		end
	end

	-- урон по игрокам не наносим (дружелюбный огонь выключен)

	burst(center, elementColor(spell), radius, 0.45)
	return hitAny
end

-- урон боссу, если он в зоне
local function damageBossIfInRange(st, center, radius, spell, mult)
	local bs = deps.bossService
	local boss = bs and bs.getActiveBoss()
	if not boss or boss.dead then return false end
	if (boss.root.Position - center).Magnitude > radius + 5 then return false end
	local power = deps.playerState.cache(st).powerMult or 1
	deps.combat.damageMob(boss, (spell.damage or 0) * power * (mult or 1), st, {
		lifesteal = spell.lifesteal, kind = "spell",
	})
	return true
end

-- ============================================================================
-- СПОСОБНОСТИ
-- ============================================================================
local function castProjectile(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then notifyFail(st, "нет персонажа") return false end

	local origin = root.Position + Vector3.new(0, 2.2, 0) + root.CFrame.LookVector * 2
	local target = aimPoint(st)
	local dir
	if target then
		dir = (target - origin)
		if dir.Magnitude < 1 then
			dir = root.CFrame.LookVector
		else
			dir = dir.Unit
		end
	else
		dir = root.CFrame.LookVector
	end

	local maxRange = spell.range or 150
	local speed = spell.speed or 100
	local radius = spell.radius or 3

	local proj = makeProjectileVisual(origin, spell, math.clamp(radius * 0.7, 1, 4))
	local traveled = 0
	local done = false

	local function explode(pos)
		deps.combat.broadcast(Net.Rep.CastFx, { kind = "boom", pos = pos, color = elementColor(spell), radius = radius * 2.2 })
		damageMobsInRadius(st, pos, radius + 1.5, spell)
		damageBossIfInRange(st, pos, radius + 3, spell)
		if proj.Parent then proj:Destroy() end
	end

	local conn
	conn = game:GetService("RunService").Heartbeat:Connect(function(dt)
		if done then conn:Disconnect() return end
		if not proj.Parent then done = true conn:Disconnect() return end
		local step = speed * dt
		traveled = traveled + step
		local newPos = proj.Position + dir * step
		proj.Position = newPos

		-- попадание в мобов
		for _, mob in ipairs(deps.mobService.getMobsNear(newPos, radius + 1.5 + 6)) do
			if not mob.dead and (mob.root.Position - newPos).Magnitude < radius + 2.0 then
				conn:Disconnect()
				explode(newPos)
				return
			end
		end

		-- попадание в босса
		local boss = deps.bossService and deps.bossService.getActiveBoss()
		if boss and not boss.dead and (boss.root.Position - newPos).Magnitude < radius + 5 then
			conn:Disconnect()
			explode(newPos)
			return
		end

		-- попадание в землю
		local gy = deps.mobService.groundY(newPos)
		if gy and newPos.Y <= gy + 0.5 then
			conn:Disconnect()
			explode(Vector3.new(newPos.X, gy + 0.5, newPos.Z))
			return
		end

		if traveled >= maxRange then
			conn:Disconnect()
			explode(newPos)
		end
	end)

	return true
end

local function castArea(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	task.delay(spell.castTime or 0.3, function()
		if not character.Parent then return end
		local center = root.Position
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "nova", pos = center, color = elementColor(spell), radius = spell.radius or 20,
		})
		damageMobsInRadius(st, center, spell.radius or 20, spell)
		damageBossIfInRange(st, center, spell.radius or 20, spell)
		if spell.lifesteal then
			deps.combat.healPlayer(st, (spell.damage or 0) * spell.lifesteal, true)
		end
	end)
	return true
end

local function castMeteor(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local target = aimPoint(st) or (root.Position + root.CFrame.LookVector * 40)
	local maxRange = spell.range or 200
	local origin = root.Position
	local delta = target - origin
	if delta.Magnitude > maxRange then
		delta = delta.Unit * maxRange
	end
	local landing = origin + Vector3.new(delta.X, 0, delta.Z)
	local gy = deps.mobService.groundY(landing)
	landing = Vector3.new(landing.X, gy or landing.Y, landing.Z)

	local color = elementColor(spell)

	-- круг предупреждения
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "meteor", pos = landing, color = color,
		radius = spell.radius or 15, delay = spell.fallTime or 0.85,
	})

	-- падающий снаряд
	local fall = Instance.new("Part")
	fall.Shape = Enum.PartType.Ball
	fall.Size = Vector3.new(spell.radius or 15, spell.radius or 15, spell.radius or 15)
	fall.Size = Vector3.new(6, 6, 6)
	fall.Color = color
	fall.Material = Enum.Material.Neon
	fall.Anchored = true
	fall.CanCollide = false
	fall.CanQuery = false
	fall.Position = landing + Vector3.new(0, 150, 0)
	fall.Parent = projectileFolder
	Debris:AddItem(fall, 5)

	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 3
	light.Range = 40
	light.Parent = fall

	local tw = TweenService:Create(fall, TweenInfo.new(spell.fallTime or 0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		Position = landing,
	})
	tw:Play()
	tw.Completed:Connect(function()
		fall:Destroy()
		damageMobsInRadius(st, landing, spell.radius or 15, spell)
		damageBossIfInRange(st, landing, spell.radius or 15, spell)
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "boom", pos = landing, color = color, radius = (spell.radius or 15) * 3,
		})
	end)
	return true
end

local function castDash(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local hum = character:FindFirstChildOfClass("Humanoid")
	local dir = root.CFrame.LookVector
	local dist = spell.distance or 30
	local moved = 0
	local hitSet = {}

	local before = root.Position
	local power = deps.playerState.cache(st).powerMult or 1
	for _, mob in ipairs(deps.mobService.getMobsNear(before, dist + (spell.radius or 7))) do
		-- проверяем, что моб примерно на линии рывка
		local toMob = mob.root.Position - before
		local along = toMob:Dot(dir)
		local perp = (toMob - dir * along).Magnitude
		if along > 0 and along < dist + 6 and perp < (spell.radius or 7) then
			deps.combat.damageMob(mob, (spell.damage or 20) * power, st, { kind = "spell" })
		end
	end

	root.AssemblyLinearVelocity = dir * 95 + Vector3.new(0, 10, 0)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "dash", pos = before, color = elementColor(spell),
	})
	return true
end

local function castBuff(st, spell)
	local now = os.clock()
	table.insert(st.buffs, {
		type = spell.buffType or "power",
		value = spell.buffValue or 0,
		expires = now + (spell.duration or 5),
	})
	deps.playerState.recompute(st, st.player.Character)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "buff", pos = st.player.Character:GetPivot().Position,
		color = elementColor(spell),
	})
	return true
end

local function castHeal(st, spell)
	deps.combat.healPlayer(st, spell.healAmount or 40, false)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "heal", pos = st.player.Character:GetPivot().Position, color = elementColor(spell),
	})
	return true
end

local function castStorm(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local center = root.Position + root.CFrame.LookVector * 25
	local gy = deps.mobService.groundY(center)
	center = Vector3.new(center.X, gy or center.Y, center.Z)
	local strikes = spell.strikes or 5
	for i = 1, strikes do
		task.delay((i - 1) * (spell.duration / strikes), function()
			if not character.Parent then return end
			local point = center + Vector3.new(math.random(-8, 8), 0, math.random(-8, 8))
			local pgy = deps.mobService.groundY(point)
			point = Vector3.new(point.X, pgy or point.Y, point.Z)
			deps.combat.broadcast(Net.Rep.CastFx, {
				kind = "bolt", pos = point, color = elementColor(spell),
			})
			damageMobsInRadius(st, point, spell.radius or 20, spell, { noFalloff = true })
			damageBossIfInRange(st, point, spell.radius or 20, spell)
		end)
	end
	return true
end

local function castChain(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local targets = deps.mobService.getMobsNear(root.Position, spell.range or 150)
	table.sort(targets, function(a, b)
		return (a.root.Position - root.Position).Magnitude < (b.root.Position - root.Position).Magnitude
	end)
	local maxN = spell.chainTargets or 3
	local lastPos = root.Position
	for i = 1, math.min(maxN, #targets) do
		local mob = targets[i]
		if mob.dead then break end
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "chain", from = lastPos, to = mob.root.Position, color = elementColor(spell),
		})
		local falloff = 1 - (i - 1) * 0.25
		deps.combat.damageMob(mob, (spell.damage or 30) * falloff * (deps.playerState.cache(st).powerMult or 1), st, { kind = "spell" })
		lastPos = mob.root.Position
	end
	damageBossIfInRange(st, lastPos, spell.radius or 40, spell)
	return true
end

-- ============================================================================
-- ПУБЛИЧНЫЙ КАСТ
-- ============================================================================
function MagicService.cast(st, spellId, aim)
	st.aimPoint = aim
	local spell, err = validateCast(st, spellId)
	if not spell then
		notifyFail(st, err)
		return false
	end

	st.mana = st.mana - (spell.manaCost or 0)
	st.lastCombat = os.clock()
	applyCooldown(st, spell)
	deps.playerState.sendVitals(st, deps.remotes)

	-- лёгкая анимация каста
	local character = st.player.Character
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	if hum then
		local animator = hum:FindFirstChildOfClass("Animator")
	end

	local kind = spell.kind
	local ok = false
	if kind == "projectile" then
		ok = castProjectile(st, spell)
	elseif kind == "area" then
		ok = castArea(st, spell)
	elseif kind == "meteor" then
		ok = castMeteor(st, spell)
	elseif kind == "dash" then
		ok = castDash(st, spell)
	elseif kind == "buff" then
		ok = castBuff(st, spell)
	elseif kind == "heal" then
		ok = castHeal(st, spell)
	elseif kind == "storm" then
		ok = castStorm(st, spell)
	elseif kind == "chain" then
		ok = castChain(st, spell)
	end

	if not ok then
		-- возвращаем ману и откат
		st.mana = st.mana + (spell.manaCost or 0)
		st.cooldowns[spell.id] = 0
		deps.playerState.sendVitals(st, deps.remotes)
	end
	return ok
end

function MagicService.cooldownRemaining(st, spellId)
	local ready = st.cooldowns[spellId] or 0
	return math.max(0, ready - os.clock())
end

return MagicService
"""

SERVER["QuestService"] = """-- Emberfall | QuestService — прогресс, сдача, награды.
-- Слушает убийства (через Combat hooks), смену зоны, инвентарь и флаги.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Quests = require(Shared:WaitForChild("Quests"))
local NPCData = require(Shared:WaitForChild("NPCData"))
local Net = require(Shared:WaitForChild("Net"))

local QuestService = {}

local deps

function QuestService.setup(d)
	deps = d
end

-- ============================================================================
-- СЕРИАЛИЗАЦИЯ ДЛЯ КЛИЕНТА
-- ============================================================================
function QuestService.progressOf(st, quest)
	local entry = st.quests[quest.id]
	local out = {}
	for i, obj in ipairs(quest.objectives) do
		local have = 0
		if entry and entry.counters and entry.counters[i] then
			have = entry.counters[i]
		end
		if obj.type == "collect" then
			have = math.max(have, math.min(QuestService.countFor(st, obj), obj.count))
		end
		table.insert(out, {
			text = obj.text or obj.type,
			have = math.min(have, obj.count),
			need = obj.count,
		})
	end
	return out
end

function QuestService.countFor(st, obj)
	if obj.type == "collect" then
		return deps.playerState.countOf(st, obj.target)
	elseif obj.type == "flag" then
		return st.data[obj.target] and 1 or 0
	elseif obj.type == "level" then
		return st.level
	end
	return 0
end

function QuestService.isComplete(st, quest)
	for i, obj in ipairs(quest.objectives) do
		local entry = st.quests[quest.id]
		local have = entry and entry.counters and entry.counters[i] or 0
		if obj.type == "collect" then
			have = math.max(have, QuestService.countFor(st, obj))
		elseif obj.type == "flag" or obj.type == "level" then
			have = QuestService.countFor(st, obj)
		end
		if have < obj.count then return false end
	end
	return true
end

local function serialize(st)
	local list = {}
	for _, quest in ipairs(Quests.List) do
		local entry = st.quests[quest.id]
		if entry then
			table.insert(list, {
				id = quest.id,
				name = quest.name,
				desc = quest.desc,
				giver = quest.giver,
				giverName = (NPCData.ByKey[quest.giver] or {}).name or quest.giver,
				state = entry.state,
				objectives = QuestService.progressOf(st, quest),
				rewards = {
					xp = quest.rewards.xp or 0,
					coins = quest.rewards.coins or 0,
					items = quest.rewards.items or {},
					statPoints = quest.rewards.statPoints or 0,
				},
			})
		end
	end
	return list
end

function QuestService.sendQuests(st)
	local r = deps.remotes:FindFirstChild(Net.Rep.Quests)
	if r then r:FireClient(st.player, serialize(st)) end
end

-- ============================================================================
-- ДОСТУПНОСТЬ
-- ============================================================================
function QuestService.prereqDone(st, quest)
	for _, pid in ipairs(quest.prereq or {}) do
		if not st.questsDone[pid] then return false end
	end
	return true
end

function QuestService.canAccept(st, quest)
	if st.quests[quest.id] then return false, "уже взят" end
	if st.questsDone[quest.id] then return false, "уже выполнен" end
	if st.level < (quest.minLevel or 1) then return false, "нужен уровень " .. quest.minLevel end
	if not QuestService.prereqDone(st, quest) then return false, "нужно сначала выполнить предыдущее задание" end
	return true
end

function QuestService.availableFor(st, npcKey)
	local out = {}
	for _, quest in ipairs(Quests.forNpc(npcKey)) do
		if QuestService.canAccept(st, quest) then table.insert(out, quest) end
	end
	return out
end

-- ============================================================================
-- ПРИНЯТЬ / СДАТЬ / БРОСИТЬ
-- ============================================================================
function QuestService.accept(st, questId)
	local quest = Quests.ById[questId]
	if not quest then return false, "нет такого задания" end
	local ok, err = QuestService.canAccept(st, quest)
	if not ok then return false, err end

	st.quests[questId] = { state = "active", counters = {} }
	for i, obj in ipairs(quest.objectives) do
		if obj.type == "collect" then
			st.quests[questId].counters[i] = math.min(QuestService.countFor(st, obj), obj.count)
		else
			st.quests[questId].counters[i] = 0
		end
	end

	deps.playerState.notify(st, deps.remotes, "Задание принято: " .. quest.name, "quest")
	QuestService.checkAll(st)
	QuestService.sendQuests(st)
	return true
end

function QuestService.claim(st, questId)
	local quest = Quests.ById[questId]
	local entry = st.quests[questId]
	if not quest or not entry then return false, "задание не взято" end
	if entry.state ~= "ready" then return false, "задание не выполнено" end

	-- расход материалов для collect-заданий
	for _, obj in ipairs(quest.objectives) do
		if obj.type == "collect" then
			local have = deps.playerState.countOf(st, obj.target)
			if have < obj.count then return false, "не хватает предметов" end
		end
	end
	for _, obj in ipairs(quest.objectives) do
		if obj.type == "collect" then
			local need = obj.count
			for uid, inv in pairs(st.inventory) do
				if need <= 0 then break end
				if inv.id == obj.target then
					local take = math.min(need, inv.count or 1)
					deps.playerState.removeItem(st, uid, take)
					need = need - take
				end
			end
		end
	end

	local rw = quest.rewards
	st.coins = st.coins + (rw.coins or 0)
	if rw.statPoints and rw.statPoints > 0 then
		st.statPoints = st.statPoints + rw.statPoints
	end
	for _, item in ipairs(rw.items or {}) do
		deps.playerState.addItem(st, item.id, item.count or 1)
	end

	st.quests[questId] = nil
	st.questsDone[questId] = true

	deps.playerState.notify(st, deps.remotes, "Задание выполнено: " .. quest.name .. " (+" .. (rw.coins or 0) .. " монет)", "quest_done")
	deps.combat.giveXp(st, rw.xp or 0)

	deps.playerState.sendInventory(st, deps.remotes)
	deps.playerState.sendStats(st, deps.remotes)
	deps.playerState.sendVitals(st, deps.remotes)
	QuestService.sendQuests(st)
	return true
end

function QuestService.abandon(st, questId)
	if st.quests[questId] then
		st.quests[questId] = nil
		deps.playerState.notify(st, deps.remotes, "Задание брошено", "warn")
		QuestService.sendQuests(st)
	end
end

-- ============================================================================
-- ПРОГРЕСС
-- ============================================================================
local function bump(st, quest, index, obj, amount)
	local entry = st.quests[quest.id]
	if not entry or entry.state ~= "active" then return false end
	local cur = entry.counters[index] or 0
	if cur >= obj.count then return false end
	entry.counters[index] = math.min(obj.count, cur + amount)
	return true
end

function QuestService.checkAll(st)
	local changed = false
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest and QuestService.isComplete(st, quest) then
				entry.state = "ready"
				deps.playerState.notify(st, deps.remotes, "Задание готово к сдаче: " .. quest.name, "quest_ready")
				changed = true
			end
		end
	end
	if changed then QuestService.sendQuests(st) end
end

function QuestService.onMobKilled(mobDef, st, zone)
	if not st or not mobDef then return end
	local changed = false
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest then
				for i, obj in ipairs(quest.objectives) do
					if obj.type == "kill" and obj.target == mobDef.id then
						if bump(st, quest, i, obj, 1) then changed = true end
					elseif obj.type == "killZone" then
						if obj.target == "any" or obj.target == mobDef.zone then
							if bump(st, quest, i, obj, 1) then changed = true end
						end
					end
				end
			end
		end
	end
	if changed then QuestService.checkAll(st) end
end

function QuestService.onBossKilled(bossDef, st)
	if not st or not bossDef then return end
	local changed = false
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest then
				for i, obj in ipairs(quest.objectives) do
					if obj.type == "boss" and obj.target == bossDef.id then
						if bump(st, quest, i, obj, 1) then changed = true end
					end
				end
			end
		end
	end
	if changed then QuestService.checkAll(st) end
end

function QuestService.onInventoryChanged(st)
	local changed = false
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest then
				for i, obj in ipairs(quest.objectives) do
					if obj.type == "collect" then
						local have = math.min(deps.playerState.countOf(st, obj.target), obj.count)
						local cur = entry.counters[i] or 0
						if have > cur then
							entry.counters[i] = have
							changed = true
						end
					end
				end
			end
		end
	end
	if changed then QuestService.checkAll(st) end
end

function QuestService.onZoneChanged(st, zoneId)
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest then
				for i, obj in ipairs(quest.objectives) do
					if obj.type == "visit" and obj.target == zoneId then
						bump(st, quest, i, obj, 1)
					end
				end
			end
		end
	end
	QuestService.checkAll(st)
end

-- установка флага (например, "choseElement")
function QuestService.setFlag(st, flag)
	st.data[flag] = true
	local changed = false
	for questId, entry in pairs(st.quests) do
		if entry.state == "active" then
			local quest = Quests.ById[questId]
			if quest then
				for i, obj in ipairs(quest.objectives) do
					if obj.type == "flag" and obj.target == flag then
						if bump(st, quest, i, obj, 1) then changed = true end
					end
				end
			end
		end
	end
	if changed then QuestService.checkAll(st) end
end

return QuestService
"""

SERVER["WorldService"] = """-- Emberfall | WorldService — NPC на маркерах, сундуки, зоны, алтарь стихий, лава.
-- Мир реагирует: подошёл к NPC — открылся диалог, нашёл сундук — лут.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Quests = require(Shared:WaitForChild("Quests"))
local NPCData = require(Shared:WaitForChild("NPCData"))
local Net = require(Shared:WaitForChild("Net"))

local WorldService = {}

local deps
local npcs = {}      -- { model, key, data, marker, prompt }
local chests = {}    -- { body, lid, tag, prompt, lootedBy = {} }
local altars = {}    -- части алтаря для вращения

-- ============================================================================
-- МОДЕЛЬ NPC
-- ============================================================================
local function makePart(name, size, color, material, parent)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function buildNPC(data, position)
	local model = Instance.new("Model")
	model.Name = "NPC_" .. data.key

	local root = makePart("Root", Vector3.new(2, 2, 1), data.color, Enum.Material.SmoothPlastic, model)
	model.PrimaryPart = root
	root.CFrame = CFrame.new(position) * CFrame.Angles(0, math.rad(180), 0)

	local torso = makePart("Torso", Vector3.new(2.1, 2.3, 1.2), data.color, Enum.Material.Fabric, model)
	torso.CFrame = root.CFrame

	local head = makePart("Head", Vector3.new(1.35, 1.35, 1.35), Color3.fromRGB(226, 200, 170), Enum.Material.SmoothPlastic, model)
	head.CFrame = root.CFrame * CFrame.new(0, 1.85, 0)

	-- капюшон/шляпа по роли
	if data.role == "quests" then
		local hood = makePart("Hood", Vector3.new(1.6, 1.1, 1.6), data.color, Enum.Material.Fabric, model)
		hood.CFrame = root.CFrame * CFrame.new(0, 2.35, 0)
	elseif data.role == "shop" then
		local hat = makePart("Hat", Vector3.new(1.9, 0.5, 1.9), Color3.fromRGB(80, 60, 40), Enum.Material.Fabric, model)
		hat.CFrame = root.CFrame * CFrame.new(0, 2.6, 0)
	elseif data.role == "heal" then
		local halo = makePart("Halo", Vector3.new(1.1, 0.15, 1.1), Color3.fromRGB(140, 255, 170), Enum.Material.Neon, model)
		halo.Shape = Enum.PartType.Cylinder
		halo.CFrame = root.CFrame * CFrame.new(0, 3.1, 0) * CFrame.Angles(0, 0, math.rad(90))
	end

	local forHead = root.CFrame * CFrame.new(0, 1.85, 0)
	local leftLeg = makePart("Leg1", Vector3.new(0.7, 2, 0.7), Color3.fromRGB(60, 56, 50), Enum.Material.Fabric, model)
	leftLeg.CFrame = forHead * CFrame.new(-0.55, -2.6, 0)
	local rightLeg = makePart("Leg2", Vector3.new(0.7, 2, 0.7), Color3.fromRGB(60, 56, 50), Enum.Material.Fabric, model)
	rightLeg.CFrame = forHead * CFrame.new(0.55, -2.6, 0)

	local welds = {}
	for _, child in ipairs(model:GetChildren()) do
		if child:IsA("BasePart") and child ~= root then
			local w = Instance.new("WeldConstraint")
			w.Part0 = root
			w.Part1 = child
			w.Parent = child
		end
	end

	-- имя над головой
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 220, 0, 46)
	billboard.StudsOffset = Vector3.new(0, 3.4, 0)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 90
	billboard.Parent = head

	local nameLabel = Instance.new("TextLabel")
	nameLabel.Size = UDim2.new(1, 0, 0.6, 0)
	nameLabel.BackgroundTransparency = 1
	nameLabel.Text = data.name
	nameLabel.TextColor3 = Color3.fromRGB(255, 235, 180)
	nameLabel.TextStrokeTransparency = 0.3
	nameLabel.TextScaled = true
	nameLabel.Font = Enum.Font.GothamBold
	nameLabel.Parent = billboard

	local roleLabel = Instance.new("TextLabel")
	roleLabel.Size = UDim2.new(1, 0, 0.4, 0)
	roleLabel.Position = UDim2.new(0, 0, 0.6, 0)
	roleLabel.BackgroundTransparency = 1
	roleLabel.Text = data.title or ""
	roleLabel.TextColor3 = Color3.fromRGB(190, 210, 230)
	roleLabel.TextStrokeTransparency = 0.5
	roleLabel.TextScaled = true
	roleLabel.Font = Enum.Font.Gotham
	roleLabel.Parent = billboard

	-- маркер «!» для квестодателей
	local marker = Instance.new("Part")
	marker.Name = "QuestMark"
	marker.Size = Vector3.new(0.9, 0.9, 0.9)
	marker.Shape = Enum.PartType.Ball
	marker.Color = Color3.fromRGB(255, 220, 80)
	marker.Material = Enum.Material.Neon
	marker.Anchored = true
	marker.CanCollide = false
	marker.CanQuery = false
	marker.CFrame = CFrame.new(position + Vector3.new(0, 6.2, 0))
	marker.Parent = model
	local ml = Instance.new("PointLight")
	ml.Color = Color3.fromRGB(255, 220, 80)
	ml.Brightness = 1.2
	ml.Range = 12
	ml.Parent = marker

	return model, marker
end

-- ============================================================================
-- СУНДУКИ
-- ============================================================================
local function setupChest(part)
	local tag = part.Name:gsub("^Chest_Body_", ""):gsub("^Chest_", "")
	local bodyPos = part.Position
	-- ищем связанный сундук по тегу (Chest_Body_X / Chest_Lid_X / Chest_Glow_X)
	return {
		tag = tag,
		body = part,
		lootedBy = {},
	}
end

-- лут из сундука по зоне
local CHEST_LOOT = {
	{ item = "C_HealthPotion", chance = 0.8, min = 1, max = 3 },
	{ item = "C_ManaPotion", chance = 0.7, min = 1, max = 3 },
	{ item = "M_Ore", chance = 0.5, min = 1, max = 3 },
	{ item = "M_Pelt", chance = 0.5, min = 1, max = 2 },
	{ item = "T_EmberCharm", chance = 0.12 },
	{ item = "C_Elixir", chance = 0.15 },
	{ item = "W_Hatchet", chance = 0.08 },
	{ item = "A_Leather", chance = 0.1 },
}

function WorldService.openChest(st, chest)
	local now = os.clock()
	local last = st.lastChest[chest.tag] or 0
	if now - last < Config.ChestCooldown then
		deps.playerState.notify(st, deps.remotes,
			"Сундук пуст. Откроется через " .. math.ceil(Config.ChestCooldown - (now - last)) .. "с", "warn")
		return false
	end
	st.lastChest[chest.tag] = now

	local gained = {}
	for _, entry in ipairs(CHEST_LOOT) do
		if math.random() < entry.chance then
			local n = math.random(entry.min or 1, entry.max or 1)
			deps.playerState.addItem(st, entry.item, n)
			local def = GameData.ItemById[entry.item]
			table.insert(gained, def.name .. (n > 1 and (" x" .. n) or ""))
		end
	end

	-- монеты
	local coins = math.random(25, 140)
	st.coins = st.coins + coins
	table.insert(gained, coins .. " монет")

	-- анимация крышки
	local lid = chest.body.Parent and (chest.body.Parent:FindFirstChild("Chest_Lid_" .. chest.tag)
		or chest.body.Parent:FindFirstChild("Chest_" .. chest.tag .. "_Lid"))
	if lid then
		local base = lid.CFrame
		local tw = TweenService:Create(lid, TweenInfo.new(0.35, Enum.EasingStyle.Back), {
			CFrame = base * CFrame.new(0, 0.35, -0.45) * CFrame.Angles(math.rad(-55), 0, 0),
		})
		tw:Play()
		task.delay(2.2, function()
			if lid.Parent then
				TweenService:Create(lid, TweenInfo.new(0.4), { CFrame = base }):Play()
			end
		end)
	end

	if #gained > 0 then
		deps.playerState.notify(st, deps.remotes, "Сундук: " .. table.concat(gained, ", "), "loot_rare")
	end
	deps.playerState.sendInventory(st, deps.remotes)
	deps.playerState.sendVitals(st, deps.remotes)
	return true
end

-- ============================================================================
-- ДИАЛОГ
-- ============================================================================
function WorldService.openDialog(st, npcKey)
	local data = NPCData.ByKey[npcKey]
	if not data then return false end

	local available = {}
	for _, quest in ipairs(Quests.forNpc(npcKey)) do
		local can, err = deps.questService.canAccept(st, quest)
		if can then
			table.insert(available, {
				id = quest.id, name = quest.name, desc = quest.desc, kind = "available",
				minLevel = quest.minLevel,
			})
		end
	end

	local active = {}
	for questId, entry in pairs(st.quests) do
		local quest = Quests.ById[questId]
		if quest and quest.giver == npcKey then
			table.insert(active, {
				id = questId, name = quest.name, desc = quest.desc,
				state = entry.state,
				objectives = deps.questService.progressOf(st, quest),
				rewards = {
					xp = quest.rewards.xp or 0, coins = quest.rewards.coins or 0,
					items = quest.rewards.items or {}, statPoints = quest.rewards.statPoints or 0,
				},
				kind = entry.state,
			})
		end
	end

	-- ассортимент магазина
	local shop = nil
	if data.role == "shop" then
		shop = {}
		for _, itemId in ipairs(GameData.ShopStock) do
			local it = GameData.ItemById[itemId]
			if it and (it.reqLevel or 1) <= st.level + 4 then
				table.insert(shop, {
					id = itemId, name = it.name, price = it.price or 0,
					rarity = it.rarity, desc = it.desc, type = it.type,
					reqLevel = it.reqLevel or 1,
				})
			end
		end
	end

	local r = deps.remotes:FindFirstChild(Net.Rep.DialogOpen)
	if r then
		r:FireClient(st.player, {
			key = npcKey, name = data.name, title = data.title,
			role = data.role, lines = data.lines,
			available = available, active = active, shop = shop,
		})
	end
	return true
end

-- ============================================================================
-- ЗОНЫ
-- ============================================================================
local ZONE_NAMES = {
	Emberfall = "Пепельная Пристань",
	Gloomwood = "Глумвуд — Мрачный Лес",
	Frostpeak = "Морозные Пики",
	Ashwaste = "Пепельные Пустоши",
	Mirefen = "Топи Мирефен",
	SunkenCoast = "Затонувший Берег",
	Bonefields = "Костяные Поля",
	HollowDeep = "Полая Бездна",
	Highlands = "Дымные Предгорья",
	Archipelago = "Северный Архипелаг",
	SouthIsles = "Южные Острова",
}
WorldService.ZoneNames = ZONE_NAMES

local zoneTriggers = {}

local function pointInTrigger(pos, part)
	local rel = part.CFrame:PointToObjectSpace(pos)
	local half = part.Size / 2
	return math.abs(rel.X) <= half.X and math.abs(rel.Y) <= half.Y and math.abs(rel.Z) <= half.Z
end

local function updateZones()
	for _, pl in ipairs(Players:GetPlayers()) do
		local st = deps.playerState.get(pl)
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if st and root then
			local found = nil
			for _, trig in ipairs(zoneTriggers) do
				if pointInTrigger(root.Position, trig.part) then
					found = trig.id
					break
				end
			end
			found = found or "Emberfall"
			if found ~= st.zone then
				st.zone = found
				local r = deps.remotes:FindFirstChild(Net.Rep.ZoneChanged)
				if r then
					r:FireClient(pl, { id = found, name = ZONE_NAMES[found] or found })
				end
				deps.questService.onZoneChanged(st, found)
			end
		end
	end
end

-- ============================================================================
-- АЛТАРЬ СТИХИЙ
-- ============================================================================
local ALTER_POS
local function buildAltar(position)
	local model = Instance.new("Model")
	model.Name = "ElementAltar"

	local base = makePart("Base", Vector3.new(10, 1.2, 10), Color3.fromRGB(90, 86, 96), Enum.Material.Slate, model)
	base.CFrame = CFrame.new(position)
	base.CanCollide = true

	local column = makePart("Column", Vector3.new(3, 5, 3), Color3.fromRGB(120, 114, 126), Enum.Material.Marble, model)
	column.CFrame = CFrame.new(position + Vector3.new(0, 3, 0))
	column.CanCollide = true

	local crystal = makePart("Crystal", Vector3.new(2.4, 2.4, 2.4), Color3.fromRGB(200, 170, 255), Enum.Material.Neon, model)
	crystal.Shape = Enum.PartType.Ball
	crystal.CFrame = CFrame.new(position + Vector3.new(0, 6.4, 0))
	local light = Instance.new("PointLight")
	light.Color = Color3.fromRGB(200, 170, 255)
	light.Brightness = 2
	light.Range = 26
	light.Parent = crystal

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 260, 0, 40)
	billboard.StudsOffset = Vector3.new(0, 3, 0)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 120
	billboard.Parent = crystal
	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = "АЛТАРЬ СТИХИЙ — коснись, чтобы выбрать"
	label.TextColor3 = Color3.fromRGB(230, 210, 255)
	label.TextStrokeTransparency = 0.4
	label.TextScaled = true
	label.Font = Enum.Font.GothamBold
	label.Parent = billboard

	table.insert(altars, crystal)

	-- подсказка «E» у алтаря
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Коснуться алтаря"
	prompt.ObjectText = "Алтарь стихий"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 16
	prompt.RequiresLineOfSight = false
	prompt.Parent = crystal
	prompt.Triggered:Connect(function(pl)
		local st = deps.playerState.get(pl)
		if not st then return end
		if not st.element then
			local r = deps.remotes:FindFirstChild(Net.Rep.ElementPick)
			if r then r:FireClient(pl, {}) end
		else
			deps.playerState.notify(st, deps.remotes,
				"Твоя стихия: " .. ((Config.ElementById[st.element] or {}).name or "?"), "info")
		end
	end)

	-- физический триггер: часть чуть выше земли
	local trig = makePart("AltarTrigger", Vector3.new(12, 6, 12), Color3.fromRGB(255, 255, 255), Enum.Material.SmoothPlastic, model)
	trig.CFrame = CFrame.new(position + Vector3.new(0, 3, 0))
	trig.Transparency = 1
	trig.CanCollide = false
	trig.CanQuery = false

	local lastTouch = {}
	trig.Touched:Connect(function(hit)
		local character = hit.Parent
		local pl = Players:GetPlayerFromCharacter(character)
		if not pl then return end
		local st = deps.playerState.get(pl)
		if not st then return end
		local now = os.clock()
		if lastTouch[pl.UserId] and now - lastTouch[pl.UserId] < 3 then return end
		lastTouch[pl.UserId] = now
		if not st.element then
			local r = deps.remotes:FindFirstChild(Net.Rep.ElementPick)
			if r then r:FireClient(pl, {}) end
		else
			deps.playerState.notify(st, deps.remotes, "Твоя стихия: " .. (Config.ElementById[st.element] or {}).name, "info")
		end
	end)
end

-- ============================================================================
-- ЛАВА
-- ============================================================================
local function updateLava()
	for _, pl in ipairs(Players:GetPlayers()) do
		local st = deps.playerState.get(pl)
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if st and root and root.Position.Y < 9 and st.zone == "Ashwaste" then
			local now = os.clock()
			st.lastLava = st.lastLava or 0
			if now - st.lastLava > 1.0 then
				st.lastLava = now
				deps.combat.damagePlayer(st, 14, "Лава", { trueDamage = true })
			end
		end
	end
end

-- ============================================================================
-- ПУБЛИЧНЫЙ API
-- ============================================================================
-- список всех NPC (для установки ProximityPrompt)
function WorldService.allNpcs()
	return npcs
end

function WorldService.allChests()
	return chests
end

function WorldService.getNpcNear(pos, radius)
	for _, npc in ipairs(npcs) do
		if npc.model.Parent and (npc.model.PrimaryPart.Position - pos).Magnitude <= radius then
			return npc
		end
	end
	return nil
end

function WorldService.getNpcByKey(key)
	for _, npc in ipairs(npcs) do
		if npc.key == key then return npc end
	end
	return nil
end

function WorldService.getChestNear(pos, radius)
	for _, chest in ipairs(chests) do
		if chest.body.Parent and (chest.body.Position - pos).Magnitude <= radius then
			return chest
		end
	end
	return nil
end

function WorldService.setup(d)
	deps = d
	local gl = Workspace:FindFirstChild("GameLogic")

	-- ---------------- NPC ----------------
	local npcMarkers = {}
	for _, inst in ipairs(Workspace:GetDescendants()) do
		if inst:IsA("BasePart") and inst.Name:match("^NPC_") then
			table.insert(npcMarkers, inst)
		end
	end
	for _, marker in ipairs(npcMarkers) do
		local key = marker.Name:match("^NPC_(.+)$")
		local data = key and NPCData.ByKey[key]
		if data then
			local gy = deps.mobService.groundY(marker.Position)
			local pos = Vector3.new(marker.Position.X, (gy or marker.Position.Y), marker.Position.Z)
			local model, questMark = buildNPC(data, pos)
			model.Parent = deps.worldFolder
			table.insert(npcs, { key = key, data = data, model = model, marker = questMark })
			marker.Transparency = 1
		end
	end
	print(("[Emberfall] NPC размещено: %d"):format(#npcs))

	-- ---------------- СУНДУКИ ----------------
	for _, part in ipairs(Workspace:GetDescendants()) do
		if part:IsA("BasePart") and part.Name:match("^Chest_") then
			table.insert(chests, setupChest(part))
		end
	end
	print(("[Emberfall] Сундуков найдено: %d"):format(#chests))

	-- ---------------- ЗОНЫ ----------------
	for _, part in ipairs(Workspace:GetDescendants()) do
		if part:IsA("BasePart") then
			local id = part.Name:match("^ZoneTrigger_(.+)$")
			if id then
				table.insert(zoneTriggers, { id = id, part = part })
				part.Transparency = 1
			end
		end
	end
	print(("[Emberfall] Зон-триггеров: %d"):format(#zoneTriggers))

	-- ---------------- АЛТАРЬ СТИХИЙ ----------------
	-- ставим на свободном пятачке площади (спавн на 0,158; таунхаусы на 40,158)
	ALTER_POS = Vector3.new(120, 12, 165)
	buildAltar(ALTER_POS)

	-- ---------------- КОСТРЫ-ОГНИ (декор уже есть, добавим свет) ----------------
end

-- обновляем золотой маркер «!» у NPC: горит, если есть что предложить/сдать
local function refreshQuestMarkers()
	for _, npc in ipairs(npcs) do
		local show = false
		local has = false
		for _, pl in ipairs(Players:GetPlayers()) do
			local st = deps.playerState.get(pl)
			if st then
				for _, quest in ipairs(Quests.forNpc(npc.key)) do
					has = true
					local can = deps.questService.canAccept(st, quest)
					if can then show = true end
				end
				for questId, entry in pairs(st.quests) do
					local quest = Quests.ById[questId]
					if quest and quest.giver == npc.key then
						has = true
						if entry.state == "ready" then show = true end
					end
				end
			end
		end
		if npc.marker then
			npc.marker.Transparency = show and 0.05 or 1
			npc.marker.CanQuery = false
		end
		-- NPC без заданий маркер не нужен
		if npc.marker and not has then npc.marker.Transparency = 1 end
	end
end

function WorldService.startLoop()
	local zoneAcc = 0
	local lavaAcc = 0
	local altAcc = 0
	local markAcc = 0
	RunService.Heartbeat:Connect(function(dt)
		zoneAcc = zoneAcc + dt
		lavaAcc = lavaAcc + dt
		altAcc = altAcc + dt

		if zoneAcc > 0.4 then
			zoneAcc = 0
			updateZones()
		end
		if lavaAcc > 0.5 then
			lavaAcc = 0
			updateLava()
		end
		if altAcc > 0.05 then
			altAcc = 0
			local t = os.clock()
			for i, crystal in ipairs(altars) do
				if crystal.Parent then
					crystal.CFrame = CFrame.new(crystal.Position) * CFrame.Angles(0, t * 0.6 + i, math.rad(15))
				end
			end
		end

		markAcc = markAcc + dt
		if markAcc > 1.5 then
			markAcc = 0
			refreshQuestMarkers()
		end
	end)
end

function WorldService.openAltar(st)
	local r = deps.remotes:FindFirstChild(Net.Rep.ElementPick)
	if r then r:FireClient(st.player, {}) end
end

return WorldService
"""

SERVER["InteractService"] = """-- Emberfall | InteractService — ProximityPrompt у NPC и сундуков:
-- подошёл, нажал E — открылся диалог/лут. Никаких клавиш не надо.

local Workspace = game:GetService("Workspace")
local Players = game:GetService("Players")

local InteractService = {}

local deps
local lastPrompt = {}

local function cooldown(pl, ms)
	local now = os.clock()
	if lastPrompt[pl] and now - lastPrompt[pl] < (ms or 0.4) then return true end
	lastPrompt[pl] = now
	return false
end

function InteractService.setup(d)
	deps = d

	-- ---------------------------------- NPC ----------------------------------
	for _, npc in ipairs(deps.worldService.allNpcs()) do
		local root = npc.model.PrimaryPart
		if root then
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = npc.data.role == "shop" and "Торговать" or "Говорить"
			prompt.ObjectText = npc.data.name
			prompt.HoldDuration = 0
			prompt.MaxActivationDistance = 14
			prompt.RequiresLineOfSight = false
			prompt.KeyboardKeyCode = Enum.KeyCode.E
			prompt.GamepadKeyCode = Enum.KeyCode.ButtonX
			prompt.Parent = root
			prompt.Triggered:Connect(function(pl)
				if cooldown(pl, 1.0) then return end
				local st = deps.playerState.get(pl)
				if st then deps.worldService.openDialog(st, npc.key) end
			end)
		end
	end

	-- -------------------------------- СУНДУКИ --------------------------------
	for _, chest in ipairs(deps.worldService.allChests()) do
		local body = chest.body
		if body and body.Parent then
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = "Открыть сундук"
			prompt.ObjectText = "Древний сундук"
			prompt.HoldDuration = 0.5
			prompt.MaxActivationDistance = 10
			prompt.RequiresLineOfSight = false
			prompt.KeyboardKeyCode = Enum.KeyCode.E
			prompt.Parent = body
			prompt.Triggered:Connect(function(pl)
				if cooldown(pl, 0.6) then return end
				local st = deps.playerState.get(pl)
				if st then deps.worldService.openChest(st, chest) end
			end)
		end
	end

	print("[Emberfall] Взаимодействия готовы: NPC + сундуки (клавиша E)")
end

return InteractService
"""

SERVER["Main"] = """-- Emberfall | Main — точка сборки: создаёт Remotes, связывает сервисы,
-- обрабатывает все запросы клиента, тикает регенерацию и комбат-стейт.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")
local StarterPlayer = game:GetService("StarterPlayer")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))
local Quests = require(Shared:WaitForChild("Quests"))
local NPCData = require(Shared:WaitForChild("NPCData"))

local serverScripts = script.Parent
local PlayerState = require(serverScripts:WaitForChild("PlayerState"))
local Combat = require(serverScripts:WaitForChild("Combat"))
local MobService = require(serverScripts:WaitForChild("MobService"))
local BossService = require(serverScripts:WaitForChild("BossService"))
local MagicService = require(serverScripts:WaitForChild("MagicService"))
local QuestService = require(serverScripts:WaitForChild("QuestService"))
local WorldService = require(serverScripts:WaitForChild("WorldService"))
local InteractService = require(serverScripts:WaitForChild("InteractService"))

Players.RespawnTime = Config.RespawnTime

-- ============================================================================
-- REMOTES
-- ============================================================================
local remotes
do
	local existing = ReplicatedStorage:FindFirstChild(Net.FolderName)
	if existing then
		existing:Destroy()
	end
	remotes = Instance.new("Folder")
	remotes.Name = Net.FolderName
	remotes.Parent = ReplicatedStorage

	local function makeRemote(name, class)
		local r = Instance.new(class or "RemoteEvent")
		r.Name = name
		r.Parent = remotes
		return r
	end

	for _, name in pairs(Net.Req) do makeRemote(name, "RemoteEvent") end
	for _, name in pairs(Net.Rep) do makeRemote(name, "RemoteEvent") end
end

-- ============================================================================
-- ПАПКИ МИРА
-- ============================================================================
local worldFolder = Instance.new("Folder")
worldFolder.Name = "EmberfallWorld"
worldFolder.Parent = Workspace

local fxFolder = Instance.new("Folder")
fxFolder.Name = "EmberfallFx"
fxFolder.Parent = Workspace

-- ============================================================================
-- СЕРВИСЫ
-- ============================================================================
local deps = {
	remotes = remotes,
	playerState = PlayerState,
	combat = Combat,
	fxFolder = fxFolder,
	worldFolder = worldFolder,
	questService = QuestService,
}

Combat.setup(deps)
MobService.setup(deps)
BossService.setup(deps)
MagicService.setup(deps)
QuestService.setup(deps)

deps.mobService = MobService
deps.bossService = BossService
deps.magicService = MagicService
WorldService.setup(deps)
InteractService.setup(deps)

Combat.onMobKilled(function(def, st, mob)
	QuestService.onMobKilled(def, st, def.zone)
end)
Combat.onBossKilled(function(def, st)
	-- босс-убийство засчитываем всем игрокам рядом с ареной
	for _, pl in ipairs(Players:GetPlayers()) do
		local pst = PlayerState.get(pl)
		if pst then
			local char = pl.Character
			local root = char and char:FindFirstChild("HumanoidRootPart")
			if root and st and st.player.Character then
				local bossRoot = st.player.Character:FindFirstChild("HumanoidRootPart")
				if bossRoot and (root.Position - bossRoot.Position).Magnitude < 400 then
					QuestService.onBossKilled(def, pst)
					PlayerState.notify(pst, remotes, "Босс повержен: " .. def.name .. "!", "boss")
					PlayerState.sendInventory(pst, remotes)
				end
			end
		end
	end
end)
Combat.onPlayerDied(function(st, source)
	task.delay(Config.RespawnTime, function()
		if st.player.Parent then
			st.dead = false
			st.hp = st.stats_cache.maxHealth or 100
			st.mana = st.stats_cache.maxMana or 100
		end
	end)
end)

-- ============================================================================
-- ПОДКЛЮЧЕНИЕ ИГРОКА
-- ============================================================================
local function setupCharacter(st, character)
	local hum = character:WaitForChild("Humanoid", 10)
	if not hum then return end
	PlayerState.recompute(st, character)
	local cache = PlayerState.cache(st)
	st.hp = cache.maxHealth
	st.mana = cache.maxMana
	st.dead = false
	hum.Health = cache.maxHealth
	hum.WalkSpeed = cache.speed
	hum.JumpPower = 50

	hum.Died:Connect(function()
		if not st.dead then
			st.dead = true
			st.hp = 0
		end
	end)

	-- подсветка выбранной стихии: аура у ног
	if st.element then
		local el = Config.ElementById[st.element]
		if el then
			local root = character:WaitForChild("HumanoidRootPart", 10)
			if root then
				local existing = root:FindFirstChild("ElementAura")
				if existing then existing:Destroy() end
				local light = Instance.new("PointLight")
				light.Name = "ElementAura"
				light.Color = el.color
				light.Brightness = 0.9
				light.Range = 12
				light.Parent = root

				local att = Instance.new("Attachment")
				att.Name = "ElementTrailAtt"
				att.Position = Vector3.new(0, 1.6, 0)
				att.Parent = root
			end
		end
	end
end

local function sendSnapshot(st)
	local c = PlayerState.cache(st)
	local data = {
		level = st.level, xp = st.xp, xpNeed = PlayerState.xpToNext(st),
		hp = st.hp, maxHp = c.maxHealth,
		mana = st.mana, maxMana = c.maxMana,
		stamina = st.stamina, coins = st.coins,
		element = st.element, spells = st.spells, hotbar = st.hotbar,
		stats = st.stats, points = st.statPoints, zone = st.zone,
	}
	local r = remotes:FindFirstChild(Net.Rep.Snapshot)
	if r then r:FireClient(st.player, data) end
	PlayerState.sendInventory(st, remotes)
	PlayerState.sendSpells(st, remotes)
	PlayerState.sendStats(st, remotes)
	PlayerState.sendVitals(st, remotes)
	QuestService.sendQuests(st)
end

-- Мастерская печатей: обмен материалов на «Печать призыва» босса (квесты/боссы)
local SEALS = {
	FrostWraith  = "Печать Ледяного Призрака",
	FrostColossus = "Печать Ледяного Колосса",
	SwampMother  = "Печать Матери Болот",
	CryptWraith  = "Печать Склепного Призрака",
	Ashlord      = "Печать Пепельного Владыки",
	NamelessKing = "Печать Безымянного Короля",
	-- v11: подземелья новых земель
	MarrowTyrant  = "Печать Костяного Тирана",
	StoneWarden   = "Печать Каменного Стража",
	BogHydra      = "Печать Болотной Гидры",
	VolcanoForge  = "Печать Владыки Кузни",
	PirateAdmiral = "Печать Адмирала-Мертвеца",
	WindArchon    = "Печать Ветряного Архипастыря",
	CoralQueen    = "Печать Коралловой Королевы",
	GlacierWyrm   = "Печать Ледяного Змея",
}
PlayerState.Seals = SEALS

STARTER_KIT = {
	{ id = "W_Stick", equip = "weapon" },
	{ id = "A_Rags", equip = "armor" },
	{ id = "C_Bread", count = 3 },
	{ id = "C_HealthPotion", count = 2 },
}

local function giveStarterKit(st)
	if st.data.starterKit then return end
	st.data.starterKit = true
	for _, entry in ipairs(STARTER_KIT) do
		local uid = PlayerState.addItem(st, entry.id, entry.count or 1)
		if uid and entry.equip then st.equip[entry.equip] = uid end
	end
end

Players.PlayerAdded:Connect(function(pl)
	local st = PlayerState.new(pl)
	giveStarterKit(st)
	pl.CharacterAdded:Connect(function(character)
		task.wait(0.2)
		setupCharacter(st, character)
		sendSnapshot(st)
		-- приветствие
		task.wait(1.5)
		PlayerState.notify(st, remotes, "Добро пожаловать в " .. Config.GameName, "info")
		if not st.element then
			task.wait(1.5)
			PlayerState.notify(st, remotes, "Коснись АЛТАРЯ СТИХИЙ у площади, чтобы выбрать магию", "hint")
		end
	end)
	if pl.Character then
		setupCharacter(st, pl.Character)
	end
	task.wait(1)
	sendSnapshot(st)
end)

Players.PlayerRemoving:Connect(function(pl)
	PlayerState.remove(pl)
end)

-- ============================================================================
-- ОБРАБОТКА ЗАПРОСОВ КЛИЕНТА
-- ============================================================================
local function reply(name, pl, payload)
	local r = remotes:FindFirstChild(name)
	if r then r:FireClient(pl, payload) end
end

local req = Net.Req

remotes[req.UseSpell].OnServerEvent:Connect(function(pl, spellId, aim)
	local st = PlayerState.get(pl)
	if not st or st.dead then return end
	if type(spellId) ~= "string" then return end
	local aimVector = nil
	if type(aim) == "Vector3" then
		aimVector = aim
	elseif type(aim) == "table" and typeof(aim.X) == "number" then
		aimVector = Vector3.new(aim.X, aim.Y, aim.Z)
	end
	MagicService.cast(st, spellId, aimVector)
end)

remotes[req.Melee].OnServerEvent:Connect(function(pl)
	local st = PlayerState.get(pl)
	if not st or st.dead then return end
	local character = pl.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local now = os.clock()
	local c = PlayerState.cache(st)
	if now - st.lastMelee < Config.MeleeCooldown * (c.weaponSpeed or 1) then return end
	st.lastMelee = now
	st.lastCombat = now

	local origin = root.Position
	local look = root.CFrame.LookVector
	local damage = (c.weaponDamage or 4) * (c.powerMult or 1)
	local hit = false

	for _, mob in ipairs(MobService.getMobsNear(origin + look * 4, Config.MeleeRange)) do
		local toMob = mob.root.Position - origin
		if toMob:Dot(look) > 0 and toMob.Magnitude < Config.MeleeRange + 3 then
			Combat.damageMob(mob, damage, st, { kind = "melee" })
			hit = true
		end
	end

	-- босс
	local boss = BossService.getActiveBoss()
	if boss and not boss.dead then
		local toBoss = boss.root.Position - origin
		if toBoss.Dot(look) > 0 and toBoss.Magnitude < Config.MeleeRange + 8 then
			Combat.damageMob(boss, damage, st, { kind = "melee" })
			hit = true
		end
	end

	-- визуальный взмах
	local r = remotes:FindFirstChild(Net.Rep.CastFx)
	if r then r:FireAllClients({ kind = "swing", pos = origin + look * 3, color = Color3.fromRGB(255, 240, 200), hit = hit }) end
end)

remotes[req.Equip].OnServerEvent:Connect(function(pl, uid)
	local st = PlayerState.get(pl)
	if not st or type(uid) ~= "string" then return end
	local inv = st.inventory[uid]
	if not inv then return end
	local def = GameData.ItemById[inv.id]
	if not def then return end
	local slot = def.type
	if slot ~= "weapon" and slot ~= "armor" and slot ~= "trinket" then
		PlayerState.notify(st, remotes, "Это нельзя надеть", "warn")
		return
	end
	if (def.reqLevel or 1) > st.level then
		PlayerState.notify(st, remotes, "Нужен уровень " .. def.reqLevel, "warn")
		return
	end
	st.equip[slot] = uid
	PlayerState.recompute(st, pl.Character)
	PlayerState.sendInventory(st, remotes)
	PlayerState.sendVitals(st, remotes)
	PlayerState.notify(st, remotes, "Надето: " .. def.name, "info")
end)

remotes[req.Unequip].OnServerEvent:Connect(function(pl, slot)
	local st = PlayerState.get(pl)
	if not st or type(slot) ~= "string" then return end
	if st.equip[slot] then
		st.equip[slot] = nil
		PlayerState.recompute(st, pl.Character)
		PlayerState.sendInventory(st, remotes)
		PlayerState.sendVitals(st, remotes)
	end
end)

remotes[req.UseItem].OnServerEvent:Connect(function(pl, uid)
	local st = PlayerState.get(pl)
	if not st or type(uid) ~= "string" or st.dead then return end
	local inv = st.inventory[uid]
	if not inv then return end
	local def = GameData.ItemById[inv.id]
	if not def or def.type ~= "consumable" then
		PlayerState.notify(st, remotes, "Это не расходник", "warn")
		return
	end
	local now = os.clock()
	st.lastPotionUse = st.lastPotionUse or 0
	if now - st.lastPotionUse < 0.8 then return end
	st.lastPotionUse = now

	if def.heal then Combat.healPlayer(st, def.heal) end
	if def.mana then Combat.restoreMana(st, def.mana) end
	if def.buffPower then
		table.insert(st.buffs, { type = "power", value = def.buffPower, expires = now + (def.buffDuration or 20) })
		PlayerState.recompute(st, pl.Character)
	end
	PlayerState.removeItem(st, uid, 1)
	PlayerState.sendInventory(st, remotes)
	PlayerState.sendVitals(st, remotes)
	QuestService.onInventoryChanged(st)
	PlayerState.notify(st, remotes, "Использовано: " .. def.name, "info")
end)

remotes[req.SpendStat].OnServerEvent:Connect(function(pl, statId)
	local st = PlayerState.get(pl)
	if not st or type(statId) ~= "string" then return end
	if st.statPoints <= 0 then
		PlayerState.notify(st, remotes, "Нет свободных очков", "warn")
		return
	end
	if st.stats[statId] == nil then return end
	st.stats[statId] = st.stats[statId] + 1
	st.statPoints = st.statPoints - 1
	PlayerState.recompute(st, pl.Character)
	PlayerState.sendStats(st, remotes)
	PlayerState.sendVitals(st, remotes)
end)

remotes[req.LearnSpell].OnServerEvent:Connect(function(pl, spellId)
	local st = PlayerState.get(pl)
	if not st or type(spellId) ~= "string" then return end
	local spell = GameData.SpellById[spellId]
	if not spell then return end
	if st.element ~= spell.element then
		PlayerState.notify(st, remotes, "Это не твоя стихия", "warn")
		return
	end
	if st.level < spell.reqLevel then
		PlayerState.notify(st, remotes, "Нужен уровень " .. spell.reqLevel, "warn")
		return
	end
	st.spells[spellId] = true
	local slot = Combat.firstFreeSlot(st)
	if slot then st.hotbar[slot] = spellId end
	PlayerState.sendSpells(st, remotes)
	PlayerState.notify(st, remotes, "Изучено: " .. spell.name, "spell")
end)

remotes[req.ChooseElement].OnServerEvent:Connect(function(pl, elementId)
	local st = PlayerState.get(pl)
	if not st or st.element then
		PlayerState.notify(st, remotes, "Стихия уже выбрана", "warn")
		return
	end
	local el = Config.ElementById[elementId]
	if not el then return end
	st.element = elementId

	-- выдаём базовое заклинание стихии
	for _, spell in ipairs(GameData.SpellsForElement(elementId)) do
		if (spell.reqLevel or 1) <= st.level then
			st.spells[spell.id] = true
			local slot = Combat.firstFreeSlot(st)
			if slot then st.hotbar[slot] = spell.id end
		end
	end

	QuestService.setFlag(st, "choseElement")
	PlayerState.sendSpells(st, remotes)
	PlayerState.notify(st, remotes, "Стихия выбрана: " .. el.name .. " " .. el.rune, "level")

	-- аура
	if pl.Character then setupCharacter(st, pl.Character) end
end)

-- магазин
remotes[req.ShopBuy].OnServerEvent:Connect(function(pl, itemId)
	local st = PlayerState.get(pl)
	if not st or type(itemId) ~= "string" then return end
	local def = GameData.ItemById[itemId]
	if not def then return end
	local price = def.price or 0
	if price <= 0 then
		PlayerState.notify(st, remotes, "Не продаётся", "warn")
		return
	end
	if (def.reqLevel or 1) > st.level then
		PlayerState.notify(st, remotes, "Требуется уровень " .. def.reqLevel, "warn")
		return
	end
	if st.coins < price then
		PlayerState.notify(st, remotes, "Не хватает монет", "warn")
		return
	end
	local uid, err = PlayerState.addItem(st, itemId, 1)
	if not uid then
		PlayerState.notify(st, remotes, err or "Ошибка", "warn")
		return
	end
	st.coins = st.coins - price
	PlayerState.sendInventory(st, remotes)
	PlayerState.sendVitals(st, remotes)
	PlayerState.notify(st, remotes, "Куплено: " .. def.name, "info")
end)

-- лечение у лекаря (40 монет)
local HEAL_PRICE = 40
-- призыв босса по печати
remotes[req.BossSummon].OnServerEvent:Connect(function(pl, bossId)
	local st = PlayerState.get(pl)
	if not st or type(bossId) ~= "string" then return end
	local ok, err = BossService.summonBoss(st, bossId)
	if ok then
		PlayerState.notify(st, remotes, "Печать сработала! Босс вызван.", "boss")
	else
		PlayerState.notify(st, remotes, "✖ " .. (err or "не удалось"), "warn")
	end
end)

remotes[req.Heal].OnServerEvent:Connect(function(pl)
	local st = PlayerState.get(pl)
	if not st then return end
	local c = PlayerState.cache(st)
	if st.hp >= c.maxHealth then
		PlayerState.notify(st, remotes, "Ты и так цел", "info")
		return
	end
	if st.coins < HEAL_PRICE then
		PlayerState.notify(st, remotes, "Нужно " .. HEAL_PRICE .. " монет", "warn")
		return
	end
	st.coins = st.coins - HEAL_PRICE
	Combat.healPlayer(st, c.maxHealth)
	PlayerState.notify(st, remotes, "Раны обработаны (-" .. HEAL_PRICE .. ")", "info")
	PlayerState.sendVitals(st, remotes)
end)

remotes[req.ShopSell].OnServerEvent:Connect(function(pl, uid)
	local st = PlayerState.get(pl)
	if not st or type(uid) ~= "string" then return end
	local inv = st.inventory[uid]
	if not inv then return end
	local def = GameData.ItemById[inv.id]
	if not def then return end
	local mult = GameData.SellableTypes[def.type] or 0.3
	local value = math.max(1, math.floor((def.price or 10) * mult))
	PlayerState.removeItem(st, uid, 1)
	st.coins = st.coins + value
	PlayerState.sendInventory(st, remotes)
	PlayerState.sendVitals(st, remotes)
	PlayerState.notify(st, remotes, "Продано: " .. def.name .. " (+" .. value .. ")", "info")
end)

-- квесты
remotes[req.QuestAccept].OnServerEvent:Connect(function(pl, questId)
	local st = PlayerState.get(pl)
	if not st or type(questId) ~= "string" then return end
	local ok, err = QuestService.accept(st, questId)
	if not ok then PlayerState.notify(st, remotes, err or "Нельзя взять", "warn") end
end)

remotes[req.QuestClaim].OnServerEvent:Connect(function(pl, questId)
	local st = PlayerState.get(pl)
	if not st or type(questId) ~= "string" then return end
	local ok, err = QuestService.claim(st, questId)
	if not ok then PlayerState.notify(st, remotes, err or "Нельзя сдать", "warn") end
end)

remotes[req.QuestAbandon].OnServerEvent:Connect(function(pl, questId)
	local st = PlayerState.get(pl)
	if not st or type(questId) ~= "string" then return end
	QuestService.abandon(st, questId)
end)

-- диалоги
remotes[req.Dialog].OnServerEvent:Connect(function(pl, npcKey)
	local st = PlayerState.get(pl)
	if not st or type(npcKey) ~= "string" then return end
	local character = pl.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local npc = WorldService.getNpcByKey(npcKey)
	if not npc then return end
	if (npc.model.PrimaryPart.Position - root.Position).Magnitude > 26 then
		PlayerState.notify(st, remotes, "Слишком далеко", "warn")
		return
	end
	WorldService.openDialog(st, npcKey)
end)

remotes[req.Ping].OnServerEvent:Connect(function(pl, t)
	reply(Net.Rep.Ping, pl, t)
end)

-- ============================================================================
-- РЕГЕНЕРАЦИЯ / ТИКИ
-- ============================================================================
local vitalsAcc = 0
RunService.Heartbeat:Connect(function(dt)
	local now = os.clock()
	vitalsAcc = vitalsAcc + dt

	local needVitals = {}
	for _, pl in ipairs(Players:GetPlayers()) do
		local st = PlayerState.get(pl)
		if st and not st.dead then
			local c = PlayerState.cache(st)
			local character = pl.Character
			local hum = character and character:FindFirstChildOfClass("Humanoid")
			if hum and hum.Health > 0 then
				-- мана
				if st.mana < c.maxMana then
					st.mana = math.min(c.maxMana, st.mana + Config.ManaRegenPerSec * dt)
				end
				-- стамина
				st.stamina = math.min(Config.StaminaMax, st.stamina + Config.StaminaRegen * dt)
				-- здоровье вне боя
				if now - st.lastCombat > Config.OutOfCombatTime and st.hp < c.maxHealth then
					st.hp = math.min(c.maxHealth, st.hp + Config.HealthRegenOutOfCombatPerSec * dt)
					hum.Health = st.hp
				end
				-- чистим протухшие баффы
				local dirty = false
				for i = #st.buffs, 1, -1 do
					if (st.buffs[i].expires or 0) <= now then
						table.remove(st.buffs, i)
						dirty = true
					end
				end
				if dirty then PlayerState.recompute(st, character) end
				-- синхронизируем hp в состоянии, если урон пришёл не через Combat (падение и т.п.)
				if math.abs(hum.Health - st.hp) > 1.5 then
					if hum.Health < st.hp then st.hp = hum.Health end
				end
			end
		end
	end

	if vitalsAcc > 0.2 then
		vitalsAcc = 0
		for _, pl in ipairs(Players:GetPlayers()) do
			local st = PlayerState.get(pl)
			if st then PlayerState.sendVitals(st, remotes) end
		end
	end
end)

-- ============================================================================
-- ЗАПУСК
-- ============================================================================
MobService.start()
MobService.startLoop()
BossService.startLoop()
WorldService.startLoop()

print("[Emberfall] v8 — магия, мобы, боссы, прокачка и квесты активны")
"""

CLIENT = {}
CLIENT["UIKit"] = """-- Emberfall | UIKit — крошечная библиотека для сборки интерфейса кодом.
local UIKit = {}

function UIKit.create(class, props, parent)
	local inst = Instance.new(class)
	for k, v in pairs(props or {}) do
		if k ~= "Parent" then
			inst[k] = v
		end
	end
	if parent then inst.Parent = parent end
	return inst
end

function UIKit.corner(inst, radius)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius or 8)
	c.Parent = inst
	return c
end

function UIKit.stroke(inst, color, thickness, transparency)
	local s = Instance.new("UIStroke")
	s.Color = color or Color3.fromRGB(120, 100, 60)
	s.Thickness = thickness or 1
	s.Transparency = transparency or 0
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = inst
	return s
end

function UIKit.padding(inst, p)
	local u = Instance.new("UIPadding")
	u.PaddingLeft = UDim.new(0, p)
	u.PaddingRight = UDim.new(0, p)
	u.PaddingTop = UDim.new(0, p)
	u.PaddingBottom = UDim.new(0, p)
	u.Parent = inst
	return u
end

function UIKit.gradient(inst, c1, c2, rotation)
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(c1, c2)
	g.Rotation = rotation or 90
	g.Parent = inst
	return g
end

function UIKit.frame(parent, size, pos, color, radius, transparency)
	local f = UIKit.create("Frame", {
		Size = size,
		Position = pos or UDim2.new(0, 0, 0, 0),
		BackgroundColor3 = color or Color3.fromRGB(18, 18, 24),
		BackgroundTransparency = transparency or 0,
		BorderSizePixel = 0,
		ClipsDescendants = false,
	}, parent)
	if radius then UIKit.corner(f, radius) end
	return f
end

function UIKit.label(parent, text, size, pos, textSize, color, font)
	local l = UIKit.create("TextLabel", {
		Size = size,
		Position = pos or UDim2.new(0, 0, 0, 0),
		BackgroundTransparency = 1,
		Text = text,
		TextSize = textSize or 16,
		TextColor3 = color or Color3.fromRGB(240, 235, 220),
		Font = font or Enum.Font.GothamMedium,
		TextXAlignment = Enum.TextXAlignment.Left,
		RichText = true,
	}, parent)
	return l
end

function UIKit.button(parent, text, size, pos, color, callback)
	local b = UIKit.create("TextButton", {
		Size = size,
		Position = pos,
		BackgroundColor3 = color or Color3.fromRGB(70, 58, 36),
		BorderSizePixel = 0,
		Text = text,
		TextColor3 = Color3.fromRGB(245, 238, 220),
		Font = Enum.Font.GothamBold,
		TextSize = 16,
		AutoButtonColor = true,
	}, parent)
	UIKit.corner(b, 6)
	UIKit.stroke(b, Color3.fromRGB(160, 132, 70), 1, 0.35)
	b.MouseButton1Click:Connect(function()
		if callback then callback() end
	end)
	return b
end

-- Полоска: возвращает { frame, fill, setRatio(0..1), setColor }
function UIKit.bar(parent, size, pos, color, bgColor)
	local back = UIKit.frame(parent, size, pos, bgColor or Color3.fromRGB(30, 30, 38), 6)
	back.ClipsDescendants = true
	back.Name = "BarBg"
	local fill = UIKit.create("Frame", {
		Size = UDim2.new(1, 0, 1, 0),
		BackgroundColor3 = color,
		BorderSizePixel = 0,
	}, back)
	UIKit.corner(fill, 6)
	UIKit.gradient(fill, color:Lerp(Color3.new(1, 1, 1), 0.25), color:Lerp(Color3.new(0, 0, 0), 0.2), 0)
	return {
		frame = back,
		fill = fill,
		setRatio = function(r)
			r = math.clamp(r or 0, 0, 1)
			fill.Size = UDim2.new(r, 0, 1, 0)
		end,
		setColor = function(c)
			fill.BackgroundColor3 = c
		end,
	}
end

return UIKit
"""

CLIENT["HUD"] = """-- Emberfall | HUD — здоровье, мана, стамина, уровень, опыт, монеты, зона,
-- цифры урона, полоса босса, уведомления, прицел.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local HUD = {}

local function req(name)
	return ReplicatedStorage:WaitForChild("Remotes"):WaitForChild(name)
end

local UIKit = require(script.Parent:WaitForChild("UIKit"))
local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))
local GameData = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("GameData"))

local gui
local ui = {}
local state = {
	hp = 100, maxHp = 100, mana = 100, maxMana = 100,
	stamina = 100, maxStamina = 100,
	level = 1, xp = 0, xpNeed = 100, coins = 0,
	zone = "Пепельная Пристань",
}
HUD.state = state

-- ============================================================================
-- ПОСТРОЕНИЕ
-- ============================================================================
local function build()
	gui = Instance.new("ScreenGui")
	gui.Name = "EmberfallHUD"
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 5
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = playerGui

	-- --------------------------- левый нижний блок ---------------------------
	local statsPanel = UIKit.frame(gui, UDim2.new(0, 330, 0, 118), UDim2.new(0, 18, 1, -136),
		Color3.fromRGB(14, 14, 20), 10, 0.25)
	ui.statsStroke = UIKit.stroke(statsPanel, Color3.fromRGB(150, 124, 66), 1, 0.4)
	ui.statsPanel = statsPanel

	-- уровень
	local lvlCircle = UIKit.frame(statsPanel, UDim2.new(0, 56, 0, 56), UDim2.new(0, 8, 0, -16),
		Color3.fromRGB(40, 34, 48), 28)
	UIKit.stroke(lvlCircle, Color3.fromRGB(220, 186, 110), 2, 0.1)
	ui.levelLabel = UIKit.create("TextLabel", {
		Size = UDim2.new(1, 0, 0.55, 0), Position = UDim2.new(0, 0, 0.1, 0),
		BackgroundTransparency = 1, Text = "1",
		TextColor3 = Color3.fromRGB(255, 230, 160), Font = Enum.Font.GothamBlack, TextSize = 24,
	}, lvlCircle)
	local lvlTag = UIKit.label(lvlCircle, "УР.", UDim2.new(1, 0, 0.3, 0), UDim2.new(0, 0, 0.62, 0), 10,
		Color3.fromRGB(180, 170, 150))
	lvlTag.TextXAlignment = Enum.TextXAlignment.Center

	-- полоски
	local barX = 72
	local barW = 246
	ui.hpBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 16), UDim2.new(0, barX, 0, 6),
		Color3.fromRGB(214, 62, 62))
	ui.hpText = UIKit.label(statsPanel, "100 / 100", UDim2.new(0, barW, 0, 14), UDim2.new(0, barX + 2, 0, 6),
		11, Color3.fromRGB(255, 240, 240), Enum.Font.GothamBold)
	ui.hpText.TextXAlignment = Enum.TextXAlignment.Center

	ui.manaBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 14), UDim2.new(0, barX, 0, 28),
		Color3.fromRGB(80, 140, 240))
	ui.manaText = UIKit.label(statsPanel, "100 / 100", UDim2.new(0, barW, 0, 12), UDim2.new(0, barX + 2, 0, 28),
		10, Color3.fromRGB(230, 240, 255), Enum.Font.GothamBold)
	ui.manaText.TextXAlignment = Enum.TextXAlignment.Center

	ui.staminaBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 10), UDim2.new(0, barX, 0, 46),
		Color3.fromRGB(120, 200, 90))

	ui.xpBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 8), UDim2.new(0, barX, 0, 60),
		Color3.fromRGB(216, 176, 74))
	ui.xpText = UIKit.label(statsPanel, "Опыт 0 / 100", UDim2.new(0, barW, 0, 14), UDim2.new(0, barX, 0, 70),
		10, Color3.fromRGB(230, 212, 160))

	-- монеты
	ui.coinsLabel = UIKit.label(statsPanel, "◈ 0", UDim2.new(0, 150, 0, 18), UDim2.new(0, barX, 0, 88),
		15, Color3.fromRGB(255, 214, 120), Enum.Font.GothamBold)

	-- имя персонажа
	ui.nameLabel = UIKit.label(statsPanel, player.DisplayName, UDim2.new(0, 150, 0, 18),
		UDim2.new(0, barX + 155, 0, 88), 13, Color3.fromRGB(200, 196, 186), Enum.Font.GothamMedium)
	ui.nameLabel.TextXAlignment = Enum.TextXAlignment.Right

	-- --------------------------- зона (верх центр) ---------------------------
	local zoneBox = UIKit.frame(gui, UDim2.new(0, 300, 0, 40), UDim2.new(0.5, -150, 0, 16),
		Color3.fromRGB(12, 12, 18), 8, 0.45)
	UIKit.stroke(zoneBox, Color3.fromRGB(150, 124, 66), 1, 0.5)
	ui.zoneLabel = UIKit.label(zoneBox, "Пепельная Пристань", UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0),
		17, Color3.fromRGB(240, 226, 190), Enum.Font.GothamBold)
	ui.zoneLabel.TextXAlignment = Enum.TextXAlignment.Center

	-- --------------------------- прицел ---------------------------
	local cross = UIKit.frame(gui, UDim2.new(0, 8, 0, 8), UDim2.new(0.5, -4, 0.5, -4),
		Color3.fromRGB(255, 255, 255), 4, 0.55)
	ui.cross = cross

	-- --------------------------- полоса босса ---------------------------
	local bossFrame = UIKit.frame(gui, UDim2.new(0, 620, 0, 76), UDim2.new(0.5, -310, 0, 76),
		Color3.fromRGB(12, 10, 16), 8, 0.15)
	UIKit.stroke(bossFrame, Color3.fromRGB(190, 80, 240), 2, 0.15)
	bossFrame.Visible = false
	ui.bossFrame = bossFrame
	ui.bossName = UIKit.label(bossFrame, "БОСС", UDim2.new(1, -24, 0, 22), UDim2.new(0, 12, 0, 6),
		18, Color3.fromRGB(240, 200, 255), Enum.Font.GothamBlack)
	ui.bossTitle = UIKit.label(bossFrame, "", UDim2.new(0, 300, 0, 16), UDim2.new(0, 12, 0, 26),
		11, Color3.fromRGB(190, 170, 210))
	ui.bossHp = UIKit.bar(bossFrame, UDim2.new(1, -24, 0, 20), UDim2.new(0, 12, 0, 46),
		Color3.fromRGB(190, 50, 200))

	-- --------------------------- уведомления (право верх) ---------------------------
	ui.notifyHolder = UIKit.frame(gui, UDim2.new(0, 330, 0, 300), UDim2.new(1, -350, 0, 120),
		Color3.fromRGB(0, 0, 0), 0, 1)
	ui.notifyHolder.BackgroundTransparency = 1

	-- --------------------------- журнал квестов (левый верх) ---------------------------
	local questBox = UIKit.frame(gui, UDim2.new(0, 280, 0, 24), UDim2.new(0, 18, 0, 90),
		Color3.fromRGB(14, 14, 20), 8, 0.35)
	UIKit.stroke(questBox, Color3.fromRGB(150, 124, 66), 1, 0.5)
	ui.questBox = questBox
	ui.questHeader = UIKit.label(questBox, "ЗАДАНИЯ  [J]", UDim2.new(1, -16, 1, 0), UDim2.new(0, 10, 0, 0),
		13, Color3.fromRGB(230, 210, 160), Enum.Font.GothamBold)
	questBox.Size = UDim2.new(0, 280, 0, 28)

	-- --------------------------- подсказки ---------------------------
	ui.hintLabel = UIKit.label(gui, "", UDim2.new(0, 720, 0, 22), UDim2.new(0.5, -360, 1, -46),
		15, Color3.fromRGB(250, 244, 220), Enum.Font.GothamMedium)
	ui.hintLabel.TextXAlignment = Enum.TextXAlignment.Center
	ui.hintLabel.TextTransparency = 1

	-- --------------------------- смерть ---------------------------
	local death = UIKit.frame(gui, UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0),
		Color3.fromRGB(80, 0, 0), 0, 0.55)
	death.Visible = false
	ui.death = death
	UIKit.label(death, "ВЫ ПОГИБЛИ", UDim2.new(1, 0, 0, 60), UDim2.new(0, 0, 0.42, 0),
		46, Color3.fromRGB(255, 90, 90), Enum.Font.GothamBlack).TextXAlignment = Enum.TextXAlignment.Center
	ui.deathSub = UIKit.label(death, "Возрождение...", UDim2.new(1, 0, 0, 30),
		UDim2.new(0, 0, 0.42, 64), 18, Color3.fromRGB(255, 200, 190), Enum.Font.GothamMedium)
	ui.deathSub.TextXAlignment = Enum.TextXAlignment.Center
end

-- ============================================================================
-- ОБНОВЛЕНИЕ
-- ============================================================================
local lastHpText = ""
local function updateVitals(d)
	if not d then return end
	state.hp = d.hp or state.hp
	state.maxHp = d.maxHp or state.maxHp
	state.mana = d.mana or state.mana
	state.maxMana = d.maxMana or state.maxMana
	state.stamina = d.stamina or state.stamina
	state.level = d.level or state.level
	state.xp = d.xp or state.xp
	state.xpNeed = d.xpNeed or state.xpNeed
	state.coins = d.coins or state.coins

	ui.hpBar.setRatio(state.hp / math.max(1, state.maxHp))
	ui.manaBar.setRatio(state.mana / math.max(1, state.maxMana))
	ui.staminaBar.setRatio(state.stamina / math.max(1, state.maxStamina))
	ui.xpBar.setRatio(state.xpNeed > 0 and (state.xp / state.xpNeed) or 1)

	local txt = math.floor(state.hp) .. " / " .. math.floor(state.maxHp)
	if txt ~= lastHpText then
		ui.hpText.Text = txt
		lastHpText = txt
	end
	ui.manaText.Text = math.floor(state.mana) .. " / " .. math.floor(state.maxMana)
	ui.xpText.Text = "Опыт " .. math.floor(state.xp) .. " / " .. (state.xpNeed > 0 and math.floor(state.xpNeed) or "МАКС")
	ui.coinsLabel.Text = "◈ " .. state.coins
	ui.levelLabel.Text = tostring(state.level)

	if state.hp / math.max(1, state.maxHp) < 0.3 then
		ui.hpBar.setColor(Color3.fromRGB(255, 60, 60))
	else
		ui.hpBar.setColor(Color3.fromRGB(214, 62, 62))
	end
end
HUD.updateVitals = updateVitals

-- уведомление
local notifY = 0
local function notify(data)
	if not data then return end
	local kindColors = {
		info = Color3.fromRGB(200, 200, 210),
		level = Color3.fromRGB(255, 220, 110),
		spell = Color3.fromRGB(170, 150, 255),
		loot = Color3.fromRGB(220, 220, 220),
		loot_common = Color3.fromRGB(210, 210, 210),
		loot_uncommon = Color3.fromRGB(130, 230, 130),
		loot_rare = Color3.fromRGB(110, 170, 255),
		loot_epic = Color3.fromRGB(200, 130, 255),
		loot_legendary = Color3.fromRGB(255, 195, 80),
		quest = Color3.fromRGB(255, 220, 110),
		quest_ready = Color3.fromRGB(120, 230, 150),
		quest_done = Color3.fromRGB(140, 255, 160),
		warn = Color3.fromRGB(255, 170, 90),
		bad = Color3.fromRGB(255, 110, 110),
		boss = Color3.fromRGB(220, 140, 255),
		hint = Color3.fromRGB(160, 220, 255),
	}

	local color = kindColors[data.kind or "info"] or kindColors.info
	local item = UIKit.frame(ui.notifyHolder, UDim2.new(1, 0, 0, 30), UDim2.new(0, 0, 0, notifY),
		Color3.fromRGB(16, 16, 22), 6, 0.2)
	UIKit.stroke(item, color, 1, 0.4)
	UIKit.label(item, data.text or "", UDim2.new(1, -14, 1, 0), UDim2.new(0, 8, 0, 0), 13, color,
		Enum.Font.GothamMedium)
	notifY = notifY + 34

	item.Position = UDim2.new(0, 40, 0, notifY - 34)
	TweenService:Create(item, TweenInfo.new(0.25, Enum.EasingStyle.Quad), {
		Position = UDim2.new(0, 0, 0, notifY - 34),
	}):Play()

	task.delay(4.5, function()
		if item.Parent then
			local tw = TweenService:Create(item, TweenInfo.new(0.4), {
				Position = UDim2.new(0, 40, 0, item.Position.Y.Offset), BackgroundTransparency = 1,
			})
			tw:Play()
			tw.Completed:Connect(function() item:Destroy() end)
		end
	end)

	-- пересобрать позиции
	task.delay(0.5, function()
		notifY = 0
		for _, child in ipairs(ui.notifyHolder:GetChildren()) do
			if child:IsA("Frame") and child.Parent and child.BackgroundTransparency < 1 then
				child.Position = UDim2.new(0, 0, 0, notifY)
				notifY = notifY + 34
			end
		end
	end)
end
HUD.notify = notify

-- подсказка внизу
local hintToken = 0
function HUD.showHint(text, duration)
	hintToken = hintToken + 1
	local token = hintToken
	ui.hintLabel.Text = text
	ui.hintLabel.TextTransparency = 0
	task.delay(duration or 2.5, function()
		if token == hintToken then
			TweenService:Create(ui.hintLabel, TweenInfo.new(0.6), { TextTransparency = 1 }):Play()
		end
	end)
end

-- цифры урона
local function damageNumber(data)
	local amount = data.amount or 0
	local isHeal = data.kind == "heal"
	local isCrit = data.kind == "crit"
	local isPlayer = data.kind == "player"

	local color = Color3.fromRGB(255, 235, 210)
	if isHeal then color = Color3.fromRGB(120, 255, 140) end
	if isCrit then color = Color3.fromRGB(255, 190, 60) end
	if isPlayer then color = Color3.fromRGB(255, 120, 120) end

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 120, 0, 44)
	billboard.StudsOffset = Vector3.new(math.random(-2, 2), 2, math.random(-2, 2))
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 220
	billboard.Adornee = nil
	billboard.Parent = gui

	local label = UIKit.create("TextLabel", {
		Size = UDim2.new(1, 0, 1, 0),
		BackgroundTransparency = 1,
		Text = (isHeal and "+" or "") .. tostring(amount) .. (isCrit and "!" or ""),
		TextColor3 = color,
		TextStrokeColor3 = Color3.fromRGB(0, 0, 0),
		TextStrokeTransparency = 0.35,
		Font = isCrit and Enum.Font.GothamBlack or Enum.Font.GothamBold,
		TextSize = isCrit and 30 or (isPlayer and 24 or 22),
	}, billboard)

	-- привязка к позиции через CFrame-точку
	local anchor = Instance.new("Part")
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.Transparency = 1
	anchor.Size = Vector3.new(0.2, 0.2, 0.2)
	anchor.Position = data.pos or Vector3.new(0, 10, 0)
	anchor.Parent = Workspace:FindFirstChild("EmberfallFx") or Workspace
	billboard.Adornee = anchor

	local startY = anchor.Position.Y
	local t0 = os.clock()
	local conn
	conn = RunService.RenderStepped:Connect(function()
		local t = (os.clock() - t0) / 0.85
		if t >= 1 or not anchor.Parent then
			conn:Disconnect()
			anchor:Destroy()
			billboard:Destroy()
			return
		end
		anchor.Position = Vector3.new(anchor.Position.X, startY + t * 5, anchor.Position.Z)
		label.TextTransparency = math.clamp((t - 0.5) * 2, 0, 1)
		label.TextStrokeTransparency = math.clamp(0.35 + (t - 0.5) * 2, 0, 1)
		label.Size = UDim2.new(1, 0, 1, 0)
	end)
end

local function showBossBar(d)
	if not d or not d.visible then
		ui.bossFrame.Visible = false
		return
	end
	ui.bossFrame.Visible = true
	ui.bossName.Text = (d.name or "БОСС") .. "  [ур. " .. tostring(d.level or "?") .. "]"
	ui.bossTitle.Text = d.title or ""
	ui.bossHp.setRatio((d.hp or 0) / math.max(1, d.maxHp or 1))
end

local function showDeath()
	ui.death.Visible = true
	ui.death.BackgroundTransparency = 0.55
	local t = 5
	ui.deathSub.Text = "Возрождение через " .. t .. "с"
	for i = t - 1, 0, -1 do
		task.wait(1)
		ui.deathSub.Text = i > 0 and ("Возрождение через " .. i .. "с") or "Готово"
	end
	ui.death.Visible = false
end

function HUD.init()
	build()
	updateVitals({
		hp = 100, maxHp = 100, mana = 100, maxMana = 100,
		stamina = 100, level = 1, xp = 0, xpNeed = 100, coins = 0,
	})

	req("Rep_Vitals").OnClientEvent:Connect(updateVitals)
	req("Rep_Notify").OnClientEvent:Connect(notify)
	req("Rep_Damage").OnClientEvent:Connect(damageNumber)
	req("Rep_BossBar").OnClientEvent:Connect(showBossBar)
	req("Rep_ZoneChanged").OnClientEvent:Connect(function(d)
		if d and d.name then
			state.zone = d.name
			ui.zoneLabel.Text = d.name
			ui.zoneLabel.TextColor3 = Color3.fromRGB(255, 245, 210)
			TweenService:Create(ui.zoneLabel, TweenInfo.new(0.5), {
				TextColor3 = Color3.fromRGB(240, 226, 190),
			}):Play()
		end
	end)
	req("Rep_Snapshot").OnClientEvent:Connect(updateVitals)
	req("Rep_Combat").OnClientEvent:Connect(function(inCombat)
		-- рамка блока характеристик подсвечивается в бою
		if ui.statsStroke then
			ui.statsStroke.Color = inCombat and Color3.fromRGB(200, 80, 80) or Color3.fromRGB(150, 124, 66)
		end
	end)
	req("Rep_BossEvent").OnClientEvent:Connect(function(d)
		if not d then return end
		if d.event == "world" then
			HUD.showHint("⚔ МИРОВОЙ БОСС: " .. tostring(d.name) .. " — " .. tostring(d.title or ""), 6)
		elseif d.event == "summon" then
			HUD.showHint("⚔ Печать сработала: " .. tostring(d.name) .. " (призвал " .. tostring(d.by or "?") .. ")", 5)
		elseif d.event == "phase" then
			HUD.showHint("☠ " .. tostring(d.name) .. ": " .. tostring(d.text or "новая фаза"), 3)
		elseif d.event == "died" then
			HUD.showHint("Босс повержен: " .. tostring(d.name), 4)
		end
	end)

	req("Rep_LevelUp").OnClientEvent:Connect(function(d)
		HUD.showHint("УРОВЕНЬ " .. tostring(d.level) .. "!", 3)
	end)
	req("Rep_CastFail").OnClientEvent:Connect(function(d)
		if d and d.reason then HUD.showHint("✖ " .. d.reason, 1.5) end
	end)

	-- отслеживаем смерть персонажа
	local function watchCharacter(char)
		local hum = char:WaitForChild("Humanoid")
		hum.Died:Connect(function()
			task.spawn(showDeath)
		end)
	end
	if player.Character then watchCharacter(player.Character) end
	player.CharacterAdded:Connect(watchCharacter)
end

return HUD
"""

CLIENT["SpellBar"] = """-- Emberfall | SpellBar — 6 слотов заклинаний, откаты, мана, перетаскивание.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local UIKit = require(script.Parent:WaitForChild("UIKit"))
local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))
local GameData = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("GameData"))

local SpellBar = {}

local ui
local slots = {}
local hotbar = {}
local spells = {}
local cooldownEnd = {}
local mana = 0
local maxMana = 100

local function req(name)
	return ReplicatedStorage:WaitForChild("Remotes"):WaitForChild(name)
end

local function slotSize() return 62 end
local function gap() return 6 end

local function build()
	local gui = Instance.new("ScreenGui")
	gui.Name = "EmberfallSpellBar"
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 6
	gui.Parent = playerGui
	ui = gui

	local totalW = 6 * slotSize() + 5 * gap()
	local holder = UIKit.frame(gui, UDim2.new(0, totalW, 0, slotSize() + 18),
		UDim2.new(0.5, -totalW / 2, 1, -100), Color3.fromRGB(0, 0, 0), 0, 1)
	holder.BackgroundTransparency = 1
	ui.holder = holder

	for i = 1, 6 do
		local slot = UIKit.frame(holder, UDim2.new(0, slotSize(), 0, slotSize()),
			UDim2.new(0, (i - 1) * (slotSize() + gap()), 0, 0),
			Color3.fromRGB(18, 18, 26), 8, 0.15)
		UIKit.stroke(slot, Color3.fromRGB(120, 104, 70), 1.5, 0.3)

		local icon = UIKit.create("TextLabel", {
			Size = UDim2.new(1, 0, 0.68, 0), Position = UDim2.new(0, 0, 0.02, 0),
			BackgroundTransparency = 1, Text = "", TextSize = 28,
			TextColor3 = Color3.fromRGB(255, 255, 255), Font = Enum.Font.GothamBold,
		}, slot)

		local keyLabel = UIKit.create("TextLabel", {
			Size = UDim2.new(0, 16, 0, 14), Position = UDim2.new(0, 4, 1, -16),
			BackgroundTransparency = 1, Text = tostring(i),
			TextSize = 11, TextColor3 = Color3.fromRGB(190, 180, 160), Font = Enum.Font.GothamBold,
		}, slot)

		local manaLabel = UIKit.create("TextLabel", {
			Size = UDim2.new(1, -6, 0, 14), Position = UDim2.new(0, 3, 1, -16),
			BackgroundTransparency = 1, Text = "", TextSize = 10,
			TextColor3 = Color3.fromRGB(150, 190, 255), Font = Enum.Font.GothamMedium,
			TextXAlignment = Enum.TextXAlignment.Right,
		}, slot)

		-- затемнение отката (растёт снизу вверх)
		local cdBack = UIKit.create("Frame", {
			Size = UDim2.new(1, 0, 0, 0), Position = UDim2.new(0, 0, 1, 0),
			BackgroundColor3 = Color3.fromRGB(0, 0, 0), BackgroundTransparency = 0.35,
			BorderSizePixel = 0, AnchorPoint = Vector2.new(0, 1),
		}, slot)
		UIKit.corner(cdBack, 8)

		local cdText = UIKit.create("TextLabel", {
			Size = UDim2.new(1, 0, 1, 0), BackgroundTransparency = 1,
			Text = "", TextSize = 20, TextColor3 = Color3.fromRGB(255, 240, 200),
			Font = Enum.Font.GothamBlack,
		}, slot)

		-- нижняя полоска готовности/маны
		local manaFill = UIKit.create("Frame", {
			Size = UDim2.new(1, 0, 0, 3), Position = UDim2.new(0, 0, 0, 0),
			BackgroundColor3 = Color3.fromRGB(90, 150, 255), BorderSizePixel = 0,
		}, slot)

		local button = UIKit.create("TextButton", {
			Size = UDim2.new(1, 0, 1, 0), BackgroundTransparency = 1, Text = "",
		}, slot)

		slots[i] = {
			frame = slot, icon = icon, key = keyLabel, manaLabel = manaLabel,
			cdBack = cdBack, cdText = cdText, manaFill = manaFill, button = button,
		}

		button.MouseButton1Click:Connect(function()
			SpellBar.cast(i)
		end)
	end

	-- подсказка выбранной стихии
	ui.elementLabel = UIKit.create("TextLabel", {
		Size = UDim2.new(0, totalW, 0, 16), Position = UDim2.new(0, 0, 1, 4),
		BackgroundTransparency = 1, Text = "", TextSize = 12,
		TextColor3 = Color3.fromRGB(200, 190, 170), Font = Enum.Font.GothamMedium,
		TextXAlignment = Enum.TextXAlignment.Center,
	}, holder)
end

local function updateSlot(i)
	local s = slots[i]
	local spellId = hotbar[i]
	local spell = spellId and GameData.SpellById[spellId]

	if not spell then
		s.icon.Text = ""
		s.manaLabel.Text = ""
		s.cdBack.Size = UDim2.new(1, 0, 0, 0)
		s.cdText.Text = ""
		s.frame.BackgroundColor3 = Color3.fromRGB(18, 18, 26)
		s.manaFill.Size = UDim2.new(0, 0, 0, 3)
		return
	end

	s.icon.Text = spell.icon or "✦"
	s.manaLabel.Text = tostring(spell.manaCost)
	local el = Config.ElementById[spell.element]
	local col = el and el.color or Color3.fromRGB(200, 200, 200)
	s.frame.BackgroundColor3 = col:Lerp(Color3.fromRGB(10, 10, 14), 0.78)
	s.manaFill.BackgroundColor3 = col
end

-- ============================================================================
-- КАСТ
-- ============================================================================
function SpellBar.cast(index)
	local spellId = hotbar[index]
	if not spellId then return end
	local spell = GameData.SpellById[spellId]
	if not spell then return end

	if mana < (spell.manaCost or 0) then
		local HUD = _G.EmberfallHUD
		if HUD then HUD.showHint("✖ Не хватает маны", 1.4) end
		return
	end
	local now = os.clock()
	if (cooldownEnd[spellId] or 0) > now then return end

	-- точка прицела: курсор или взгляд
	local aim
	local mouse = player:GetMouse()
	if mouse and mouse.Hit then
		aim = mouse.Hit.Position
	else
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if root then aim = root.Position + root.CFrame.LookVector * 40 end
	end
	local remotes = ReplicatedStorage:WaitForChild("Remotes")
	remotes:WaitForChild("Req_UseSpell"):FireServer(spellId, aim)

	-- локальный предварительный откат (сервер всё равно проверит)
	cooldownEnd[spellId] = now + (spell.cooldown or 1)
end

function SpellBar.castBySlot(i)
	SpellBar.cast(i)
end

-- ============================================================================
-- ОБНОВЛЕНИЕ ОТКАТОВ
-- ============================================================================
local function tick()
	local now = os.clock()
	for i = 1, 6 do
		local s = slots[i]
		local spellId = hotbar[i]
		if spellId then
			local spell = GameData.SpellById[spellId]
			if spell then
				local ready = cooldownEnd[spellId] or 0
				local total = spell.cooldown or 1
				local remain = math.max(0, ready - now)
				if remain > 0 then
					s.cdBack.Size = UDim2.new(1, 0, remain / total, 0)
					s.cdText.Text = string.format("%.1f", remain)
				else
					s.cdBack.Size = UDim2.new(1, 0, 0, 0)
					s.cdText.Text = ""
				end
				-- индикатор доступности маны
				local hasMana = mana >= (spell.manaCost or 0)
				s.icon.TextTransparency = (hasMana and remain <= 0) and 0 or 0.45
				s.manaLabel.TextColor3 = hasMana and Color3.fromRGB(150, 190, 255) or Color3.fromRGB(220, 90, 90)
			end
		end
	end
end

function SpellBar.init()
	build()

	local remotes = ReplicatedStorage:WaitForChild("Remotes")
	remotes:WaitForChild("Rep_Spells").OnClientEvent:Connect(function(d)
		if not d then return end
		hotbar = d.hotbar or {}
		spells = d.spells or {}
		local el = d.element and Config.ElementById[d.element]
		ui.elementLabel.Text = el and (el.rune .. "  " .. el.name .. "  —  " .. el.desc) or "Стихия не выбрана — найди АЛТАРЬ СТИХИЙ у площади"
		for i = 1, 6 do updateSlot(i) end
	end)

	remotes:WaitForChild("Rep_Snapshot").OnClientEvent:Connect(function(d)
		if d then
			hotbar = d.hotbar or {}
			spells = d.spells or {}
			mana = d.mana or mana
			maxMana = d.maxMana or maxMana
			local el = d.element and Config.ElementById[d.element]
			ui.elementLabel.Text = el and (el.rune .. "  " .. el.name) or "Стихия не выбрана — коснись алтаря у площади"
			for i = 1, 6 do updateSlot(i) end
		end
	end)

	remotes:WaitForChild("Rep_Vitals").OnClientEvent:Connect(function(d)
		if d then
			mana = d.mana or mana
			maxMana = d.maxMana or maxMana
		end
	end)

	-- горячие клавиши 1..6 (и цифры на нампаде)
	local NUMBER_KEYS = {
		[Enum.KeyCode.One] = 1, [Enum.KeyCode.Two] = 2, [Enum.KeyCode.Three] = 3,
		[Enum.KeyCode.Four] = 4, [Enum.KeyCode.Five] = 5, [Enum.KeyCode.Six] = 6,
		[Enum.KeyCode.KeypadOne] = 1, [Enum.KeyCode.KeypadTwo] = 2,
		[Enum.KeyCode.KeypadThree] = 3, [Enum.KeyCode.KeypadFour] = 4,
		[Enum.KeyCode.KeypadFive] = 5, [Enum.KeyCode.KeypadSix] = 6,
	}
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed then return end
		if input.UserInputType ~= Enum.UserInputType.Keyboard then return end
		local n = NUMBER_KEYS[input.KeyCode]
		if n then SpellBar.cast(n) end
	end)

	RunService.RenderStepped:Connect(tick)
end

return SpellBar
"""

CLIENT["Panels"] = """-- Emberfall | Panels — большие окна: персонаж/статы/магия (C),
-- журнал заданий (J), диалог NPC и магазин, выбор стихии, инвентарь.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local UIKit = require(script.Parent:WaitForChild("UIKit"))
local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))
local GameData = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("GameData"))
local Quests = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Quests"))

local Panels = {}

local gui
local remotes
local state = {
	level = 1, points = 0, stats = {},
	weaponDamage = 0, armor = 0,
	element = nil, spells = {}, hotbar = {},
	items = {}, equip = {},
	quests = {},
	coins = 0,
}

local ui = {}

local PALETTE = {
	bg = Color3.fromRGB(16, 15, 20),
	panel = Color3.fromRGB(24, 22, 30),
	accent = Color3.fromRGB(206, 172, 96),
	text = Color3.fromRGB(238, 232, 216),
	dim = Color3.fromRGB(160, 152, 138),
	good = Color3.fromRGB(130, 220, 140),
	bad = Color3.fromRGB(230, 110, 110),
}

local function req(name)
	return remotes:WaitForChild(name)
end

-- ============================================================================
-- ОБЩЕЕ ОКНО
-- ============================================================================
local function makeWindow(name, title, size)
	size = size or UDim2.new(0, 760, 0, 520)
	local w = size.X.Offset
	local h = size.Y.Offset
	local frame = UIKit.frame(gui, size, UDim2.new(0.5, -w / 2, 0.5, -h / 2),
		PALETTE.bg, 12, 0.03)
	UIKit.stroke(frame, PALETTE.accent, 2, 0.25)
	frame.Visible = false
	frame.Name = name

	local header = UIKit.frame(frame, UDim2.new(1, 0, 0, 46), UDim2.new(0, 0, 0, 0), PALETTE.panel, 12)
	header.BackgroundTransparency = 0
	UIKit.corner(header, 12)
	local hfix = UIKit.frame(frame, UDim2.new(1, 0, 0, 12), UDim2.new(0, 0, 0, 40), PALETTE.panel, 0)
	local titleLabel = UIKit.label(header, title, UDim2.new(1, -120, 1, 0), UDim2.new(0, 16, 0, 0), 20,
		PALETTE.accent, Enum.Font.GothamBlack)
	frame:SetAttribute("Window", true)

	local close = UIKit.button(header, "✕", UDim2.new(0, 34, 0, 30), UDim2.new(1, -42, 0, 8),
		Color3.fromRGB(70, 40, 40), function() frame.Visible = false end)

	local content = UIKit.frame(frame, UDim2.new(1, -24, 1, -66), UDim2.new(0, 12, 0, 54),
		PALETTE.bg, 0, 1)
	content.BackgroundTransparency = 1
	return frame, content, titleLabel
end

local function scrollList(parent, size, pos)
	local scroll = UIKit.create("ScrollingFrame", {
		Size = size, Position = pos,
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 6,
		ScrollBarImageColor3 = PALETTE.accent,
		CanvasSize = UDim2.new(0, 0, 0, 0),
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
	}, parent)
	return scroll
end

-- ============================================================================
-- ОКНО ПЕРСОНАЖА (C)
-- ============================================================================
local charWindow, charContent
local statRows = {}

local function refreshStats()
	if not charContent then return end
	for _, child in ipairs(charContent:GetChildren()) do
		if child:GetAttribute("StatRow") or child:GetAttribute("Dynamic") then child:Destroy() end
	end

	local left = charContent:FindFirstChild("LeftCol")
	-- уровень/очки
	ui.levelText.Text = "Уровень " .. state.level
	ui.pointsText.Text = state.points > 0 and ("Свободных очков: " .. state.points) or "Нет свободных очков"
	ui.pointsText.TextColor3 = state.points > 0 and PALETTE.good or PALETTE.dim

	-- статы
	local y = 56
	for _, stat in ipairs(Config.Stats) do
		local value = state.stats[stat.id] or 0
		local row = UIKit.frame(left, UDim2.new(1, -20, 0, 40), UDim2.new(0, 0, 0, y),
			PALETTE.panel, 6, 0.1)
		row:SetAttribute("StatRow", true)
		UIKit.label(row, stat.icon .. "  " .. stat.name, UDim2.new(0, 150, 1, 0), UDim2.new(0, 10, 0, 0),
			15, PALETTE.text, Enum.Font.GothamBold)
		UIKit.label(row, stat.desc, UDim2.new(0, 240, 1, 0), UDim2.new(0, 150, 0, 0), 12, PALETTE.dim)
		UIKit.label(row, tostring(value), UDim2.new(0, 40, 1, 0), UDim2.new(1, -110, 0, 0), 16,
			PALETTE.accent, Enum.Font.GothamBlack).TextXAlignment = Enum.TextXAlignment.Center
		local plus = UIKit.button(row, "+", UDim2.new(0, 30, 0, 28), UDim2.new(1, -38, 0, 6),
			state.points > 0 and Color3.fromRGB(60, 110, 60) or Color3.fromRGB(50, 50, 58),
			function()
				req("Req_SpendStat"):FireServer(stat.id)
			end)
		y = y + 46
	end

	-- экипировка справа
	local right = charContent:FindFirstChild("RightCol")
	for _, child in ipairs(right:GetChildren()) do
		if child:GetAttribute("Dynamic") then child:Destroy() end
	end

	UIKit.label(right, "ЭКИПИРОВКА", UDim2.new(1, 0, 0, 20), UDim2.new(0, 0, 0, 0), 14,
		PALETTE.accent, Enum.Font.GothamBold):SetAttribute("Dynamic", true)

	local yy = 24
	for _, slot in ipairs({ "weapon", "armor", "trinket" }) do
		local uid = state.equip[slot]
		local item = nil
		if uid then
			for _, it in pairs(state.items) do
				if it.uid == uid then item = GameData.ItemById[it.id] end
			end
		end
		local row = UIKit.frame(right, UDim2.new(1, 0, 0, 44), UDim2.new(0, 0, 0, yy),
			PALETTE.panel, 6, 0.1)
		row:SetAttribute("Dynamic", true)
		local slotName = Config.EquipSlots[slot] or slot
		UIKit.label(row, slotName, UDim2.new(0, 90, 1, 0), UDim2.new(0, 10, 0, 0), 12, PALETTE.dim)
		if item then
			local rar = GameData.Rarities[item.rarity] or GameData.Rarities.common
			UIKit.label(row, item.name, UDim2.new(0, 200, 1, 0), UDim2.new(0, 100, 0, 0), 14, rar.color,
				Enum.Font.GothamBold)
			UIKit.button(row, "снять", UDim2.new(0, 60, 0, 28), UDim2.new(1, -70, 0, 8),
				Color3.fromRGB(70, 50, 50), function()
					req("Req_Unequip"):FireServer(slot)
				end)
		else
			UIKit.label(row, "— пусто —", UDim2.new(0, 200, 1, 0), UDim2.new(0, 100, 0, 0), 13, PALETTE.dim)
		end
		yy = yy + 50
	end

	-- характеристики
	UIKit.label(right, "ХАРАКТЕРИСТИКИ", UDim2.new(1, 0, 0, 20), UDim2.new(0, 0, 0, yy + 8), 14,
		PALETTE.accent, Enum.Font.GothamBold):SetAttribute("Dynamic", true)
	yy = yy + 34
	local hudState = (_G.EmberfallHUD and _G.EmberfallHUD.state) or {}
	local lines = {
		{"Здоровье", tostring(math.floor(hudState.maxHp or 100))},
		{"Мана", tostring(math.floor(hudState.maxMana or 100))},
		{"Урон оружия", tostring(state.weaponDamage or 0)},
		{"Броня", tostring(state.armor or 0)},
		{"Стихия", state.element and ((Config.ElementById[state.element] or {}).name or state.element) or "нет"},
	}
	for _, line in ipairs(lines) do
		local l = UIKit.label(right, line[1], UDim2.new(0, 200, 0, 20), UDim2.new(0, 0, 0, yy), 13, PALETTE.dim)
		l:SetAttribute("Dynamic", true)
		local v = UIKit.label(right, line[2], UDim2.new(0, 100, 0, 20), UDim2.new(1, -100, 0, yy), 13,
			PALETTE.text, Enum.Font.GothamBold)
		v:SetAttribute("Dynamic", true)
		v.TextXAlignment = Enum.TextXAlignment.Right
		yy = yy + 22
	end
end

local function buildCharWindow()
	charWindow, charContent = makeWindow("CharWindow", "ПЕРСОНАЖ", UDim2.new(0, 820, 0, 560))

	local left = UIKit.frame(charContent, UDim2.new(0.5, -14, 1, 0), UDim2.new(0, 0, 0, 0), PALETTE.bg, 0, 1)
	left.Name = "LeftCol"
	left.BackgroundTransparency = 1

	local right = UIKit.frame(charContent, UDim2.new(0.5, -6, 1, 0), UDim2.new(0.5, 12, 0, 0), PALETTE.bg, 0, 1)
	right.Name = "RightCol"
	right.BackgroundTransparency = 1

	ui.levelText = UIKit.label(left, "Уровень 1", UDim2.new(1, 0, 0, 24), UDim2.new(0, 0, 0, 0), 20,
		PALETTE.accent, Enum.Font.GothamBlack)
	ui.pointsText = UIKit.label(left, "Нет свободных очков", UDim2.new(1, 0, 0, 18), UDim2.new(0, 0, 0, 26), 13,
		PALETTE.dim)
end

-- ============================================================================
-- ОКНО МАГИИ
-- ============================================================================
local spellWindow, spellContent

local function refreshSpells()
	if not spellContent then return end
	for _, child in ipairs(spellContent:GetChildren()) do
		if child:GetAttribute("Dynamic") then child:Destroy() end
	end

	local el = state.element and Config.ElementById[state.element]
	local title = el and (el.rune .. "  " .. el.name) or "СТИХИЯ НЕ ВЫБРАНА"
	local sub = el and el.desc or "Коснись алтаря стихий у площади Пепельной Пристани"
	UIKit.label(spellContent, title, UDim2.new(1, 0, 0, 26), UDim2.new(0, 0, 0, 0), 20,
		el and el.color or PALETTE.dim, Enum.Font.GothamBlack):SetAttribute("Dynamic", true)
	UIKit.label(spellContent, sub, UDim2.new(1, 0, 0, 18), UDim2.new(0, 0, 0, 28), 12,
		PALETTE.dim):SetAttribute("Dynamic", true)

	local scroll = scrollList(spellContent, UDim2.new(1, 0, 1, -60), UDim2.new(0, 0, 0, 54))
	scroll:SetAttribute("Dynamic", true)

	local y = 0
	for _, spell in ipairs(GameData.Spells) do
		local isMine = state.element == spell.element
		local known = state.spells[spell.id]
		local canLearn = isMine and not known and state.level >= (spell.reqLevel or 1)

		local card = UIKit.frame(scroll, UDim2.new(1, -8, 0, 68), UDim2.new(0, 0, 0, y),
			PALETTE.panel, 8, isMine and 0.05 or 0.55)
		UIKit.stroke(card, isMine and (el and el.color or PALETTE.accent) or Color3.fromRGB(70, 68, 64), 1, isMine and 0.3 or 0.6)

		UIKit.label(card, spell.icon or "✦", UDim2.new(0, 44, 0, 44), UDim2.new(0, 10, 0, 10), 28,
			Color3.fromRGB(255, 255, 255))

		local elDef = Config.ElementById[spell.element]
		UIKit.label(card, spell.name, UDim2.new(0, 240, 0, 20), UDim2.new(0, 60, 0, 6), 15,
			elDef and elDef.color or PALETTE.text, Enum.Font.GothamBold)
		UIKit.label(card, spell.desc or "", UDim2.new(1, -260, 0, 16), UDim2.new(0, 60, 0, 28), 11,
			PALETTE.dim)
		UIKit.label(card, "мана " .. (spell.manaCost or 0) .. "  •  откат " .. (spell.cooldown or 0) .. "с  •  ур."
			.. (spell.reqLevel or 1), UDim2.new(0, 320, 0, 16), UDim2.new(0, 60, 0, 46), 11,
			Color3.fromRGB(150, 170, 210))

		local statusText, statusColor
		if known then
			statusText, statusColor = "ИЗУЧЕНО", PALETTE.good
		elseif not isMine then
			statusText, statusColor = "другая стихия", PALETTE.dim
		elseif state.level < (spell.reqLevel or 1) then
			statusText, statusColor = "нужен ур. " .. spell.reqLevel, PALETTE.bad
		else
			statusText, statusColor = "ИЗУЧИТЬ", PALETTE.accent
		end

		if canLearn then
			UIKit.button(card, statusText, UDim2.new(0, 130, 0, 30), UDim2.new(1, -142, 0, 18),
				Color3.fromRGB(70, 62, 40), function()
					req("Req_LearnSpell"):FireServer(spell.id)
				end)
		else
			UIKit.label(card, statusText, UDim2.new(0, 130, 0, 30), UDim2.new(1, -142, 0, 24), 12,
				statusColor, Enum.Font.GothamBold).TextXAlignment = Enum.TextXAlignment.Right
		end

		y = y + 74
	end
end

local function buildSpellWindow()
	spellWindow, spellContent = makeWindow("SpellWindow", "МАГИЯ", UDim2.new(0, 820, 0, 560))
end

-- ============================================================================
-- ЖУРНАЛ ЗАДАНИЙ (J)
-- ============================================================================
local questWindow, questContent

local function refreshQuests()
	if not questContent then return end
	for _, child in ipairs(questContent:GetChildren()) do
		if child:GetAttribute("Dynamic") then child:Destroy() end
	end

	if #state.quests == 0 then
		UIKit.label(questContent, "Заданий нет.\\nНайди NPC с золотым «!» над головой — Хранитель Знаний стоит у площади.",
			UDim2.new(1, -20, 0, 80), UDim2.new(0, 10, 0, 20), 15, PALETTE.dim):SetAttribute("Dynamic", true)
		return
	end

	local scroll = scrollList(questContent, UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0))
	scroll:SetAttribute("Dynamic", true)

	local y = 0
	for _, q in ipairs(state.quests) do
		local stateColor = q.state == "ready" and PALETTE.good or (q.state == "active" and PALETTE.accent or PALETTE.dim)
		local card = UIKit.frame(scroll, UDim2.new(1, -8, 0, 150), UDim2.new(0, 0, 0, y),
			PALETTE.panel, 8, 0.05)
		UIKit.stroke(card, stateColor, 1, 0.45)

		UIKit.label(card, q.name, UDim2.new(0, 400, 0, 22), UDim2.new(0, 12, 0, 6), 16,
			stateColor, Enum.Font.GothamBold)
		UIKit.label(card, "у " .. (q.giverName or "?"), UDim2.new(0, 260, 0, 16), UDim2.new(0, 12, 0, 28), 11,
			PALETTE.dim)
		UIKit.label(card, q.desc or "", UDim2.new(1, -24, 0, 32), UDim2.new(0, 12, 0, 46), 12,
			PALETTE.text)

		local oy = 80
		for _, obj in ipairs(q.objectives or {}) do
			local done = obj.have >= obj.need
			UIKit.label(card, (done and "✔ " or "• ") .. obj.text .. ": " .. obj.have .. "/" .. obj.need,
				UDim2.new(0, 340, 0, 18), UDim2.new(0, 14, 0, oy), 12,
				done and PALETTE.good or PALETTE.dim)
			oy = oy + 18
		end

		local rw = q.rewards or {}
		UIKit.label(card, "Награда: " .. (rw.xp or 0) .. " опыта, " .. (rw.coins or 0) .. " монет",
			UDim2.new(0, 380, 0, 18), UDim2.new(0, 12, 0, oy), 11, Color3.fromRGB(200, 180, 130))

		if q.state == "ready" then
			UIKit.button(card, "СДАТЬ", UDim2.new(0, 110, 0, 30), UDim2.new(1, -122, 0, 8),
				Color3.fromRGB(60, 110, 60), function()
					req("Req_QuestClaim"):FireServer(q.id)
				end)
		elseif q.state == "active" then
			UIKit.button(card, "БРОСИТЬ", UDim2.new(0, 90, 0, 26), UDim2.new(1, -102, 0, 8),
				Color3.fromRGB(70, 44, 44), function()
					req("Req_QuestAbandon"):FireServer(q.id)
				end)
		end

		y = y + 158
	end
end

local function buildQuestWindow()
	questWindow, questContent = makeWindow("QuestWindow", "ЖУРНАЛ ЗАДАНИЙ", UDim2.new(0, 760, 0, 560))
end

-- ============================================================================
-- ДИАЛОГ NPC / МАГАЗИН
-- ============================================================================
local dialogWindow, dialogContent
local dialogTab = "quests"

local function renderDialog(payload)
	if not dialogContent then return end
	for _, child in ipairs(dialogContent:GetChildren()) do
		if child:GetAttribute("Dynamic") then child:Destroy() end
	end

	-- шапка
	local line = (payload.lines and payload.lines[math.random(1, math.max(1, #payload.lines))]) or ""
	UIKit.label(dialogContent, "«" .. line .. "»", UDim2.new(1, -20, 0, 40), UDim2.new(0, 4, 0, 0), 14,
		Color3.fromRGB(215, 205, 180), Enum.Font.GothamMedium):SetAttribute("Dynamic", true)

	-- вкладки
	local tabs = {}
	if payload.role == "shop" then table.insert(tabs, { id = "shop", name = "ТОВАР" }) end
	table.insert(tabs, { id = "quests", name = "ЗАДАНИЯ" })
	table.insert(tabs, { id = "sell", name = "ПРОДАТЬ" })
	if payload.role == "heal" then table.insert(tabs, { id = "heal", name = "ЛЕЧЕНИЕ" }) end

	if dialogTab == "shop" and payload.role ~= "shop" then
		dialogTab = "quests"
	end

	local tx = 0
	for _, tab in ipairs(tabs) do
		local active = dialogTab == tab.id
		local b = UIKit.button(dialogContent, tab.name, UDim2.new(0, 120, 0, 30), UDim2.new(0, tx, 0, 44),
			active and Color3.fromRGB(78, 66, 40) or Color3.fromRGB(36, 34, 42), function()
				dialogTab = tab.id
				renderDialog(payload)
			end)
		b:SetAttribute("Dynamic", true)
		tx = tx + 126
	end

	local area = scrollList(dialogContent, UDim2.new(1, 0, 1, -86), UDim2.new(0, 0, 0, 82))
	area:SetAttribute("Dynamic", true)

	local y = 0

	-- -------- вкладка заданий --------
	if dialogTab == "quests" then
		local function questCard(q, kind)
			local card = UIKit.frame(area, UDim2.new(1, -8, 0, 128), UDim2.new(0, 0, 0, y), PALETTE.panel, 8, 0.05)
			local col = kind == "ready" and PALETTE.good or (kind == "available" and PALETTE.accent or PALETTE.dim)
			UIKit.stroke(card, col, 1, 0.4)
			UIKit.label(card, q.name, UDim2.new(0, 420, 0, 20), UDim2.new(0, 12, 0, 6), 15, col,
				Enum.Font.GothamBold)
			UIKit.label(card, q.desc or "", UDim2.new(1, -24, 0, 36), UDim2.new(0, 12, 0, 28), 12, PALETTE.text)
			for i, obj in ipairs(q.objectives or {}) do
				local done = obj.have >= obj.need
				UIKit.label(card, (done and "✔ " or "• ") .. obj.text .. ": " .. obj.have .. "/" .. obj.need,
					UDim2.new(0, 320, 0, 16), UDim2.new(0, 14, 0, 68 + (i - 1) * 16), 11,
					done and PALETTE.good or PALETTE.dim)
			end
			local rw = q.rewards or {}
			UIKit.label(card, "+" .. (rw.xp or 0) .. " опыта  ·  +" .. (rw.coins or 0) .. " монет",
				UDim2.new(0, 300, 0, 16), UDim2.new(1, -320, 0, 8), 11, Color3.fromRGB(200, 180, 130))

			if kind == "available" then
				UIKit.button(card, "ВЗЯТЬ", UDim2.new(0, 110, 0, 30), UDim2.new(1, -122, 0, 8),
					Color3.fromRGB(62, 88, 56), function()
						req("Req_QuestAccept"):FireServer(q.id)
					end)
			elseif kind == "ready" then
				UIKit.button(card, "СДАТЬ", UDim2.new(0, 110, 0, 30), UDim2.new(1, -122, 0, 8),
					Color3.fromRGB(62, 110, 62), function()
						req("Req_QuestClaim"):FireServer(q.id)
					end)
			end
			y = y + 134
		end

		for _, q in ipairs(payload.active or {}) do
			questCard(q, q.kind or "active")
		end
		for _, q in ipairs(payload.available or {}) do
			questCard(q, "available")
		end
		if y == 0 then
			UIKit.label(area, "Сейчас у меня для тебя ничего нет. Возвращайся позже.",
				UDim2.new(1, 0, 0, 30), UDim2.new(0, 4, 0, 4), 13, PALETTE.dim):SetAttribute("Dynamic", true)
		end
	end

	-- -------- вкладка магазина --------
	if dialogTab == "shop" and payload.shop then
		UIKit.label(area, "Монет у тебя: " .. state.coins, UDim2.new(1, 0, 0, 20), UDim2.new(0, 4, 0, 0),
			13, Color3.fromRGB(255, 214, 120)):SetAttribute("Dynamic", true)
		y = 26
		for _, it in ipairs(payload.shop) do
			local def = GameData.ItemById[it.id]
			local rar = GameData.Rarities[it.rarity] or GameData.Rarities.common
			local card = UIKit.frame(area, UDim2.new(1, -8, 0, 54), UDim2.new(0, 0, 0, y), PALETTE.panel, 6, 0.05)
			UIKit.label(card, it.name, UDim2.new(0, 280, 0, 18), UDim2.new(0, 10, 0, 4), 14, rar.color,
				Enum.Font.GothamBold)
			UIKit.label(card, it.desc or "", UDim2.new(1, -300, 0, 16), UDim2.new(0, 10, 0, 24), 11, PALETTE.dim)
			UIKit.label(card, it.price .. " ◈", UDim2.new(0, 100, 0, 18), UDim2.new(1, -230, 0, 4), 14,
				Color3.fromRGB(255, 214, 120), Enum.Font.GothamBold).TextXAlignment = Enum.TextXAlignment.Right
			UIKit.button(card, "КУПИТЬ", UDim2.new(0, 110, 0, 28), UDim2.new(1, -122, 0, 13),
				state.coins >= (it.price or 0) and Color3.fromRGB(72, 66, 40) or Color3.fromRGB(52, 48, 46),
				function()
					req("Req_ShopBuy"):FireServer(it.id)
				end)
			y = y + 60
		end
	end

	-- -------- вкладка продажи --------
	if dialogTab == "sell" then
		UIKit.label(area, "Выбери, что продать:", UDim2.new(1, 0, 0, 20), UDim2.new(0, 4, 0, 0), 13,
			PALETTE.dim):SetAttribute("Dynamic", true)
		y = 24
		for _, inv in pairs(state.items) do
			local def = GameData.ItemById[inv.id]
			if def then
				local mult = GameData.SellableTypes[def.type] or 0.3
				local value = math.max(1, math.floor((def.price or 10) * mult))
				local rar = GameData.Rarities[def.rarity] or GameData.Rarities.common
				local card = UIKit.frame(area, UDim2.new(1, -8, 0, 40), UDim2.new(0, 0, 0, y), PALETTE.panel, 6, 0.05)
				UIKit.label(card, def.name .. (inv.count > 1 and (" x" .. inv.count) or ""),
					UDim2.new(0, 380, 1, 0), UDim2.new(0, 10, 0, 0), 13, rar.color, Enum.Font.GothamBold)
				UIKit.label(card, value .. " ◈", UDim2.new(0, 90, 1, 0), UDim2.new(1, -210, 0, 0), 13,
					Color3.fromRGB(255, 214, 120), Enum.Font.GothamBold).TextXAlignment = Enum.TextXAlignment.Right
				UIKit.button(card, "ПРОДАТЬ", UDim2.new(0, 110, 0, 28), UDim2.new(1, -120, 0, 6),
					Color3.fromRGB(72, 66, 40), function()
						req("Req_ShopSell"):FireServer(inv.uid)
					end)
				y = y + 46
			end
		end
		if y == 24 then
			UIKit.label(area, "Рюкзак пуст.", UDim2.new(1, 0, 0, 20), UDim2.new(0, 4, 0, 28), 13,
				PALETTE.dim):SetAttribute("Dynamic", true)
		end
	end

	-- -------- лечение --------
	if dialogTab == "heal" then
		UIKit.label(area, "Лекарь восстановит здоровье за 40 монет.", UDim2.new(1, 0, 0, 24),
			UDim2.new(0, 4, 0, 0), 14, PALETTE.text):SetAttribute("Dynamic", true)
		local healBtn = UIKit.button(area, "ЛЕЧИТЬСЯ (40 ◈)", UDim2.new(0, 220, 0, 34),
			UDim2.new(0, 4, 0, 30), Color3.fromRGB(60, 100, 70), function()
				req("Req_Heal"):FireServer()
			end)
		healBtn:SetAttribute("Dynamic", true)
	end
end

local function buildDialogWindow()
	local titleLabel
	dialogWindow, dialogContent, titleLabel = makeWindow("DialogWindow", "РАЗГОВОР", UDim2.new(0, 820, 0, 560))
	ui.dialogTitle = titleLabel
end

-- ============================================================================
-- ВЫБОР СТИХИИ
-- ============================================================================
local pickWindow

local function buildPickWindow()
	pickWindow = UIKit.frame(gui, UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0),
		Color3.fromRGB(8, 6, 14), 0, 0.4)
	pickWindow.Visible = false
	pickWindow.ZIndex = 20

	local card = UIKit.frame(pickWindow, UDim2.new(0, 900, 0, 480), UDim2.new(0.5, -450, 0.5, -240),
		PALETTE.bg, 14, 0.02)
	UIKit.stroke(card, PALETTE.accent, 2, 0.2)

	UIKit.label(card, "ВЫБЕРИ СТИХИЮ", UDim2.new(1, 0, 0, 34), UDim2.new(0, 0, 0, 16), 26,
		PALETTE.accent, Enum.Font.GothamBlack).TextXAlignment = Enum.TextXAlignment.Center
	UIKit.label(card, "Это навсегда. Стихию нельзя поменять.", UDim2.new(1, 0, 0, 20),
		UDim2.new(0, 0, 0, 50), 13, PALETTE.dim).TextXAlignment = Enum.TextXAlignment.Center

	local n = #Config.Elements
	local w = 168
	local total = n * w + (n - 1) * 8
	local startX = (900 - total) / 2
	for i, el in ipairs(Config.Elements) do
		local btn = UIKit.frame(card, UDim2.new(0, w, 0, 300), UDim2.new(0, startX + (i - 1) * (w + 8), 0, 92),
			el.color:Lerp(Color3.fromRGB(12, 10, 16), 0.78), 10, 0)
		UIKit.stroke(btn, el.color, 2, 0.15)
		UIKit.label(btn, el.rune, UDim2.new(1, 0, 0, 64), UDim2.new(0, 0, 0, 20), 46, el.color)
			.TextXAlignment = Enum.TextXAlignment.Center
		UIKit.label(btn, el.name, UDim2.new(1, 0, 0, 24), UDim2.new(0, 0, 0, 88), 18, el.color,
			Enum.Font.GothamBlack).TextXAlignment = Enum.TextXAlignment.Center
		local desc = UIKit.label(btn, el.desc, UDim2.new(1, -16, 0, 100), UDim2.new(0, 8, 0, 118), 11,
			PALETTE.text)
		desc.TextWrapped = true
		desc.TextYAlignment = Enum.TextYAlignment.Top
		desc.TextXAlignment = Enum.TextXAlignment.Center
		UIKit.button(btn, "ВЫБРАТЬ", UDim2.new(1, -20, 0, 34), UDim2.new(0, 10, 1, -46),
			el.color:Lerp(Color3.fromRGB(20, 18, 26), 0.45), function()
				req("Req_ChooseElement"):FireServer(el.id)
				pickWindow.Visible = false
			end)
	end
end

-- ============================================================================
-- ИНВЕНТАРЬ (I)
-- ============================================================================
local invWindow, invContent

local function refreshInventory()
	if not invContent then return end
	for _, child in ipairs(invContent:GetChildren()) do
		if child:GetAttribute("Dynamic") then child:Destroy() end
	end

	local scroll = scrollList(invContent, UDim2.new(1, 0, 1, -34), UDim2.new(0, 0, 0, 0))
	scroll:SetAttribute("Dynamic", true)
	UIKit.label(invContent, "Монет: " .. state.coins .. "   ·   клик по предмету — надеть / использовать",
		UDim2.new(1, 0, 0, 20), UDim2.new(0, 2, 1, -22), 12, PALETTE.dim):SetAttribute("Dynamic", true)

	local cols = 4
	local cw = 240
	local ch = 56
	local i = 0
	for _, inv in pairs(state.items) do
		local def = GameData.ItemById[inv.id]
		if def then
			local col = i % cols
			local row = math.floor(i / cols)
			local rar = GameData.Rarities[def.rarity] or GameData.Rarities.common
			local card = UIKit.frame(scroll, UDim2.new(0, cw - 8, 0, ch), UDim2.new(0, col * cw, 0, row * (ch + 6)),
				PALETTE.panel, 6, 0.05)
			UIKit.stroke(card, rar.color, 1, 0.5)
			UIKit.label(card, def.name .. (inv.count > 1 and (" x" .. inv.count) or ""),
				UDim2.new(1, -12, 0, 18), UDim2.new(0, 8, 0, 4), 12, rar.color, Enum.Font.GothamBold)
			local equipped = false
			for slot, uid in pairs(state.equip) do
				if uid == inv.uid then equipped = true end
			end
			UIKit.label(card, equipped and "надето" or (def.type == "consumable" and "использовать" or def.type),
				UDim2.new(1, -12, 0, 16), UDim2.new(0, 8, 0, 26), 10, PALETTE.dim)

			local btn = UIKit.create("TextButton", {
				Size = UDim2.new(1, 0, 1, 0), BackgroundTransparency = 1, Text = "",
			}, card)
			btn.MouseButton1Click:Connect(function()
				if def.type == "consumable" then
					req("Req_UseItem"):FireServer(inv.uid)
				elseif def.type == "weapon" or def.type == "armor" or def.type == "trinket" then
					req("Req_Equip"):FireServer(inv.uid)
				end
			end)
			i = i + 1
		end
	end
end

local function buildInvWindow()
	invWindow, invContent = makeWindow("InvWindow", "РЮКЗАК", UDim2.new(0, 980, 0, 560))
end

-- ============================================================================
-- ПУБЛИЧНЫЕ ДЕЙСТВИЯ
-- ============================================================================
function Panels.toggleChar()
	charWindow.Visible = not charWindow.Visible
	if charWindow.Visible then refreshStats() end
end

function Panels.toggleSpells()
	spellWindow.Visible = not spellWindow.Visible
	if spellWindow.Visible then
		charWindow.Visible = false
		refreshSpells()
	end
end

function Panels.toggleQuests()
	questWindow.Visible = not questWindow.Visible
	if questWindow.Visible then refreshQuests() end
end

function Panels.toggleInv()
	invWindow.Visible = not invWindow.Visible
	if invWindow.Visible then refreshInventory() end
end

function Panels.closeAll()
	for _, w in ipairs({ charWindow, spellWindow, questWindow, invWindow, dialogWindow }) do
		if w then w.Visible = false end
	end
end

function Panels.init()
	gui = Instance.new("ScreenGui")
	gui.Name = "EmberfallPanels"
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 10
	gui.Parent = playerGui
	remotes = ReplicatedStorage:WaitForChild("Remotes")

	buildCharWindow()
	buildSpellWindow()
	buildQuestWindow()
	buildInvWindow()
	buildDialogWindow()
	buildPickWindow()

	-- «C» — персонаж, повторное нажатие — магия
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed then return end
		local key = input.KeyCode
		if key == Enum.KeyCode.C then
			if charWindow.Visible then Panels.toggleSpells() else Panels.toggleChar() end
		elseif key == Enum.KeyCode.J then
			Panels.toggleQuests()
		elseif key == Enum.KeyCode.I or key == Enum.KeyCode.Tab then
			Panels.toggleInv()
		elseif key == Enum.KeyCode.Escape then
			Panels.closeAll()
		end
	end)

	req("Rep_Stats").OnClientEvent:Connect(function(d)
		if not d then return end
		state.level = d.level or state.level
		state.points = d.points or 0
		state.stats = d.stats or {}
		if charWindow.Visible then refreshStats() end
	end)

	req("Rep_Spells").OnClientEvent:Connect(function(d)
		if not d then return end
		state.spells = d.spells or {}
		state.hotbar = d.hotbar or {}
		state.element = d.element
		if spellWindow.Visible then refreshSpells() end
	end)

	req("Rep_Inventory").OnClientEvent:Connect(function(d)
		if not d then return end
		state.items = d.items or {}
		state.equip = d.equip or {}
		if invWindow.Visible then refreshInventory() end
		if charWindow.Visible then refreshStats() end
	end)

	req("Rep_Quests").OnClientEvent:Connect(function(list)
		state.quests = list or {}
		if questWindow.Visible then refreshQuests() end
	end)

	req("Rep_Vitals").OnClientEvent:Connect(function(d)
		if d then
			state.coins = d.coins or state.coins
			state.level = d.level or state.level
			state.weaponDamage = d.power or state.weaponDamage
			state.armor = d.armor or state.armor
		end
	end)

	req("Rep_Snapshot").OnClientEvent:Connect(function(d)
		if not d then return end
		state.level = d.level or 1
		state.stats = d.stats or {}
		state.points = d.points or 0
		state.element = d.element
		state.spells = d.spells or {}
		state.coins = d.coins or 0
	end)

	req("Rep_Dialog").OnClientEvent:Connect(function(payload)
		if not payload then return end
		dialogTab = payload.role == "shop" and "shop" or "quests"
		ui.lastDialog = payload
		dialogWindow.Visible = true
		if ui.dialogTitle then
			ui.dialogTitle.Text = (payload.name or "NPC") .. (payload.title and ("  —  " .. payload.title) or "")
		end
		for _, c in ipairs(dialogContent:GetChildren()) do
			if c:IsA("ScrollingFrame") then c:Destroy() end
			if c:GetAttribute("Dynamic") then c:Destroy() end
		end
		renderDialog(payload)
	end)

	req("Rep_ElementPick").OnClientEvent:Connect(function()
		pickWindow.Visible = true
	end)
end

return Panels
"""

CLIENT["Fx"] = """-- Emberfall | Fx — визуальные эффекты заклинаний на клиенте (сервер шлёт события).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Fx = {}

local fxFolder

local function makePart(shape, size, color)
	local p = Instance.new("Part")
	p.Shape = shape or Enum.PartType.Ball
	p.Size = size
	p.Color = color or Color3.fromRGB(255, 255, 255)
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Parent = fxFolder
	return p
end

local function boom(pos, color, radius)
	local p = makePart(Enum.PartType.Ball, Vector3.new(2, 2, 2), color)
	p.Position = pos
	Debris:AddItem(p, 1.2)
	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 3
	light.Range = radius or 30
	light.Parent = p
	local tw = TweenService:Create(p, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(radius or 20, radius or 20, radius or 20),
		Transparency = 1,
	})
	tw:Play()

	-- кольцо
	local ring = makePart(Enum.PartType.Cylinder, Vector3.new(0.5, 2, 2), color)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	Debris:AddItem(ring, 1.2)
	local rw = TweenService:Create(ring, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(0.5, (radius or 20) * 1.6, (radius or 20) * 1.6),
		Transparency = 1,
	})
	rw:Play()
end

local function nova(pos, color, radius)
	for i = 0, 16 do
		local a = (i / 16) * math.pi * 2
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local p = makePart(Enum.PartType.Ball, Vector3.new(2.5, 2.5, 2.5), color)
		p.Position = pos + Vector3.new(0, 1, 0)
		Debris:AddItem(p, 1)
		local tw = TweenService:Create(p, TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			Position = p.Position + dir * radius, Size = Vector3.new(1, 1, 1), Transparency = 1,
		})
		tw:Play()
	end
end

local function bolt(pos, color)
	local p = makePart(Enum.PartType.Block, Vector3.new(1.6, 90, 1.6), color)
	p.Position = pos + Vector3.new(0, 45, 0)
	Debris:AddItem(p, 0.6)
	local tw = TweenService:Create(p, TweenInfo.new(0.28), { Transparency = 1, Size = Vector3.new(0.2, 90, 0.2) })
	tw:Play()
	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 4
	light.Range = 40
	light.Parent = p
	boom(pos, color, 10)
end

local function chain(fromPos, toPos, color)
	local dist = (toPos - fromPos).Magnitude
	local beam = makePart(Enum.PartType.Block, Vector3.new(1, 1, dist), color)
	beam.CFrame = CFrame.lookAt((fromPos + toPos) / 2, toPos)
	Debris:AddItem(beam, 0.5)
	TweenService:Create(beam, TweenInfo.new(0.35), { Transparency = 1 }):Play()
end

local function meteorWarn(pos, color, radius, delayTime)
	local ring = makePart(Enum.PartType.Cylinder, Vector3.new(0.4, radius * 2, radius * 2), color)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	ring.Transparency = 0.55
	Debris:AddItem(ring, (delayTime or 0.9) + 0.2)
	task.delay(delayTime or 0.9, function()
		if ring.Parent then
			boom(pos, color, radius * 1.6)
			ring:Destroy()
		end
	end)
end

local function swing(pos, color, hit)
	local p = makePart(Enum.PartType.Block, Vector3.new(3.4, 0.35, 0.35), color)
	p.Position = pos
	Debris:AddItem(p, 0.3)
	TweenService:Create(p, TweenInfo.new(0.22), { Transparency = 1, Size = Vector3.new(5, 0.1, 0.1) }):Play()
end

local function auraFlash(target, color)
	local char = target and target.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local p = makePart(Enum.PartType.Ball, Vector3.new(6, 6, 6), color)
	p.Position = root.Position
	p.Transparency = 0.55
	Debris:AddItem(p, 0.8)
	TweenService:Create(p, TweenInfo.new(0.5, Enum.EasingStyle.Quad), {
		Size = Vector3.new(3, 3, 3), Transparency = 1,
	}):Play()
end

function Fx.init()
	fxFolder = Workspace:FindFirstChild("EmberfallFx")
	if not fxFolder then
		fxFolder = Instance.new("Folder")
		fxFolder.Name = "EmberfallFx"
		fxFolder.Parent = Workspace
	end

	local remotes = ReplicatedStorage:WaitForChild("Remotes")
	remotes:WaitForChild("Rep_CastFx").OnClientEvent:Connect(function(d)
		if not d then return end
		local color = d.color or Color3.fromRGB(200, 200, 255)
		if d.kind == "boom" then
			boom(d.pos, color, d.radius or 20)
		elseif d.kind == "nova" then
			nova(d.pos, color, d.radius or 18)
			boom(d.pos, color, d.radius or 18)
		elseif d.kind == "bolt" then
			bolt(d.pos, color)
		elseif d.kind == "chain" then
			chain(d.from, d.to, color)
		elseif d.kind == "meteor" then
			meteorWarn(d.pos, color, d.radius or 15, d.delay or 0.9)
		elseif d.kind == "dash" then
			boom(d.pos, color, 8)
		elseif d.kind == "buff" or d.kind == "heal" then
			auraFlash(game.Players.LocalPlayer, color)
		elseif d.kind == "swing" then
			swing(d.pos, d.color or Color3.fromRGB(255, 240, 200), d.hit)
		end
	end)
end

return Fx
"""

CLIENT["Controls"] = """-- Emberfall | Controls — ближний бой ЛКМ, спринт на Shift, камера, подсказки.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))

local Controls = {}

local remotes
local baseSpeed = Config.WalkSpeed
local sprinting = false
local stamina = Config.StaminaMax
local lastCombat = 0
local exhaustionUntil = 0

local HUD

-- есть ли под курсором кликабельный элемент интерфейса
local function mouseOverGui()
	local loc = UserInputService:GetMouseLocation()
	local ok, objects = pcall(function()
		return UserInputService:GetGuiObjectsAtPosition(loc.X, loc.Y)
	end)
	if not ok or not objects then return false end
	for _, obj in ipairs(objects) do
		if obj:IsA("GuiButton") or obj:IsA("ScrollingFrame") or obj:IsA("TextBox") then
			return true
		end
	end
	return false
end

local function setupMelee()
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed then return end
		if input.UserInputType ~= Enum.UserInputType.MouseButton1 then return end
		if mouseOverGui() then return end
		Controls.melee()
	end)
end

function Controls.melee()
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return end
	local now = os.clock()
	if now - (Controls._lastMelee or 0) < Config.MeleeCooldown then return end
	Controls._lastMelee = now

	remotes:WaitForChild("Req_Melee"):FireServer()

	-- лёгкая тряска камеры (сам взмах рисует Fx на сервере)
	local cam = workspace.CurrentCamera
	if cam then
		local baseCF = cam.CFrame
		task.delay(0.02, function()
			if cam then
				cam.CFrame = baseCF * CFrame.Angles(math.rad(0.4), 0, math.rad(-0.5))
			end
		end)
	end
end

local function sprintLoop(dt)
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum then return end
	local now = os.clock()

	local wantSprint = UserInputService:IsKeyDown(Enum.KeyCode.LeftShift)
		or UserInputService:IsKeyDown(Enum.KeyCode.RightShift)
	local moving = hum.MoveDirection.Magnitude > 0.1

	if wantSprint and moving and now > exhaustionUntil and stamina > 1 then
		sprinting = true
		stamina = math.max(0, stamina - Config.StaminaSprintDrain * dt)
		if stamina <= 0 then
			exhaustionUntil = now + 1.6
			sprinting = false
			if HUD then HUD.showHint("✖ Выдохся", 1.2) end
		end
	else
		sprinting = false
		if now - lastCombat > Config.StaminaRegenDelay then
			stamina = math.min(Config.StaminaMax, stamina + Config.StaminaRegen * dt)
		end
	end

	local base = hum:GetAttribute("EmberSpeed") or baseSpeed
	if sprinting then
		base = base + 9
	end
	if hum.WalkSpeed < base or hum.WalkSpeed > base then
		hum.WalkSpeed = base
	end

	if HUD then
		HUD.state.stamina = stamina
	end
end

function Controls.init(hudRef)
	HUD = hudRef
	remotes = ReplicatedStorage:WaitForChild("Remotes")

	setupMelee()

	-- базовая скорость из сервера
	remotes:WaitForChild("Rep_Vitals").OnClientEvent:Connect(function(d)
		if d and d.power then
			-- не трогаем, скорость приходит через recompute
		end
		lastCombat = os.clock()
	end)

	player.CharacterAdded:Connect(function(char)
		local hum = char:WaitForChild("Humanoid")
		baseSpeed = hum.WalkSpeed
		stamina = Config.StaminaMax
	end)
	if player.Character then
		local hum = player.Character:FindFirstChildOfClass("Humanoid")
		if hum then baseSpeed = hum.WalkSpeed end
	end

	RunService.Heartbeat:Connect(function(dt)
		sprintLoop(dt)
	end)

	-- подсказки управления при входе
	task.delay(6, function()
		if HUD then
			HUD.showHint("ЛКМ — удар · Цифры 1-6 — заклинания · Shift — бег · C — персонаж · J — задания · I — рюкзак", 9)
		end
	end)
end

return Controls
"""

CLIENT["ClientMain"] = """-- Emberfall | ClientMain — запуск всех клиентских модулей по порядку.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PlayerScripts = script.Parent

local hudModule = PlayerScripts:WaitForChild("HUD")
local HUD = require(hudModule)
local SpellBar = require(PlayerScripts:WaitForChild("SpellBar"))
local Panels = require(PlayerScripts:WaitForChild("Panels"))
local Fx = require(PlayerScripts:WaitForChild("Fx"))
local Controls = require(PlayerScripts:WaitForChild("Controls"))

HUD.init()
_G.EmberfallHUD = HUD   -- быстрый доступ из других модулей
SpellBar.init()
Panels.init()
Fx.init()
Controls.init(HUD)

print("[Emberfall] Клиент v8 загружен")
"""

CLIENT_MODULES = ['UIKit', 'HUD', 'SpellBar', 'Panels', 'Fx', 'Controls']
