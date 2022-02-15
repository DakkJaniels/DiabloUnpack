import mmap
import os
import struct


def get_value(m, start_pos, size, is_signed=False):
    # note - last value is not pulled
    chunk = m[start_pos:start_pos + size]
    unpack_string = "<"
    if size == 1:
        unpack_string = (unpack_string + "B")
    elif size == 2:
        unpack_string = (unpack_string + "H")
    elif size == 4:
        unpack_string = (unpack_string + "I")
    elif size == 8:
        unpack_string = (unpack_string + "Q")
    else:
        print("error, get value size incorrect")
        return 0
    # print(unpack_string)
    value = struct.unpack(unpack_string, chunk)[0]
    if is_signed:
        value = twos_complement(str(value), size * 8)
    return value


def get_string(m, address):
    temp_string = ""
    while m[address] != 0:
        temp_string = temp_string + chr(m[address])
        address += 1
    return (temp_string)


def get_mflags(value):
    MFLAG_HIDDEN = 1 << 0
    MFLAG_LOCK_ANIMATION = 1 << 1
    MFLAG_ALLOW_SPECIAL = 1 << 2
    MFLAG_NOHEAL = 1 << 3
    MFLAG_TARGETS_MONSTER = 1 << 4
    MFLAG_GOLEM = 1 << 5
    MFLAG_QUEST_COMPLETE = 1 << 6
    MFLAG_KNOCKBACK = 1 << 7
    MFLAG_SEARCH = 1 << 8
    MFLAG_CAN_OPEN_DOOR = 1 << 9
    MFLAG_NO_ENEMY = 1 << 10
    MFLAG_BERSERK = 1 << 11
    MFLAG_NOLIFESTEAL = 1 << 12

    mflag_string = ""
    mflag = value
    if ((mflag & MFLAG_HIDDEN) != 0):
        mflag_string += "MFLAG_HIDDEN | "
    if ((mflag & MFLAG_LOCK_ANIMATION) != 0):
        mflag_string += "MFLAG_LOCK_ANIMATION | "
    if ((mflag & MFLAG_ALLOW_SPECIAL) != 0):
        mflag_string += "MFLAG_ALLOW_SPECIAL | "
    if ((mflag & MFLAG_NOHEAL) != 0):
        mflag_string += "MFLAG_NOHEAL | "
    if ((mflag & MFLAG_TARGETS_MONSTER) != 0):
        mflag_string += "MFLAG_TARGETS_MONSTER | "
    if ((mflag & MFLAG_GOLEM) != 0):
        mflag_string += "MFLAG_GOLEM | "
    if ((mflag & MFLAG_QUEST_COMPLETE) != 0):
        mflag_string += "MFLAG_QUEST_COMPLETE | "
    if ((mflag & MFLAG_KNOCKBACK) != 0):
        mflag_string += "MFLAG_KNOCKBACK | "
    if ((mflag & MFLAG_SEARCH) != 0):
        mflag_string += "MFLAG_SEARCH | "
    if ((mflag & MFLAG_CAN_OPEN_DOOR) != 0):
        mflag_string += "MFLAG_CAN_OPEN_DOOR | "
    if ((mflag & MFLAG_NO_ENEMY) != 0):
        mflag_string += "MFLAG_NO_ENEMY | "
    if ((mflag & MFLAG_BERSERK) != 0):
        mflag_string += "MFLAG_BERSERK | "
    if ((mflag & MFLAG_NOLIFESTEAL) != 0):
        mflag_string += "MFLAG_NOLIFESTEAL | "
    mflag_string = mflag_string.strip()
    mflag_string = mflag_string.strip("|")
    if mflag_string == "":
        mflag_string = 0
    return (mflag_string)


def get_resists(value):
    RESIST_MAGIC = 1 << 0
    RESIST_FIRE = 1 << 1
    RESIST_LIGHTNING = 1 << 2
    IMMUNE_MAGIC = 1 << 3
    IMMUNE_FIRE = 1 << 4
    IMMUNE_LIGHTNING = 1 << 5
    IMMUNE_NULL_40 = 1 << 6
    IMMUNE_ACID = 1 << 7

    resistance_string = ""
    res = value
    if ((res & (
            RESIST_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40 | IMMUNE_ACID)) == 0):
        resistance_string = "0"

    else:
        if ((res & RESIST_MAGIC) != 0):
            resistance_string += "RESIST_MAGIC | "
        if ((res & RESIST_FIRE) != 0):
            resistance_string += "RESIST_FIRE | "
        if ((res & RESIST_LIGHTNING) != 0):
            resistance_string += "RESIST_LIGHTNING | "
        if ((res & IMMUNE_MAGIC) != 0):
            resistance_string += "IMMUNE_MAGIC | "
        if ((res & IMMUNE_FIRE) != 0):
            resistance_string += "IMMUNE_FIRE | "
        if ((res & IMMUNE_LIGHTNING) != 0):
            resistance_string += "IMMUNE_LIGHTNING | "
        if ((res & IMMUNE_NULL_40) != 0):
            resistance_string += "IMMUNE_NULL_40 | "
        if ((res & IMMUNE_ACID) != 0):
            resistance_string += "IMMUNE_ACID"
        resistance_string = resistance_string.strip()
        resistance_string = resistance_string.strip("|")
    return resistance_string


def convert_monster_data(m):
    # monster data
    monster_package = [("animation_size", 4),
                       ("seeding_size", 4),
                       ("animation_pointer", 4),
                       ("trigger_flag_second_attack", 4),
                       ("sounds_pointer", 4),
                       ("trigger_flag_special_sounds", 4),
                       ("trigger_flag_color_file", 4),
                       ("color_trn_pointer", 4),
                       ("idle_frameset", 4),
                       ("walk_frameset", 4),
                       ("attack_frameset", 4),
                       ("hit_recovery_frameset", 4),
                       ("death_frameset", 4),
                       ("second_attack_frameset", 4),
                       ("idle_playback_speed", 4),
                       ("walk_playback_speed", 4),
                       ("attack_playback_speed", 4),
                       ("hit_recovery_speed", 4),
                       ("death_playback_speed", 4),
                       ("second_attack_playback_speed", 4),
                       ("monster_name_pointer", 4),
                       ("min_dungeon_level", 1),
                       ("max_dungeon_level", 1),
                       ("monster_level", 2),
                       ("min_hp", 4),
                       ("max_hp", 4),
                       ("mAi", 4),
                       ("mFlags", 4),
                       ("subtype", 1),
                       ("to_hit_pct", 1),
                       ("to_hit_frame", 1),
                       ("min_attack_dmg", 1),
                       ("max_attack_dmg", 1),
                       ("secondary_attack_to_hit_pct", 1),
                       ("secondary_attack_to_hit_frame", 1),
                       ("secondary_attack_min_dmg", 1),
                       ("secondary_attack_max_dmg", 1),
                       ("monster_ac", 1),
                       ("monster_type", 2),
                       ("resistances_immunities_norm_nm", 2),
                       ("resistances_immunities_hell", 2),
                       ("item_drop_specials", 2),
                       ("monster_selection_outline", 2),
                       ("xp", 4)
                       ]

    monster_ai_list = [
        "AI_ZOMBIE",
        "AI_FAT",
        "AI_SKELSD",
        "AI_SKELBOW",
        "AI_SCAV",
        "AI_RHINO",
        "AI_GOATMC",
        "AI_GOATBOW",
        "AI_FALLEN",
        "AI_MAGMA",
        "AI_SKELKING",
        "AI_BAT",
        "AI_GARG",
        "AI_CLEAVER",
        "AI_SUCC",
        "AI_SNEAK",
        "AI_STORM",
        "AI_FIREMAN",
        "AI_GARBUD",
        "AI_ACID",
        "AI_ACIDUNIQ",
        "AI_GOLUM",
        "AI_ZHAR",
        "AI_SNOTSPIL",
        "AI_SNAKE",
        "AI_COUNSLR",
        "AI_MEGA",
        "AI_DIABLO",
        "AI_LAZARUS",
        "AI_LAZHELP",
        "AI_LACHDAN",
        "AI_WARLORD",
        "AI_FIREBAT",
        "AI_TORCHANT",
        "AI_HORKDMN",
        "AI_LICH",
        "AI_ARCHLICH",
        "AI_PSYCHORB",
        "AI_NECROMORB",
        "AI_BONEDEMON",
        # "AI_INVALID" = -1
    ]

    monster_class_list = [
        "MonsterClass::Undead",
        "MonsterClass::Demon",
        "MonsterClass::Animal",
    ]

    bool_list = [
        "trigger_flag_second_attack",
        "trigger_flag_special_sounds",
        "trigger_flag_color_file",
    ]

    # print(monster_dict)

    mem_offset = 0x402200
    monster_start = 0x00096C70
    monster_size = 0x80
    monster_count = 112

    monster_dict = {}
    cur_address = monster_start
    monster_table = []
    for monster_address in range(monster_start, monster_start + monster_size * monster_count, monster_size):
        monster_dict.clear()
        cur_address = monster_address
        # pull memory info for single monster
        for name, length in monster_package:
            monster_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length
        # place memory info in correct order for row
        # print(monster_dict["animation_pointer"])
        monster_row = [
            f'P_("monster", "{get_string(m, monster_dict["monster_name_pointer"] - mem_offset)}")',
            f'\"{get_string(m, monster_dict["animation_pointer"] - mem_offset)}\"' if monster_dict[
                                                                                          "animation_pointer"] != 0 else "nullptr",
            f'\"{get_string(m, monster_dict["sounds_pointer"] - mem_offset)}\"' if monster_dict[
                                                                                       "sounds_pointer"] != 0 else "nullptr",
            f'\"{get_string(m, monster_dict["color_trn_pointer"] - mem_offset)}\"' if monster_dict[
                                                                                          "color_trn_pointer"] != 0 else "nullptr",
            monster_dict["animation_size"],
            monster_dict["seeding_size"],
            "true" if monster_dict["trigger_flag_second_attack"] else "false",
            "true" if monster_dict["trigger_flag_special_sounds"] else "false",
            "true" if monster_dict["trigger_flag_color_file"] else "false",
            f"{{{monster_dict['idle_frameset']}, {monster_dict['walk_frameset']}, {monster_dict['attack_frameset']}, {monster_dict['hit_recovery_frameset']}, {monster_dict['death_frameset']}, {monster_dict['second_attack_frameset']}}}",
            f"{{{monster_dict['idle_playback_speed']}, {monster_dict['walk_playback_speed']}, {monster_dict['attack_playback_speed']}, {monster_dict['hit_recovery_speed']}, {monster_dict['death_playback_speed']}, {monster_dict['second_attack_playback_speed']}}}",
            monster_dict["min_dungeon_level"],
            monster_dict["max_dungeon_level"],
            monster_dict["monster_level"],
            monster_dict["min_hp"],
            monster_dict["max_hp"],
            monster_ai_list[monster_dict["mAi"]],
            get_mflags(monster_dict["mFlags"]),
            monster_dict["subtype"],
            monster_dict["to_hit_pct"],
            monster_dict["to_hit_frame"],
            monster_dict["min_attack_dmg"],
            monster_dict["max_attack_dmg"],
            monster_dict["secondary_attack_to_hit_pct"],
            monster_dict["secondary_attack_to_hit_frame"],
            monster_dict["secondary_attack_min_dmg"],
            monster_dict["secondary_attack_max_dmg"],
            monster_dict["monster_ac"],
            monster_class_list[monster_dict["monster_type"]],
            get_resists(monster_dict["resistances_immunities_norm_nm"]),
            get_resists(monster_dict["resistances_immunities_hell"]),
            monster_dict["item_drop_specials"],
            monster_dict["monster_selection_outline"],
            monster_dict["xp"],
        ]
        # print(monster_row)
        monster_table.append(monster_row)

    for row in monster_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def get_affix_type(m, type):
    affix_type = {'IPL_TOHIT': 0x0, 'IPL_TOHIT_CURSE': 0x1, 'IPL_DAMP': 0x2, 'IPL_DAMP_CURSE': 0x3,
                  'IPL_TOHIT_DAMP': 0x4, 'IPL_TOHIT_DAMP_CURSE': 0x5, 'IPL_ACP': 0x6, 'IPL_ACP_CURSE': 0x7,
                  'IPL_FIRERES': 0x8, 'IPL_LIGHTRES': 0x9, 'IPL_MAGICRES': 0xA, 'IPL_ALLRES': 0xB, 'IPL_SPLCOST': 0xC,
                  'IPL_SPLDUR': 0xD, 'IPL_SPLLVLADD': 0xE, 'IPL_CHARGES': 0xF, 'IPL_FIREDAM': 0x10,
                  'IPL_LIGHTDAM': 0x11, 'IPL_STR': 0x13, 'IPL_STR_CURSE': 0x14, 'IPL_MAG': 0x15, 'IPL_MAG_CURSE': 0x16,
                  'IPL_DEX': 0x17, 'IPL_DEX_CURSE': 0x18, 'IPL_VIT': 0x19, 'IPL_VIT_CURSE': 0x1A, 'IPL_ATTRIBS': 0x1B,
                  'IPL_ATTRIBS_CURSE': 0x1C, 'IPL_GETHIT_CURSE': 0x1D, 'IPL_GETHIT': 0x1E, 'IPL_LIFE': 0x1F,
                  'IPL_LIFE_CURSE': 0x20, 'IPL_MANA': 0x21, 'IPL_MANA_CURSE': 0x22, 'IPL_DUR': 0x23,
                  'IPL_DUR_CURSE': 0x24, 'IPL_INDESTRUCTIBLE': 0x25, 'IPL_LIGHT': 0x26, 'IPL_LIGHT_CURSE': 0x27,
                  'IPL_MULT_ARROWS': 0x29, 'IPL_FIRE_ARROWS': 0x2A, 'IPL_LIGHT_ARROWS': 0x2B, 'IPL_INVCURS': 0x2C,
                  'IPL_THORNS': 0x2D, 'IPL_NOMANA': 0x2E, 'IPL_NOHEALPLR': 0x2F, 'IPL_FIREBALL': 0x32,
                  'IPL_ABSHALFTRAP': 0x34, 'IPL_KNOCKBACK': 0x35, 'IPL_NOHEALMON': 0x36, 'IPL_STEALMANA': 0x37,
                  'IPL_STEALLIFE': 0x38, 'IPL_TARGAC': 0x39, 'IPL_FASTATTACK': 0x3A, 'IPL_FASTRECOVER': 0x3B,
                  'IPL_FASTBLOCK': 0x3C, 'IPL_DAMMOD': 0x3D, 'IPL_RNDARROWVEL': 0x3E, 'IPL_SETDAM': 0x3F,
                  'IPL_SETDUR': 0x40, 'IPL_NOMINSTR': 0x41, 'IPL_SPELL': 0x42, 'IPL_FASTSWING': 0x43,
                  'IPL_ONEHAND': 0x44, 'IPL_3XDAMVDEM': 0x45, 'IPL_ALLRESZERO': 0x46, 'IPL_DRAINLIFE': 0x48,
                  'IPL_RNDSTEALLIFE': 0x49, 'IPL_INFRAVISION': 0x4A, 'IPL_SETAC': 0x4B, 'IPL_ADDACLIFE': 0x4C,
                  'IPL_ADDMANAAC': 0x4D, 'IPL_FIRERESCLVL': 0x4E, 'IPL_AC_CURSE': 0x4F, 'IPL_FIRERES_CURSE': 0x50,
                  'IPL_LIGHTRES_CURSE': 0x51, 'IPL_MAGICRES_CURSE': 0x52, 'IPL_ALLRES_CURSE': 0x53,
                  'IPL_DEVASTATION': 0x54, 'IPL_DECAY': 0x55, 'IPL_PERIL': 0x56, 'IPL_JESTERS': 0x57,
                  'IPL_CRYSTALLINE': 0x58, 'IPL_DOPPELGANGER': 0x59, 'IPL_ACDEMON': 0x5A, 'IPL_ACUNDEAD': 0x5B,
                  'IPL_MANATOLIFE': 0x5C, 'IPL_LIFETOMANA': 0x5D, 'IPL_INVALID': -1}
    for key in affix_type.keys():
        if type == affix_type[key]:
            return key
    return "FAIL"


def get_affix_itype(value):
    itypes = {'PLT_MISC': 0x1, 'PLT_BOW': 0x10, 'PLT_STAFF': 0x100, 'PLT_WEAP': 0x1000, 'PLT_SHLD': 0x10000,
              'PLT_ARMO': 0x100000}

    itype_string = ""

    for itype in itypes.keys():
        if (itypes[itype] & value) != 0:
            itype_string += f"{itype} | "
    itype_string = itype_string.strip()
    itype_string = itype_string.strip("|")
    return itype_string


def convert_exclusive_flag(value, flag_dict):
    temp_string = ""
    for key in flag_dict.keys():
        if flag_dict[key] == value:
            return key
    return "fail"


def convert_bit_flag(value, flag_dict):
    temp_string = ""
    for key in flag_dict.keys():
        if (flag_dict[key] & value) != 0:
            temp_string += f"{key} | "
    temp_string = temp_string.strip()
    temp_string = temp_string.strip("|")
    return temp_string


def twos_complement(hexstr, bits):
    value = int(hexstr)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


def convert_affix_data(m):
    # affix data
    affix_package = [("ptr_PLName", 4),
                     ("PLPower", 4),
                     ("PLParam1", 4),
                     ("PLParam2", 4),
                     ("PLMinLvl", 4),
                     ("PLIType", 4),
                     ("PLGOE", 4),
                     ("PLDouble", 4),
                     ("PLOk", 4),
                     ("PLMinVal", 4),
                     ("PLMaxVal", 4),
                     ("PLMultVal", 4),
                     ]

    affix_item_type = [
        "PLT_MISC",  # = 0x1,
        "PLT_BOW",  # = 0x10,
        "PLT_STAFF",  # = 0x100,
        "PLT_WEAP",  # = 0x1000,
        "PLT_SHLD",  # = 0x10000,
        "PLT_ARMO",  # = 0x100000,
    ]

    GOE_ANY = 0x0
    GOE_EVIL = 0x01
    GOE_GOOD = 0x10

    affix_goe_list = [
        "GOE_ANY",
        "GOE_EVIL",
        "GOE_GOOD",
    ]
    affix_type = {'IPL_TOHIT': 0x0, 'IPL_TOHIT_CURSE': 0x1, 'IPL_DAMP': 0x2, 'IPL_DAMP_CURSE': 0x3,
                  'IPL_TOHIT_DAMP': 0x4, 'IPL_TOHIT_DAMP_CURSE': 0x5, 'IPL_ACP': 0x6, 'IPL_ACP_CURSE': 0x7,
                  'IPL_FIRERES': 0x8, 'IPL_LIGHTRES': 0x9, 'IPL_MAGICRES': 0xA, 'IPL_ALLRES': 0xB, 'IPL_SPLCOST': 0xC,
                  'IPL_SPLDUR': 0xD, 'IPL_SPLLVLADD': 0xE, 'IPL_CHARGES': 0xF, 'IPL_FIREDAM': 0x10,
                  'IPL_LIGHTDAM': 0x11, 'IPL_STR': 0x13, 'IPL_STR_CURSE': 0x14, 'IPL_MAG': 0x15, 'IPL_MAG_CURSE': 0x16,
                  'IPL_DEX': 0x17, 'IPL_DEX_CURSE': 0x18, 'IPL_VIT': 0x19, 'IPL_VIT_CURSE': 0x1A, 'IPL_ATTRIBS': 0x1B,
                  'IPL_ATTRIBS_CURSE': 0x1C, 'IPL_GETHIT_CURSE': 0x1D, 'IPL_GETHIT': 0x1E, 'IPL_LIFE': 0x1F,
                  'IPL_LIFE_CURSE': 0x20, 'IPL_MANA': 0x21, 'IPL_MANA_CURSE': 0x22, 'IPL_DUR': 0x23,
                  'IPL_DUR_CURSE': 0x24, 'IPL_INDESTRUCTIBLE': 0x25, 'IPL_LIGHT': 0x26, 'IPL_LIGHT_CURSE': 0x27,
                  'IPL_MULT_ARROWS': 0x29, 'IPL_FIRE_ARROWS': 0x2A, 'IPL_LIGHT_ARROWS': 0x2B, 'IPL_INVCURS': 0x2C,
                  'IPL_THORNS': 0x2D, 'IPL_NOMANA': 0x2E, 'IPL_NOHEALPLR': 0x2F, 'IPL_FIREBALL': 0x32,
                  'IPL_ABSHALFTRAP': 0x34, 'IPL_KNOCKBACK': 0x35, 'IPL_NOHEALMON': 0x36, 'IPL_STEALMANA': 0x37,
                  'IPL_STEALLIFE': 0x38, 'IPL_TARGAC': 0x39, 'IPL_FASTATTACK': 0x3A, 'IPL_FASTRECOVER': 0x3B,
                  'IPL_FASTBLOCK': 0x3C, 'IPL_DAMMOD': 0x3D, 'IPL_RNDARROWVEL': 0x3E, 'IPL_SETDAM': 0x3F,
                  'IPL_SETDUR': 0x40, 'IPL_NOMINSTR': 0x41, 'IPL_SPELL': 0x42, 'IPL_FASTSWING': 0x43,
                  'IPL_ONEHAND': 0x44, 'IPL_3XDAMVDEM': 0x45, 'IPL_ALLRESZERO': 0x46, 'IPL_DRAINLIFE': 0x48,
                  'IPL_RNDSTEALLIFE': 0x49, 'IPL_INFRAVISION': 0x4A, 'IPL_SETAC': 0x4B, 'IPL_ADDACLIFE': 0x4C,
                  'IPL_ADDMANAAC': 0x4D, 'IPL_FIRERESCLVL': 0x4E, 'IPL_AC_CURSE': 0x4F, 'IPL_FIRERES_CURSE': 0x50,
                  'IPL_LIGHTRES_CURSE': 0x51, 'IPL_MAGICRES_CURSE': 0x52, 'IPL_ALLRES_CURSE': 0x53,
                  'IPL_DEVASTATION': 0x54, 'IPL_DECAY': 0x55, 'IPL_PERIL': 0x56, 'IPL_JESTERS': 0x57,
                  'IPL_CRYSTALLINE': 0x58, 'IPL_DOPPELGANGER': 0x59, 'IPL_ACDEMON': 0x5A, 'IPL_ACUNDEAD': 0x5B,
                  'IPL_MANATOLIFE': 0x5C, 'IPL_LIFETOMANA': 0x5D, 'IPL_INVALID': -1}

    affix_goe_list = {"GOE_ANY": 0, "GOE_EVIL": 0x01, "GOE_GOOD": 0x10}

    mem_offset = 0x402200
    affix_start = 0x0007AAF8
    affix_size = 48
    affix_count = 180

    affix_dict = {}
    affix_table = []
    for affix_address in range(affix_start, affix_start + affix_size * affix_count, affix_size):
        affix_dict.clear()
        cur_address = affix_address
        # pull memory info for single affix
        for name, length in affix_package:
            affix_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length
        # place memory info in correct order for row
        affix_row = [
            f'N_("{get_string(m, affix_dict["ptr_PLName"] - mem_offset)}")',
            f'{{{get_affix_type(m, affix_dict["PLPower"])}',
            f'{affix_dict["PLParam1"]}',
            f'{affix_dict["PLParam2"]} }}',
            affix_dict["PLMinLvl"],
            get_affix_itype(affix_dict["PLIType"]),
            convert_exclusive_flag(affix_dict["PLGOE"], affix_goe_list),
            "true" if affix_dict["PLDouble"] else "false",
            "true" if affix_dict["PLOk"] else "false",
            twos_complement(str(affix_dict["PLMinVal"]), 32),
            twos_complement(str(affix_dict["PLMaxVal"]), 32),
            twos_complement(str(affix_dict["PLMultVal"]), 32),
        ]
        # print(monster_row)
        affix_table.append(affix_row)

    for row in affix_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_unique_data(m):
    # affix data
    package = [("UIName", 4),
               ("UIItemId", 1),
               ("UIMinLvl", 1),
               ("UINumPL", 2),
               ("UIValue", 4),
               ("ItemPower[0].type", 4),
               ("ItemPower[0].param1", 4),
               ("ItemPower[0].param2", 4),
               ("ItemPower[1].type", 4),
               ("ItemPower[1].param1", 4),
               ("ItemPower[1].param2", 4),
               ("ItemPower[2].type", 4),
               ("ItemPower[2].param1", 4),
               ("ItemPower[2].param2", 4),
               ("ItemPower[3].type", 4),
               ("ItemPower[3].param1", 4),
               ("ItemPower[3].param2", 4),
               ("ItemPower[4].type", 4),
               ("ItemPower[4].param1", 4),
               ("ItemPower[4].param2", 4),
               ("ItemPower[5].type", 4),
               ("ItemPower[5].param1", 4),
               ("ItemPower[5].param2", 4),
               ]

    type_dict = {'UITYPE_NONE': 0x0, 'UITYPE_SHORTBOW': 0x1, 'UITYPE_LONGBOW': 0x2, 'UITYPE_HUNTBOW': 0x3,
                 'UITYPE_COMPBOW': 0x4, 'UITYPE_WARBOW': 0x5, 'UITYPE_BATTLEBOW': 0x6, 'UITYPE_DAGGER': 0x7,
                 'UITYPE_FALCHION': 0x8, 'UITYPE_CLAYMORE': 0x9, 'UITYPE_BROADSWR': 0xA, 'UITYPE_SABRE': 0xB,
                 'UITYPE_SCIMITAR': 0xC, 'UITYPE_LONGSWR': 0xD, 'UITYPE_BASTARDSWR': 0xE, 'UITYPE_TWOHANDSWR': 0xF,
                 'UITYPE_GREATSWR': 0x10, 'UITYPE_CLEAVER': 0x11, 'UITYPE_LARGEAXE': 0x12, 'UITYPE_BROADAXE': 0x13,
                 'UITYPE_SMALLAXE': 0x14, 'UITYPE_BATTLEAXE': 0x15, 'UITYPE_GREATAXE': 0x16, 'UITYPE_MACE': 0x17,
                 'UITYPE_MORNSTAR': 0x18, 'UITYPE_SPIKCLUB': 0x19, 'UITYPE_MAUL': 0x1A, 'UITYPE_WARHAMMER': 0x1B,
                 'UITYPE_FLAIL': 0x1C, 'UITYPE_LONGSTAFF': 0x1D, 'UITYPE_SHORTSTAFF': 0x1E, 'UITYPE_COMPSTAFF': 0x1F,
                 'UITYPE_QUARSTAFF': 0x20, 'UITYPE_WARSTAFF': 0x21, 'UITYPE_SKULLCAP': 0x22, 'UITYPE_HELM': 0x23,
                 'UITYPE_GREATHELM': 0x24, 'UITYPE_CROWN': 0x25, 'UITYPE_38': 0x26, 'UITYPE_RAGS': 0x27,
                 'UITYPE_STUDARMOR': 0x28, 'UITYPE_CLOAK': 0x29, 'UITYPE_ROBE': 0x2A, 'UITYPE_CHAINMAIL': 0x2B,
                 'UITYPE_LEATHARMOR': 0x2C, 'UITYPE_BREASTPLATE': 0x2D, 'UITYPE_CAPE': 0x2E, 'UITYPE_PLATEMAIL': 0x2F,
                 'UITYPE_FULLPLATE': 0x30, 'UITYPE_BUCKLER': 0x31, 'UITYPE_SMALLSHIELD': 0x32,
                 'UITYPE_LARGESHIELD': 0x33, 'UITYPE_KITESHIELD': 0x34, 'UITYPE_GOTHSHIELD': 0x35, 'UITYPE_RING': 0x36,
                 'UITYPE_55': 0x37, 'UITYPE_AMULET': 0x38, 'UITYPE_SKCROWN': 0x39, 'UITYPE_INFRARING': 0x3A,
                 'UITYPE_OPTAMULET': 0x3B, 'UITYPE_TRING': 0x3C, 'UITYPE_HARCREST': 0x3D, 'UITYPE_MAPOFDOOM': 0x3E,
                 'UITYPE_ELIXIR': 0x3F, 'UITYPE_ARMOFVAL': 0x40, 'UITYPE_STEELVEIL': 0x41, 'UITYPE_GRISWOLD': 0x42,
                 'UITYPE_LGTFORGE': 0x43, 'UITYPE_LAZSTAFF': 0x44, 'UITYPE_NUMSWORD': 102, 'UITYPE_MAJAMULET': 103,
                 'UITYPE_WARAXE': 104, 'UITYPE_HEAVYXBOW': 105, 'UITYPE_MALLORNBOW': 106, 'UITYPE_WARFLAIL': 107,
                 'UITYPE_WARHELM': 108, 'UITYPE_NUMSHIELD': 109, 'UITYPE_ELVISHSBOW': 111, 'UITYPE_MITHCHAINMAIL': 117,
                 'UITYPE_ELVENBLADE': 118, 'UITYPE_MITHRILSHIELD': 119, 'UITYPE_ELVENBOW': 120,
                 'UITYPE_MITHRILHELM': 121, 'UITYPE_MAJRING': 122, 'UITYPE_LESSRING': -128, 'UITYPE_NORMRING': -127,
                 'UITYPE_LCAP': -111,
                 'UITYPE_CHAINSHIRT': -112, 'UITYPE_FULLHELM': -109, 'UITYPE_SDSCALE': -107, 'UITYPE_GREATFLAIL': -106,
                 'UITYPE_SHBATTLEBOW': -104, 'UITYPE_DWARVENSHIELD': -64, 'UITYPE_LEATHERARMOR': -63,
                 'UITYPE_MAGEROBE': -62, 'UITYPE_SCALEMAIL': -61, 'UITYPE_HAUBERK': -60, 'UITYPE_DWARVENAXE': -59,
                 'UITYPE_LONGKNIFE': -58, 'UITYPE_CSABRE': -57, 'UITYPE_WOODAXE': -56, 'UITYPE_SHWARBOW': -55,
                 'UITYPE_MINRING': -54, 'UITYPE_INVALID': -1}

    mem_offset = 0x402200
    mem_start = 0x0007CCB8
    block_size = 84
    block_count = 91

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single affix
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address,
                                        length) if name != "UIItemID" else get_value(m, cur_address, length, True)
            cur_address = cur_address + length
        # place memory info in correct order for row
        conv_row = [
            f'N_("{get_string(m, conv_dict["UIName"] - mem_offset)}")',
            convert_exclusive_flag(twos_complement(conv_dict["UIItemId"], 8), type_dict) if convert_exclusive_flag(
                twos_complement(conv_dict["UIItemId"], 8),
                type_dict) != "fail" else
            conv_dict["UIItemId"],
            conv_dict["UIMinLvl"],
            conv_dict["UINumPL"],
            conv_dict["UIValue"],

            f'{{ {{ {get_affix_type(m, conv_dict["ItemPower[0].type"])}',
            f'{twos_complement(conv_dict["ItemPower[0].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[0].param2"], 32)} }}',

            f'{{ {get_affix_type(m, conv_dict["ItemPower[1].type"])}',
            f'{twos_complement(conv_dict["ItemPower[1].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[1].param2"], 32)} }}',

            f'{{ {get_affix_type(m, conv_dict["ItemPower[2].type"])}',
            f'{twos_complement(conv_dict["ItemPower[2].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[2].param2"], 32)} }}',

            f'{{ {get_affix_type(m, conv_dict["ItemPower[3].type"])}',
            f'{twos_complement(conv_dict["ItemPower[3].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[3].param2"], 32)} }}',

            f'{{ {get_affix_type(m, conv_dict["ItemPower[4].type"])}',
            f'{twos_complement(conv_dict["ItemPower[4].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[4].param2"], 32)} }}',

            f'{{ {get_affix_type(m, conv_dict["ItemPower[5].type"])}',
            f'{twos_complement(conv_dict["ItemPower[5].param1"], 32)}',
            f'{twos_complement(conv_dict["ItemPower[5].param2"], 32)} }} }}',
        ]
        # print(monster_row)
        conv_table.append(conv_row)

    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_item_data(m):
    # item data
    package = [("iRnd", 4),
               ("iClass", 1),
               ("iLoc", 1),
               ("padding", 2),
               ("iCurs", 4),
               ("itype", 1),
               ("iItemId", 1),
               ("padding2", 2),
               ("iName", 4),
               ("isName", 4),
               ("iMinMLvl", 4),
               ("iDurability", 4),
               ("iMinDam", 4),
               ("iMaxDam", 4),
               ("iMinAC", 4),
               ("iMaxAC", 4),
               ("iMinStr", 1),
               ("iMinMag", 1),
               ("iMinDex", 1),
               ("padding3", 1),
               ("iFlags", 4),
               ("iMiscId", 4),
               ("iSpell", 4),
               ("iUsable", 4),
               ("iValue", 4),
               ("iMaxValue", 4),
               ]

    item_drop_rate = {'IDROP_NEVER': 0, 'IDROP_REGULAR': 1, 'IDROP_DOUBLE': 2}
    item_class = {'ICLASS_NONE': 0, 'ICLASS_WEAPON': 1, 'ICLASS_ARMOR': 2, 'ICLASS_MISC': 3, 'ICLASS_GOLD': 4,
                  'ICLASS_QUEST': 5}
    item_equip_type = {'ILOC_NONE': 0x0, 'ILOC_ONEHAND': 0x1, 'ILOC_TWOHAND': 0x2, 'ILOC_ARMOR': 0x3, 'ILOC_HELM': 0x4,
                       'ILOC_RING': 0x5, 'ILOC_AMULET': 0x6, 'ILOC_UNEQUIPABLE': 0x7, 'ILOC_BELT': 0x8,
                       'ILOC_INVALID': -1}
    item_cursor_graphic = {'ICURS_POTION_OF_FULL_MANA': 0, 'ICURS_SCROLL_OF': 1, 'ICURS_GOLD_SMALL': 4,
                           'ICURS_GOLD_MEDIUM': 5, 'ICURS_GOLD_LARGE': 6, 'ICURS_RING_OF_TRUTH': 10, 'ICURS_RING': 12,
                           'ICURS_LES_RING': 13, 'ICURS_NORM_RING': 14, 'ICURS_SPECTRAL_ELIXIR': 15,
                           'ICURS_GOLDEN_ELIXIR': 17, 'ICURS_EMPYREAN_BAND': 18, 'ICURS_EAR_SORCERER': 19,
                           'ICURS_EAR_WARRIOR': 20, 'ICURS_EAR_ROGUE': 21, 'ICURS_BLOOD_STONE': 25, 'ICURS_GEM': 26,
                           'ICURS_OIL': 30, 'ICURS_ELIXIR_OF_VITALITY': 31, 'ICURS_POTION_OF_HEALING': 32,
                           'ICURS_POTION_OF_FULL_REJUVENATION': 33, 'ICURS_ELIXIR_OF_MAGIC': 34,
                           'ICURS_POTION_OF_FULL_HEALING': 35, 'ICURS_ELIXIR_OF_DEXTERITY': 36,
                           'ICURS_POTION_OF_REJUVENATION': 37, 'ICURS_ELIXIR_OF_STRENGTH': 38,
                           'ICURS_POTION_OF_MANA': 39, 'ICURS_BRAIN': 40, 'ICURS_CLAW': 41, 'ICURS_OPTIC_AMULET': 44,
                           'ICURS_AMULET': 45, 'ICURS_MAJ_AMULET': 48, 'ICURS_MORGUL_KNIFE': 50, 'ICURS_DAGGER': 51,
                           'ICURS_LONG_KNIFE': 54, 'ICURS_BLADE': 56, 'ICURS_BASTARD_SWORD': 57, 'ICURS_MACE': 59,
                           'ICURS_LONG_SWORD': 60, 'ICURS_BROAD_SWORD': 61, 'ICURS_FALCHION': 62,
                           'ICURS_MORNING_STAR': 63, 'ICURS_SHORT_SWORD': 64, 'ICURS_CLAYMORE': 65, 'ICURS_CLUB': 66,
                           'ICURS_SABRE': 67, 'ICURS_SH_SWORD': 68, 'ICURS_SPIKED_CLUB': 70, 'ICURS_SPIKED_CLUB2': 71,
                           'ICURS_SCIMITAR': 72, 'ICURS_ELVEN_BLADE': 73, 'ICURS_FULL_HELM': 75, 'ICURS_MAGIC_ROCK': 76,
                           'ICURS_THE_UNDEAD_CROWN': 78, 'ICURS_HELM': 82, 'ICURS_BUCKLER': 83, 'ICRUS_GREAT_HELM': 84,
                           'ICURS_VIEL_OF_STEEL': 85, 'ICURS_BOOK_GREY': 86, 'ICURS_BOOK_RED': 87,
                           'ICURS_BOOK_BLUE': 88, 'ICURS_BLACK_MUSHROOM': 89, 'ICURS_SKULL_CAP': 90, 'ICURS_CAP': 91,
                           'ICURS_HARLEQUIN_CREST': 93, 'ICURS_SHIRT': 94, 'ICURS_CROWN': 95,
                           'ICURS_MAP_OF_THE_STARS': 96, 'ICURS_FUNGAL_TOME': 97, 'ICURS_GREAT_HELM': 98,
                           'ICURS_MITHRIL_SHIELD': 100, 'ICURS_BATTLE_AXE': 101, 'ICURS_HUNTERS_BOW': 102,
                           'ICURS_FIELD_PLATE': 103, 'ICURS_SMALL_SHIELD': 105, 'ICURS_CLEAVER': 106,
                           'ICURS_STUDDED_LEATHER_ARMOR': 107, 'ICURS_SHORT_STAFF': 109, 'ICURS_TWO_HANDED_SWORD': 110,
                           'ICURS_CHAIN_MAIL': 111, 'ICURS_SMALL_AXE': 112, 'ICURS_KITE_SHIELD': 113,
                           'ICURS_SCALE_MAIL': 114, 'ICURS_DWARVEN_SHIELD': 115, 'ICURS_SHORT_BOW': 118,
                           'ICURS_LONG_BATTLE_BOW': 119, 'ICURS_LONG_WAR_BOW': 120, 'ICURS_WAR_HAMMER': 121,
                           'ICURS_MAUL': 122, 'ICURS_LONG_STAFF': 123, 'ICURS_WAR_STAFF': 124, 'ICURS_TAVERN_SIGN': 126,
                           'ICURS_HARD_LEATHER_ARMOR': 127, 'ICURS_RAGS': 128, 'ICURS_QUILTED_ARMOR': 129,
                           'ICURS_WAR_FLAIL': 130, 'ICURS_FLAIL': 131, 'ICURS_TOWER_SHIELD': 132,
                           'ICURS_COMPOSITE_BOW': 133, 'ICURS_GREAT_SWORD': 134, 'ICURS_LEATHER_ARMOR': 135,
                           'ICURS_SPLINT_MAIL': 136, 'ICURS_ROBE': 137, 'ICURS_MAGE_ROBES': 138,
                           'ICURS_CHAIN_SHIRT': 139, 'ICURS_ANVIL_OF_FURY': 140, 'ICURS_BROAD_AXE': 141,
                           'ICURS_LARGE_AXE': 142, 'ICURS_GREAT_AXE': 143, 'ICURS_AXE': 144, 'ICURS_NUM_SHIELD': 146,
                           'ICURS_LARGE_SHIELD': 147, 'ICURS_GOTHIC_SHIELD': 148, 'ICURS_CLOAK': 149, 'ICURS_CAPE': 150,
                           'ICURS_FULL_PLATE_MAIL': 151, 'ICURS_GOTHIC_PLATE': 152, 'ICURS_BREAST_PLATE': 153,
                           'ICURS_RING_MAIL': 154, 'ICURS_STAFF_OF_LAZARUS': 155, 'ICURS_WAR_AXE': 156,
                           'ICURS_ARKAINES_VALOR': 157, 'ICURS_HEAVY_XBOW': 158, 'ICURS_ROMACIL': 160,
                           'ICURS_DWARVEN_AXE': 163, 'ICURS_MALLORN_BOW': 164, 'ICURS_SHORT_WAR_BOW': 165,
                           'ICURS_COMPOSITE_STAFF': 166, 'ICURS_SHORT_BATTLE_BOW': 167, 'ICURS_GOLD': 168,
                           'ICURS_AURIC_AMULET': 180, 'ICURS_RUNE_BOMB': 187, 'ICURS_THEODORE': 188,
                           'ICURS_TORN_NOTE_1': 189, 'ICURS_TORN_NOTE_2': 190, 'ICURS_TORN_NOTE_3': 191,
                           'ICURS_RECONSTRUCTED_NOTE': 192, 'ICURS_RUNE_OF_FIRE': 193,
                           'ICURS_GREATER_RUNE_OF_FIRE': 194, 'ICURS_RUNE_OF_LIGHTNING': 195,
                           'ICURS_GREATER_RUNE_OF_LIGHTNING': 196, 'ICURS_RUNE_OF_STONE': 197, 'ICURS_GREY_SUIT': 198,
                           'ICURS_BROWN_SUIT': 199, 'ICURS_BOVINE': 226, 'ICURS_NEW_HELM': 236, 'ICURS_SKULLCAP': 240,
                           'ICURS_PLATE_MAIL': 243, 'ICURS_GREAT_BLADE': 244, 'ICURS_LONG_BOW': 248,
                           'ICURS_ELVEN_SH_BOW': 249}

    item_type = {'ITYPE_MISC': 0x0, 'ITYPE_SWORD': 0x1, 'ITYPE_AXE': 0x2, 'ITYPE_BOW': 0x3, 'ITYPE_MACE': 0x4,
                 'ITYPE_SHIELD': 0x5, 'ITYPE_LARMOR': 0x6, 'ITYPE_HELM': 0x7, 'ITYPE_MARMOR': 0x8, 'ITYPE_HARMOR': 0x9,
                 'ITYPE_STAFF': 0xA, 'ITYPE_GOLD': 0xB, 'ITYPE_RING': 0xC, 'ITYPE_AMULET': 0xD, 'ITYPE_FOOD': 0xE,
                 'ITYPE_NONE': -1}

    item_type_conv = {'ITYPE_MISC': "ItemType::Misc", 'ITYPE_SWORD': "ItemType::Sword", 'ITYPE_AXE': "ItemType::Axe",
                      'ITYPE_BOW': "ItemType::Bow", 'ITYPE_MACE': "ItemType::Mace", 'ITYPE_SHIELD': "ItemType::Shield",
                      'ITYPE_LARMOR': "ItemType::LightArmor", 'ITYPE_HELM': "ItemType::Helm",
                      'ITYPE_MARMOR': "ItemType::MediumArmor",
                      'ITYPE_HARMOR': "ItemType::HeavyArmor", 'ITYPE_STAFF': "ItemType::Staff",
                      'ITYPE_GOLD': "ItemType::Gold",
                      'ITYPE_RING': "ItemType::Ring", 'ITYPE_AMULET': "ItemType::Amulet",
                      'ITYPE_FOOD': "ItemType::Food",
                      'ITYPE_NONE': "ItemType::None"}

    item_special_effect = {'ISPL_NONE': 0x00000000, 'ISPL_INFRAVISION': 0x00000001, 'ISPL_RNDSTEALLIFE': 0x00000002,
                           'ISPL_RNDARROWVEL': 0x00000004, 'ISPL_FIRE_ARROWS': 0x00000008, 'ISPL_FIREDAM': 0x00000010,
                           'ISPL_LIGHTDAM': 0x00000020, 'ISPL_DRAINLIFE': 0x00000040, 'ISPL_UNKNOWN_1': 0x00000080,
                           'ISPL_NOHEALPLR': 0x00000100, 'ISPL_MULT_ARROWS': 0x00000200, 'ISPL_UNKNOWN_3': 0x00000400,
                           'ISPL_KNOCKBACK': 0x00000800, 'ISPL_NOHEALMON': 0x00001000, 'ISPL_STEALMANA_3': 0x00002000,
                           'ISPL_STEALMANA_5': 0x00004000, 'ISPL_STEALLIFE_3': 0x00008000,
                           'ISPL_STEALLIFE_5': 0x00010000, 'ISPL_QUICKATTACK': 0x00020000,
                           'ISPL_FASTATTACK': 0x00040000, 'ISPL_FASTERATTACK': 0x00080000,
                           'ISPL_FASTESTATTACK': 0x00100000, 'ISPL_FASTRECOVER': 0x00200000,
                           'ISPL_FASTERRECOVER': 0x00400000, 'ISPL_FASTESTRECOVER': 0x00800000,
                           'ISPL_FASTBLOCK': 0x01000000, 'ISPL_LIGHT_ARROWS': 0x02000000, 'ISPL_THORNS': 0x04000000,
                           'ISPL_NOMANA': 0x08000000, 'ISPL_ABSHALFTRAP': 0x10000000, 'ISPL_UNKNOWN_4': 0x20000000,
                           'ISPL_3XDAMVDEM': 0x40000000, 'ISPL_ALLRESZERO': 0x80000000}

    item_misc_id = {'IMISC_NONE': 0x0, 'IMISC_USEFIRST': 0x1, 'IMISC_FULLHEAL': 0x2, 'IMISC_HEAL': 0x3,
                    'IMISC_OLDHEAL': 0x4, 'IMISC_DEADHEAL': 0x5, 'IMISC_MANA': 0x6, 'IMISC_FULLMANA': 0x7,
                    'IMISC_POTEXP': 0x8, 'IMISC_POTFORG': 0x9, 'IMISC_ELIXSTR': 0xA, 'IMISC_ELIXMAG': 0xB,
                    'IMISC_ELIXDEX': 0xC, 'IMISC_ELIXVIT': 0xD, 'IMISC_ELIXWEAK': 0xE, 'IMISC_ELIXDIS': 0xF,
                    'IMISC_ELIXCLUM': 0x10, 'IMISC_ELIXSICK': 0x11, 'IMISC_REJUV': 0x12, 'IMISC_FULLREJUV': 0x13,
                    'IMISC_USELAST': 0x14, 'IMISC_SCROLL': 0x15, 'IMISC_SCROLLT': 0x16, 'IMISC_STAFF': 0x17,
                    'IMISC_BOOK': 0x18, 'IMISC_RING': 0x19, 'IMISC_AMULET': 0x1A, 'IMISC_UNIQUE': 0x1B,
                    'IMISC_FOOD': 0x1C, 'IMISC_OILFIRST': 0x1D, 'IMISC_OILOF': 0x1E, 'IMISC_OILACC': 0x1F,
                    'IMISC_OILMAST': 0x20, 'IMISC_OILSHARP': 0x21, 'IMISC_OILDEATH': 0x22, 'IMISC_OILSKILL': 0x23,
                    'IMISC_OILBSMTH': 0x24, 'IMISC_OILFORT': 0x25, 'IMISC_OILPERM': 0x26, 'IMISC_OILHARD': 0x27,
                    'IMISC_OILIMP': 0x28, 'IMISC_OILLAST': 0x29, 'IMISC_MAPOFDOOM': 0x2A, 'IMISC_EAR': 0x2B,
                    'IMISC_SPECELIX': 0x2C, 'IMISC_INVALID': -1}

    spell_id = {'SPL_NULL': 0x0, 'SPL_FIREBOLT': 0x1, 'SPL_HEAL': 0x2, 'SPL_LIGHTNING': 0x3, 'SPL_FLASH': 0x4,
                'SPL_IDENTIFY': 0x5, 'SPL_FIREWALL': 0x6, 'SPL_TOWN': 0x7, 'SPL_STONE': 0x8, 'SPL_INFRA': 0x9,
                'SPL_RNDTELEPORT': 0xA, 'SPL_MANASHIELD': 0xB, 'SPL_FIREBALL': 0xC, 'SPL_GUARDIAN': 0xD,
                'SPL_CHAIN': 0xE, 'SPL_WAVE': 0xF, 'SPL_DOOMSERP': 0x10, 'SPL_BLODRIT': 0x11, 'SPL_NOVA': 0x12,
                'SPL_INVISIBIL': 0x13, 'SPL_FLAME': 0x14, 'SPL_GOLEM': 0x15, 'SPL_BLODBOIL': 0x16, 'SPL_TELEPORT': 0x17,
                'SPL_APOCA': 0x18, 'SPL_ETHEREALIZE': 0x19, 'SPL_REPAIR': 0x1A, 'SPL_RECHARGE': 0x1B,
                'SPL_DISARM': 0x1C, 'SPL_ELEMENT': 0x1D, 'SPL_CBOLT': 0x1E, 'SPL_HBOLT': 0x1F, 'SPL_RESURRECT': 0x20,
                'SPL_TELEKINESIS': 0x21, 'SPL_HEALOTHER': 0x22, 'SPL_FLARE': 0x23, 'SPL_BONESPIRIT': 0x24,
                'SPL_INVALID': -1}

    unique_base_item = {'UITYPE_NONE': 0x0, 'UITYPE_SHORTBOW': 0x1, 'UITYPE_LONGBOW': 0x2, 'UITYPE_HUNTBOW': 0x3,
                        'UITYPE_COMPBOW': 0x4, 'UITYPE_WARBOW': 0x5, 'UITYPE_BATTLEBOW': 0x6, 'UITYPE_DAGGER': 0x7,
                        'UITYPE_FALCHION': 0x8, 'UITYPE_CLAYMORE': 0x9, 'UITYPE_BROADSWR': 0xA, 'UITYPE_SABRE': 0xB,
                        'UITYPE_SCIMITAR': 0xC, 'UITYPE_LONGSWR': 0xD, 'UITYPE_BASTARDSWR': 0xE,
                        'UITYPE_TWOHANDSWR': 0xF,
                        'UITYPE_GREATSWR': 0x10, 'UITYPE_CLEAVER': 0x11, 'UITYPE_LARGEAXE': 0x12,
                        'UITYPE_BROADAXE': 0x13,
                        'UITYPE_SMALLAXE': 0x14, 'UITYPE_BATTLEAXE': 0x15, 'UITYPE_GREATAXE': 0x16, 'UITYPE_MACE': 0x17,
                        'UITYPE_MORNSTAR': 0x18, 'UITYPE_SPIKCLUB': 0x19, 'UITYPE_MAUL': 0x1A, 'UITYPE_WARHAMMER': 0x1B,
                        'UITYPE_FLAIL': 0x1C, 'UITYPE_LONGSTAFF': 0x1D, 'UITYPE_SHORTSTAFF': 0x1E,
                        'UITYPE_COMPSTAFF': 0x1F,
                        'UITYPE_QUARSTAFF': 0x20, 'UITYPE_WARSTAFF': 0x21, 'UITYPE_SKULLCAP': 0x22, 'UITYPE_HELM': 0x23,
                        'UITYPE_GREATHELM': 0x24, 'UITYPE_CROWN': 0x25, 'UITYPE_38': 0x26, 'UITYPE_RAGS': 0x27,
                        'UITYPE_STUDARMOR': 0x28, 'UITYPE_CLOAK': 0x29, 'UITYPE_ROBE': 0x2A, 'UITYPE_CHAINMAIL': 0x2B,
                        'UITYPE_LEATHARMOR': 0x2C, 'UITYPE_BREASTPLATE': 0x2D, 'UITYPE_CAPE': 0x2E,
                        'UITYPE_PLATEMAIL': 0x2F,
                        'UITYPE_FULLPLATE': 0x30, 'UITYPE_BUCKLER': 0x31, 'UITYPE_SMALLSHIELD': 0x32,
                        'UITYPE_LARGESHIELD': 0x33, 'UITYPE_KITESHIELD': 0x34, 'UITYPE_GOTHSHIELD': 0x35,
                        'UITYPE_RING': 0x36,
                        'UITYPE_55': 0x37, 'UITYPE_AMULET': 0x38, 'UITYPE_SKCROWN': 0x39, 'UITYPE_INFRARING': 0x3A,
                        'UITYPE_OPTAMULET': 0x3B, 'UITYPE_TRING': 0x3C, 'UITYPE_HARCREST': 0x3D,
                        'UITYPE_MAPOFDOOM': 0x3E,
                        'UITYPE_ELIXIR': 0x3F, 'UITYPE_ARMOFVAL': 0x40, 'UITYPE_STEELVEIL': 0x41,
                        'UITYPE_GRISWOLD': 0x42,
                        'UITYPE_LGTFORGE': 0x43, 'UITYPE_LAZSTAFF': 0x44, 'UITYPE_NUMSWORD': 102,
                        'UITYPE_MAJAMULET': 103,
                        'UITYPE_WARAXE': 104, 'UITYPE_HEAVYXBOW': 105, 'UITYPE_MALLORNBOW': 106, 'UITYPE_WARFLAIL': 107,
                        'UITYPE_WARHELM': 108, 'UITYPE_NUMSHIELD': 109, 'UITYPE_ELVISHSBOW': 111,
                        'UITYPE_MITHCHAINMAIL': 117,
                        'UITYPE_ELVENBLADE': 118, 'UITYPE_MITHRILSHIELD': 119, 'UITYPE_ELVENBOW': 120,
                        'UITYPE_MITHRILHELM': 121, 'UITYPE_MAJRING': 122, 'UITYPE_LESSRING': -128,
                        'UITYPE_NORMRING': -127, 'UITYPE_LCAP': -111,
                        'UITYPE_CHAINSHIRT': -112, 'UITYPE_FULLHELM': -109, 'UITYPE_SDSCALE': -107,
                        'UITYPE_GREATFLAIL': -106,
                        'UITYPE_SHBATTLEBOW': -104, 'UITYPE_DWARVENSHIELD': -64, 'UITYPE_LEATHERARMOR': -63,
                        'UITYPE_MAGEROBE': -62, 'UITYPE_SCALEMAIL': -61, 'UITYPE_HAUBERK': -60,
                        'UITYPE_DWARVENAXE': -59,
                        'UITYPE_LONGKNIFE': -58, 'UITYPE_CSABRE': -57, 'UITYPE_WOODAXE': -56, 'UITYPE_SHWARBOW': -55,
                        'UITYPE_MINRING': -54, 'UITYPE_INVALID': -1}

    mem_offset = 0x402200
    mem_start = 0x0008E448
    block_size = 76
    block_count = 157

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single affix
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length
        # place memory info in correct order for row
        conv_row = [
            convert_exclusive_flag(conv_dict["iRnd"], item_drop_rate),
            convert_exclusive_flag(conv_dict["iClass"], item_class),
            convert_exclusive_flag(conv_dict["iLoc"], item_equip_type),
            convert_exclusive_flag(conv_dict["iCurs"], item_cursor_graphic) if convert_exclusive_flag(
                conv_dict["iCurs"], item_cursor_graphic) != "fail" else conv_dict["iCurs"],
            item_type_conv[(convert_exclusive_flag(conv_dict["itype"], item_type))],
            convert_exclusive_flag(twos_complement(conv_dict["iItemId"], 8),
                                   unique_base_item) if convert_exclusive_flag(twos_complement(conv_dict["iItemId"], 8),
                                                                               unique_base_item) != "fail" else twos_complement(
                conv_dict["iItemId"], 8),
            f'N_("{get_string(m, conv_dict["iName"] - mem_offset)}")' if conv_dict["iName"] != 0 else "nullptr",
            f'N_("{get_string(m, conv_dict["isName"] - mem_offset)}")' if conv_dict["isName"] != 0 else "nullptr",
            conv_dict["iMinMLvl"],
            conv_dict["iDurability"],
            conv_dict["iMinDam"],
            conv_dict["iMaxDam"],
            conv_dict["iMinAC"],
            conv_dict["iMaxAC"],
            conv_dict["iMinStr"],
            conv_dict["iMinMag"],
            conv_dict["iMinDex"],
            convert_bit_flag(conv_dict["iFlags"], item_special_effect) if convert_bit_flag(conv_dict["iFlags"],
                                                                                           item_special_effect) != "" else "0",
            convert_exclusive_flag(conv_dict["iMiscId"], item_misc_id),
            convert_exclusive_flag(conv_dict["iSpell"], spell_id),
            "true" if conv_dict["iUsable"] != 0 else "false",
            conv_dict["iValue"],
        ]
        conv_table.append(conv_row)
    actual_label_order = [
        "iRnd",
        "iClass",
        "iLoc",
        "iCurs",
        "itype",
        "iItemId",
        "iName",
        "isName",
        "iMinMLvl",
        "iDurability",
        "iMinDam",
        "iMaxDam",
        "iMinAC",
        "iMaxAC",
        "iMinStr",
        "iMinMag",
        "iMinDex",
        "iFlags",
        "iMiscId",
        "iSpell",
        "iUsable",
        "iValue",
    ]

    print("; ".join(actual_label_order))
    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def get_item_from_array(value, array, fail_return):
    if value < 0:
        return fail_return
    return array[value]


def convert_unique_monsters(m):
    mem_start = 0x0009A560
    block_size = 32
    block_count = 97

    # data
    package = [("mtype", 4), # 0-3
               ("mName", 4),
               ("mTrnName", 4),
               ("mlevel", 2),
               ("mmaxhp", 2),
               ("mAi", 1),
               ("mint", 1),
               ("mMinDamage", 1),
               ("mMaxDamage", 1),
               ("mMagicRes", 2),
               ("mUnqAttr", 2),
               # ("mUnqVar1", 1),
               # ("mUnqVar2", 1),
               # ("padding", 2),
               ("mUnqVar1", 1),
               ("mlevelNorm", 1),
               ("mlevelNM", 1),
               ("mlevelHell", 1),
               ("mtalkmsg", 4),
               ]

    speech_list = ["TEXT_NONE",
                   "TEXT_KING1",
                   "TEXT_KING2",
                   "TEXT_KING3",
                   "TEXT_KING4",
                   "TEXT_KING5",
                   "TEXT_KING6",
                   "TEXT_KING7",
                   "TEXT_KING8",
                   "TEXT_KING9",
                   "TEXT_KING10",
                   "TEXT_KING11",
                   "TEXT_BANNER1",
                   "TEXT_BANNER2",
                   "TEXT_BANNER3",
                   "TEXT_BANNER4",
                   "TEXT_BANNER5",
                   "TEXT_BANNER6",
                   "TEXT_BANNER7",
                   "TEXT_BANNER8",
                   "TEXT_BANNER9",
                   "TEXT_BANNER10",
                   "TEXT_BANNER11",
                   "TEXT_BANNER12",
                   "TEXT_VILE1",
                   "TEXT_VILE2",
                   "TEXT_VILE3",
                   "TEXT_VILE4",
                   "TEXT_VILE5",
                   "TEXT_VILE6",
                   "TEXT_VILE7",
                   "TEXT_VILE8",
                   "TEXT_VILE9",
                   "TEXT_VILE10",
                   "TEXT_VILE11",
                   "TEXT_VILE12",
                   "TEXT_VILE13",
                   "TEXT_VILE14",
                   "TEXT_POISON1",
                   "TEXT_POISON2",
                   "TEXT_POISON3",
                   "TEXT_POISON4",
                   "TEXT_POISON5",
                   "TEXT_POISON6",
                   "TEXT_POISON7",
                   "TEXT_POISON8",
                   "TEXT_POISON9",
                   "TEXT_POISON10",
                   "TEXT_BONE1",
                   "TEXT_BONE2",
                   "TEXT_BONE3",
                   "TEXT_BONE4",
                   "TEXT_BONE5",
                   "TEXT_BONE6",
                   "TEXT_BONE7",
                   "TEXT_BONE8",
                   "TEXT_BUTCH1",
                   "TEXT_BUTCH2",
                   "TEXT_BUTCH3",
                   "TEXT_BUTCH4",
                   "TEXT_BUTCH5",
                   "TEXT_BUTCH6",
                   "TEXT_BUTCH7",
                   "TEXT_BUTCH8",
                   "TEXT_BUTCH9",
                   "TEXT_BUTCH10",
                   "TEXT_BLIND1",
                   "TEXT_BLIND2",
                   "TEXT_BLIND3",
                   "TEXT_BLIND4",
                   "TEXT_BLIND5",
                   "TEXT_BLIND6",
                   "TEXT_BLIND7",
                   "TEXT_BLIND8",
                   "TEXT_VEIL1",
                   "TEXT_VEIL2",
                   "TEXT_VEIL3",
                   "TEXT_VEIL4",
                   "TEXT_VEIL5",
                   "TEXT_VEIL6",
                   "TEXT_VEIL7",
                   "TEXT_VEIL8",
                   "TEXT_VEIL9",
                   "TEXT_VEIL10",
                   "TEXT_VEIL11",
                   "TEXT_ANVIL1",
                   "TEXT_ANVIL2",
                   "TEXT_ANVIL3",
                   "TEXT_ANVIL4",
                   "TEXT_ANVIL5",
                   "TEXT_ANVIL6",
                   "TEXT_ANVIL7",
                   "TEXT_ANVIL8",
                   "TEXT_ANVIL9",
                   "TEXT_ANVIL10",
                   "TEXT_BLOOD1",
                   "TEXT_BLOOD2",
                   "TEXT_BLOOD3",
                   "TEXT_BLOOD4",
                   "TEXT_BLOOD5",
                   "TEXT_BLOOD6",
                   "TEXT_BLOOD7",
                   "TEXT_BLOOD8",
                   "TEXT_WARLRD1",
                   "TEXT_WARLRD2",
                   "TEXT_WARLRD3",
                   "TEXT_WARLRD4",
                   "TEXT_WARLRD5",
                   "TEXT_WARLRD6",
                   "TEXT_WARLRD7",
                   "TEXT_WARLRD8",
                   "TEXT_WARLRD9",
                   "TEXT_INFRA1",
                   "TEXT_INFRA2",
                   "TEXT_INFRA3",
                   "TEXT_INFRA4",
                   "TEXT_INFRA5",
                   "TEXT_INFRA6",
                   "TEXT_INFRA7",
                   "TEXT_INFRA8",
                   "TEXT_INFRA9",
                   "TEXT_INFRA10",
                   "TEXT_MUSH1",
                   "TEXT_MUSH2",
                   "TEXT_MUSH3",
                   "TEXT_MUSH4",
                   "TEXT_MUSH5",
                   "TEXT_MUSH6",
                   "TEXT_MUSH7",
                   "TEXT_MUSH8",
                   "TEXT_MUSH9",
                   "TEXT_MUSH10",
                   "TEXT_MUSH11",
                   "TEXT_MUSH12",
                   "TEXT_MUSH13",
                   "TEXT_DOOM1",
                   "TEXT_DOOM2",
                   "TEXT_DOOM3",
                   "TEXT_DOOM4",
                   "TEXT_DOOM5",
                   "TEXT_DOOM6",
                   "TEXT_DOOM7",
                   "TEXT_DOOM8",
                   "TEXT_DOOM9",
                   "TEXT_DOOM10",
                   "TEXT_GARBUD1",
                   "TEXT_GARBUD2",
                   "TEXT_GARBUD3",
                   "TEXT_GARBUD4",
                   "TEXT_ZHAR1",
                   "TEXT_ZHAR2",
                   "TEXT_STORY1",
                   "TEXT_STORY2",
                   "TEXT_STORY3",
                   "TEXT_STORY4",
                   "TEXT_STORY5",
                   "TEXT_STORY6",
                   "TEXT_STORY7",
                   "TEXT_STORY9",
                   "TEXT_STORY10",
                   "TEXT_STORY11",
                   "TEXT_OGDEN1",
                   "TEXT_OGDEN2",
                   "TEXT_OGDEN3",
                   "TEXT_OGDEN4",
                   "TEXT_OGDEN5",
                   "TEXT_OGDEN6",
                   "TEXT_OGDEN8",
                   "TEXT_OGDEN9",
                   "TEXT_OGDEN10",
                   "TEXT_PEPIN1",
                   "TEXT_PEPIN2",
                   "TEXT_PEPIN3",
                   "TEXT_PEPIN4",
                   "TEXT_PEPIN5",
                   "TEXT_PEPIN6",
                   "TEXT_PEPIN7",
                   "TEXT_PEPIN9",
                   "TEXT_PEPIN10",
                   "TEXT_PEPIN11",
                   "TEXT_GILLIAN1",
                   "TEXT_GILLIAN2",
                   "TEXT_GILLIAN3",
                   "TEXT_GILLIAN4",
                   "TEXT_GILLIAN5",
                   "TEXT_GILLIAN6",
                   "TEXT_GILLIAN7",
                   "TEXT_GILLIAN9",
                   "TEXT_GILLIAN10",
                   "TEXT_GRISWOLD1",
                   "TEXT_GRISWOLD2",
                   "TEXT_GRISWOLD3",
                   "TEXT_GRISWOLD4",
                   "TEXT_GRISWOLD5",
                   "TEXT_GRISWOLD6",
                   "TEXT_GRISWOLD7",
                   "TEXT_GRISWOLD8",
                   "TEXT_GRISWOLD9",
                   "TEXT_GRISWOLD10",
                   "TEXT_GRISWOLD12",
                   "TEXT_GRISWOLD13",
                   "TEXT_FARNHAM1",
                   "TEXT_FARNHAM2",
                   "TEXT_FARNHAM3",
                   "TEXT_FARNHAM4",
                   "TEXT_FARNHAM5",
                   "TEXT_FARNHAM6",
                   "TEXT_FARNHAM8",
                   "TEXT_FARNHAM9",
                   "TEXT_FARNHAM10",
                   "TEXT_FARNHAM11",
                   "TEXT_FARNHAM12",
                   "TEXT_FARNHAM13",
                   "TEXT_ADRIA1",
                   "TEXT_ADRIA2",
                   "TEXT_ADRIA3",
                   "TEXT_ADRIA4",
                   "TEXT_ADRIA5",
                   "TEXT_ADRIA6",
                   "TEXT_ADRIA7",
                   "TEXT_ADRIA8",
                   "TEXT_ADRIA9",
                   "TEXT_ADRIA10",
                   "TEXT_ADRIA12",
                   "TEXT_ADRIA13",
                   "TEXT_WIRT1",
                   "TEXT_WIRT2",
                   "TEXT_WIRT3",
                   "TEXT_WIRT4",
                   "TEXT_WIRT5",
                   "TEXT_WIRT6",
                   "TEXT_WIRT7",
                   "TEXT_WIRT8",
                   "TEXT_WIRT9",
                   "TEXT_WIRT11",
                   "TEXT_WIRT12",
                   "TEXT_BONER",
                   "TEXT_BLOODY",
                   "TEXT_BLINDING",
                   "TEXT_BLOODWAR",
                   "TEXT_MBONER",
                   "TEXT_MBLOODY",
                   "TEXT_MBLINDING",
                   "TEXT_MBLOODWAR",
                   "TEXT_RBONER",
                   "TEXT_RBLOODY",
                   "TEXT_RBLINDING",
                   "TEXT_RBLOODWAR",
                   "TEXT_COW1",
                   "TEXT_COW2",
                   "TEXT_BOOK11",
                   "TEXT_BOOK12",
                   "TEXT_BOOK13",
                   "TEXT_BOOK21",
                   "TEXT_BOOK22",
                   "TEXT_BOOK23",
                   "TEXT_BOOK31",
                   "TEXT_BOOK32",
                   "TEXT_BOOK33",
                   "TEXT_INTRO",
                   "TEXT_HBONER",
                   "TEXT_HBLOODY",
                   "TEXT_HBLINDING",
                   "TEXT_HBLOODWAR",
                   "TEXT_BBONER",
                   "TEXT_BBLOODY",
                   "TEXT_BBLINDING",
                   "TEXT_BBLOODWAR",
                   "TEXT_GRAVE1",
                   "TEXT_GRAVE2",
                   "TEXT_GRAVE3",
                   "TEXT_GRAVE4",
                   "TEXT_GRAVE5",
                   "TEXT_GRAVE6",
                   "TEXT_GRAVE7",
                   "TEXT_GRAVE8",
                   "TEXT_GRAVE9",
                   "TEXT_GRAVE10",
                   "TEXT_FARMER1",
                   "TEXT_FARMER2",
                   "TEXT_FARMER3",
                   "TEXT_FARMER4",
                   "TEXT_FARMER5",
                   "TEXT_GIRL1",
                   "TEXT_GIRL2",
                   "TEXT_GIRL3",
                   "TEXT_GIRL4",
                   "TEXT_DEFILER1",
                   "TEXT_DEFILER2",
                   "TEXT_DEFILER3",
                   "TEXT_DEFILER4",
                   "TEXT_DEFILER5",
                   "TEXT_NAKRUL1",
                   "TEXT_NAKRUL2",
                   "TEXT_NAKRUL3",
                   "TEXT_NAKRUL4",
                   "TEXT_NAKRUL5",
                   "TEXT_CORNSTN",
                   "TEXT_JERSEY1",
                   "TEXT_JERSEY2",
                   "TEXT_JERSEY3",
                   "TEXT_JERSEY4",
                   "TEXT_JERSEY5",
                   "TEXT_JERSEY6",
                   "TEXT_JERSEY7",
                   "TEXT_JERSEY8",
                   "TEXT_JERSEY9",
                   "TEXT_TRADER",
                   "TEXT_FARMER6",
                   "TEXT_FARMER7",
                   "TEXT_FARMER8",
                   "TEXT_FARMER9",
                   "TEXT_FARMER10",
                   "TEXT_JERSEY10",
                   "TEXT_JERSEY11",
                   "TEXT_JERSEY12",
                   "TEXT_JERSEY13",
                   "TEXT_SKLJRN",
                   "TEXT_BOOK4",
                   "TEXT_BOOK5",
                   "TEXT_BOOK6",
                   "TEXT_BOOK7",
                   "TEXT_BOOK8",
                   "TEXT_BOOK9",
                   "TEXT_BOOKA",
                   "TEXT_BOOKB",
                   "TEXT_BOOKC",
                   "TEXT_OBOOKA",
                   "TEXT_OBOOKB",
                   "TEXT_OBOOKC",
                   "TEXT_MBOOKA",
                   "TEXT_MBOOKB",
                   "TEXT_MBOOKC",
                   "TEXT_RBOOKA",
                   "TEXT_RBOOKB",
                   "TEXT_RBOOKC",
                   "TEXT_BBOOKA",
                   "TEXT_BBOOKB",
                   "TEXT_BBOOKC", ]

    mtype_list = [
        "MT_NZOMBIE",
        "MT_BZOMBIE",
        "MT_GZOMBIE",
        "MT_YZOMBIE",
        "MT_RFALLSP",
        "MT_DFALLSP",
        "MT_YFALLSP",
        "MT_BFALLSP",
        "MT_WSKELAX",
        "MT_TSKELAX",
        "MT_RSKELAX",
        "MT_XSKELAX",
        "MT_RFALLSD",
        "MT_DFALLSD",
        "MT_YFALLSD",
        "MT_BFALLSD",
        "MT_NSCAV",
        "MT_BSCAV",
        "MT_WSCAV",
        "MT_YSCAV",
        "MT_WSKELBW",
        "MT_TSKELBW",
        "MT_RSKELBW",
        "MT_XSKELBW",
        "MT_WSKELSD",
        "MT_TSKELSD",
        "MT_RSKELSD",
        "MT_XSKELSD",
        "MT_INVILORD",
        "MT_SNEAK",
        "MT_STALKER",
        "MT_UNSEEN",
        "MT_ILLWEAV",
        "MT_LRDSAYTR",
        "MT_NGOATMC",
        "MT_BGOATMC",
        "MT_RGOATMC",
        "MT_GGOATMC",
        "MT_FIEND",
        "MT_BLINK",
        "MT_GLOOM",
        "MT_FAMILIAR",
        "MT_NGOATBW",
        "MT_BGOATBW",
        "MT_RGOATBW",
        "MT_GGOATBW",
        "MT_NACID",
        "MT_RACID",
        "MT_BACID",
        "MT_XACID",
        "MT_SKING",
        "MT_CLEAVER",
        "MT_FAT",
        "MT_MUDMAN",
        "MT_TOAD",
        "MT_FLAYED",
        "MT_WYRM",
        "MT_CAVSLUG",
        "MT_DVLWYRM",
        "MT_DEVOUR",
        "MT_NMAGMA",
        "MT_YMAGMA",
        "MT_BMAGMA",
        "MT_WMAGMA",
        "MT_HORNED",
        "MT_MUDRUN",
        "MT_FROSTC",
        "MT_OBLORD",
        "MT_BONEDMN",
        "MT_REDDTH",
        "MT_LTCHDMN",
        "MT_UDEDBLRG",
        "MT_INCIN",
        "MT_FLAMLRD",
        "MT_DOOMFIRE",
        "MT_HELLBURN",
        "MT_STORM",
        "MT_RSTORM",
        "MT_STORML",
        "MT_MAEL",
        "MT_BIGFALL",
        "MT_WINGED",
        "MT_GARGOYLE",
        "MT_BLOODCLW",
        "MT_DEATHW",
        "MT_MEGA",
        "MT_GUARD",
        "MT_VTEXLRD",
        "MT_BALROG",
        "MT_NSNAKE",
        "MT_RSNAKE",
        "MT_BSNAKE",
        "MT_GSNAKE",
        "MT_NBLACK",
        "MT_RTBLACK",
        "MT_BTBLACK",
        "MT_RBLACK",
        "MT_UNRAV",
        "MT_HOLOWONE",
        "MT_PAINMSTR",
        "MT_REALWEAV",
        "MT_SUCCUBUS",
        "MT_SNOWWICH",
        "MT_HLSPWN",
        "MT_SOLBRNR",
        "MT_COUNSLR",
        "MT_MAGISTR",
        "MT_CABALIST",
        "MT_ADVOCATE",
        "MT_GOLEM",
        "MT_DIABLO",
        "MT_DARKMAGE",
        "MT_HELLBOAR",
        "MT_STINGER",
        "MT_PSYCHORB",
        "MT_ARACHNON",
        "MT_FELLTWIN",
        "MT_HORKSPWN",
        "MT_VENMTAIL",
        "MT_NECRMORB",
        "MT_SPIDLORD",
        "MT_LASHWORM",
        "MT_TORCHANT",
        "MT_HORKDMN",
        "MT_DEFILER",
        "MT_GRAVEDIG",
        "MT_TOMBRAT",
        "MT_FIREBAT",
        "MT_SKLWING",
        "MT_LICH",
        "MT_CRYPTDMN",
        "MT_HELLBAT",
        "MT_BONEDEMN",
        "MT_ARCHLICH",
        "MT_BICLOPS",
        "MT_FLESTHNG",
        "MT_REAPER",
        "MT_NAKRUL",
        "NUM_MTYPES",
        # MT_INVALID = -1,
    ]

    monster_ai_list = [
        "AI_ZOMBIE",
        "AI_FAT",
        "AI_SKELSD",
        "AI_SKELBOW",
        "AI_SCAV",
        "AI_RHINO",
        "AI_GOATMC",
        "AI_GOATBOW",
        "AI_FALLEN",
        "AI_MAGMA",
        "AI_SKELKING",
        "AI_BAT",
        "AI_GARG",
        "AI_CLEAVER",
        "AI_SUCC",
        "AI_SNEAK",
        "AI_STORM",
        "AI_FIREMAN",
        "AI_GARBUD",
        "AI_ACID",
        "AI_ACIDUNIQ",
        "AI_GOLUM",
        "AI_ZHAR",
        "AI_SNOTSPIL",
        "AI_SNAKE",
        "AI_COUNSLR",
        "AI_MEGA",
        "AI_DIABLO",
        "AI_LAZARUS",
        "AI_LAZHELP",
        "AI_LACHDAN",
        "AI_WARLORD",
        "AI_FIREBAT",
        "AI_TORCHANT",
        "AI_HORKDMN",
        "AI_LICH",
        "AI_ARCHLICH",
        "AI_PSYCHORB",
        "AI_NECROMORB",
        "AI_BONEDEMON",
        # "AI_INVALID" = -1
    ]

    mem_offset = 0x402200

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single affix
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length
        # place memory info in correct order for row
        conv_row = [
            get_item_from_array(twos_complement(conv_dict["mtype"],32), mtype_list, "MT_INVALID"),
            f'P_("monster", "{get_string(m, conv_dict["mName"] - mem_offset)}")',
            f'"{get_string(m, conv_dict["mTrnName"]-mem_offset)}"',
            conv_dict["mlevel"],
            conv_dict["mmaxhp"],
            monster_ai_list[conv_dict["mAi"]],
            conv_dict["mint"],
            conv_dict["mMinDamage"],
            conv_dict["mMaxDamage"],
            get_resists(conv_dict["mMagicRes"]),
            conv_dict["mUnqAttr"],
            # conv_dict["mUnqVar1"],
            # conv_dict["mUnqVar2"],
            (conv_dict["mUnqVar1"]),
            (conv_dict["mlevelNorm"]),
            (conv_dict["mlevelNM"]),
            (conv_dict["mlevelHell"]),
            speech_list[conv_dict["mtalkmsg"]]
        ]
        # need some additional logic to put the rest of this together
        pack_value = conv_dict["mUnqAttr"]
        pack_string = "UniqueMonsterPack::"
        if (pack_value & 0b0001) != 0:
            if (pack_value & 0b0010) != 0:
                pack_string += "Leashed"
            else:
                pack_string += "Independent"
        else:
            pack_string += "None"

        customToHit = 0
        # Unique Attribute is To Hit modifier
        if (pack_value & 0b0100) != 0:
            customToHit = conv_dict["mUnqVar1"]

        customArmorClass = 0
        # Unique Attribute is Armor Modifier
        if (pack_value & 0b1000) != 0:
            customArmorClass = conv_dict["mUnqVar1"]

        conv_table.append(conv_row)
    actual_label_order = [
        "iRnd",
        "iClass",
        "iLoc",
        "iCurs",
        "itype",
        "iItemId",
        "iName",
        "isName",
        "iMinMLvl",
        "iDurability",
        "iMinDam",
        "iMaxDam",
        "iMinAC",
        "iMaxAC",
        "iMinStr",
        "iMinMag",
        "iMinDex",
        "iFlags",
        "iMiscId",
        "iSpell",
        "iUsable",
        "iValue",
    ]

    print("; ".join(actual_label_order))
    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def main():
    with open("DIABLO.EXE", 'rb') as f:
        size_bytes = os.fstat(f.fileno()).st_size
        print(f"file size: {size_bytes}\n")
        m = mmap.mmap(f.fileno(), length=size_bytes, access=mmap.ACCESS_READ)

    # convert_monster_data(m)
    # convert_affix_data(m)
    # convert_unique_data(m)
    # convert_item_data(m)
    convert_unique_monsters(m)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
