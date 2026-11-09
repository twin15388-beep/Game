-- Emberfall | Config — все числа баланса и палитра в одном месте.
-- Правка баланса не требует трогать логику.

local Config = {}

Config.Version = "v10"
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
