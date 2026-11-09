-- Emberfall | QuestService — прогресс, сдача, награды.
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
