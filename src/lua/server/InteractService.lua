-- Emberfall | InteractService — ProximityPrompt у NPC и сундуков:
-- подошёл, нажал E — открылся диалог/лут. Никаких клавиш не надо.

local Workspace = game:GetService("Workspace")
local Players = game:GetService("Players")

local InteractService = {}

local deps
local lastPrompt = {}

local function cooldown(pl, ms)
	local now = os.clock()
	if lastPrompt[pl] and now - lastPrompt[pl] < (ms or 0.4) then return true end
	lastPrompt[pl] = now
	return false
end

function InteractService.setup(d)
	deps = d

	-- ---------------------------------- NPC ----------------------------------
	for _, npc in ipairs(deps.worldService.allNpcs()) do
		local root = npc.model.PrimaryPart
		if root then
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = npc.data.role == "shop" and "Торговать" or "Говорить"
			prompt.ObjectText = npc.data.name
			prompt.HoldDuration = 0
			prompt.MaxActivationDistance = 14
			prompt.RequiresLineOfSight = false
			prompt.KeyboardKeyCode = Enum.KeyCode.E
			prompt.GamepadKeyCode = Enum.KeyCode.ButtonX
			prompt.Parent = root
			prompt.Triggered:Connect(function(pl)
				if cooldown(pl, 1.0) then return end
				local st = deps.playerState.get(pl)
				if st then deps.worldService.openDialog(st, npc.key) end
			end)
		end
	end

	-- -------------------------------- СУНДУКИ --------------------------------
	for _, chest in ipairs(deps.worldService.allChests()) do
		local body = chest.body
		if body and body.Parent then
			local prompt = Instance.new("ProximityPrompt")
			prompt.ActionText = "Открыть сундук"
			prompt.ObjectText = "Древний сундук"
			prompt.HoldDuration = 0.5
			prompt.MaxActivationDistance = 10
			prompt.RequiresLineOfSight = false
			prompt.KeyboardKeyCode = Enum.KeyCode.E
			prompt.Parent = body
			prompt.Triggered:Connect(function(pl)
				if cooldown(pl, 0.6) then return end
				local st = deps.playerState.get(pl)
				if st then deps.worldService.openChest(st, chest) end
			end)
		end
	end

	print("[Emberfall] Взаимодействия готовы: NPC + сундуки (клавиша E)")
end

return InteractService
