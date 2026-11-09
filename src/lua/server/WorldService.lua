-- Emberfall | WorldService — NPC на маркерах, сундуки, зоны, алтарь стихий, лава.
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
