-- Emberfall | Dungeons — соответствие данжей и их обитателей зонам.
-- Нужно, чтобы мобы в данже подходили по уровню, а не брались из общего списка.
local Dungeons = {}

-- dungeon -> зона (по ней ищем мобов для волн)
Dungeons.OfBoss = {
	FrostWraith      = "Frostpeak",
	FrostColossus    = "Frostpeak",
	SwampMother      = "Mirefen",
	CryptWraith      = "Bonefields",
	Ashlord          = "Ashwaste",
	NamelessKing     = "HollowDeep",
	-- v11: новые подземелья
	MarrowTyrant     = "Bonefields",
	StoneWarden      = "Highlands",
	BogHydra         = "Mirefen",
	VolcanoForge     = "Ashwaste",
	PirateAdmiral    = "Archipelago",
	WindArchon       = "Frostpeak",
	CoralQueen       = "SouthIsles",
	GlacierWyrm      = "Frostpeak",
}

-- Подписи входов в данжи (для указателей и UI)
Dungeons.Titles = {
	FrostWraith   = "Ледяная Гробница",
	FrostColossus = "Арена Ледяного Колосса",
	SwampMother   = "Топь Матери Болот",
	CryptWraith   = "Крипта Костяных Полей",
	Ashlord       = "Арена Пепельного Владыки",
	NamelessKing  = "Трон Безымянного Короля",
	MarrowTyrant  = "Костяная Оссуария",
	StoneWarden   = "Забытые Шахты Предгорий",
	BogHydra      = "Затонувший Храм Гнили",
	VolcanoForge  = "Кузня в Жерле",
	PirateAdmiral = "Затонувший Фрегат",
	WindArchon    = "Пик Ветров",
	CoralQueen    = "Коралловый Грот",
	GlacierWyrm   = "Логово Ледяного Змея",
}

return Dungeons
