-- Emberfall | Quests — цепочки заданий.
-- objective: kill / boss / collect / visit / level
local Quests = {}

Quests.List = {
	-- ========================= ПЕПЕЛЬНАЯ ПРИСТАНЬ (хаб) =====================
	{
		id = "Q_FirstSteps", name = "Первые шаги", giver = "QuestKeeper", minLevel = 1,
		desc = "Хранитель знаний хочет убедиться, что ты выживешь за стенами. Убей 5 тварей в любой зоне.",
		objectives = { { type = "killZone", target = "any", count = 5, text = "Убить тварей" } },
		rewards = { xp = 180, coins = 60, items = { { id = "C_HealthPotion", count = 3 } } },
	},
	{
		id = "Q_WelcomeGift", name = "Дар пристани", giver = "Merchant", minLevel = 1,
		desc = "Торговец ищет шкуры для пошива. Принеси 4 шкуры из Глумвуда.",
		objectives = { { type = "collect", target = "M_Pelt", count = 4, text = "Собрать шкур" } },
		rewards = { xp = 220, coins = 120, items = { { id = "W_ShortSword", count = 1 } } },
	},
	{
		id = "Q_FirstSpell", name = "Первый ритуал", giver = "QuestKeeper", minLevel = 2,
		prereq = { "Q_FirstSteps" },
		desc = "Пора выбрать стихию. Подойди к алтарю у площади и коснись его.",
		objectives = { { type = "flag", target = "choseElement", count = 1, text = "Выбрать стихию" } },
		rewards = { xp = 260, coins = 80, items = { { id = "C_ManaPotion", count = 3 } } },
	},
	{
		id = "Q_BlacksmithOre", name = "Кузнецу нужна руда", giver = "Blacksmith", minLevel = 4,
		desc = "Кузнец Гарм просит 6 кусков руды. Руду роняют гоблины и разбойники.",
		objectives = { { type = "collect", target = "M_Ore", count = 6, text = "Собрать руды" } },
		rewards = { xp = 420, coins = 200, items = { { id = "A_Chain", count = 1 } } },
	},
	{
		id = "Q_GateGuard", name = "Стража ворот", giver = "GateCaptain", minLevel = 6,
		desc = "Капрал просит проредить разбойников у западного тракта: убей 6 разбойников.",
		objectives = { { type = "kill", target = "Bandit", count = 6, text = "Убить разбойников" } },
		rewards = { xp = 650, coins = 260, items = { { id = "W_Sabre", count = 1 } } },
	},

	-- ============================== ГЛУМВУД ==================================
	{
		id = "Q_Wolves", name = "Волчья напасть", giver = "Herbalist", minLevel = 8,
		desc = "Травница Тенегрива: теневые волки рвут скот. Убей 8 теневых волков.",
		objectives = { { type = "kill", target = "ShadowWolf", count = 8, text = "Убить теневых волков" } },
		rewards = { xp = 800, coins = 300, items = { { id = "C_HealthPotion", count = 5 }, { id = "T_EmberCharm", count = 1 } } },
	},
	{
		id = "Q_ForestHorror", name = "Ужас чащи", giver = "Hunter", minLevel = 14,
		desc = "Охотник видел нечто огромное между деревьями. Убей Лесного ужаса.",
		objectives = { { type = "kill", target = "ForestHorror", count = 1, text = "Убить Лесного ужаса" } },
		rewards = { xp = 1200, coins = 450, items = { { id = "T_SwiftCharm", count = 1 } } },
	},
	{
		id = "Q_GloomTrial", name = "Испытание Глумвуда", giver = "QuestKeeper", minLevel = 12,
		prereq = { "Q_FirstSpell" },
		desc = "Испытание леса: убей 10 любых тварей Глумвуда и вернись.",
		objectives = { { type = "killZone", target = "Gloomwood", count = 10, text = "Убить в Глумвуде" } },
		rewards = { xp = 1400, coins = 500, items = { { id = "A_Chain", count = 1 } } },
	},

	-- ============================ МОРОЗНЫЕ ПИКИ ==============================
	{
		id = "Q_FrozenPass", name = "Мёрзлый перевал", giver = "Farmer", minLevel = 20,
		desc = "Фермер с хутора слышал вой с перевала. Убей 8 морозных волков.",
		objectives = { { type = "kill", target = "FrostWolf", count = 8, text = "Убить морозных волков" } },
		rewards = { xp = 2100, coins = 700, items = { { id = "C_ManaPotion", count = 5 } } },
	},
	{
		id = "Q_BossFrost", name = "Страж гробницы", giver = "QuestKeeper", minLevel = 26,
		prereq = { "Q_FrozenPass" },
		desc = "Ледяной Призрак стережёт древнюю гробницу. Уничтожь его.",
		objectives = { { type = "boss", target = "FrostWraith", count = 1, text = "Победить Ледяного Призрака" } },
		rewards = { xp = 4000, coins = 1500, items = { { id = "W_FrostBlade", count = 1 }, { id = "C_Elixir", count = 2 } }, statPoints = 1 },
	},
	{
		id = "Q_Colossus", name = "Колосс пробудился", giver = "QuestKeeper", minLevel = 32,
		prereq = { "Q_BossFrost" },
		desc = "На арене Морозных Пиков стоит Ледяной Колосс. Сокруши титана.",
		objectives = { { type = "boss", target = "FrostColossus", count = 1, text = "Победить Ледяного Колосса" } },
		rewards = { xp = 7000, coins = 2600, items = { { id = "A_FrostPlate", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ЗАТОНУВШИЙ БЕРЕГ ===========================
	{
		id = "Q_DrownedFleet", name = "Затонувший флот", giver = "Portmaster", minLevel = 16,
		desc = "Портмейстер: утопленники лезут на причалы. Убей 10 утопленников.",
		objectives = { { type = "kill", target = "Drowned", count = 10, text = "Убить утопленников" } },
		rewards = { xp = 1600, coins = 600, items = { { id = "C_HealthPotion", count = 6 } } },
	},
	{
		id = "Q_PirateGold", name = "Проклятое золото", giver = "Fishmonger", minLevel = 18,
		desc = "Рыботорговец нашёл монету с проклятием. Убей 6 пиратов-мертвецов.",
		objectives = { { type = "kill", target = "PirateDead", count = 6, text = "Убить пиратов-мертвецов" } },
		rewards = { xp = 1800, coins = 800, items = { { id = "T_SwiftCharm", count = 1 } } },
	},

	-- ============================ ТОПИ МИРЕФЕН ===============================
	{
		id = "Q_MireHerbs", name = "Болотные травы", giver = "Herbalist", minLevel = 24,
		desc = "Травнице нужны костяная пыль и эссенции. Принеси 5 костяной пыли.",
		objectives = { { type = "collect", target = "M_BoneDust", count = 5, text = "Собрать костяной пыли" } },
		rewards = { xp = 2600, coins = 900, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_SwampMother", name = "Мать Болот", giver = "QuestKeeper", minLevel = 34,
		desc = "Остров в Топях Мирефен — логово Матери Болот. Убей её.",
		objectives = { { type = "boss", target = "SwampMother", count = 1, text = "Победить Мать Болот" } },
		rewards = { xp = 9000, coins = 3200, items = { { id = "T_FocusCharm", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ПЕПЕЛЬНЫЕ ПУСТОШИ ==========================
	{
		id = "Q_AshCull", name = "Пепельная чистка", giver = "GateCaptain", minLevel = 36,
		desc = "Пустоши кишат пепельными псами. Убей 12.",
		objectives = { { type = "kill", target = "AshHound", count = 12, text = "Убить пепельных псов" } },
		rewards = { xp = 5200, coins = 1800, items = { { id = "C_Elixir", count = 2 } } },
	},
	{
		id = "Q_Ashlord", name = "Владыка Пепла", giver = "QuestKeeper", minLevel = 42,
		prereq = { "Q_Colossus" },
		desc = "Пепельный Владыка ждёт на арене Пустошей. Положи конец его власти.",
		objectives = { { type = "boss", target = "Ashlord", count = 1, text = "Победить Пепельного Владыку" } },
		rewards = { xp = 14000, coins = 5000, items = { { id = "W_AshCleaver", count = 1 }, { id = "A_AshPlate", count = 1 } }, statPoints = 1 },
	},

	-- ============================ КОСТЯНЫЕ ПОЛЯ ==============================
	{
		id = "Q_BoneTide", name = "Костяной прилив", giver = "Healer", minLevel = 30,
		desc = "Лекарь пристани: нежить поднимается волнами. Убей 12 скелетов.",
		objectives = { { type = "kill", target = "Skeleton", count = 12, text = "Убить скелетов" } },
		rewards = { xp = 4800, coins = 1600, items = { { id = "C_HealthPotion", count = 8 } } },
	},
	{
		id = "Q_Cult", name = "Тайный культ", giver = "GateCaptain", minLevel = 38,
		desc = "Культисты собираются у кладбища. Убей 8 культистов и их вожаков.",
		objectives = { { type = "kill", target = "Cultist", count = 8, text = "Убить культистов" } },
		rewards = { xp = 6000, coins = 2200, items = { { id = "T_BloodCharm", count = 1 } } },
	},
	{
		id = "Q_CryptWraith", name = "Склепный призрак", giver = "QuestKeeper", minLevel = 44,
		prereq = { "Q_BoneTide" },
		desc = "В крипте Костяных Полей заперт Склепный Призрак. Открой склеп и уничтожь его.",
		objectives = { { type = "boss", target = "CryptWraith", count = 1, text = "Победить Склепного Призрака" } },
		rewards = { xp = 16000, coins = 5600, items = { { id = "W_BoneScythe", count = 1 } }, statPoints = 1 },
	},

	-- ============================ ПРЕДГОРЬЯ ==================================
	{
		id = "Q_Trolls", name = "Тролльи тропы", giver = "Highlander", minLevel = 27,
		desc = "Горец Бран: каменные тролли раздавили торговый караван. Убей 5 троллей.",
		objectives = { { type = "kill", target = "RockTroll", count = 5, text = "Убить каменных троллей" } },
		rewards = { xp = 3600, coins = 1200, items = { { id = "A_AshPlate", count = 1 } } },
	},
	{
		id = "Q_MineShadows", name = "Тени шахты", giver = "Miner", minLevel = 25,
		desc = "Шахтёр Гром: из забоя лезут гули. Убей 10 шахтных гулей.",
		objectives = { { type = "kill", target = "MinerGhoul", count = 10, text = "Убить шахтных гулей" } },
		rewards = { xp = 3200, coins = 1100, items = { { id = "M_Ore", count = 8 } } },
	},
	{
		id = "Q_Highway", name = "Горный тракт", giver = "Highlander", minLevel = 30,
		desc = "Горные разбойники грабят предгорья. Убей 8.",
		objectives = { { type = "kill", target = "Highwayman", count = 8, text = "Убить горных разбойников" } },
		rewards = { xp = 4200, coins = 1500, items = { { id = "C_Elixir", count = 2 } } },
	},

	-- ============================ АРХИПЕЛАГ ==================================
	{
		id = "Q_PiratesBane", name = "Гибель пиратов", giver = "Pirate", minLevel = 32,
		desc = "Кровавый Джо хочет покоя: убей 8 пиратов-капитанов.",
		objectives = { { type = "kill", target = "PirateLord", count = 8, text = "Убить пиратских капитанов" } },
		rewards = { xp = 6000, coins = 2200, items = { { id = "T_BloodCharm", count = 1 } } },
	},
	{
		id = "Q_SeaWraiths", name = "Призраки архипелага", giver = "Pirate", minLevel = 30,
		desc = "Морские призраки не дают рыбачить. Убей 10.",
		objectives = { { type = "kill", target = "SeaWraith", count = 10, text = "Убить морских призраков" } },
		rewards = { xp = 5200, coins = 1900, items = { { id = "C_ManaPotion", count = 6 } } },
	},

	-- ============================ ЮЖНЫЕ ОСТРОВА ==============================
	{
		id = "Q_Coral", name = "Коралловый риф", giver = "Fishmonger", minLevel = 22,
		desc = "Рыбак просит кораллы: принеси 4.",
		objectives = { { type = "collect", target = "M_Coral", count = 4, text = "Собрать кораллы" } },
		rewards = { xp = 2600, coins = 900, items = { { id = "T_SwiftCharm", count = 1 } } },
	},
	{
		id = "Q_BeachRaiders", name = "Налётчики", giver = "Farmer", minLevel = 24,
		desc = "Береговые налётчики жгут дома. Убей 8.",
		objectives = { { type = "kill", target = "BeachRaider", count = 8, text = "Убить налётчиков" } },
		rewards = { xp = 3000, coins = 1000, items = { { id = "C_HealthPotion", count = 6 } } },
	},
	{
		id = "Q_FrostWind", name = "Ветроград", giver = "Villager", minLevel = 28,
		desc = "Житель Ветрограда просит зачистить морозных волков у стен.",
		objectives = { { type = "kill", target = "FrostWolf", count = 12, text = "Убить морозных волков" } },
		rewards = { xp = 4600, coins = 1600, items = { { id = "A_FrostPlate", count = 1 } } },
	},

	-- ============================ ПОЛАЯ БЕЗДНА ===============================
	{
		id = "Q_VoidShards", name = "Осколки Бездны", giver = "QuestKeeper", minLevel = 48,
		desc = "Бездна смотрит в ответ. Принеси 3 осколка Бездны из каньона.",
		objectives = { { type = "collect", target = "M_VoidShard", count = 3, text = "Собрать осколки Бездны" } },
		rewards = { xp = 18000, coins = 6000, items = { { id = "C_Elixir", count = 3 } } },
	},
	{
		id = "Q_NamelessKing", name = "Безымянный Король", giver = "QuestKeeper", minLevel = 52,
		prereq = { "Q_Ashlord" },
		desc = "Финальная цель: трон в глубине каньона. Победи Безымянного Короля.",
		objectives = { { type = "boss", target = "NamelessKing", count = 1, text = "Победить Безымянного Короля" } },
		rewards = { xp = 40000, coins = 15000, items = { { id = "W_VoidEdge", count = 1 }, { id = "A_VoidShroud", count = 1 } }, statPoints = 3 },
	},
}

Quests.ById = {}
for _, q in ipairs(Quests.List) do
	Quests.ById[q.id] = q
end

function Quests.forNpc(npcKey)
	local out = {}
	for _, q in ipairs(Quests.List) do
		if q.giver == npcKey then table.insert(out, q) end
	end
	return out
end

return Quests
