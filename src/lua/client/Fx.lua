-- Emberfall | Fx — визуальные эффекты заклинаний на клиенте (сервер шлёт события).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Fx = {}

local fxFolder

local function makePart(shape, size, color)
	local p = Instance.new("Part")
	p.Shape = shape or Enum.PartType.Ball
	p.Size = size
	p.Color = color or Color3.fromRGB(255, 255, 255)
	p.Material = Enum.Material.Neon
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Parent = fxFolder
	return p
end

local function boom(pos, color, radius)
	local p = makePart(Enum.PartType.Ball, Vector3.new(2, 2, 2), color)
	p.Position = pos
	Debris:AddItem(p, 1.2)
	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 3
	light.Range = radius or 30
	light.Parent = p
	local tw = TweenService:Create(p, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(radius or 20, radius or 20, radius or 20),
		Transparency = 1,
	})
	tw:Play()

	-- кольцо
	local ring = makePart(Enum.PartType.Cylinder, Vector3.new(0.5, 2, 2), color)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	Debris:AddItem(ring, 1.2)
	local rw = TweenService:Create(ring, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(0.5, (radius or 20) * 1.6, (radius or 20) * 1.6),
		Transparency = 1,
	})
	rw:Play()
end

local function nova(pos, color, radius)
	for i = 0, 16 do
		local a = (i / 16) * math.pi * 2
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local p = makePart(Enum.PartType.Ball, Vector3.new(2.5, 2.5, 2.5), color)
		p.Position = pos + Vector3.new(0, 1, 0)
		Debris:AddItem(p, 1)
		local tw = TweenService:Create(p, TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			Position = p.Position + dir * radius, Size = Vector3.new(1, 1, 1), Transparency = 1,
		})
		tw:Play()
	end
end

local function bolt(pos, color)
	local p = makePart(Enum.PartType.Block, Vector3.new(1.6, 90, 1.6), color)
	p.Position = pos + Vector3.new(0, 45, 0)
	Debris:AddItem(p, 0.6)
	local tw = TweenService:Create(p, TweenInfo.new(0.28), { Transparency = 1, Size = Vector3.new(0.2, 90, 0.2) })
	tw:Play()
	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 4
	light.Range = 40
	light.Parent = p
	boom(pos, color, 10)
end

local function chain(fromPos, toPos, color)
	local dist = (toPos - fromPos).Magnitude
	local beam = makePart(Enum.PartType.Block, Vector3.new(1, 1, dist), color)
	beam.CFrame = CFrame.lookAt((fromPos + toPos) / 2, toPos)
	Debris:AddItem(beam, 0.5)
	TweenService:Create(beam, TweenInfo.new(0.35), { Transparency = 1 }):Play()
end

local function meteorWarn(pos, color, radius, delayTime)
	local ring = makePart(Enum.PartType.Cylinder, Vector3.new(0.4, radius * 2, radius * 2), color)
	ring.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	ring.Transparency = 0.55
	Debris:AddItem(ring, (delayTime or 0.9) + 0.2)
	task.delay(delayTime or 0.9, function()
		if ring.Parent then
			boom(pos, color, radius * 1.6)
			ring:Destroy()
		end
	end)
end

local function swing(pos, color, hit)
	local p = makePart(Enum.PartType.Block, Vector3.new(3.4, 0.35, 0.35), color)
	p.Position = pos
	Debris:AddItem(p, 0.3)
	TweenService:Create(p, TweenInfo.new(0.22), { Transparency = 1, Size = Vector3.new(5, 0.1, 0.1) }):Play()
end

local function auraFlash(target, color)
	local char = target and target.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local p = makePart(Enum.PartType.Ball, Vector3.new(6, 6, 6), color)
	p.Position = root.Position
	p.Transparency = 0.55
	Debris:AddItem(p, 0.8)
	TweenService:Create(p, TweenInfo.new(0.5, Enum.EasingStyle.Quad), {
		Size = Vector3.new(3, 3, 3), Transparency = 1,
	}):Play()
end

function Fx.init()
	fxFolder = Workspace:FindFirstChild("EmberfallFx")
	if not fxFolder then
		fxFolder = Instance.new("Folder")
		fxFolder.Name = "EmberfallFx"
		fxFolder.Parent = Workspace
	end

	local remotes = ReplicatedStorage:WaitForChild("Remotes")
	remotes:WaitForChild("Rep_CastFx").OnClientEvent:Connect(function(d)
		if not d then return end
		local color = d.color or Color3.fromRGB(200, 200, 255)
		if d.kind == "boom" then
			boom(d.pos, color, d.radius or 20)
		elseif d.kind == "nova" then
			nova(d.pos, color, d.radius or 18)
			boom(d.pos, color, d.radius or 18)
		elseif d.kind == "bolt" then
			bolt(d.pos, color)
		elseif d.kind == "chain" then
			chain(d.from, d.to, color)
		elseif d.kind == "meteor" then
			meteorWarn(d.pos, color, d.radius or 15, d.delay or 0.9)
		elseif d.kind == "dash" then
			boom(d.pos, color, 8)
		elseif d.kind == "buff" or d.kind == "heal" then
			auraFlash(game.Players.LocalPlayer, color)
		elseif d.kind == "swing" then
			swing(d.pos, d.color or Color3.fromRGB(255, 240, 200), d.hit)
		end
	end)
end

return Fx
