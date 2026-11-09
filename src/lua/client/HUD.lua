-- Emberfall | HUD — здоровье, мана, стамина, уровень, опыт, монеты, зона,
-- цифры урона, полоса босса, уведомления, прицел.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local HUD = {}

local function req(name)
	return ReplicatedStorage:WaitForChild("Remotes"):WaitForChild(name)
end

local UIKit = require(script.Parent:WaitForChild("UIKit"))
local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))
local GameData = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("GameData"))

local gui
local ui = {}
local state = {
	hp = 100, maxHp = 100, mana = 100, maxMana = 100,
	stamina = 100, maxStamina = 100,
	level = 1, xp = 0, xpNeed = 100, coins = 0,
	zone = "Пепельная Пристань",
}
HUD.state = state

-- ============================================================================
-- ПОСТРОЕНИЕ
-- ============================================================================
local function build()
	gui = Instance.new("ScreenGui")
	gui.Name = "EmberfallHUD"
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 5
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = playerGui

	-- --------------------------- левый нижний блок ---------------------------
	local statsPanel = UIKit.frame(gui, UDim2.new(0, 330, 0, 118), UDim2.new(0, 18, 1, -136),
		Color3.fromRGB(14, 14, 20), 10, 0.25)
	ui.statsStroke = UIKit.stroke(statsPanel, Color3.fromRGB(150, 124, 66), 1, 0.4)
	ui.statsPanel = statsPanel

	-- уровень
	local lvlCircle = UIKit.frame(statsPanel, UDim2.new(0, 56, 0, 56), UDim2.new(0, 8, 0, -16),
		Color3.fromRGB(40, 34, 48), 28)
	UIKit.stroke(lvlCircle, Color3.fromRGB(220, 186, 110), 2, 0.1)
	ui.levelLabel = UIKit.create("TextLabel", {
		Size = UDim2.new(1, 0, 0.55, 0), Position = UDim2.new(0, 0, 0.1, 0),
		BackgroundTransparency = 1, Text = "1",
		TextColor3 = Color3.fromRGB(255, 230, 160), Font = Enum.Font.GothamBlack, TextSize = 24,
	}, lvlCircle)
	local lvlTag = UIKit.label(lvlCircle, "УР.", UDim2.new(1, 0, 0.3, 0), UDim2.new(0, 0, 0.62, 0), 10,
		Color3.fromRGB(180, 170, 150))
	lvlTag.TextXAlignment = Enum.TextXAlignment.Center

	-- полоски
	local barX = 72
	local barW = 246
	ui.hpBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 16), UDim2.new(0, barX, 0, 6),
		Color3.fromRGB(214, 62, 62))
	ui.hpText = UIKit.label(statsPanel, "100 / 100", UDim2.new(0, barW, 0, 14), UDim2.new(0, barX + 2, 0, 6),
		11, Color3.fromRGB(255, 240, 240), Enum.Font.GothamBold)
	ui.hpText.TextXAlignment = Enum.TextXAlignment.Center

	ui.manaBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 14), UDim2.new(0, barX, 0, 28),
		Color3.fromRGB(80, 140, 240))
	ui.manaText = UIKit.label(statsPanel, "100 / 100", UDim2.new(0, barW, 0, 12), UDim2.new(0, barX + 2, 0, 28),
		10, Color3.fromRGB(230, 240, 255), Enum.Font.GothamBold)
	ui.manaText.TextXAlignment = Enum.TextXAlignment.Center

	ui.staminaBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 10), UDim2.new(0, barX, 0, 46),
		Color3.fromRGB(120, 200, 90))

	ui.xpBar = UIKit.bar(statsPanel, UDim2.new(0, barW, 0, 8), UDim2.new(0, barX, 0, 60),
		Color3.fromRGB(216, 176, 74))
	ui.xpText = UIKit.label(statsPanel, "Опыт 0 / 100", UDim2.new(0, barW, 0, 14), UDim2.new(0, barX, 0, 70),
		10, Color3.fromRGB(230, 212, 160))

	-- монеты
	ui.coinsLabel = UIKit.label(statsPanel, "◈ 0", UDim2.new(0, 150, 0, 18), UDim2.new(0, barX, 0, 88),
		15, Color3.fromRGB(255, 214, 120), Enum.Font.GothamBold)

	-- имя персонажа
	ui.nameLabel = UIKit.label(statsPanel, player.DisplayName, UDim2.new(0, 150, 0, 18),
		UDim2.new(0, barX + 155, 0, 88), 13, Color3.fromRGB(200, 196, 186), Enum.Font.GothamMedium)
	ui.nameLabel.TextXAlignment = Enum.TextXAlignment.Right

	-- --------------------------- зона (верх центр) ---------------------------
	local zoneBox = UIKit.frame(gui, UDim2.new(0, 300, 0, 40), UDim2.new(0.5, -150, 0, 16),
		Color3.fromRGB(12, 12, 18), 8, 0.45)
	UIKit.stroke(zoneBox, Color3.fromRGB(150, 124, 66), 1, 0.5)
	ui.zoneLabel = UIKit.label(zoneBox, "Пепельная Пристань", UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0),
		17, Color3.fromRGB(240, 226, 190), Enum.Font.GothamBold)
	ui.zoneLabel.TextXAlignment = Enum.TextXAlignment.Center

	-- --------------------------- прицел ---------------------------
	local cross = UIKit.frame(gui, UDim2.new(0, 8, 0, 8), UDim2.new(0.5, -4, 0.5, -4),
		Color3.fromRGB(255, 255, 255), 4, 0.55)
	ui.cross = cross

	-- --------------------------- полоса босса ---------------------------
	local bossFrame = UIKit.frame(gui, UDim2.new(0, 620, 0, 76), UDim2.new(0.5, -310, 0, 76),
		Color3.fromRGB(12, 10, 16), 8, 0.15)
	UIKit.stroke(bossFrame, Color3.fromRGB(190, 80, 240), 2, 0.15)
	bossFrame.Visible = false
	ui.bossFrame = bossFrame
	ui.bossName = UIKit.label(bossFrame, "БОСС", UDim2.new(1, -24, 0, 22), UDim2.new(0, 12, 0, 6),
		18, Color3.fromRGB(240, 200, 255), Enum.Font.GothamBlack)
	ui.bossTitle = UIKit.label(bossFrame, "", UDim2.new(0, 300, 0, 16), UDim2.new(0, 12, 0, 26),
		11, Color3.fromRGB(190, 170, 210))
	ui.bossHp = UIKit.bar(bossFrame, UDim2.new(1, -24, 0, 20), UDim2.new(0, 12, 0, 46),
		Color3.fromRGB(190, 50, 200))

	-- --------------------------- уведомления (право верх) ---------------------------
	ui.notifyHolder = UIKit.frame(gui, UDim2.new(0, 330, 0, 300), UDim2.new(1, -350, 0, 120),
		Color3.fromRGB(0, 0, 0), 0, 1)
	ui.notifyHolder.BackgroundTransparency = 1

	-- --------------------------- журнал квестов (левый верх) ---------------------------
	local questBox = UIKit.frame(gui, UDim2.new(0, 280, 0, 24), UDim2.new(0, 18, 0, 90),
		Color3.fromRGB(14, 14, 20), 8, 0.35)
	UIKit.stroke(questBox, Color3.fromRGB(150, 124, 66), 1, 0.5)
	ui.questBox = questBox
	ui.questHeader = UIKit.label(questBox, "ЗАДАНИЯ  [J]", UDim2.new(1, -16, 1, 0), UDim2.new(0, 10, 0, 0),
		13, Color3.fromRGB(230, 210, 160), Enum.Font.GothamBold)
	questBox.Size = UDim2.new(0, 280, 0, 28)

	-- --------------------------- подсказки ---------------------------
	ui.hintLabel = UIKit.label(gui, "", UDim2.new(0, 720, 0, 22), UDim2.new(0.5, -360, 1, -46),
		15, Color3.fromRGB(250, 244, 220), Enum.Font.GothamMedium)
	ui.hintLabel.TextXAlignment = Enum.TextXAlignment.Center
	ui.hintLabel.TextTransparency = 1

	-- --------------------------- смерть ---------------------------
	local death = UIKit.frame(gui, UDim2.new(1, 0, 1, 0), UDim2.new(0, 0, 0, 0),
		Color3.fromRGB(80, 0, 0), 0, 0.55)
	death.Visible = false
	ui.death = death
	UIKit.label(death, "ВЫ ПОГИБЛИ", UDim2.new(1, 0, 0, 60), UDim2.new(0, 0, 0.42, 0),
		46, Color3.fromRGB(255, 90, 90), Enum.Font.GothamBlack).TextXAlignment = Enum.TextXAlignment.Center
	ui.deathSub = UIKit.label(death, "Возрождение...", UDim2.new(1, 0, 0, 30),
		UDim2.new(0, 0, 0.42, 64), 18, Color3.fromRGB(255, 200, 190), Enum.Font.GothamMedium)
	ui.deathSub.TextXAlignment = Enum.TextXAlignment.Center
end

-- ============================================================================
-- ОБНОВЛЕНИЕ
-- ============================================================================
local lastHpText = ""
local function updateVitals(d)
	if not d then return end
	state.hp = d.hp or state.hp
	state.maxHp = d.maxHp or state.maxHp
	state.mana = d.mana or state.mana
	state.maxMana = d.maxMana or state.maxMana
	state.stamina = d.stamina or state.stamina
	state.level = d.level or state.level
	state.xp = d.xp or state.xp
	state.xpNeed = d.xpNeed or state.xpNeed
	state.coins = d.coins or state.coins

	ui.hpBar.setRatio(state.hp / math.max(1, state.maxHp))
	ui.manaBar.setRatio(state.mana / math.max(1, state.maxMana))
	ui.staminaBar.setRatio(state.stamina / math.max(1, state.maxStamina))
	ui.xpBar.setRatio(state.xpNeed > 0 and (state.xp / state.xpNeed) or 1)

	local txt = math.floor(state.hp) .. " / " .. math.floor(state.maxHp)
	if txt ~= lastHpText then
		ui.hpText.Text = txt
		lastHpText = txt
	end
	ui.manaText.Text = math.floor(state.mana) .. " / " .. math.floor(state.maxMana)
	ui.xpText.Text = "Опыт " .. math.floor(state.xp) .. " / " .. (state.xpNeed > 0 and math.floor(state.xpNeed) or "МАКС")
	ui.coinsLabel.Text = "◈ " .. state.coins
	ui.levelLabel.Text = tostring(state.level)

	if state.hp / math.max(1, state.maxHp) < 0.3 then
		ui.hpBar.setColor(Color3.fromRGB(255, 60, 60))
	else
		ui.hpBar.setColor(Color3.fromRGB(214, 62, 62))
	end
end
HUD.updateVitals = updateVitals

-- уведомление
local notifY = 0
local function notify(data)
	if not data then return end
	local kindColors = {
		info = Color3.fromRGB(200, 200, 210),
		level = Color3.fromRGB(255, 220, 110),
		spell = Color3.fromRGB(170, 150, 255),
		loot = Color3.fromRGB(220, 220, 220),
		loot_common = Color3.fromRGB(210, 210, 210),
		loot_uncommon = Color3.fromRGB(130, 230, 130),
		loot_rare = Color3.fromRGB(110, 170, 255),
		loot_epic = Color3.fromRGB(200, 130, 255),
		loot_legendary = Color3.fromRGB(255, 195, 80),
		quest = Color3.fromRGB(255, 220, 110),
		quest_ready = Color3.fromRGB(120, 230, 150),
		quest_done = Color3.fromRGB(140, 255, 160),
		warn = Color3.fromRGB(255, 170, 90),
		bad = Color3.fromRGB(255, 110, 110),
		boss = Color3.fromRGB(220, 140, 255),
		hint = Color3.fromRGB(160, 220, 255),
	}

	local color = kindColors[data.kind or "info"] or kindColors.info
	local item = UIKit.frame(ui.notifyHolder, UDim2.new(1, 0, 0, 30), UDim2.new(0, 0, 0, notifY),
		Color3.fromRGB(16, 16, 22), 6, 0.2)
	UIKit.stroke(item, color, 1, 0.4)
	UIKit.label(item, data.text or "", UDim2.new(1, -14, 1, 0), UDim2.new(0, 8, 0, 0), 13, color,
		Enum.Font.GothamMedium)
	notifY = notifY + 34

	item.Position = UDim2.new(0, 40, 0, notifY - 34)
	TweenService:Create(item, TweenInfo.new(0.25, Enum.EasingStyle.Quad), {
		Position = UDim2.new(0, 0, 0, notifY - 34),
	}):Play()

	task.delay(4.5, function()
		if item.Parent then
			local tw = TweenService:Create(item, TweenInfo.new(0.4), {
				Position = UDim2.new(0, 40, 0, item.Position.Y.Offset), BackgroundTransparency = 1,
			})
			tw:Play()
			tw.Completed:Connect(function() item:Destroy() end)
		end
	end)

	-- пересобрать позиции
	task.delay(0.5, function()
		notifY = 0
		for _, child in ipairs(ui.notifyHolder:GetChildren()) do
			if child:IsA("Frame") and child.Parent and child.BackgroundTransparency < 1 then
				child.Position = UDim2.new(0, 0, 0, notifY)
				notifY = notifY + 34
			end
		end
	end)
end
HUD.notify = notify

-- подсказка внизу
local hintToken = 0
function HUD.showHint(text, duration)
	hintToken = hintToken + 1
	local token = hintToken
	ui.hintLabel.Text = text
	ui.hintLabel.TextTransparency = 0
	task.delay(duration or 2.5, function()
		if token == hintToken then
			TweenService:Create(ui.hintLabel, TweenInfo.new(0.6), { TextTransparency = 1 }):Play()
		end
	end)
end

-- цифры урона
local function damageNumber(data)
	local amount = data.amount or 0
	local isHeal = data.kind == "heal"
	local isCrit = data.kind == "crit"
	local isPlayer = data.kind == "player"

	local color = Color3.fromRGB(255, 235, 210)
	if isHeal then color = Color3.fromRGB(120, 255, 140) end
	if isCrit then color = Color3.fromRGB(255, 190, 60) end
	if isPlayer then color = Color3.fromRGB(255, 120, 120) end

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 120, 0, 44)
	billboard.StudsOffset = Vector3.new(math.random(-2, 2), 2, math.random(-2, 2))
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 220
	billboard.Adornee = nil
	billboard.Parent = gui

	local label = UIKit.create("TextLabel", {
		Size = UDim2.new(1, 0, 1, 0),
		BackgroundTransparency = 1,
		Text = (isHeal and "+" or "") .. tostring(amount) .. (isCrit and "!" or ""),
		TextColor3 = color,
		TextStrokeColor3 = Color3.fromRGB(0, 0, 0),
		TextStrokeTransparency = 0.35,
		Font = isCrit and Enum.Font.GothamBlack or Enum.Font.GothamBold,
		TextSize = isCrit and 30 or (isPlayer and 24 or 22),
	}, billboard)

	-- привязка к позиции через CFrame-точку
	local anchor = Instance.new("Part")
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.Transparency = 1
	anchor.Size = Vector3.new(0.2, 0.2, 0.2)
	anchor.Position = data.pos or Vector3.new(0, 10, 0)
	anchor.Parent = Workspace:FindFirstChild("EmberfallFx") or Workspace
	billboard.Adornee = anchor

	local startY = anchor.Position.Y
	local t0 = os.clock()
	local conn
	conn = RunService.RenderStepped:Connect(function()
		local t = (os.clock() - t0) / 0.85
		if t >= 1 or not anchor.Parent then
			conn:Disconnect()
			anchor:Destroy()
			billboard:Destroy()
			return
		end
		anchor.Position = Vector3.new(anchor.Position.X, startY + t * 5, anchor.Position.Z)
		label.TextTransparency = math.clamp((t - 0.5) * 2, 0, 1)
		label.TextStrokeTransparency = math.clamp(0.35 + (t - 0.5) * 2, 0, 1)
		label.Size = UDim2.new(1, 0, 1, 0)
	end)
end

local function showBossBar(d)
	if not d or not d.visible then
		ui.bossFrame.Visible = false
		return
	end
	ui.bossFrame.Visible = true
	ui.bossName.Text = (d.name or "БОСС") .. "  [ур. " .. tostring(d.level or "?") .. "]"
	ui.bossTitle.Text = d.title or ""
	ui.bossHp.setRatio((d.hp or 0) / math.max(1, d.maxHp or 1))
end

local function showDeath()
	ui.death.Visible = true
	ui.death.BackgroundTransparency = 0.55
	local t = 5
	ui.deathSub.Text = "Возрождение через " .. t .. "с"
	for i = t - 1, 0, -1 do
		task.wait(1)
		ui.deathSub.Text = i > 0 and ("Возрождение через " .. i .. "с") or "Готово"
	end
	ui.death.Visible = false
end

function HUD.init()
	build()
	updateVitals({
		hp = 100, maxHp = 100, mana = 100, maxMana = 100,
		stamina = 100, level = 1, xp = 0, xpNeed = 100, coins = 0,
	})

	req("Rep_Vitals").OnClientEvent:Connect(updateVitals)
	req("Rep_Notify").OnClientEvent:Connect(notify)
	req("Rep_Damage").OnClientEvent:Connect(damageNumber)
	req("Rep_BossBar").OnClientEvent:Connect(showBossBar)
	req("Rep_ZoneChanged").OnClientEvent:Connect(function(d)
		if d and d.name then
			state.zone = d.name
			ui.zoneLabel.Text = d.name
			ui.zoneLabel.TextColor3 = Color3.fromRGB(255, 245, 210)
			TweenService:Create(ui.zoneLabel, TweenInfo.new(0.5), {
				TextColor3 = Color3.fromRGB(240, 226, 190),
			}):Play()
		end
	end)
	req("Rep_Snapshot").OnClientEvent:Connect(updateVitals)
	req("Rep_Combat").OnClientEvent:Connect(function(inCombat)
		-- рамка блока характеристик подсвечивается в бою
		if ui.statsStroke then
			ui.statsStroke.Color = inCombat and Color3.fromRGB(200, 80, 80) or Color3.fromRGB(150, 124, 66)
		end
	end)
	req("Rep_BossEvent").OnClientEvent:Connect(function(d)
		if not d then return end
		if d.event == "world" then
			HUD.showHint("⚔ МИРОВОЙ БОСС: " .. tostring(d.name) .. " — " .. tostring(d.title or ""), 6)
		elseif d.event == "summon" then
			HUD.showHint("⚔ Печать сработала: " .. tostring(d.name) .. " (призвал " .. tostring(d.by or "?") .. ")", 5)
		elseif d.event == "phase" then
			HUD.showHint("☠ " .. tostring(d.name) .. ": " .. tostring(d.text or "новая фаза"), 3)
		elseif d.event == "died" then
			HUD.showHint("Босс повержен: " .. tostring(d.name), 4)
		end
	end)

	req("Rep_LevelUp").OnClientEvent:Connect(function(d)
		HUD.showHint("УРОВЕНЬ " .. tostring(d.level) .. "!", 3)
	end)
	req("Rep_CastFail").OnClientEvent:Connect(function(d)
		if d and d.reason then HUD.showHint("✖ " .. d.reason, 1.5) end
	end)

	-- отслеживаем смерть персонажа
	local function watchCharacter(char)
		local hum = char:WaitForChild("Humanoid")
		hum.Died:Connect(function()
			task.spawn(showDeath)
		end)
	end
	if player.Character then watchCharacter(player.Character) end
	player.CharacterAdded:Connect(watchCharacter)
end

return HUD
