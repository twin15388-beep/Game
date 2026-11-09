-- Emberfall | Util — мелкие помощники, общие для сервера и клиента.

local Util = {}

function Util.round(n, digits)
	digits = digits or 0
	local m = 10 ^ digits
	return math.floor(n * m + 0.5) / m
end

function Util.clamp(v, lo, hi)
	if v < lo then return lo end
	if v > hi then return hi end
	return v
end

function Util.lerp(a, b, t)
	return a + (b - a) * t
end

function Util.pick(rng, list)
	if #list == 0 then return nil end
	return list[rng:NextInteger(1, #list)]
end

function Util.weighted(rng, entries, key)
	-- entries: { {weight=3, ...}, ... } или {[id]=weight}
	key = key or "weight"
	local total = 0
	for _, e in ipairs(entries) do
		total = total + (e[key] or 1)
	end
	if total <= 0 then return entries[1] end
	local roll = rng:NextNumber() * total
	local acc = 0
	for _, e in ipairs(entries) do
		acc = acc + (e[key] or 1)
		if roll <= acc then return e end
	end
	return entries[#entries]
end

-- Форматирование чисел с разделителями тысяч: 12345 -> "12 345"
function Util.fmtNum(n)
	local s = tostring(math.floor(n + 0.5))
	local out = s:reverse():gsub("(%d%d%d)", "%1 "):reverse()
	return (out:gsub("^%s+", ""))
end

function Util.fmtTime(sec)
	sec = math.max(0, math.floor(sec))
	local m = math.floor(sec / 60)
	local s = sec % 60
	if m <= 0 then return s .. "с" end
	return m .. ":" .. string.format("%02d", s)
end

function Util.inBox(pos, center, halfSize)
	return math.abs(pos.X - center.X) <= halfSize.X
		and math.abs(pos.Y - center.Y) <= halfSize.Y
		and math.abs(pos.Z - center.Z) <= halfSize.Z
end

function Util.horizontalDist(a, b)
	return math.sqrt((a.X - b.X) ^ 2 + (a.Z - b.Z) ^ 2)
end

-- Сортировка списка игроков по близости к точке
function Util.sortedByDistance(list, pos)
	local copy = {}
	for i, v in ipairs(list) do copy[i] = v end
	table.sort(copy, function(a, b)
		return (a - pos).Magnitude < (b - pos).Magnitude
	end)
	return copy
end

return Util
