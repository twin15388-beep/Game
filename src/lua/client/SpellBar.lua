-- Emberfall | SpellBar — 6 слотов заклинаний, откаты, мана, перетаскивание.
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
