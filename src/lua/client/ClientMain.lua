-- Emberfall | ClientMain — запуск всех клиентских модулей по порядку.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PlayerScripts = script.Parent

local hudModule = PlayerScripts:WaitForChild("HUD")
local HUD = require(hudModule)
local SpellBar = require(PlayerScripts:WaitForChild("SpellBar"))
local Panels = require(PlayerScripts:WaitForChild("Panels"))
local Fx = require(PlayerScripts:WaitForChild("Fx"))
local Controls = require(PlayerScripts:WaitForChild("Controls"))

HUD.init()
_G.EmberfallHUD = HUD   -- быстрый доступ из других модулей
SpellBar.init()
Panels.init()
Fx.init()
Controls.init(HUD)

print("[Emberfall] Клиент v8 загружен")
