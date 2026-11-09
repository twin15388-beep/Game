-- Emberfall | Net — имена Remote-объектов (сервер и клиент читают отсюда).
local Net = {}

Net.FolderName = "Remotes"

-- Client -> Server
Net.Req = {
	UseSpell = "Req_UseSpell",       -- (spellId)
	Melee = "Req_Melee",             -- ()
	Equip = "Req_Equip",             -- (itemUid)
	Unequip = "Req_Unequip",         -- (slotType)
	UseItem = "Req_UseItem",         -- (itemUid)
	SpendStat = "Req_SpendStat",     -- (statId)
	LearnSpell = "Req_LearnSpell",   -- (spellId)
	ChooseElement = "Req_ChooseElement", -- (elementId)
	ShopBuy = "Req_ShopBuy",         -- (itemId)
	ShopSell = "Req_ShopSell",       -- (itemUid)
	QuestAccept = "Req_QuestAccept", -- (questId)
	QuestClaim = "Req_QuestClaim",   -- (questId)
	QuestAbandon = "Req_QuestAbandon", -- (questId)
	Dialog = "Req_Dialog",           -- (npcMarkerName)
	Respawn = "Req_Respawn",         -- ()
	Ping = "Req_Ping",               -- (clientTime)
	Interact = "Req_Interact",       -- (targetInstance)
	Heal = "Req_Heal",               -- (): лечение у лекаря
	BossSummon = "Req_BossSummon",   -- (bossId): крафт «Печати призыва»
}

-- Server -> Client
Net.Rep = {
	Snapshot = "Rep_Snapshot",       -- полное состояние игрока (при входе/смерти/уровне)
	Vitals = "Rep_Vitals",           -- hp/mana/stamina/xp/level/coins
	Inventory = "Rep_Inventory",     -- предметы + экипировка
	Spells = "Rep_Spells",           -- известные заклинания + выбранный хотбар
	Stats = "Rep_Stats",             -- очки характеристик
	Quests = "Rep_Quests",           -- журнал квестов
	Notify = "Rep_Notify",           -- всплывающие сообщения
	CastFail = "Rep_CastFail",       -- почему не скастовалось
	ZoneChanged = "Rep_ZoneChanged", -- вошёл в новую зону
	DialogOpen = "Rep_Dialog",       -- данные окна диалога NPC
	ShopOpen = "Rep_Shop",           -- ассортимент лавки
	DamageNumber = "Rep_Damage",     -- цифры урона над целями
	BossBar = "Rep_BossBar",         -- полоса здоровья босса
	BossEvent = "Rep_BossEvent",     -- анонсы/фазы/смерть босса
	LevelUp = "Rep_LevelUp",         -- эффект повышения уровня
	CastFx = "Rep_CastFx",           -- визуал каста (лучи, вспышки)
	ElementPick = "Rep_ElementPick", -- предложение выбрать стихию
	CombatState = "Rep_Combat",      -- в бою / вне боя
}

function Net.Get(req, folder)
	return folder:FindFirstChild(req)
end

return Net
