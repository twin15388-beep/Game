-- Emberfall | MagicService — каст заклинаний, снаряды, зоны, снаряд-визуал.
-- Клиент шлёт только id заклинания; сервер проверяет всё остальное.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Shared = ReplicatedStorage:WaitForChild("EmberfallShared")
local Config = require(Shared:WaitForChild("Config"))
local GameData = require(Shared:WaitForChild("GameData"))
local Net = require(Shared:WaitForChild("Net"))

local MagicService = {}

local deps
local projectileFolder

function MagicService.setup(d)
	deps = d
	projectileFolder = Instance.new("Folder")
	projectileFolder.Name = "EmberfallProjectiles"
	projectileFolder.Parent = deps.fxFolder
end

local function notifyFail(st, reason)
	local r = deps.remotes:FindFirstChild(Net.Rep.CastFail)
	if r then r:FireClient(st.player, { reason = reason }) end
end

local function elementColor(spell)
	local el = Config.ElementById[spell.element]
	return el and el.color or Color3.fromRGB(200, 200, 255)
end

local function makeProjectileVisual(pos, spell, size)
	local color = elementColor(spell)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(size, size, size)
	p.Color = color
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Position = pos
	p.Parent = projectileFolder
	Debris:AddItem(p, 5)

	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 2
	light.Range = 18
	light.Parent = p

	local trail = Instance.new("Trail")
	trail.Color = ColorSequence.new(color)
	trail.Lifetime = 0.28
	trail.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
	trail.WidthScale = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0) })
	trail.Attachment0 = Instance.new("Attachment")
	trail.Attachment0.Parent = p
	trail.Attachment1 = Instance.new("Attachment")
	trail.Attachment1.Parent = p
	trail.Parent = p

	return p
end

-- визуальная вспышка
local function burst(pos, color, radius, duration)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(1, 1, 1)
	p.Color = color
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Position = pos
	p.Parent = projectileFolder
	local tw = TweenService:Create(p, TweenInfo.new(duration or 0.35, Enum.EasingStyle.Quad), {
		Size = Vector3.new(radius * 2, radius * 2, radius * 2), Transparency = 1,
	})
	tw:Play()
	tw.Completed:Connect(function() p:Destroy() end)
end

-- ============================================================================
-- ОБЩИЕ ПРОВЕРКИ
-- ============================================================================
local function validateCast(st, spellId)
	local spell = GameData.SpellById[spellId]
	if not spell then return nil, "нет такого заклинания" end
	if not st.spells[spellId] then return nil, "заклинание не изучено" end
	if st.level < (spell.reqLevel or 1) then return nil, "нужен уровень " .. spell.reqLevel end

	local c = deps.playerState.cache(st)
	local manaCost = spell.manaCost or 10
	if st.mana < manaCost then return nil, "не хватает маны" end

	local now = os.clock()
	local ready = st.cooldowns[spellId] or 0
	if now < ready then return nil, "откат ещё " .. math.ceil(ready - now) .. "с" end

	local character = st.player.Character
	if not character then return nil, "нет персонажа" end
	local hum = character:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then return nil, "нет персонажа" end
	return spell, nil
end

local function applyCooldown(st, spell)
	local c = deps.playerState.cache(st)
	local cd = (spell.cooldown or 1) * (c.cdMult or 1)
	st.cooldowns[spell.id] = os.clock() + cd
end

local function aimPoint(st)
	-- точка прицела клиента: смотрим на mouse.Hit через ремоут клиента
	return st.aimPoint or nil
end

-- ============================================================================
-- НАНЕСЕНИЕ УРОНА ПО ОБЛАСТИ
-- ============================================================================
local function damageMobsInRadius(st, center, radius, spell, opts)
	opts = opts or {}
	local power = deps.playerState.cache(st).powerMult or 1
	local dmg = (spell.damage or 0) * power
	if opts.damageMult then dmg = dmg * opts.damageMult end

	local hitAny = false
	for _, mob in ipairs(deps.mobService.getMobsNear(center, radius)) do
		local d = (mob.root.Position - center).Magnitude
		if d <= radius then
			local falloff = opts.noFalloff and 1 or math.clamp(1 - (d / radius) * 0.45, 0.55, 1)
			deps.combat.damageMob(mob, dmg * falloff, st, {
				lifesteal = spell.lifesteal, kind = "spell",
			})
			if spell.slow then
				-- замедление моба: множитель живёт на самом мобе, не на общем def
				mob.speedMult = spell.slow.mult
				mob.slowToken = (mob.slowToken or 0) + 1
				local token = mob.slowToken
				task.delay(spell.slow.duration, function()
					if mob.slowToken == token then mob.speedMult = 1 end
				end)
			end
			hitAny = true
		end
	end

	-- урон по игрокам не наносим (дружелюбный огонь выключен)

	burst(center, elementColor(spell), radius, 0.45)
	return hitAny
end

-- урон боссу, если он в зоне
local function damageBossIfInRange(st, center, radius, spell, mult)
	local bs = deps.bossService
	local boss = bs and bs.getActiveBoss()
	if not boss or boss.dead then return false end
	if (boss.root.Position - center).Magnitude > radius + 5 then return false end
	local power = deps.playerState.cache(st).powerMult or 1
	deps.combat.damageMob(boss, (spell.damage or 0) * power * (mult or 1), st, {
		lifesteal = spell.lifesteal, kind = "spell",
	})
	return true
end

-- ============================================================================
-- СПОСОБНОСТИ
-- ============================================================================
local function castProjectile(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then notifyFail(st, "нет персонажа") return false end

	local origin = root.Position + Vector3.new(0, 2.2, 0) + root.CFrame.LookVector * 2
	local target = aimPoint(st)
	local dir
	if target then
		dir = (target - origin)
		if dir.Magnitude < 1 then
			dir = root.CFrame.LookVector
		else
			dir = dir.Unit
		end
	else
		dir = root.CFrame.LookVector
	end

	local maxRange = spell.range or 150
	local speed = spell.speed or 100
	local radius = spell.radius or 3

	local proj = makeProjectileVisual(origin, spell, math.clamp(radius * 0.7, 1, 4))
	local traveled = 0
	local done = false

	local function explode(pos)
		deps.combat.broadcast(Net.Rep.CastFx, { kind = "boom", pos = pos, color = elementColor(spell), radius = radius * 2.2 })
		damageMobsInRadius(st, pos, radius + 1.5, spell)
		damageBossIfInRange(st, pos, radius + 3, spell)
		if proj.Parent then proj:Destroy() end
	end

	local conn
	conn = game:GetService("RunService").Heartbeat:Connect(function(dt)
		if done then conn:Disconnect() return end
		if not proj.Parent then done = true conn:Disconnect() return end
		local step = speed * dt
		traveled = traveled + step
		local newPos = proj.Position + dir * step
		proj.Position = newPos

		-- попадание в мобов
		for _, mob in ipairs(deps.mobService.getMobsNear(newPos, radius + 1.5 + 6)) do
			if not mob.dead and (mob.root.Position - newPos).Magnitude < radius + 2.0 then
				conn:Disconnect()
				explode(newPos)
				return
			end
		end

		-- попадание в босса
		local boss = deps.bossService and deps.bossService.getActiveBoss()
		if boss and not boss.dead and (boss.root.Position - newPos).Magnitude < radius + 5 then
			conn:Disconnect()
			explode(newPos)
			return
		end

		-- попадание в землю
		local gy = deps.mobService.groundY(newPos)
		if gy and newPos.Y <= gy + 0.5 then
			conn:Disconnect()
			explode(Vector3.new(newPos.X, gy + 0.5, newPos.Z))
			return
		end

		if traveled >= maxRange then
			conn:Disconnect()
			explode(newPos)
		end
	end)

	return true
end

local function castArea(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	task.delay(spell.castTime or 0.3, function()
		if not character.Parent then return end
		local center = root.Position
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "nova", pos = center, color = elementColor(spell), radius = spell.radius or 20,
		})
		damageMobsInRadius(st, center, spell.radius or 20, spell)
		damageBossIfInRange(st, center, spell.radius or 20, spell)
		if spell.lifesteal then
			deps.combat.healPlayer(st, (spell.damage or 0) * spell.lifesteal, true)
		end
	end)
	return true
end

local function castMeteor(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local target = aimPoint(st) or (root.Position + root.CFrame.LookVector * 40)
	local maxRange = spell.range or 200
	local origin = root.Position
	local delta = target - origin
	if delta.Magnitude > maxRange then
		delta = delta.Unit * maxRange
	end
	local landing = origin + Vector3.new(delta.X, 0, delta.Z)
	local gy = deps.mobService.groundY(landing)
	landing = Vector3.new(landing.X, gy or landing.Y, landing.Z)

	local color = elementColor(spell)

	-- круг предупреждения
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "meteor", pos = landing, color = color,
		radius = spell.radius or 15, delay = spell.fallTime or 0.85,
	})

	-- падающий снаряд
	local fall = Instance.new("Part")
	fall.Shape = Enum.PartType.Ball
	fall.Size = Vector3.new(spell.radius or 15, spell.radius or 15, spell.radius or 15)
	fall.Size = Vector3.new(6, 6, 6)
	fall.Color = color
	fall.Material = Enum.Material.Neon
	fall.Anchored = true
	fall.CanCollide = false
	fall.CanQuery = false
	fall.Position = landing + Vector3.new(0, 150, 0)
	fall.Parent = projectileFolder
	Debris:AddItem(fall, 5)

	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 3
	light.Range = 40
	light.Parent = fall

	local tw = TweenService:Create(fall, TweenInfo.new(spell.fallTime or 0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		Position = landing,
	})
	tw:Play()
	tw.Completed:Connect(function()
		fall:Destroy()
		damageMobsInRadius(st, landing, spell.radius or 15, spell)
		damageBossIfInRange(st, landing, spell.radius or 15, spell)
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "boom", pos = landing, color = color, radius = (spell.radius or 15) * 3,
		})
	end)
	return true
end

local function castDash(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local hum = character:FindFirstChildOfClass("Humanoid")
	local dir = root.CFrame.LookVector
	local dist = spell.distance or 30
	local moved = 0
	local hitSet = {}

	local before = root.Position
	local power = deps.playerState.cache(st).powerMult or 1
	for _, mob in ipairs(deps.mobService.getMobsNear(before, dist + (spell.radius or 7))) do
		-- проверяем, что моб примерно на линии рывка
		local toMob = mob.root.Position - before
		local along = toMob:Dot(dir)
		local perp = (toMob - dir * along).Magnitude
		if along > 0 and along < dist + 6 and perp < (spell.radius or 7) then
			deps.combat.damageMob(mob, (spell.damage or 20) * power, st, { kind = "spell" })
		end
	end

	root.AssemblyLinearVelocity = dir * 95 + Vector3.new(0, 10, 0)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "dash", pos = before, color = elementColor(spell),
	})
	return true
end

local function castBuff(st, spell)
	local now = os.clock()
	table.insert(st.buffs, {
		type = spell.buffType or "power",
		value = spell.buffValue or 0,
		expires = now + (spell.duration or 5),
	})
	deps.playerState.recompute(st, st.player.Character)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "buff", pos = st.player.Character:GetPivot().Position,
		color = elementColor(spell),
	})
	return true
end

local function castHeal(st, spell)
	deps.combat.healPlayer(st, spell.healAmount or 40, false)
	deps.combat.broadcast(Net.Rep.CastFx, {
		kind = "heal", pos = st.player.Character:GetPivot().Position, color = elementColor(spell),
	})
	return true
end

local function castStorm(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local center = root.Position + root.CFrame.LookVector * 25
	local gy = deps.mobService.groundY(center)
	center = Vector3.new(center.X, gy or center.Y, center.Z)
	local strikes = spell.strikes or 5
	for i = 1, strikes do
		task.delay((i - 1) * (spell.duration / strikes), function()
			if not character.Parent then return end
			local point = center + Vector3.new(math.random(-8, 8), 0, math.random(-8, 8))
			local pgy = deps.mobService.groundY(point)
			point = Vector3.new(point.X, pgy or point.Y, point.Z)
			deps.combat.broadcast(Net.Rep.CastFx, {
				kind = "bolt", pos = point, color = elementColor(spell),
			})
			damageMobsInRadius(st, point, spell.radius or 20, spell, { noFalloff = true })
			damageBossIfInRange(st, point, spell.radius or 20, spell)
		end)
	end
	return true
end

local function castChain(st, spell)
	local character = st.player.Character
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return false end
	local targets = deps.mobService.getMobsNear(root.Position, spell.range or 150)
	table.sort(targets, function(a, b)
		return (a.root.Position - root.Position).Magnitude < (b.root.Position - root.Position).Magnitude
	end)
	local maxN = spell.chainTargets or 3
	local lastPos = root.Position
	for i = 1, math.min(maxN, #targets) do
		local mob = targets[i]
		if mob.dead then break end
		deps.combat.broadcast(Net.Rep.CastFx, {
			kind = "chain", from = lastPos, to = mob.root.Position, color = elementColor(spell),
		})
		local falloff = 1 - (i - 1) * 0.25
		deps.combat.damageMob(mob, (spell.damage or 30) * falloff * (deps.playerState.cache(st).powerMult or 1), st, { kind = "spell" })
		lastPos = mob.root.Position
	end
	damageBossIfInRange(st, lastPos, spell.radius or 40, spell)
	return true
end

-- ============================================================================
-- ПУБЛИЧНЫЙ КАСТ
-- ============================================================================
function MagicService.cast(st, spellId, aim)
	st.aimPoint = aim
	local spell, err = validateCast(st, spellId)
	if not spell then
		notifyFail(st, err)
		return false
	end

	st.mana = st.mana - (spell.manaCost or 0)
	st.lastCombat = os.clock()
	applyCooldown(st, spell)
	deps.playerState.sendVitals(st, deps.remotes)

	-- лёгкая анимация каста
	local character = st.player.Character
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	if hum then
		local animator = hum:FindFirstChildOfClass("Animator")
	end

	local kind = spell.kind
	local ok = false
	if kind == "projectile" then
		ok = castProjectile(st, spell)
	elseif kind == "area" then
		ok = castArea(st, spell)
	elseif kind == "meteor" then
		ok = castMeteor(st, spell)
	elseif kind == "dash" then
		ok = castDash(st, spell)
	elseif kind == "buff" then
		ok = castBuff(st, spell)
	elseif kind == "heal" then
		ok = castHeal(st, spell)
	elseif kind == "storm" then
		ok = castStorm(st, spell)
	elseif kind == "chain" then
		ok = castChain(st, spell)
	end

	if not ok then
		-- возвращаем ману и откат
		st.mana = st.mana + (spell.manaCost or 0)
		st.cooldowns[spell.id] = 0
		deps.playerState.sendVitals(st, deps.remotes)
	end
	return ok
end

function MagicService.cooldownRemaining(st, spellId)
	local ready = st.cooldowns[spellId] or 0
	return math.max(0, ready - os.clock())
end

return MagicService
