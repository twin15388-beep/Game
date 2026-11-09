-- Emberfall | PlayerState — уровень, статы, инвентарь, экипировка, заклинания.
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
