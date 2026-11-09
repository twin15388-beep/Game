-- Emberfall | Main — точка сборки: создаёт Remotes, связывает сервисы,
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

local STARTER_KIT = {
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
