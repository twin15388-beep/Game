-- Emberfall | MobService — спавн мобов по маркерам GameLogic/MobSpawns,
-- погоня, атаки (ближние и дальние), респавн, привязка к земле.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local MobService = {}

local deps               -- { remotes, playerState, combat }
local mobFolder
local mobs = {}          -- массив активных мобов
local spawnPoints = {}   -- { marker, zone, x, y, z, respawnAt, mobId }
local activeRadius = 260
local maxActive = 42
local templateCache = {}

-- зоны-«лагеря» в маркерах -> конкретные мобы
local CAMP_MOB = {
	Bandits  = "Bandit",
	Hunters  = "FrostRenegade",
	Marauders = "Marauder",
	Cult     = "Cultist",
	Fishers  = "Drowned",
}

function MobService.setup(d)
	deps = d
	mobFolder = Instance.new("Folder")
	mobFolder.Name = "EmberfallMobs"
	mobFolder.Parent = Workspace
end

-- ============================================================================
-- МОДЕЛЬ МОБА
-- ============================================================================
local function part(name, size, color, material, shape, transparency)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Shape = shape or Enum.PartType.Block
	p.Transparency = transparency or 0
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	return p
end

local function eyePair(parent, head, def, scale)
	local eyeColor = def.glow and Color3.fromRGB(255, 240, 140) or Color3.fromRGB(255, 90, 60)
	for _, sx in ipairs({ -1, 1 }) do
		local e = part("Eye", Vector3.new(0.28, 0.22, 0.14) * scale, eyeColor, Enum.Material.Neon)
		e.CFrame = head.CFrame * CFrame.new(sx * 0.3 * scale, 0.12 * scale, -0.46 * scale)
		e.Parent = parent
		local w = Instance.new("WeldConstraint")
		w.Part0 = head
		w.Part1 = e
		w.Parent = e
		e.Anchored = false
	end
end

local function buildModel(def)
	-- возвращает Model с якорным корнем; остальные части приварены
	local scale = def.scale or 1
	local model = Instance.new("Model")
	model.Name = def.name

	local col = def.color or Color3.fromRGB(120, 120, 120)
	local mat = Enum.Material.SmoothPlastic
	if def.model == "golem" then mat = Enum.Material.Slate end
	if def.model == "floating" then mat = Enum.Material.Neon end
	if def.model == "beast" then mat = Enum.Material.Fabric end

	local root = part("Root", Vector3.new(2, 2, 2) * scale, col, mat, Enum.PartType.Block, 1)
	root.CanQuery = false
	root.Parent = model
	model.PrimaryPart = root

	-- вспомогательная функция приварки
	local function weld(child, offset, rot)
		local w = Instance.new("WeldConstraint")
		w.Part0 = root
		w.Part1 = child
		w.Parent = child
		child.Anchored = false
		child.CFrame = root.CFrame * offset * (rot or CFrame.new())
		return child
	end

	local parts = { root = root }
	local torsoSize, headSize, limbSize

	if def.model == "beast" then
		torsoSize = Vector3.new(1.8, 1.5, 4.2) * scale
		headSize = Vector3.new(1.5, 1.4, 1.9) * scale
		limbSize = Vector3.new(0.5, 2.0, 0.5) * scale
	elseif def.model == "floating" then
		torsoSize = Vector3.new(2.0, 2.6, 1.3) * scale
		headSize = Vector3.new(1.5, 1.5, 1.5) * scale
		limbSize = Vector3.new(0.5, 2.2, 0.5) * scale
	elseif def.model == "golem" then
		torsoSize = Vector3.new(3.2, 3.2, 2.2) * scale
		headSize = Vector3.new(1.6, 1.5, 1.5) * scale
		limbSize = Vector3.new(1.1, 2.8, 1.1) * scale
	else
		torsoSize = Vector3.new(2.0, 2.2, 1.1) * scale
		headSize = Vector3.new(1.3, 1.3, 1.3) * scale
		limbSize = Vector3.new(0.55, 2.0, 0.55) * scale
	end

	local torso = part("Torso", torsoSize, col, mat)
	torso.Parent = model
	weld(torso, CFrame.new(0, def.model == "beast" and 0.2 * scale or 0, 0))
	parts.torso = torso

	local head = part("Head", headSize, col, mat)
	head.Parent = model
	local headY = (torsoSize.Y / 2 + headSize.Y / 2 + 0.1) * (def.model == "beast" and 0.35 or 1)
	local headZ = def.model == "beast" and (-torsoSize.Z / 2 - headSize.Z / 2 + 0.6 * scale) or 0
	weld(head, CFrame.new(0, headY, headZ))
	parts.head = head
	eyePair(model, head, def, scale)

	-- конечности (для вида; анимация — покачивание)
	local limbOffsets
	if def.model == "beast" then
		limbOffsets = {
			{ -torsoSize.X / 2 + 0.1, -torsoSize.Y / 2, -torsoSize.Z / 3 },
			{ torsoSize.X / 2 - 0.1, -torsoSize.Y / 2, -torsoSize.Z / 3 },
			{ -torsoSize.X / 2 + 0.1, -torsoSize.Y / 2, torsoSize.Z / 3 },
			{ torsoSize.X / 2 - 0.1, -torsoSize.Y / 2, torsoSize.Z / 3 },
		}
	else
		limbOffsets = {
			{ -torsoSize.X / 2 - limbSize.X / 2, -0.1 * scale, 0 },
			{ torsoSize.X / 2 + limbSize.X / 2, -0.1 * scale, 0 },
		}
	end

	parts.limbs = {}
	for i, o in ipairs(limbOffsets) do
		local l = part("Limb" .. i, limbSize, col, mat)
		l.Parent = model
		weld(l, CFrame.new(table.unpack(o)) * CFrame.new(0, -limbSize.Y / 2, 0))
		parts.limbs[i] = l
	end

	-- аура/свечение
	if def.glow then
		local light = Instance.new("PointLight")
		light.Color = col
		light.Brightness = 1.4
		light.Range = 18 * scale
		light.Parent = torso
	end

	-- полоска здоровья над головой (BillboardGui)
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "HpBar"
	billboard.Size = UDim2.new(0, 90 * math.min(scale, 1.6), 0, 14)
	billboard.StudsOffset = Vector3.new(0, headSize.Y + 1.2, 0)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = 140
	billboard.Parent = head

	local bg = Instance.new("Frame")
	bg.Size = UDim2.new(1, 0, 1, 0)
	bg.BackgroundColor3 = Color3.fromRGB(20, 20, 22)
	bg.BackgroundTransparency = 0.35
	bg.BorderSizePixel = 0
	bg.Parent = billboard

	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.new(1, 0, 1, 0)
	fill.BackgroundColor3 = Color3.fromRGB(200, 60, 60)
	fill.BorderSizePixel = 0
	fill.Parent = bg

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = def.name .. "  ур." .. tostring(def.level)
	label.TextColor3 = Color3.fromRGB(255, 255, 255)
	label.TextStrokeTransparency = 0.4
	label.TextScaled = true
	label.Font = Enum.Font.GothamBold
	label.Parent = bg

	return model, parts
end

-- ============================================================================
-- ЗЕМЛЯ
-- ============================================================================
local groundParams
local function ensureParams()
	groundParams = RaycastParams.new()
	groundParams.FilterType = Enum.RaycastFilterType.Exclude
	local ignore = { mobFolder }
	local gl = Workspace:FindFirstChild("GameLogic")
	if gl then table.insert(ignore, gl) end
	for _, name in ipairs({ "EmberfallFx", "EmberfallWorld" }) do
		local f = Workspace:FindFirstChild(name)
		if f then table.insert(ignore, f) end
	end
	groundParams.FilterDescendantsInstances = ignore
	groundParams.IgnoreWater = true
	return groundParams
end

function MobService.groundY(pos)
	local params = ensureParams()
	local origin = Vector3.new(pos.X, pos.Y + 220, pos.Z)
	local result = Workspace:Raycast(origin, Vector3.new(0, -600, 0), params)
	if result then
		return result.Position.Y
	end
	return nil
end

-- ============================================================================
-- СОЗДАНИЕ МОБА
-- ============================================================================
local function nearestPlayer(position, maxDist)
	local best, bestD = nil, maxDist or 1e9
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if root and hum and hum.Health > 0 then
			local d = (root.Position - position).Magnitude
			if d < bestD then best, bestD = pl, d end
		end
	end
	return best, bestD
end

local function shootProjectile(fromPos, targetPlayer, def, damage)
	local char = targetPlayer.Character
	local torso = char and (char:FindFirstChild("HumanoidRootPart") or char:FindFirstChild("Torso"))
	if not torso then return end

	local col = def.color or Color3.fromRGB(200, 100, 255)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(0.9, 0.9, 0.9)
	p.Color = col
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Parent = deps.fxFolder
	p.Position = fromPos

	local start = fromPos
	local target = torso.Position
	local dist = (target - start).Magnitude
	local speed = 70
	local t = dist / speed

	local TweenService = game:GetService("TweenService")
	local tw = TweenService:Create(p, TweenInfo.new(t, Enum.EasingStyle.Linear), { CFrame = CFrame.new(target) })
	tw:Play()
	tw.Completed:Connect(function()
		p:Destroy()
		-- урон, если игрок ещё жив и близко
		local st = deps.playerState.get(targetPlayer)
		if st and st.player.Character then
			local r = st.player.Character:FindFirstChild("HumanoidRootPart")
			if r and (r.Position - target).Magnitude < 14 then
				deps.combat.damagePlayer(st, damage, def.name)
			end
		end
	end)
end

function MobService.spawnMob(def, position)
	local model, parts = buildModel(def)
	model.Parent = mobFolder

	local mob = {
		model = model,
		parts = parts,
		root = parts.root,
		def = def,
		health = def.health,
		maxHealth = def.health,
		dead = false,
		lastAttack = 0,
		lastGroundCheck = 0,
		groundY = position.Y,
		pos = position,
		yaw = math.random() * math.pi * 2,
		speedMult = 1,
		home = position,
		walkPhase = math.random() * 10,
		aggroOn = nil,
	}

	-- обработчик полоски здоровья
	local fill = parts.head:FindFirstChild("HpBar") and parts.head.HpBar:FindFirstChild("Frame"):FindFirstChild("Fill")
	local baseColor = Color3.fromRGB(200, 60, 60)
	mob.setBar = function()
		if not fill then return end
		local ratio = math.clamp(mob.health / mob.maxHealth, 0, 1)
		fill.Size = UDim2.new(ratio, 0, 1, 0)
		if def.isBoss then
			fill.BackgroundColor3 = Color3.fromRGB(180, 40, 220)
		elseif def.elite then
			fill.BackgroundColor3 = Color3.fromRGB(240, 170, 50)
		else
			fill.BackgroundColor3 = baseColor
		end
	end
	mob.setBar()

	mob.onDamaged = function()
		mob.setBar()
		if not mob.aggroOn then
			local pl = nearestPlayer(mob.pos, 90)
			if pl then mob.aggroOn = pl end
		end
	end

	mob.onDeath = function()
		-- эффект смерти
		local root = mob.root
		local burst = Instance.new("Part")
		burst.Shape = Enum.PartType.Ball
		burst.Size = Vector3.new(1, 1, 1)
		burst.Color = def.color or Color3.fromRGB(150, 150, 150)
		burst.Material = Enum.Material.Neon
		burst.Anchored = true
		burst.CanCollide = false
		burst.CanQuery = false
		burst.Position = root.Position
		burst.Parent = deps.fxFolder
		local T = game:GetService("TweenService")
		local tw = T:Create(burst, TweenInfo.new(0.45, Enum.EasingStyle.Quad), {
			Size = Vector3.new(9, 9, 9), Transparency = 1,
		})
		tw:Play()
		tw.Completed:Connect(function() burst:Destroy() end)
		model:Destroy()
	end

	mob.root.CFrame = CFrame.new(position) * CFrame.Angles(0, mob.yaw, 0)
	table.insert(mobs, mob)
	return mob
end

-- ============================================================================
-- ИИ
-- ============================================================================
local function updateMob(mob, dt, now)
	if mob.dead then return end
	local root = mob.root
	if not root or not root.Parent then mob.dead = true return end

	local myPos = root.Position
	-- земля
	if now - mob.lastGroundCheck > 0.35 then
		mob.lastGroundCheck = now
		local gy = MobService.groundY(myPos)
		if gy then mob.groundY = gy end
	end

	local target = mob.aggroOn
	if target and (not target.Parent or not target.Character) then target = nil; mob.aggroOn = nil end
	if target then
		local char = target.Character
		local tr = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if not tr or not hum or hum.Health <= 0 then
			mob.aggroOn = nil
			target = nil
		end
	end

	if not target then
		local pl, d = nearestPlayer(myPos, mob.def.aggro or 55)
		if pl then
			mob.aggroOn = pl
			target = pl
		end
	end

	local moveTo = nil
	local attackRange = mob.def.ranged and (mob.def.ranged - 8) or 6.5

	if target then
		local tr = target.Character.HumanoidRootPart
		local toPlayer = tr.Position - myPos
		local dist = toPlayer.Magnitude
		local dir = Vector3.new(toPlayer.X, 0, toPlayer.Z).Unit

		if dist > attackRange then
			moveTo = myPos + dir * math.min(dist - attackRange + 1, 8)
			mob.yaw = math.atan2(dir.X, dir.Z)
		else
			mob.yaw = math.atan2(toPlayer.X, toPlayer.Z)
			if now - mob.lastAttack > (mob.def.attackCooldown or 1.5) then
				mob.lastAttack = now
				local st = deps.playerState.get(target)
				if st then
					if mob.def.ranged then
						shootProjectile(myPos + Vector3.new(0, 2, 0), target, mob.def, mob.def.damage)
					else
						deps.combat.damagePlayer(st, mob.def.damage, mob.def.name)
					end
				end
			end
		end
	elseif (myPos - mob.home).Magnitude > 45 then
		-- возврат домой
		local dir = (mob.home - myPos)
		dir = Vector3.new(dir.X, 0, dir.Z).Unit
		moveTo = myPos + dir * 6
		mob.yaw = math.atan2(dir.X, dir.Z)
	end

	local newPos = myPos
	if moveTo then
		local speed = (mob.def.speed or 14) * (mob.speedMult or 1) * (mob.enraged and 1.25 or 1)
		local step = Vector3.new(moveTo.X - myPos.X, 0, moveTo.Z - myPos.Z)
		if step.Magnitude > 0.05 then
			step = step.Unit * math.min(speed * dt, step.Magnitude)
			newPos = myPos + step
			mob.walkPhase = mob.walkPhase + dt * 9
		end
	end

	-- держим на земле + покачивание при ходьбе
	local bob = math.sin(mob.walkPhase) * 0.18
	local y = (mob.groundY or myPos.Y) + (mob.def.model == "floating" and 3.2 or 2.2)
	if mob.def.model == "floating" then
		y = y + math.sin(now * 1.6 + mob.walkPhase) * 0.5
	else
		y = y + bob
	end

	local tilt = moveTo and math.sin(mob.walkPhase) * 0.06 or 0
	root.CFrame = CFrame.new(newPos.X, y, newPos.Z) * CFrame.Angles(tilt, mob.yaw, 0)
	mob.pos = root.Position
end

-- ============================================================================
-- СПАВН-ПОИНТЫ
-- ============================================================================
local function chooseMobForZone(zone, rng)
	local explicit = CAMP_MOB[zone]
	if explicit then return GameData.MobById[explicit] end
	local list = GameData.MobsInZone(zone)
	if #list == 0 then return nil end
	return list[rng:NextInteger(1, #list)]
end

function MobService.start()
	local gl = Workspace:FindFirstChild("GameLogic")
	local spawnsFolder = gl and gl:FindFirstChild("MobSpawns")
	if not spawnsFolder then
		warn("[Emberfall] MobSpawns не найдены")
		return
	end

	local rng = Random.new(os.time())
	local count = 0
	for _, marker in ipairs(spawnsFolder:GetChildren()) do
		if marker:IsA("BasePart") and marker.Name:match("^MobSpawn_") then
			local zone = marker.Name:match("^MobSpawn_([^_]+)_")
			local def = chooseMobForZone(zone, rng)
			if def then
				table.insert(spawnPoints, {
					def = def,
					pos = marker.Position,
					marker = marker,
					respawnAt = 0,
					mob = nil,
					zone = zone,
				})
				count = count + 1
			end
		end
	end
	print(("[Emberfall] Точек спавна мобов: %d"):format(count))
end

-- активность: спавним точки рядом с игроками, убираем далёких
local function manageSpawns(now)
	local players = Players:GetPlayers()
	if #players == 0 then return end

	local activeCount = 0
	for _, m in ipairs(mobs) do
		if not m.dead then activeCount = activeCount + 1 end
	end

	for _, sp in ipairs(spawnPoints) do
		local near = false
		for _, pl in ipairs(players) do
			local char = pl.Character
			local root = char and char:FindFirstChild("HumanoidRootPart")
			if root and (root.Position - sp.pos).Magnitude < activeRadius then
				near = true
				break
			end
		end

		if sp.mob and sp.mob.dead then
			sp.mob = nil
			sp.respawnAt = now + 14 + math.random() * 12
		elseif sp.mob and not near then
			-- далеко: убираем, чтобы не жечь ресурсы
			if sp.mob.model then sp.mob.model:Destroy() end
			sp.mob.dead = true
			sp.mob = nil
			sp.respawnAt = now + 1
		end

		if not sp.mob and near and now >= sp.respawnAt and activeCount < maxActive then
			local gy = MobService.groundY(sp.pos)
			local pos = Vector3.new(sp.pos.X, (gy or sp.pos.Y - 1), sp.pos.Z)
			sp.mob = MobService.spawnMob(sp.def, pos)
			activeCount = activeCount + 1
		end
	end

	-- чистка мёртвых
	for i = #mobs, 1, -1 do
		local m = mobs[i]
		if m.dead or not m.model.Parent then table.remove(mobs, i) end
	end
end

-- ============================================================================
-- ПУБЛИЧНЫЙ API
-- ============================================================================
function MobService.getMobsNear(pos, radius)
	local out = {}
	for _, m in ipairs(mobs) do
		if not m.dead and m.root and m.root.Parent then
			if (m.root.Position - pos).Magnitude <= radius then
				table.insert(out, m)
			end
		end
	end
	return out
end

-- доступ для автотестов
function MobService.spawnPointsForTest()
	return spawnPoints
end

function MobService.allMobs()
	return mobs
end

function MobService.startLoop()
	local acc = 0
	local manageAcc = 0
	RunService.Heartbeat:Connect(function(dt)
		local now = os.clock()
		acc = acc + dt
		manageAcc = manageAcc + dt
		if manageAcc > 1.0 then
			manageAcc = 0
			manageSpawns(now)
		end
		for _, m in ipairs(mobs) do
			-- LOD: далёкие мобы думают реже
			local pl = Players:GetPlayers()[1]
			updateMob(m, dt, now)
		end
	end)
end

return MobService
