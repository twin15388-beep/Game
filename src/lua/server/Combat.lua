-- Emberfall | Combat — единая точка нанесения урона, смерти, лута и опыта.
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
