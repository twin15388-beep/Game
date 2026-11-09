-- Emberfall | NPCData — кто стоит на маркерах NPC_* и что говорит.
local NPCData = {}

-- assistant: подсказки новичку
NPCData.List = {
	{
		key = "QuestKeeper", name = "Хранитель Знаний", title = "Элдрин", color = Color3.fromRGB(120, 90, 200),
		lines = {
			"Ты пришёл вовремя. Мир трещит по швам.",
			"Выбери стихию у алтаря на площади — без магии ты просто мясо.",
			"Бери задания: опыт, монеты, снаряжение. Всё пригодится.",
		},
		role = "quests",
	},
	{
		key = "Merchant", name = "Торговец", title = "Бор", color = Color3.fromRGB(200, 160, 70),
		lines = {
			"Покупаю шкуры, руду, всё что блестит.",
			"Зелья не бесплатные, но жизнь дороже.",
		},
		role = "shop",
	},
	{
		key = "Blacksmith", name = "Кузнец", title = "Гарм", color = Color3.fromRGB(150, 120, 100),
		lines = {
			"Сталь — единственное, чему я верю.",
			"Принеси руду — скуём что-нибудь стоящее.",
		},
		role = "shop",
	},
	{
		key = "Healer", name = "Лекарь", title = "Мирра", color = Color3.fromRGB(120, 220, 160),
		lines = {
			"Раны затянутся, шрамы останутся.",
			"Не умирай слишком часто — опыт теряется.",
		},
		role = "heal",
	},
	{
		key = "GateCaptain", name = "Капрал стражи", title = "Дорн", color = Color3.fromRGB(150, 150, 170),
		lines = {
			"За воротами не прогулка, а война.",
			"Держись дорог — в чаще тебя сожрут.",
		},
		role = "quests",
	},
	{
		key = "Herbalist", name = "Травница", title = "Сайра", color = Color3.fromRGB(120, 200, 110),
		lines = {
			"Теневые волки рвут наших овец. Помоги — отблагодарю.",
			"Болотные грибы светятся, но они не добрые.",
		},
		role = "quests",
	},
	{
		key = "Hunter", name = "Охотник", title = "Кайл", color = Color3.fromRGB(140, 110, 80),
		lines = {
			"В чаще что-то ходит. Большое.",
			"Убей его — и я поверю, что ты не просто мальчишка с палкой.",
		},
		role = "quests",
	},
	{
		key = "Farmer", name = "Фермер", title = "Хэм", color = Color3.fromRGB(180, 150, 90),
		lines = {
			"Волки с перевала воют всю ночь.",
			"Хутор держится, но не долго.",
		},
		role = "quests",
	},
	{
		key = "Portmaster", name = "Портмейстер", title = "Сэл", color = Color3.fromRGB(90, 160, 200),
		lines = {
			"Утопленники лезут на причалы каждую ночь.",
			"Море забирает всех. И возвращает не такими.",
		},
		role = "quests",
	},
	{
		key = "Fishmonger", name = "Рыботорговец", title = "Нэд", color = Color3.fromRGB(110, 180, 190),
		lines = {
			"Монета была тёплой. Потом стало холодно.",
			"Пираты-мертвецы ходят по берегу. Не ходи туда ночью.",
		},
		role = "quests",
	},
}

NPCData.ByKey = {}
for _, n in ipairs(NPCData.List) do
	NPCData.ByKey[n.key] = n
end

return NPCData
