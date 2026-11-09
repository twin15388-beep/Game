-- Emberfall | GameData — заклинания, мобы, боссы, предметы, лут.
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
}

-- «Печати призыва»: босса можно вызвать в его зоне, даже если арена пуста
GameData.BossSummons = {
	{ id = "FrostWraith",  seal = "P_FrostWraith",  mats = { { item = "M_IceShard", count = 4 } } },
	{ id = "FrostColossus", seal = "P_FrostColossus", mats = { { item = "M_IceShard", count = 6 }, { item = "M_Ore", count = 4 } } },
	{ id = "SwampMother",  seal = "P_SwampMother",  mats = { { item = "M_BoneDust", count = 5 }, { item = "M_Pelt", count = 3 } } },
	{ id = "CryptWraith",  seal = "P_CryptWraith",  mats = { { item = "M_BoneDust", count = 6 }, { item = "M_AshEssence", count = 3 } } },
	{ id = "Ashlord",      seal = "P_Ashlord",      mats = { { item = "M_AshEssence", count = 6 }, { item = "M_EmberStone", count = 4 } } },
	{ id = "NamelessKing", seal = "P_NamelessKing", mats = { { item = "M_VoidShard", count = 5 }, { item = "M_BoneDust", count = 8 } } },
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
