-- Emberfall | Panels — большие окна: персонаж/статы/магия (C),
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
		UIKit.label(questContent, "Заданий нет.\nНайди NPC с золотым «!» над головой — Хранитель Знаний стоит у площади.",
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
