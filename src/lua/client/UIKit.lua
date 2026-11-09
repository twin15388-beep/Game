-- Emberfall | UIKit — крошечная библиотека для сборки интерфейса кодом.
local UIKit = {}

function UIKit.create(class, props, parent)
	local inst = Instance.new(class)
	for k, v in pairs(props or {}) do
		if k ~= "Parent" then
			inst[k] = v
		end
	end
	if parent then inst.Parent = parent end
	return inst
end

function UIKit.corner(inst, radius)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius or 8)
	c.Parent = inst
	return c
end

function UIKit.stroke(inst, color, thickness, transparency)
	local s = Instance.new("UIStroke")
	s.Color = color or Color3.fromRGB(120, 100, 60)
	s.Thickness = thickness or 1
	s.Transparency = transparency or 0
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = inst
	return s
end

function UIKit.padding(inst, p)
	local u = Instance.new("UIPadding")
	u.PaddingLeft = UDim.new(0, p)
	u.PaddingRight = UDim.new(0, p)
	u.PaddingTop = UDim.new(0, p)
	u.PaddingBottom = UDim.new(0, p)
	u.Parent = inst
	return u
end

function UIKit.gradient(inst, c1, c2, rotation)
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(c1, c2)
	g.Rotation = rotation or 90
	g.Parent = inst
	return g
end

function UIKit.frame(parent, size, pos, color, radius, transparency)
	local f = UIKit.create("Frame", {
		Size = size,
		Position = pos or UDim2.new(0, 0, 0, 0),
		BackgroundColor3 = color or Color3.fromRGB(18, 18, 24),
		BackgroundTransparency = transparency or 0,
		BorderSizePixel = 0,
		ClipsDescendants = false,
	}, parent)
	if radius then UIKit.corner(f, radius) end
	return f
end

function UIKit.label(parent, text, size, pos, textSize, color, font)
	local l = UIKit.create("TextLabel", {
		Size = size,
		Position = pos or UDim2.new(0, 0, 0, 0),
		BackgroundTransparency = 1,
		Text = text,
		TextSize = textSize or 16,
		TextColor3 = color or Color3.fromRGB(240, 235, 220),
		Font = font or Enum.Font.GothamMedium,
		TextXAlignment = Enum.TextXAlignment.Left,
		RichText = true,
	}, parent)
	return l
end

function UIKit.button(parent, text, size, pos, color, callback)
	local b = UIKit.create("TextButton", {
		Size = size,
		Position = pos,
		BackgroundColor3 = color or Color3.fromRGB(70, 58, 36),
		BorderSizePixel = 0,
		Text = text,
		TextColor3 = Color3.fromRGB(245, 238, 220),
		Font = Enum.Font.GothamBold,
		TextSize = 16,
		AutoButtonColor = true,
	}, parent)
	UIKit.corner(b, 6)
	UIKit.stroke(b, Color3.fromRGB(160, 132, 70), 1, 0.35)
	b.MouseButton1Click:Connect(function()
		if callback then callback() end
	end)
	return b
end

-- Полоска: возвращает { frame, fill, setRatio(0..1), setColor }
function UIKit.bar(parent, size, pos, color, bgColor)
	local back = UIKit.frame(parent, size, pos, bgColor or Color3.fromRGB(30, 30, 38), 6)
	back.ClipsDescendants = true
	back.Name = "BarBg"
	local fill = UIKit.create("Frame", {
		Size = UDim2.new(1, 0, 1, 0),
		BackgroundColor3 = color,
		BorderSizePixel = 0,
	}, back)
	UIKit.corner(fill, 6)
	UIKit.gradient(fill, color:Lerp(Color3.new(1, 1, 1), 0.25), color:Lerp(Color3.new(0, 0, 0), 0.2), 0)
	return {
		frame = back,
		fill = fill,
		setRatio = function(r)
			r = math.clamp(r or 0, 0, 1)
			fill.Size = UDim2.new(r, 0, 1, 0)
		end,
		setColor = function(c)
			fill.BackgroundColor3 = c
		end,
	}
end

return UIKit
