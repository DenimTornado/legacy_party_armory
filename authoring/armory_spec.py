"""Authored content; engine identifiers are resolved against index.json at build time."""
import uuid
MODULE='5d96794a-b84b-4bf7-afaa-74063318d3a6'
VERSION='0.3.1'
def uid(key): return str(uuid.uuid5(uuid.UUID(MODULE),'armory:'+key))
def textid(key): return 'h'+uid('text:'+key).replace('-','g')
ITEMS=[]
def item(key,bag,base,parent,en,ru,lore_en,lore_ru,colour,**data):
 data['Rarity']='Legendary'
 ITEMS.append(dict(key=key,bag=bag,base=base,parent=parent,en=en,ru=ru,lore_en=lore_en,lore_ru=lore_ru,colour=colour,data=data,uuid=uid(key),stats='LPA_'+key))

# Paladin: late-game legendary weapon, without a class or oath gate.
item('Carsomyr','paladin','f01c3f5d-c542-420f-86c5-bdddf7819e29','WPN_Greatsword_2','Carsomyr','Карсомир',
 'A holy avenger once sought among a red dragon’s hoard. Its silver edge severs hostile enchantments as readily as flesh; the vows of its bearer are their own to keep.',
 'Святой мститель, некогда хранившийся в сокровищнице красного дракона. Серебряное лезвие рассекает чужие чары так же уверенно, как плоть; за свои обеты его владелец отвечает сам.',
 'holy',Rarity='Legendary',DefaultBoosts='WeaponEnchantment(3);WeaponProperty(Magical);WeaponDamage(1d4,Radiant)',PassivesOnEquip='LPA_HolyWard',Boosts='UnlockSpell(Target_LPA_Unweave)')
item('CharonsClaw','wyll','WPN_Longsword_2','WPN_Longsword_2',"Charon’s Claw",'Коготь Харона',
 'Entreri’s blackened blade carries the memory of Netherese malice. A curtain of ash can hide its wielder, while its edge answers the force of their will.',
 'Чернёный клинок Энтрери хранит память о нетерильской злобе. Пепельная завеса скрывает владельца, а остриё подчиняется силе его воли.',
 'oxblood',Rarity='Legendary',DefaultBoosts='WeaponEnchantment(2);WeaponProperty(Magical);WeaponDamage(1d4,Necrotic)',**{'Weapon Properties':'Light;Finesse;Melee;Dippable;Magical','VersatileDamage':'','Proficiency Group':'Longswords;MartialWeapons','PassivesOnEquip':'MAG_MeleeCaster_Passive;LPA_ClawTraining','Boosts':'UnlockSpell(Target_LPA_AshVeil)'})
item('CharonsGauntlet','wyll','ARM_Gloves_Leather','ARM_Gloves_Leather',"Gauntlet of Charon’s Claw",'Перчатка Когтя Харона',
 'A dark gauntlet made to master a murderous sword. Spellcraft falters against its grip; together with the Claw it steadies the hand against an unseen foe.',
 'Тёмная перчатка, созданная для обуздания смертоносного меча. Чужие чары слабеют перед её хваткой; вместе с Когтем она надёжно оберегает руку владельца.',
 'oxblood',Rarity='VeryRare',PassivesOnEquip='LPA_GauntletWard;LPA_ClawBond',Boosts='UnlockSpell(Target_LPA_Counterspell)')
item('EntreriDagger','wyll','MAG_WYR_Orin_Bhaalist_Dagger','WPN_Dagger_2',"Entreri’s Jeweled Dagger",'Драгоценный кинжал Энтрери',
 'The emerald in its hilt has watched too many lives end. With each measured stroke the assassin steals a little of the warmth his victim is losing.',
 'Изумруд в рукояти видел слишком много смертей. Точным ударом убийца забирает частицу тепла, покидающего жертву.',
 'emerald',Rarity='VeryRare',DefaultBoosts='WeaponEnchantment(2);WeaponProperty(Magical);WeaponDamage(1d4,Necrotic)',PassivesOnEquip='LPA_LifeDrink')
item('DragonsBreath','karlach','WPN_Halberd_2','WPN_Halberd_2',"Dragon’s Breath",'Дыхание Дракона',
 'A red-hafted halberd that bears five draconic tempers within its steel. Fire sleeps nearest its edge, but cold, lightning, acid and venom each answer a deliberate turn of the grip.',
 'Алебарда с красным древком хранит в стали силу пяти драконьих стихий. Ближе всего к острию дремлет огонь, но холод, молния, кислота и яд тоже отвечают осознанному повороту рукояти.',
 'dragon_red',Rarity='Legendary',DefaultBoosts='WeaponEnchantment(3);WeaponProperty(Magical)',PassivesOnEquip='LPA_DragonElements',Boosts='UnlockSpell(Shout_LPA_Fire);UnlockSpell(Shout_LPA_Cold);UnlockSpell(Shout_LPA_Lightning);UnlockSpell(Shout_LPA_Acid);UnlockSpell(Shout_LPA_Poison)')
item('InfernalMaul','karlach','MAG_SWA_Roaring_Maul','WPN_Maul_2','Infernal Maul','Инфернальный молот',
 'Forged for hands that have hauled chains through Avernus. A low furnace glow leaks from the head whenever rage heats the blood of its bearer.',
 'Выкован для рук, тащивших цепи по Аверно. Из бойка сочится тусклый жар горна, когда ярость вскипает в крови владельца.',
 'infernal',Rarity='VeryRare',DefaultBoosts='WeaponEnchantment(2);WeaponProperty(Magical);WeaponDamage(1d4,Fire)',PassivesOnEquip='LPA_InfernalImpact')
item('Icingdeath','minthara','MAG_MeleeDebuff_AttackDebuff1_OnDamage_Scimitar','WPN_Scimitar_2','Icingdeath','Ледяная Смерть',
 'Named for the white wyrm whose hoard yielded it, Drizzt’s frostbrand drinks the heat of nearby flames. A pale blue glimmer follows its silver edge.',
 'Морозный клинок Дзирта назван в честь белого змея, в чьей сокровищнице был найден. Он поглощает жар пламени, и по серебряному лезвию скользит бледно-голубой свет.',
 'ice',Rarity='VeryRare',DefaultBoosts='WeaponEnchantment(2);WeaponProperty(Magical);WeaponDamage(1d4,Cold)',PassivesOnEquip='LPA_Frostbrand',Boosts='UnlockSpell(Target_LPA_Quench)')
item('Twinkle','minthara','WPN_Scimitar_2','WPN_Scimitar_2','Twinkle','Мерцающий',
 'An elven defender entrusted to Drizzt by Malchor Harpell. Its blue light is a promise of shelter, and the blade finds its purpose guarding the hand that holds it.',
 'Эльфийский защитник, вручённый Дзирту Малкором Гарпеллом. Его синий свет обещает укрытие, а истинное предназначение клинка — оберегать держащую его руку.',
 'blue',Rarity='VeryRare',DefaultBoosts='WeaponEnchantment(2);WeaponProperty(Magical)',PassivesOnEquip='LPA_Defender')
item('HarperFinery','jaheira','c0c0534c-b7fc-4d0b-a335-b8f4c548852d','ARM_StuddedLeather_Body','Harper’s Woodland Armour','Лесной доспех арфиста',
 'Supple brown leather and muted green panels carry the colours of bark and leaf. Bronze clasps hold a veteran Harper’s armour close without announcing her passage through the woods.',
 'Мягкая коричневая кожа и приглушённые зелёные вставки повторяют цвета коры и листвы. Бронзовые застёжки надёжно удерживают доспех опытной арфистки, не выдавая её шагов в лесу.',
 'harper',ArmorClass='13',Boosts='RollBonus(SavingThrow,1);Advantage(Skill,Nature);Advantage(Skill,Survival)')
# Safe copies retain native combat abilities but receive private templates/materials.
for key,bag,base,en,ru,col,le,lr in [
 ('SharSpear','shar','MAG_SHA_SharBlessing_Spear',"Shar’s Spear of Evening",'Копьё вечера Шар','shar','A shadow of the Lady of Loss’s spear, freed from the bargain that first called it into mortal hands.','Отблеск копья Владычицы Утрат, освобождённый от сделки, впервые призвавшей его в руки смертных.'),
 ('ViconiaRobe','shar','MAG_Viconia_Robe',"Viconia’s Priestess Robe",'Жреческая мантия Виконии','shar','Graphite cloth and cold silver conceal the vestments of a priestess who learned to make a fortress of her faith.','Графитовая ткань и холодное серебро скрывают облачение жрицы, научившейся обращать веру в крепость.'),
 ('WalkingFortress','shar','MAG_TheBulwark_Shield',"Viconia’s Walking Fortress",'Ходячая крепость Виконии','shar','A shield built around a simple lesson: make the enemy regret the one blow that reaches you.','Щит, воплощающий простой урок: пусть враг пожалеет даже о единственном ударе, достигшем цели.'),
 ('SeluneSpear','selune','MAG_SHA_SeluneBlessing_Spear',"Selûne’s Spear of Night",'Копьё ночи Селунэ','moon','Moonlight rests along a spear made for a path freely chosen. This echo asks for no sacrifice and binds no fate.','Лунный свет скользит вдоль копья, созданного для свободно избранного пути. Его отражение не требует жертв и не связывает судьбу.'),
 ('MoonRobe','selune','MAG_Selunite_Isobel_Robe','Moon Devotion Robe','Мантия лунной преданности','moon','Silver threads catch the faintest light. Beneath their cool shimmer, a quiet devotion stands watch through the longest night.','Серебряные нити ловят самый слабый свет. Под их прохладным мерцанием тихая преданность несёт дозор даже самой долгой ночью.')]:
 item(key,bag,base,base,en,ru,le,lr,col)

BAGS={
 'outer':('Legacy Party Armory','Legacy Party Armory'),
 'paladin':('Paladin','Паладин'), 'wyll':('Wyll — Artemis Entreri','Уилл — Артемис Энтрери'),
 'karlach':('Karlach — Infernal Viking','Карлах — Инфернальный викинг'),
 'minthara':('Minthara — Drizzt Do’Urden','Минтара — Дзирт До’Урден'),
 'jaheira':('Jaheira — Legacy','Джахейра — Наследие'), 'shadowheart':('Shadowheart','Шэдоухарт'),
 'shar':('Shadowheart — Shar','Шэдоухарт — Шар'), 'selune':('Shadowheart — Selûne','Шэдоухарт — Селунэ')}
PREVIEW={
 'wyll':['MAG_Shadow_StealthBonusWhileObscured_Armor','MAG_ofMarksmanship_Hat','MAG_PHB_CloakOfDisplacement_Cloak','OBJ_Dye_BlackRed','OBJ_Dye_BlackBlue'],
 'karlach':['MAG_Barbarian_BoneSpike_Armor','MAG_Fire_BurningOnDamaged_Cloak','OBJ_Dye_WhiteRed'],
 'minthara':['ARM_Cloak_Long_B','OBJ_Dye_BlackTeal','OBJ_Dye_GreenSwamp','OBJ_Dye_GreenSage'],
 'jaheira':['MAG_PHB_OfSpeed_Scimitar','MAG_HAV_Sylvan_Scimitar'],
 'shar':['UNI_DarkJusticiar_Helmet','OBJ_Dye_WhiteBlack','OBJ_Dye_BlackBlue']}
# Retain the established dragon UUIDs. New definitions are balanced separately.
DRAGONS=[('a22abf50-a0a1-47ad-9bd0-5866e72d9d95','DENIM_RedDragon_Armor'),('b44e7251-75b9-46bf-9b67-79551ae6d603','DENIM_RedDragon_Helmet')]
FINAL_DYES={'wyll':['OBJ_Dye_BlackRed'],'karlach':['OBJ_Dye_WhiteRed'],'minthara':['OBJ_Dye_BlackTeal'],'shar':['OBJ_Dye_WhiteBlack']}
