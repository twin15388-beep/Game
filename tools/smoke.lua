-- Прогон игровой логики без Roblox: заглушки API + проверки.
-- Запускается из tools/smoke_test.py, источники приходят в глобальной таблице SRC.

local checks, failures = 0, {}

local function check(name, cond, extra)
	checks = checks + 1
	if not cond then
		table.insert(failures, name .. (extra and (" | " .. tostring(extra)) or ""))
	end
end

-- ============================================================================
-- ЗАГЛУШКИ ROBLOX
-- ============================================================================
local function AnyObject(name)
	local t = { Name = name or "Any" }
	setmetatable(t, {
		__index = function(tb, k)
			if k == "Position" then return Vector3.new(0, 10, 0) end
			if k == "CFrame" then return CFrameStub end
			if k == "Size" then return Vector3.new(4, 4, 4) end
			if k == "Magnitude" then return 0 end
			return setmetatable({}, { __call = function() return AnyObject(k) end, __index = function() return AnyObject(k) end })
		end,
		__newindex = function() end,
	})
	return t
end

CFrameStub = setmetatable({}, {
	__index = function() return CFrameStub end,
	__call = function() return CFrameStub end,
})

-- Vector3
local Vector3 = {}
Vector3.__index = Vector3
function Vector3.new(x, y, z)
	return setmetatable({ X = x or 0, Y = y or 0, Z = z or 0 }, Vector3)
end
function Vector3.__add(a, b) return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
function Vector3.__sub(a, b) return Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
function Vector3.__mul(a, b)
	if type(a) == "number" then return Vector3.new(a * b.X, a * b.Y, a * b.Z) end
	if type(b) == "number" then return Vector3.new(a.X * b, a.Y * b, a.Z * b) end
	return Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
function Vector3.__div(a, b) return Vector3.new(a.X / b, a.Y / b, a.Z / b) end
function Vector3.__eq(a, b) return a.X == b.X and a.Y == b.Y and a.Z == b.Z end
function Vector3:Dot(o) return self.X * o.X + self.Y * o.Y + self.Z * o.Z end
Vector3.__index = function(t, k)
	if k == "Magnitude" then return math.sqrt(t.X ^ 2 + t.Y ^ 2 + t.Z ^ 2) end
	if k == "Unit" then
		local m = math.sqrt(t.X ^ 2 + t.Y ^ 2 + t.Z ^ 2)
		if m == 0 then m = 1 end
		return Vector3.new(t.X / m, t.Y / m, t.Z / m)
	end
	return rawget(Vector3, k)
end
_G.Vector3 = Vector3

-- Color3
local Color3 = {}
function Color3.new(r, g, b) return { R = r or 0, G = g or 0, B = b or 0,
	Lerp = function(self) return self end } end
function Color3.fromRGB(r, g, b) return Color3.new((r or 0) / 255, (g or 0) / 255, (b or 0) / 255) end
_G.Color3 = Color3

-- UDim2 / UDim
local UDim2 = {}
function UDim2.new(...) return AnyObject("UDim2") end
_G.UDim2 = UDim2
_G.UDim = { new = function() return AnyObject("UDim") end }
_G.UDim2 = UDim2
_G.NumberRange = { new = function() return AnyObject() end }
_G.NumberSequence = { new = function() return AnyObject() end }
_G.ColorSequence = { new = function() return AnyObject() end }
_G.Vector2 = { new = function(x, y) return { X = x, Y = y } end }
_G.CFrame = CFrameStub
_G.Instance = { new = function(cls) return AnyObject(cls) end }
_G.typeof = function(v) return type(v) end
_G.Random = { new = function(seed)
	local s = seed or 1
	return {
		NextInteger = function(self, a, b) s = (s * 1103515245 + 12345) % 2147483648
			return a + (s % (b - a + 1)) end,
		NextNumber = function() s = (s * 1103515245 + 12345) % 2147483648
			return s / 2147483648 end,
	}
end }
-- Roblox math.clamp
math.clamp = function(v, lo, hi)
	if v < lo then return lo end
	if v > hi then return hi end
	return v
end
_G.warn = function(...) end
_G.task = {
	wait = function() end,
	delay = function(_, fn) if fn then pcall(fn) end end,
	spawn = function(fn) pcall(fn) end,
}

-- Enum: любой ключ возвращает «значение»
_G.Enum = setmetatable({}, {
	__index = function(_, cat)
		return setmetatable({}, {
			__index = function(_, item)
				return setmetatable({ Name = item }, { __tostring = function() return item end })
			end,
		})
	end,
})

-- ============================================================================
-- "ДЕРЕВО" ИГРЫ
-- ============================================================================
local moduleObjs = {}

local function makeContainer(name)
	local t = { Name = name, _children = {}, _map = {} }
	function t:FindFirstChild(n) return self._map[n] end
	function t:WaitForChild(n) return self._map[n] end
	function t:GetChildren()
		local out = {}
		for _, c in pairs(self._map) do table.insert(out, c) end
		return out
	end
	return t
end

local replicated = makeContainer("ReplicatedStorage")
local SSS = makeContainer("ServerScriptService")
local playersService = makeContainer("Players")

function playersService:GetPlayers() return {} end

local services = {
	ReplicatedStorage = replicated,
	ServerScriptService = SSS,
	Players = playersService,
	Workspace = makeContainer("Workspace"),
	RunService = setmetatable({ Heartbeat = { Connect = function() end },
		RenderStepped = { Connect = function() end } }, { __index = function() return
		{ Connect = function() end } end }),
	TweenService = { Create = function() return { Play = function() end, Completed = { Connect = function() end } } end },
	Debris = { AddItem = function() end },
	Lighting = makeContainer("Lighting"),
	StarterPlayer = makeContainer("StarterPlayer"),
}

_G.game = { GetService = function(_, name) return services[name] or makeContainer(name) end }
_G.workspace = services.Workspace

local shared = makeContainer("EmberfallShared")
local server = makeContainer("EmberfallServer")
replicated._map["EmberfallShared"] = shared
SSS._map["EmberfallServer"] = server

local function registerModule(container, name, src)
	local chunk, err = (loadstring or load)(src, name)
	if not chunk then error("Не загрузился " .. name .. ": " .. tostring(err)) end
	local obj = makeContainer(name)
	obj.__chunk = chunk
	container._map[name] = obj
	moduleObjs[name] = obj
end

for name, src in pairs(SRC.shared) do registerModule(shared, name, src) end
for name, src in pairs(SRC.server) do registerModule(server, name, src) end

-- require: выполняем чанк один раз и кешируем
local cache = {}
_G.require = function(obj)
	if type(obj) == "table" and obj.__chunk then
		if not cache[obj.Name] then
			cache[obj.Name] = obj.__chunk() or true
		end
		return cache[obj.Name]
	end
	return {}
end

-- ============================================================================
-- ТЕСТЫ
-- ============================================================================
local Config = require(shared:WaitForChild("Config"))
local GameData = require(shared:WaitForChild("GameData"))
local Quests = require(shared:WaitForChild("Quests"))
local PlayerState = require(server:WaitForChild("PlayerState"))
local Combat = require(server:WaitForChild("Combat"))
local QuestService = require(server:WaitForChild("QuestService"))

local remotes = makeContainer("Remotes")
local fxFolder = makeContainer("EmberfallFx")

Combat.setup({ remotes = remotes, playerState = PlayerState })
QuestService.setup({ remotes = remotes, playerState = PlayerState, combat = Combat })

-- ------------------------------ данные --------------------------------------
check("Config: стихий 5", #Config.Elements == 5, #Config.Elements)
check("GameData: заклинаний >= 20", #GameData.Spells >= 20, #GameData.Spells)
check("GameData: все заклинания имеют id", (function()
	local ids = {}
	for _, s in ipairs(GameData.Spells) do
		if not s.id or not s.name or not s.element or not s.kind then return false end
		if ids[s.id] then return false end
		ids[s.id] = true
	end
	return true
end)())
check("GameData: у каждого моба есть зона и лут", (function()
	for _, m in ipairs(GameData.Mobs) do
		if not m.zone or not m.loot or #m.loot == 0 then return false end
	end
	return true
end)())
check("GameData: каждая зона с мобами существует в ZoneConfig-списке", (function()
	local zones = { Gloomwood = 1, Frostpeak = 1, Ashwaste = 1, Mirefen = 1,
		SunkenCoast = 1, Bonefields = 1, HollowDeep = 1 }
	for _, m in ipairs(GameData.Mobs) do
		if not zones[m.zone] then return false end
	end
	return true
end)())
check("Quests: цели ссылаются на существующих мобов/боссов/предметы", (function()
	local ok = true
	for _, q in ipairs(Quests.List) do
		for _, obj in ipairs(q.objectives) do
			if obj.type == "kill" and not GameData.MobById[obj.target] then ok = false end
			if obj.type == "boss" and not GameData.BossById[obj.target] then ok = false end
			if obj.type == "collect" and not GameData.ItemById[obj.target] then ok = false end
		end
		for _, item in ipairs(q.rewards.items or {}) do
			if not GameData.ItemById[item.id] then ok = false end
		end
		for _, pre in ipairs(q.prereq or {}) do
			if not Quests.ById[pre] then ok = false end
		end
	end
	return ok
end)())
check("GameData: магазин ссылается на существующие предметы", (function()
	for _, id in ipairs(GameData.ShopStock) do
		if not GameData.ItemById[id] then return false end
	end
	return true
end)())

-- ------------------------------ игрок --------------------------------------
-- минимальный персонаж: Humanoid + RootPart
local humanoid = { Health = 100, MaxHealth = 100, WalkSpeed = 16,
	SetAttribute = function() end, GetAttribute = function() return 16 end }
local rootPart = { Position = Vector3.new(0, 10, 0), Name = "HumanoidRootPart" }
local character = { Name = "Character" }
character._map = { HumanoidRootPart = rootPart, Humanoid = humanoid, Head = rootPart,
	"HumanoidRootPart" }
function character:FindFirstChild(n) return self._map[n] end
function character:WaitForChild(n) return self._map[n] end
function character:FindFirstChildOfClass(cls)
	if cls == "Humanoid" then return humanoid end
	return nil
end
function character:GetPivot() return { Position = Vector3.new(0, 10, 0) } end
function character:IsA(cls) return cls == "Model" end

local fakePlayer = { UserId = 1, Name = "Tester", Parent = AnyObject("Player"),
	DisplayName = "Tester", Character = character }
local st = PlayerState.new(fakePlayer)
PlayerState.recompute(st, nil)
local c = PlayerState.cache(st)
check("PlayerState: базовое здоровье", c.maxHealth == Config.BaseHealth, c.maxHealth)
check("PlayerState: базовая мана", c.maxMana == Config.BaseMana, c.maxMana)

-- опыт и уровни
local ups = PlayerState.addXp(st, 100)
check("Опыт: 100 xp даёт уровень 2", st.level == 2, st.level)
check("Опыт: начислены очки статов", st.statPoints == Config.StartingStatPoints + Config.StatPointsPerLevel, st.statPoints)

-- трата очков
st.stats.Power = st.stats.Power + 1
st.statPoints = st.statPoints - 1
PlayerState.recompute(st, nil)
check("Статы: сила повышает урон", PlayerState.cache(st).powerMult > 1)

-- инвентарь
local uid = PlayerState.addItem(st, "C_HealthPotion", 3)
check("Инвентарь: зелья в стопке", st.inventory[uid].count == 3, st.inventory[uid].count)
local uid2 = PlayerState.addItem(st, "C_HealthPotion", 2)
check("Инвентарь: стопка увеличилась", st.inventory[uid].count == 5, st.inventory[uid].count)
check("Инвентарь: countOf", PlayerState.countOf(st, "C_HealthPotion") == 5)
PlayerState.removeItem(st, uid, 2)
check("Инвентарь: списание", PlayerState.countOf(st, "C_HealthPotion") == 3)

-- экипировка
PlayerState.addItem(st, "W_ShortSword", 1)
local swordUid = PlayerState.findStack(st, "W_ShortSword")
st.equip.weapon = swordUid
PlayerState.recompute(st, nil)
check("Экипировка: урон оружия", PlayerState.cache(st).weaponDamage == 12,
	PlayerState.cache(st).weaponDamage)

-- ------------------------------ бой -----------------------------------------
local killed = 0
Combat.onMobKilled(function() killed = killed + 1 end)

local wolfDef = GameData.MobById.ShadowWolf
local mob = {
	def = wolfDef, health = 1000, maxHealth = 1000, dead = false,
	root = { Position = Vector3.new(0, 10, 0) },
	parts = { head = { Position = Vector3.new(0, 12, 0) } },
	onDamaged = function() end,
}
local dealt = Combat.damageMob(mob, 10, st, { crit = false, silent = true })
check("Бой: урон нанесён", dealt == 10, dealt)
check("Бой: здоровье моба уменьшилось", mob.health == 990, mob.health)

mob.health = 1
Combat.damageMob(mob, 50, st, { crit = false, silent = true })
check("Бой: моб умер", mob.dead == true)
check("Бой: хук убийства вызван", killed == 1, killed)
check("Бой: лут выдан (рюкзак пополнился)", PlayerState.countOf(st, "M_Pelt") >= 0)

-- урон по игроку: без брони урон полный
st.hp = 100
humanoid.Health = 100
local dmgNoArmor = Combat.damagePlayer(st, 30, "test")
check("Бой: без брони урон полный", dmgNoArmor == 30, dmgNoArmor)
check("Бой: hp в состоянии синхронно", st.hp == 70, st.hp)

-- с бронёй урон снижается
PlayerState.addItem(st, "A_Chain", 1)
local armorUid = PlayerState.findStack(st, "A_Chain")
st.equip.armor = armorUid
PlayerState.recompute(st, nil)
st.hp = 100
humanoid.Health = 100
local dmgArmor = Combat.damagePlayer(st, 30, "test")
check("Бой: броня снижает урон", dmgArmor < 30 and dmgArmor > 0, dmgArmor)

-- ------------------------------ квесты --------------------------------------
local accepted = QuestService.accept(st, "Q_FirstSteps")
check("Квест: принят Q_FirstSteps", accepted == true)
check("Квест: счётчик создан", st.quests.Q_FirstSteps ~= nil)

for i = 1, 5 do
	QuestService.onMobKilled(wolfDef, st)
end
check("Квест: прогресс убийств", st.quests.Q_FirstSteps and
	st.quests.Q_FirstSteps.counters[1] == 5, st.quests.Q_FirstSteps and st.quests.Q_FirstSteps.counters[1])
check("Квест: готов к сдаче", st.quests.Q_FirstSteps and st.quests.Q_FirstSteps.state == "ready",
	st.quests.Q_FirstSteps and st.quests.Q_FirstSteps.state)

local coinsBefore = st.coins
local claimed = QuestService.claim(st, "Q_FirstSteps")
check("Квест: сдан", claimed == true)
check("Квест: отмечен выполненным", st.questsDone.Q_FirstSteps == true)
check("Квест: монеты начислены", st.coins > coinsBefore, st.coins .. " vs " .. coinsBefore)

-- квест сбора предметов
QuestService.accept(st, "Q_WelcomeGift")
PlayerState.addItem(st, "M_Pelt", 4)
QuestService.onInventoryChanged(st)
local gift = st.quests.Q_WelcomeGift
check("Квест-сбор: счётчик подхватил предметы", gift and gift.counters[1] == 4,
	gift and gift.counters[1])
check("Квест-сбор: готов", gift and gift.state == "ready", gift and gift.state)

-- предпосылки
local okNext = QuestService.canAccept(st, Quests.ById.Q_GloomTrial)
check("Квест: проверка предпосылок не падает", type(okNext) == "boolean")

-- ------------------------------ урон/мана -----------------------------------
st.mana = 100
local spell = GameData.SpellById.Fire_Ember
check("Заклинания: у базового огня есть урон", spell.damage > 0)

-- проверка всех заклинаний на обязательные поля
check("Заклинания: у всех есть мана/откат", (function()
	for _, s in ipairs(GameData.Spells) do
		if not s.manaCost or not s.cooldown then return false end
		if s.kind == "projectile" and (not s.damage or not s.speed) then return false end
		if s.kind == "meteor" and (not s.radius or not s.fallTime) then return false end
		if s.kind == "buff" and not s.buffType then return false end
		if s.kind == "heal" and not s.healAmount then return false end
	end
	return true
end)())

-- боссы
check("Боссы: у всех есть фазы с способностями", (function()
	local valid = { Slam = 1, Volley = 1, FrostNova = 1, PoisonNova = 1, Meteor = 1, Summon = 1 }
	for _, b in ipairs(GameData.Bosses) do
		if not b.phases or #b.phases == 0 then return false end
		for _, ph in ipairs(b.phases) do
			for _, a in ipairs(ph.abilities) do
				if not valid[a] then return false, a end
			end
		end
		if not b.loot or #b.loot == 0 then return false end
	end
	return true
end)())

-- ============================================================================
-- ФАЗА 2: сервисы мира на подставных маркерах
-- ============================================================================
local MobService = require(server:WaitForChild("MobService"))
local BossService = require(server:WaitForChild("BossService"))

local function marker(name, pos, size)
	local m = { Name = name, Position = pos or Vector3.new(0, 10, 0),
		Size = size or Vector3.new(4, 4, 4), Transparency = 0 }
	function m:IsA(cls) return cls == "BasePart" end
	return m
end

local workspaceService = services.Workspace
function workspaceService:Raycast() return nil end

local gl = makeContainer("GameLogic")
workspaceService._map["GameLogic"] = gl
local mobSpawns = makeContainer("MobSpawns")
gl._map["MobSpawns"] = mobSpawns
local mobList = {}
for i, zone in ipairs({ "Gloomwood", "Gloomwood", "Frostpeak", "Ashwaste",
	"Mirefen", "SunkenCoast", "Bonefields", "HollowDeep", "Bandits" }) do
	local m = marker("MobSpawn_" .. zone .. "_" .. string.format("%02d", i))
	mobSpawns._map[m.Name] = m
	table.insert(mobList, m)
end
function mobSpawns:GetChildren() return mobList end

local bossSpawns = makeContainer("BossSpawns")
local bossList = {}
for _, id in ipairs({ "FrostColossus", "Ashlord", "SwampMother", "NamelessKing",
	"CryptWraith", "FrostWraith" }) do
	local m = marker("BossSpawn_" .. id)
	bossSpawns._map[m.Name] = m
	table.insert(bossList, m)
end
function bossSpawns:GetChildren() return bossList end

local allInstances = {}
for _, m in ipairs(mobList) do table.insert(allInstances, m) end
for _, m in ipairs(bossList) do table.insert(allInstances, m) end
for i, id in ipairs({ "FrostColossus", "Ashlord", "SwampMother", "NamelessKing", "CryptWraith" }) do
	local m = marker("ArenaTrigger_" .. id, Vector3.new(0, 40, 0), Vector3.new(60, 154, 154))
	table.insert(allInstances, m)
end
function workspaceService:GetDescendants() return allInstances end
function workspaceService:FindFirstChild(n) return self._map[n] end

MobService.setup({ remotes = remotes, playerState = PlayerState, combat = Combat,
	fxFolder = fxFolder })
MobService.start()
local points = MobService.spawnPointsForTest and MobService.spawnPointsForTest() or nil

BossService.setup({ remotes = remotes, playerState = PlayerState, combat = Combat,
	mobService = MobService, fxFolder = fxFolder })
local arenas = BossService.arenasForTest and BossService.arenasForTest() or nil

check("MobService: точки спавна собраны (9)", points and #points == 9,
	points and #points or "нет доступа")
check("MobService: лагерь Bandits даёт моба Bandit", (function()
	if not points then return false end
	for _, p in ipairs(points) do
		if p.zone == "Bandits" then return p.def and p.def.id == "Bandit" end
	end
	return false
end)())
check("MobService: у каждой точки есть def", (function()
	if not points then return false end
	for _, p in ipairs(points) do
		if not p.def then return false end
	end
	return true
end)())
check("BossService: арены собраны (>=5)", arenas and #arenas >= 5,
	arenas and #arenas or "нет доступа")
check("BossService: у арены есть радиус", (function()
	if not arenas then return false end
	for _, a in ipairs(arenas) do
		if not a.def or not (a.radius or a.arenaRadius) then return false end
	end
	return true
end)())

-- ============================================================================
-- ИТОГ
-- ============================================================================
print(("Проверок: %d, провалов: %d"):format(checks, #failures))
for _, f in ipairs(failures) do print("  ❌ " .. f) end
return #failures
