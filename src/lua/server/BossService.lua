-- Emberfall | BossService — боссы на аренах: спавн по входу в ArenaTrigger_*,
-- фазы, способности, полоса HP, анонсы, респавн, лут.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local BossService = {}

local deps
local arenas = {}   -- { def, center, radius, marker, boss, respawnAt }
local activeBoss = nil

local function broadcast(name, ...)
	local r = deps.remotes:FindFirstChild(name)
	if r then r:FireAllClients(...) end
end

local function ringEffect(pos, color, radius, duration)
	local ring = Instance.new("Part")
	ring.Shape = Enum.PartType.Cylinder
	ring.Size = Vector3.new(0.4, radius * 2, radius * 2)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	ring.Color = color
	ring.Material = Enum.Material.Neon
	ring.Transparency = 0.35
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.Parent = deps.fxFolder
	local tw = TweenService:Create(ring, TweenInfo.new(duration or 0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Transparency = 1, Size = Vector3.new(0.4, radius * 3, radius * 3),
	})
	tw:Play()
	tw.Completed:Connect(function() ring:Destroy() end)
	return ring
end

local function damageCircle(center, radius, damage, bossDef, opts)
	opts = opts or {}
	ringEffect(center, opts.color or (bossDef.color or Color3.fromRGB(200, 80, 80)), radius, opts.ringTime or 0.45)
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if root then
			local d = (root.Position - center)
			if Vector3.new(d.X, 0, d.Z).Magnitude <= radius then
				local st = deps.playerState.get(pl)
				if st then
					deps.combat.damagePlayer(st, damage, bossDef.name)
					if opts.slow then
						table.insert(st.buffs, { type = "speed", value = -6, expires = os.clock() + opts.slow })
					end
				end
			end
		end
	end
end

local function meteorStrike(bossDef, targetPos, damage, radius, color)
	-- предупреждение на земле
	local warn = Instance.new("Part")
	warn.Shape = Enum.PartType.Cylinder
	warn.Size = Vector3.new(0.3, radius * 2, radius * 2)
	warn.CFrame = CFrame.new(targetPos) * CFrame.Angles(0, 0, math.rad(90))
	warn.Color = color
	warn.Material = Enum.Material.Neon
	warn.Transparency = 0.55
	warn.Anchored = true
	warn.CanCollide = false
	warn.CanQuery = false
	warn.Parent = deps.fxFolder

	local fall = Instance.new("Part")
	fall.Shape = Enum.PartType.Ball
	fall.Size = Vector3.new(radius * 0.9, radius * 0.9, radius * 0.9)
	fall.Color = color
	fall.Material = Enum.Material.Neon
	fall.Anchored = true
	fall.CanCollide = false
	fall.CanQuery = false
	fall.Position = targetPos + Vector3.new(0, 160, 0)
	fall.Parent = deps.fxFolder

	local tw = TweenService:Create(fall, TweenInfo.new(0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		Position = targetPos,
	})
	tw:Play()
	tw.Completed:Connect(function()
		fall:Destroy()
		warn:Destroy()
		damageCircle(targetPos, radius, damage, bossDef, { color = color, ringTime = 0.6 })
	end)
end

-- ============================================================================
-- СПОСОБНОСТИ
-- ============================================================================
local function abilityVolley(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Залп" })
	local targets = {}
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local r = char and char:FindFirstChild("HumanoidRootPart")
		if r and (r.Position - root.Position).Magnitude < 180 then
			table.insert(targets, pl)
		end
	end
	for i, pl in ipairs(targets) do
		task.delay(i * 0.12, function()
			if boss.dead or not root.Parent then return end
			local char = pl.Character
			local tr = char and char:FindFirstChild("HumanoidRootPart")
			if not tr then return end
			local proj = Instance.new("Part")
			proj.Shape = Enum.PartType.Ball
			proj.Size = Vector3.new(1.6, 1.6, 1.6)
			proj.Color = def.color or Color3.fromRGB(200, 100, 255)
			proj.Material = Enum.Material.Neon
			proj.Anchored = true
			proj.CanCollide = false
			proj.CanQuery = false
			proj.Position = root.Position + Vector3.new(0, 4, 0)
			proj.Parent = deps.fxFolder
			local targetPos = tr.Position
			local dist = (targetPos - proj.Position).Magnitude
			local tw = TweenService:Create(proj, TweenInfo.new(dist / 70, Enum.EasingStyle.Linear), {
				Position = targetPos,
			})
			tw:Play()
			tw.Completed:Connect(function()
				proj:Destroy()
				local st = deps.playerState.get(pl)
				local c = pl.Character
				local rr = c and c:FindFirstChild("HumanoidRootPart")
				if st and rr and (rr.Position - targetPos).Magnitude < 12 then
					deps.combat.damagePlayer(st, def.damage * 0.55, def.name)
				end
			end)
		end)
	end
end

local function abilitySlam(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Сокрушающий удар" })
	task.wait(0.55)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 22, def.damage * 0.8, def, { slow = 0 })
	-- тряска: толкаем игроков
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		if rr and (rr.Position - root.Position).Magnitude < 26 then
			local dir = (rr.Position - root.Position).Unit
			rr.AssemblyLinearVelocity = dir * 55 + Vector3.new(0, 26, 0)
		end
	end
end

local function abilityFrostNova(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Ледяная новая" })
	task.wait(0.4)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 34, def.damage * 0.7, def, {
		color = Color3.fromRGB(150, 220, 255), slow = 4, ringTime = 0.7,
	})
end

local function abilityPoisonNova(boss, def)
	local root = boss.root
	if not root then return end
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Ядовитая волна" })
	task.wait(0.4)
	if boss.dead or not root.Parent then return end
	damageCircle(root.Position, 30, def.damage * 0.5, def, {
		color = Color3.fromRGB(120, 200, 80), ringTime = 0.8,
	})
	-- отравление: тикающий урон
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		if rr and (rr.Position - root.Position).Magnitude < 34 then
			local st = deps.playerState.get(pl)
			if st then
				task.spawn(function()
					for i = 1, 4 do
						task.wait(1)
						if st.hp <= 0 then break end
						deps.combat.damagePlayer(st, def.damage * 0.14, def.name, { trueDamage = true })
					end
				end)
			end
		end
	end
end

local function abilityMeteor(boss, def)
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Метеоритный дождь" })
	local players = Players:GetPlayers()
	for i = 1, 3 do
		task.delay((i - 1) * 0.5, function()
			if boss.dead then return end
			-- цель: случайный игрок, либо случайная точка рядом с боссом
			local pl = players[math.random(1, math.max(1, #players))]
			local char = pl and pl.Character
			local rr = char and char:FindFirstChild("HumanoidRootPart")
			local targetPos
			if rr and (rr.Position - boss.root.Position).Magnitude < 200 then
				targetPos = rr.Position
			else
				targetPos = boss.root.Position + Vector3.new(math.random(-25, 25), 0, math.random(-25, 25))
			end
			local gy = deps.mobService.groundY(targetPos)
			targetPos = Vector3.new(targetPos.X, gy or targetPos.Y, targetPos.Z)
			meteorStrike(def, targetPos, def.damage * 0.85, 14, def.color or Color3.fromRGB(255, 120, 40))
		end)
	end
end

local function abilitySummon(boss, def)
	broadcast(Net.Rep.BossEvent, { event = "ability", id = def.id, name = "Зов слуг" })
	local zone = nil
	for _, z in ipairs({ "Gloomwood", "Frostpeak", "Mirefen", "Ashwaste", "SunkenCoast", "Bonefields", "HollowDeep" }) do
		if def.name == "Ледяной Призрак" or def.name == "Ледяной Колосс" then zone = "Frostpeak" end
	end
	zone = zone or "Bonefields"
	local list = GameData.MobsInZone(zone)
	if #list == 0 then return end
	for i = 1, 2 do
		task.delay(i * 0.25, function()
			if boss.dead then return end
			local angle = math.random() * math.pi * 2
			local off = Vector3.new(math.cos(angle) * 12, 0, math.sin(angle) * 12)
			local def2 = list[math.random(1, #list)]
			local gy = deps.mobService.groundY(boss.root.Position + off)
			local m = deps.mobService.spawnMob(def2, Vector3.new(
				boss.root.Position.X + off.X, gy or boss.root.Position.Y, boss.root.Position.Z + off.Z))
			-- слуги босса агрессивны сразу
			for _, pl in ipairs(Players:GetPlayers()) do
				local rr = pl.Character and pl.Character:FindFirstChild("HumanoidRootPart")
				if rr and (rr.Position - m.root.Position).Magnitude < 90 then
					m.aggroOn = pl
					break
				end
			end
		end)
	end
end

local ABILITIES = {
	Volley = abilityVolley,
	Slam = abilitySlam,
	FrostNova = abilityFrostNova,
	PoisonNova = abilityPoisonNova,
	Meteor = abilityMeteor,
	Summon = abilitySummon,
}

-- ============================================================================
-- ФАЗЫ / БОЙ
-- ============================================================================
local function currentPhase(boss)
	local ratio = boss.health / boss.maxHealth
	local phase = boss.def.phases[1]
	for _, p in ipairs(boss.def.phases) do
		if ratio <= p.at then phase = p end
	end
	return phase
end

local function bossThink(boss, def, now)
	if boss.dead then return end
	local root = boss.root
	if not root or not root.Parent then boss.dead = true return end

	-- фаза
	local phase = currentPhase(boss)
	if boss.phase ~= phase then
		if boss.phase ~= nil then
			broadcast(Net.Rep.BossEvent, {
				event = "phase", id = def.id, name = def.name,
				text = "Фаза " .. (phase == def.phases[#def.phases] and "финальная" or "изменилась") .. "!",
			})
		end
		boss.phase = phase
		if phase.enrage then
			boss.enraged = true
		end
	end

	local phaseAbilities = phase.abilities or { "Slam" }

	-- движение к ближайшему игроку
	local bestPl, bestD = nil, 1e9
	for _, pl in ipairs(Players:GetPlayers()) do
		local char = pl.Character
		local rr = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if rr and hum and hum.Health > 0 then
			local d = (rr.Position - root.Position).Magnitude
			if d < bestD then bestPl, bestD = pl, d end
		end
	end

	if not bestPl then
		boss.idleTime = (boss.idleTime or 0) + 0.1
		boss.lastAttack = now
		return
	end

	local tr = bestPl.Character.HumanoidRootPart
	local toP = tr.Position - root.Position
	local dist = toP.Magnitude
	local dir = Vector3.new(toP.X, 0, toP.Z).Unit

	-- смотрим на игрока
	boss.yaw = math.atan2(toP.X, toP.Z)

	-- подходим, если далеко
	if dist > 16 then
		local speed = (def.baseSpeed or def.speed or 12) * (boss.enraged and 1.35 or 1)
		local step = dir * math.min(speed * 0.1, dist - 16)
		local newPos = root.Position + step
		local gy = deps.mobService.groundY(newPos)
		local y = (gy or root.Position.Y) + 4
		if def.model == "floating" then y = y + 1 end
		root.CFrame = CFrame.new(newPos.X, y, newPos.Z) * CFrame.Angles(0, boss.yaw, 0)
	end

	-- атака
	if now - boss.lastAttack > (boss.attackInterval or 3.2) then
		boss.lastAttack = now
		local abilityName = phaseAbilities[math.random(1, #phaseAbilities)]
		local fn = ABILITIES[abilityName]
		if fn then
			task.spawn(function()
				local ok, err = pcall(fn, boss, def)
				if not ok then warn("[Emberfall] Босс-способность ошибка: " .. tostring(err)) end
			end)
		end
		boss.attackInterval = 2.6 + math.random() * 1.6
	end

	-- ближняя атака вплотную
	if dist < 12 and now - (boss.lastMelee or 0) > 2.0 then
		boss.lastMelee = now
		local st = deps.playerState.get(bestPl)
		if st then deps.combat.damagePlayer(st, def.damage * 0.5, def.name) end
	end
end

-- ============================================================================
-- СПАВН / СМЕРТЬ
-- ============================================================================
local function applyBossBar()
	if not activeBoss or activeBoss.dead then
		broadcast(Net.Rep.BossBar, { visible = false })
		return
	end
	local b = activeBoss
	broadcast(Net.Rep.BossBar, {
		visible = true,
		name = b.def.name,
		title = b.def.title,
		level = b.def.level,
		hp = b.health,
		maxHp = b.maxHealth,
		phase = b.phase and b.phase.at or 1.0,
	})
end

local function spawnBoss(arena, now)
	local def = arena.def
	local markerPos = arena.marker.Position
	local gy = deps.mobService.groundY(markerPos) or markerPos.Y
	local pos = Vector3.new(markerPos.X, gy, markerPos.Z)

	broadcast(Net.Rep.BossEvent, {
		event = "appear", id = def.id, name = def.name, title = def.title, level = def.level,
	})
	broadcast(Net.Rep.BossBar, { visible = true, name = def.name, title = def.title,
		level = def.level, hp = def.health, maxHp = def.health, phase = 1 })

	local defCopy = {}
	for k, v in pairs(def) do defCopy[k] = v end
	defCopy.isBoss = true
	defCopy.baseSpeed = def.speed

	local mob = deps.mobService.spawnMob(defCopy, pos)
	-- боссу увеличиваем полоску (BillboardGui уже есть) — полоса сверху экрана важнее
	mob.isBoss = true
	mob.attackInterval = 3.0
	mob.lastAttack = now

	-- перехватываем onDamaged для полосы
	local origDamaged = mob.onDamaged
	mob.onDamaged = function(dmg, st)
		origDamaged(dmg, st)
		if st then mob.lastAttackerPlayer = st.player end
		applyBossBar()
	end

	mob.onDeath = function()
		-- эффект
		ringEffect(mob.root.Position, def.color or Color3.fromRGB(200, 120, 255), 40, 1.2)
		for i = 1, 6 do
			task.delay(i * 0.15, function()
				local p = mob.root.Position + Vector3.new(math.random(-20, 20), math.random(2, 18), math.random(-20, 20))
				ringEffect(p, def.color or Color3.fromRGB(200, 120, 255), math.random(4, 12), 0.6)
			end)
		end
		mob.model:Destroy()
		activeBoss = nil
		arena.mob = nil
		arena.respawnAt = now + (def.respawn or 180)
		applyBossBar()
	end

	arena.mob = mob
	activeBoss = mob
	return mob
end

-- ============================================================================
-- СБОРКА АРЕН
-- ============================================================================
function BossService.setup(d)
	deps = d
	-- маркеры разложены по папкам биомов внутри Workspace.World
	local bossMarkers = {}
	local arenaMarkers = {}
	for _, inst in ipairs(Workspace:GetDescendants()) do
		if inst:IsA("BasePart") then
			if inst.Name:match("^BossSpawn_") then
				table.insert(bossMarkers, inst)
			elseif inst.Name:match("^ArenaTrigger_") then
				table.insert(arenaMarkers, inst)
			end
		end
	end

	if true then
		for _, marker in ipairs(bossMarkers) do
			do
				local bossId = marker.Name:match("^BossSpawn_(.+)$")
				local def = bossId and GameData.BossById[bossId]
				if def then
					table.insert(arenas, {
						def = def, marker = marker,
						center = marker.Position,
						radius = def.arenaRadius or 70,
						respawnAt = 0, mob = nil,
					})
				end
			end
		end
	end

	if true then
		for _, marker in ipairs(arenaMarkers) do
			do
				local bossId = marker.Name:match("^ArenaTrigger_(.+)$")
				local def = bossId and GameData.BossById[bossId]
				if def then
					local exists = false
					for _, a in ipairs(arenas) do
						if a.def.id == def.id then exists = true end
					end
					if not exists then
						table.insert(arenas, {
							def = def, marker = marker, center = marker.Position,
							radius = def.arenaRadius or 70, respawnAt = 0, mob = nil,
						})
					else
						-- уточняем радиус из маркера арены (Size.Y = r*2)
						for _, a in ipairs(arenas) do
							if a.def.id == def.id then
								a.arenaMarker = marker
								a.arenaRadius = math.floor(marker.Size.Y / 2)
								a.center = marker.Position
							end
						end
					end
				end
			end
		end
	end
	print(("[Emberfall] Арен с боссами: %d"):format(#arenas))
end

function BossService.startLoop()
	local barAcc = 0
	local arenaAcc = 0
	RunService.Heartbeat:Connect(function(dt)
		local now = os.clock()
		arenaAcc = arenaAcc + dt
		barAcc = barAcc + dt

		if barAcc > 0.25 then
			barAcc = 0
			applyBossBar()
			if activeBoss and not activeBoss.dead then
				bossThink(activeBoss, activeBoss.def, now)
			end
		end

		if arenaAcc > 0.5 then
			arenaAcc = 0
			-- проверяем вход на арену
			for _, arena in ipairs(arenas) do
				if not arena.mob and now >= arena.respawnAt then
					local center = arena.arenaMarker and arena.arenaMarker.Position or arena.center
					local r = arena.arenaRadius or arena.radius
					for _, pl in ipairs(Players:GetPlayers()) do
						local char = pl.Character
						local rr = char and char:FindFirstChild("HumanoidRootPart")
						local hum = char and char:FindFirstChildOfClass("Humanoid")
						if rr and hum and hum.Health > 0 then
							local d = rr.Position - center
							if Vector3.new(d.X, 0, d.Z).Magnitude <= r then
								spawnBoss(arena, now)
								break
							end
						end
					end
				end
			end
			-- убрать мёртвого активного босса
			if activeBoss and (activeBoss.dead or not activeBoss.root.Parent) then
				activeBoss = nil
				applyBossBar()
			end
		end
	end)
end

-- доступ для автотестов
function BossService.arenasForTest()
	return arenas
end

function BossService.getActiveBoss()
	return activeBoss
end

return BossService
