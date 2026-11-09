-- Emberfall | Controls — ближний бой ЛКМ, спринт на Shift, камера, подсказки.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local Config = require(ReplicatedStorage:WaitForChild("EmberfallShared"):WaitForChild("Config"))

local Controls = {}

local remotes
local baseSpeed = Config.WalkSpeed
local sprinting = false
local stamina = Config.StaminaMax
local lastCombat = 0
local exhaustionUntil = 0

local HUD

-- есть ли под курсором кликабельный элемент интерфейса
local function mouseOverGui()
	local loc = UserInputService:GetMouseLocation()
	local ok, objects = pcall(function()
		return UserInputService:GetGuiObjectsAtPosition(loc.X, loc.Y)
	end)
	if not ok or not objects then return false end
	for _, obj in ipairs(objects) do
		if obj:IsA("GuiButton") or obj:IsA("ScrollingFrame") or obj:IsA("TextBox") then
			return true
		end
	end
	return false
end

local function setupMelee()
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed then return end
		if input.UserInputType ~= Enum.UserInputType.MouseButton1 then return end
		if mouseOverGui() then return end
		Controls.melee()
	end)
end

function Controls.melee()
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return end
	local now = os.clock()
	if now - (Controls._lastMelee or 0) < Config.MeleeCooldown then return end
	Controls._lastMelee = now

	remotes:WaitForChild("Req_Melee"):FireServer()

	-- лёгкая тряска камеры (сам взмах рисует Fx на сервере)
	local cam = workspace.CurrentCamera
	if cam then
		local baseCF = cam.CFrame
		task.delay(0.02, function()
			if cam then
				cam.CFrame = baseCF * CFrame.Angles(math.rad(0.4), 0, math.rad(-0.5))
			end
		end)
	end
end

local function sprintLoop(dt)
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum then return end
	local now = os.clock()

	local wantSprint = UserInputService:IsKeyDown(Enum.KeyCode.LeftShift)
		or UserInputService:IsKeyDown(Enum.KeyCode.RightShift)
	local moving = hum.MoveDirection.Magnitude > 0.1

	if wantSprint and moving and now > exhaustionUntil and stamina > 1 then
		sprinting = true
		stamina = math.max(0, stamina - Config.StaminaSprintDrain * dt)
		if stamina <= 0 then
			exhaustionUntil = now + 1.6
			sprinting = false
			if HUD then HUD.showHint("✖ Выдохся", 1.2) end
		end
	else
		sprinting = false
		if now - lastCombat > Config.StaminaRegenDelay then
			stamina = math.min(Config.StaminaMax, stamina + Config.StaminaRegen * dt)
		end
	end

	local base = hum:GetAttribute("EmberSpeed") or baseSpeed
	if sprinting then
		base = base + 9
	end
	if hum.WalkSpeed < base or hum.WalkSpeed > base then
		hum.WalkSpeed = base
	end

	if HUD then
		HUD.state.stamina = stamina
	end
end

function Controls.init(hudRef)
	HUD = hudRef
	remotes = ReplicatedStorage:WaitForChild("Remotes")

	setupMelee()

	-- базовая скорость из сервера
	remotes:WaitForChild("Rep_Vitals").OnClientEvent:Connect(function(d)
		if d and d.power then
			-- не трогаем, скорость приходит через recompute
		end
		lastCombat = os.clock()
	end)

	player.CharacterAdded:Connect(function(char)
		local hum = char:WaitForChild("Humanoid")
		baseSpeed = hum.WalkSpeed
		stamina = Config.StaminaMax
	end)
	if player.Character then
		local hum = player.Character:FindFirstChildOfClass("Humanoid")
		if hum then baseSpeed = hum.WalkSpeed end
	end

	RunService.Heartbeat:Connect(function(dt)
		sprintLoop(dt)
	end)

	-- подсказки управления при входе
	task.delay(6, function()
		if HUD then
			HUD.showHint("ЛКМ — удар · Цифры 1-6 — заклинания · Shift — бег · C — персонаж · J — задания · I — рюкзак", 9)
		end
	end)
end

return Controls
