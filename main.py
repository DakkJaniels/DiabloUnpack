import mmap
import os
import struct
import re


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
    flag = 0
    if ((res & (
            RESIST_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_ACID)) == 0):
        resistance_string = "0"

    else:
        if (res & (RESIST_MAGIC | IMMUNE_MAGIC)) == 0:
            resistance_string += "            "
            # flag = 0
        elif res & RESIST_MAGIC != 0:
            resistance_string += "RESIST_MAGIC"
            flag = 1
        else:
            resistance_string += "IMMUNE_MAGIC"
            flag = 1

        if (res & (RESIST_FIRE | IMMUNE_FIRE)) == 0:
            resistance_string += "              "
        elif res & RESIST_FIRE != 0:
            if flag == 1:
                resistance_string += " | "
            else:
                resistance_string += "   "
            resistance_string += "RESIST_FIRE"
            flag = 1
        else:
            if flag == 1:
                resistance_string += " | "
            else:
                resistance_string += "   "
            resistance_string += "IMMUNE_FIRE"
            flag = 1

        if (res & (RESIST_LIGHTNING | IMMUNE_LIGHTNING)) == 0:
            resistance_string += "                   "
        elif res & RESIST_LIGHTNING != 0:
            if flag == 1:
                resistance_string += " | "
            else:
                resistance_string += "   "
            resistance_string += "RESIST_LIGHTNING"
            flag = 1
        else:
            if flag == 1:
                resistance_string += " | "
            else:
                resistance_string += "   "
            resistance_string += "IMMUNE_LIGHTNING"
            flag = 1

        if (res & IMMUNE_NULL_40) != 0:
            pass
            # resistance_string += "IMMUNE_NULL_40 | "
        if (res & IMMUNE_ACID) != 0:
            if flag == 1:
                resistance_string += " | "
            else:
                resistance_string += "   "
            resistance_string += "IMMUNE_ACID"
        else:
            resistance_string += "              "
        resistance_string += "            "
        # resistance_string = resistance_string.strip("|")
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
            f'\"{(get_string(m, monster_dict["animation_pointer"] - mem_offset))}\"' if monster_dict[
                                                                                            "animation_pointer"] != 0 else "nullptr",
            f'\"{(get_string(m, monster_dict["sounds_pointer"] - mem_offset))}\"' if monster_dict[
                                                                                         "sounds_pointer"] != 0 else "nullptr",
            f'\"{(get_string(m, monster_dict["color_trn_pointer"] - mem_offset))}\"' if monster_dict[
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
            monster_dict["monster_selection_outline"],
            monster_dict["item_drop_specials"],
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
                           'ICURS_SPECTRAL_ELIXIR': 15, 'ICURS_GOLDEN_ELIXIR': 17, 'ICURS_EMPYREAN_BAND': 18,
                           'ICURS_EAR_SORCEROR': 19, 'ICURS_EAR_WARRIOR': 20, 'ICURS_EAR_ROGUE': 21,
                           'ICURS_BLOOD_STONE': 25, 'ICURS_ELIXIR_OF_VITALITY': 31, 'ICURS_POTION_OF_HEALING': 32,
                           'ICURS_POTION_OF_FULL_REJUVENATION': 33, 'ICURS_ELIXIR_OF_MAGIC': 34,
                           'ICURS_POTION_OF_FULL_HEALING': 35, 'ICURS_ELIXIR_OF_DEXTERITY': 36,
                           'ICURS_POTION_OF_REJUVENATION': 37, 'ICURS_ELIXIR_OF_STRENGTH': 38,
                           'ICURS_POTION_OF_MANA': 39, 'ICURS_BRAIN': 40, 'ICURS_OPTIC_AMULET': 44, 'ICURS_AMULET': 45,
                           'ICURS_DAGGER': 51, 'ICURS_BLADE': 56, 'ICURS_BASTARD_SWORD': 57, 'ICURS_MACE': 59,
                           'ICURS_LONG_SWORD': 60, 'ICURS_BROAD_SWORD': 61, 'ICURS_FALCHION': 62,
                           'ICURS_MORNING_STAR': 63, 'ICURS_SHORT_SWORD': 64, 'ICURS_CLAYMORE': 65, 'ICURS_CLUB': 66,
                           'ICURS_SABRE': 67, 'ICURS_SPIKED_CLUB': 70, 'ICURS_SCIMITAR': 72, 'ICURS_FULL_HELM': 75,
                           'ICURS_MAGIC_ROCK': 76, 'ICURS_THE_UNDEAD_CROWN': 78, 'ICURS_HELM': 82, 'ICURS_BUCKLER': 83,
                           'ICURS_VIEL_OF_STEEL': 85, 'ICURS_BOOK_GREY': 86, 'ICURS_BOOK_RED': 87,
                           'ICURS_BOOK_BLUE': 88, 'ICURS_BLACK_MUSHROOM': 89, 'ICURS_SKULL_CAP': 90, 'ICURS_CAP': 91,
                           'ICURS_HARLEQUIN_CREST': 93, 'ICURS_CROWN': 95, 'ICURS_MAP_OF_THE_STARS': 96,
                           'ICURS_FUNGAL_TOME': 97, 'ICURS_GREAT_HELM': 98, 'ICURS_BATTLE_AXE': 101,
                           'ICURS_HUNTERS_BOW': 102, 'ICURS_FIELD_PLATE': 103, 'ICURS_SMALL_SHIELD': 105,
                           'ICURS_CLEAVER': 106, 'ICURS_STUDDED_LEATHER_ARMOR': 107, 'ICURS_SHORT_STAFF': 109,
                           'ICURS_TWO_HANDED_SWORD': 110, 'ICURS_CHAIN_MAIL': 111, 'ICURS_SMALL_AXE': 112,
                           'ICURS_KITE_SHIELD': 113, 'ICURS_SCALE_MAIL': 114, 'ICURS_SHORT_BOW': 118,
                           'ICURS_LONG_WAR_BOW': 119, 'ICURS_WAR_HAMMER': 121, 'ICURS_MAUL': 122,
                           'ICURS_LONG_STAFF': 123, 'ICURS_WAR_STAFF': 124, 'ICURS_TAVERN_SIGN': 126,
                           'ICURS_HARD_LEATHER_ARMOR': 127, 'ICURS_RAGS': 128, 'ICURS_QUILTED_ARMOR': 129,
                           'ICURS_FLAIL': 131, 'ICURS_TOWER_SHIELD': 132, 'ICURS_COMPOSITE_BOW': 133,
                           'ICURS_GREAT_SWORD': 134, 'ICURS_LEATHER_ARMOR': 135, 'ICURS_SPLINT_MAIL': 136,
                           'ICURS_ROBE': 137, 'ICURS_ANVIL_OF_FURY': 140, 'ICURS_BROAD_AXE': 141,
                           'ICURS_LARGE_AXE': 142, 'ICURS_GREAT_AXE': 143, 'ICURS_AXE': 144, 'ICURS_LARGE_SHIELD': 147,
                           'ICURS_GOTHIC_SHIELD': 148, 'ICURS_CLOAK': 149, 'ICURS_CAPE': 150,
                           'ICURS_FULL_PLATE_MAIL': 151, 'ICURS_GOTHIC_PLATE': 152, 'ICURS_BREAST_PLATE': 153,
                           'ICURS_RING_MAIL': 154, 'ICURS_STAFF_OF_LAZARUS': 155, 'ICURS_ARKAINES_VALOR': 157,
                           'ICURS_SHORT_WAR_BOW': 165, 'ICURS_COMPOSITE_STAFF': 166, 'ICURS_SHORT_BATTLE_BOW': 167,
                           'ICURS_GOLD': 168}

    # item_cursor_graphic = {'ICURS_POTION_OF_FULL_MANA': 0, 'ICURS_SCROLL_OF': 1, 'ICURS_GOLD_SMALL': 4,
    #                        'ICURS_GOLD_MEDIUM': 5, 'ICURS_GOLD_LARGE': 6, 'ICURS_RING_OF_TRUTH': 10, 'ICURS_RING': 12,
    #                        'ICURS_LES_RING': 13, 'ICURS_NORM_RING': 14, 'ICURS_SPECTRAL_ELIXIR': 15,
    #                        'ICURS_GOLDEN_ELIXIR': 17, 'ICURS_EMPYREAN_BAND': 18, 'ICURS_EAR_SORCERER': 19,
    #                        'ICURS_EAR_WARRIOR': 20, 'ICURS_EAR_ROGUE': 21, 'ICURS_BLOOD_STONE': 25, 'ICURS_GEM': 26,
    #                        'ICURS_OIL': 30, 'ICURS_ELIXIR_OF_VITALITY': 31, 'ICURS_POTION_OF_HEALING': 32,
    #                        'ICURS_POTION_OF_FULL_REJUVENATION': 33, 'ICURS_ELIXIR_OF_MAGIC': 34,
    #                        'ICURS_POTION_OF_FULL_HEALING': 35, 'ICURS_ELIXIR_OF_DEXTERITY': 36,
    #                        'ICURS_POTION_OF_REJUVENATION': 37, 'ICURS_ELIXIR_OF_STRENGTH': 38,
    #                        'ICURS_POTION_OF_MANA': 39, 'ICURS_BRAIN': 40, 'ICURS_CLAW': 41, 'ICURS_OPTIC_AMULET': 44,
    #                        'ICURS_AMULET': 45, 'ICURS_MAJ_AMULET': 48, 'ICURS_MORGUL_KNIFE': 50, 'ICURS_DAGGER': 51,
    #                        'ICURS_LONG_KNIFE': 54, 'ICURS_BLADE': 56, 'ICURS_BASTARD_SWORD': 57, 'ICURS_MACE': 59,
    #                        'ICURS_LONG_SWORD': 60, 'ICURS_BROAD_SWORD': 61, 'ICURS_FALCHION': 62,
    #                        'ICURS_MORNING_STAR': 63, 'ICURS_SHORT_SWORD': 64, 'ICURS_CLAYMORE': 65, 'ICURS_CLUB': 66,
    #                        'ICURS_SABRE': 67, 'ICURS_SH_SWORD': 68, 'ICURS_SPIKED_CLUB': 70, 'ICURS_SPIKED_CLUB2': 71,
    #                        'ICURS_SCIMITAR': 72, 'ICURS_ELVEN_BLADE': 73, 'ICURS_FULL_HELM': 75, 'ICURS_MAGIC_ROCK': 76,
    #                        'ICURS_THE_UNDEAD_CROWN': 78, 'ICURS_HELM': 82, 'ICURS_BUCKLER': 83, 'ICRUS_GREAT_HELM': 84,
    #                        'ICURS_VIEL_OF_STEEL': 85, 'ICURS_BOOK_GREY': 86, 'ICURS_BOOK_RED': 87,
    #                        'ICURS_BOOK_BLUE': 88, 'ICURS_BLACK_MUSHROOM': 89, 'ICURS_SKULL_CAP': 90, 'ICURS_CAP': 91,
    #                        'ICURS_HARLEQUIN_CREST': 93, 'ICURS_SHIRT': 94, 'ICURS_CROWN': 95,
    #                        'ICURS_MAP_OF_THE_STARS': 96, 'ICURS_FUNGAL_TOME': 97, 'ICURS_GREAT_HELM': 98,
    #                        'ICURS_MITHRIL_SHIELD': 100, 'ICURS_BATTLE_AXE': 101, 'ICURS_HUNTERS_BOW': 102,
    #                        'ICURS_FIELD_PLATE': 103, 'ICURS_SMALL_SHIELD': 105, 'ICURS_CLEAVER': 106,
    #                        'ICURS_STUDDED_LEATHER_ARMOR': 107, 'ICURS_SHORT_STAFF': 109, 'ICURS_TWO_HANDED_SWORD': 110,
    #                        'ICURS_CHAIN_MAIL': 111, 'ICURS_SMALL_AXE': 112, 'ICURS_KITE_SHIELD': 113,
    #                        'ICURS_SCALE_MAIL': 114, 'ICURS_DWARVEN_SHIELD': 115, 'ICURS_SHORT_BOW': 118,
    #                        'ICURS_LONG_BATTLE_BOW': 119, 'ICURS_LONG_WAR_BOW': 120, 'ICURS_WAR_HAMMER': 121,
    #                        'ICURS_MAUL': 122, 'ICURS_LONG_STAFF': 123, 'ICURS_WAR_STAFF': 124, 'ICURS_TAVERN_SIGN': 126,
    #                        'ICURS_HARD_LEATHER_ARMOR': 127, 'ICURS_RAGS': 128, 'ICURS_QUILTED_ARMOR': 129,
    #                        'ICURS_WAR_FLAIL': 130, 'ICURS_FLAIL': 131, 'ICURS_TOWER_SHIELD': 132,
    #                        'ICURS_COMPOSITE_BOW': 133, 'ICURS_GREAT_SWORD': 134, 'ICURS_LEATHER_ARMOR': 135,
    #                        'ICURS_SPLINT_MAIL': 136, 'ICURS_ROBE': 137, 'ICURS_MAGE_ROBES': 138,
    #                        'ICURS_CHAIN_SHIRT': 139, 'ICURS_ANVIL_OF_FURY': 140, 'ICURS_BROAD_AXE': 141,
    #                        'ICURS_LARGE_AXE': 142, 'ICURS_GREAT_AXE': 143, 'ICURS_AXE': 144, 'ICURS_NUM_SHIELD': 146,
    #                        'ICURS_LARGE_SHIELD': 147, 'ICURS_GOTHIC_SHIELD': 148, 'ICURS_CLOAK': 149, 'ICURS_CAPE': 150,
    #                        'ICURS_FULL_PLATE_MAIL': 151, 'ICURS_GOTHIC_PLATE': 152, 'ICURS_BREAST_PLATE': 153,
    #                        'ICURS_RING_MAIL': 154, 'ICURS_STAFF_OF_LAZARUS': 155, 'ICURS_WAR_AXE': 156,
    #                        'ICURS_ARKAINES_VALOR': 157, 'ICURS_HEAVY_XBOW': 158, 'ICURS_ROMACIL': 160,
    #                        'ICURS_DWARVEN_AXE': 163, 'ICURS_MALLORN_BOW': 164, 'ICURS_SHORT_WAR_BOW': 165,
    #                        'ICURS_COMPOSITE_STAFF': 166, 'ICURS_SHORT_BATTLE_BOW': 167, 'ICURS_GOLD': 168,
    #                        'ICURS_AURIC_AMULET': 180, 'ICURS_RUNE_BOMB': 187, 'ICURS_THEODORE': 188,
    #                        'ICURS_TORN_NOTE_1': 189, 'ICURS_TORN_NOTE_2': 190, 'ICURS_TORN_NOTE_3': 191,
    #                        'ICURS_RECONSTRUCTED_NOTE': 192, 'ICURS_RUNE_OF_FIRE': 193,
    #                        'ICURS_GREATER_RUNE_OF_FIRE': 194, 'ICURS_RUNE_OF_LIGHTNING': 195,
    #                        'ICURS_GREATER_RUNE_OF_LIGHTNING': 196, 'ICURS_RUNE_OF_STONE': 197, 'ICURS_GREY_SUIT': 198,
    #                        'ICURS_BROWN_SUIT': 199, 'ICURS_BOVINE': 226, 'ICURS_NEW_HELM': 236, 'ICURS_SKULLCAP': 240,
    #                        'ICURS_PLATE_MAIL': 243, 'ICURS_GREAT_BLADE': 244, 'ICURS_LONG_BOW': 248,
    #                        'ICURS_ELVEN_SH_BOW': 249}

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
    package = [("mtype", 4),  # 0-3
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
            get_item_from_array(twos_complement(conv_dict["mtype"], 32), mtype_list, "MT_INVALID"),
            f'P_("monster", "{get_string(m, conv_dict["mName"] - mem_offset)}")',
            f'"{get_string(m, conv_dict["mTrnName"] - mem_offset)}"',
            conv_dict["mlevel"],
            conv_dict["mmaxhp"],
            monster_ai_list[conv_dict["mAi"]],
            conv_dict["mint"],
            conv_dict["mMinDamage"],
            conv_dict["mMaxDamage"],
            get_resists(conv_dict["mMagicRes"]),
            # conv_dict["mUnqAttr"],
            # # conv_dict["mUnqVar1"],
            # # conv_dict["mUnqVar2"],
            # (conv_dict["mUnqVar1"]),

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
        conv_row.append(pack_string)
        customToHit = 0
        # Unique Attribute is To Hit modifier
        if (pack_value & 0b0100) != 0:
            customToHit = conv_dict["mUnqVar1"]

        customArmorClass = 0
        # Unique Attribute is Armor Modifier
        if (pack_value & 0b1000) != 0:
            customArmorClass = conv_dict["mUnqVar1"]
        conv_row.append(customToHit)
        conv_row.append(customArmorClass)

        # conv_row.append((conv_dict["mUnqVar1"]))
        conv_row.append((conv_dict["mlevelNorm"]))
        conv_row.append((conv_dict["mlevelNM"]))
        conv_row.append((conv_dict["mlevelHell"]))
        conv_row.append(speech_list[conv_dict["mtalkmsg"]])

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


def convert_spell_data(m):
    mem_start = 0x000A1288
    block_size = 56
    block_count = 36

    # data
    package = [("sName", 1),  # 0-3
               ("sManaCost", 1),
               ("sType", 1),
               ("padding", 1),
               ("sNameText", 4),
               ("sSkillText", 4),
               ("sBookLvl", 4),
               ("sStaffLvl", 4),
               ("sTargeted", 4),
               ("sTownSpell", 4),
               ("sMinInt", 4),
               ("sSFX", 1),
               ("sMissiles0", 1),
               ("sMissiles1", 1),
               ("sMissiles2", 1),
               ("sManaAdj", 1),
               ("sMinMana", 1),
               ("padding2", 2),
               ("sStaffMin", 4),
               ("sStaffMax", 4),
               ("sBookCost", 4),
               ("sStaffCost", 4),
               ]

    spell_id = {'SPL_NULL': 0x0, 'SPL_FIREBOLT': 0x1, 'SPL_HEAL': 0x2, 'SPL_LIGHTNING': 0x3, 'SPL_FLASH': 0x4,
                'SPL_IDENTIFY': 0x5, 'SPL_FIREWALL': 0x6, 'SPL_TOWN': 0x7, 'SPL_STONE': 0x8, 'SPL_INFRA': 0x9,
                'SPL_RNDTELEPORT': 0xA, 'SPL_MANASHIELD': 0xB, 'SPL_FIREBALL': 0xC, 'SPL_GUARDIAN': 0xD,
                'SPL_CHAIN': 0xE, 'SPL_WAVE': 0xF, 'SPL_DOOMSERP': 0x10, 'SPL_BLODRIT': 0x11, 'SPL_NOVA': 0x12,
                'SPL_INVISIBIL': 0x13, 'SPL_FLAME': 0x14, 'SPL_GOLEM': 0x15, 'SPL_BLODBOIL': 0x16, 'SPL_TELEPORT': 0x17,
                'SPL_APOCA': 0x18, 'SPL_ETHEREALIZE': 0x19, 'SPL_REPAIR': 0x1A, 'SPL_RECHARGE': 0x1B,
                'SPL_DISARM': 0x1C, 'SPL_ELEMENT': 0x1D, 'SPL_CBOLT': 0x1E, 'SPL_HBOLT': 0x1F, 'SPL_RESURRECT': 0x20,
                'SPL_TELEKINESIS': 0x21, 'SPL_HEALOTHER': 0x22, 'SPL_FLARE': 0x23, 'SPL_BONESPIRIT': 0x24,
                'SPL_INVALID': -1}

    magic_type = {'STYPE_FIRE': 0x0, 'STYPE_LIGHTNING': 0x1, 'STYPE_MAGIC': 0x2}

    sfx_id_list = [
        "PS_WALK1",
        "PS_WALK2",
        "PS_WALK3",
        "PS_WALK4",
        "PS_BFIRE",
        "PS_FMAG",
        "PS_TMAG",
        "PS_LGHIT",
        "PS_LGHIT1",
        "PS_SWING",
        "PS_SWING2",
        "PS_DEAD",
        "IS_QUESTDN",
        "IS_ARMRFKD",
        "IS_BARLFIRE",
        "IS_BARREL",
        "IS_BHIT",
        "IS_BHIT1",
        "IS_CHEST",
        "IS_DOORCLOS",
        "IS_DOOROPEN",
        "IS_FANVL",
        "IS_FAXE",
        "IS_FBLST",
        "IS_FBODY",
        "IS_FBOOK",
        "IS_FBOW",
        "IS_FCAP",
        "IS_FHARM",
        "IS_FLARM",
        "IS_FMAG",
        "IS_FMAG1",
        "IS_FMUSH",
        "IS_FPOT",
        "IS_FRING",
        "IS_FROCK",
        "IS_FSCRL",
        "IS_FSHLD",
        "IS_FSIGN",
        "IS_FSTAF",
        "IS_FSWOR",
        "IS_GOLD",
        "IS_HLMTFKD",
        "IS_IANVL",
        "IS_IAXE",
        "IS_IBLST",
        "IS_IBODY",
        "IS_IBOOK",
        "IS_IBOW",
        "IS_ICAP",
        "IS_IGRAB",
        "IS_IHARM",
        "IS_ILARM",
        "IS_IMUSH",
        "IS_IPOT",
        "IS_IRING",
        "IS_IROCK",
        "IS_ISCROL",
        "IS_ISHIEL",
        "IS_ISIGN",
        "IS_ISTAF",
        "IS_ISWORD",
        "IS_LEVER",
        "IS_MAGIC",
        "IS_MAGIC1",
        "IS_RBOOK",
        "IS_SARC",
        "IS_SHLDFKD",
        "IS_SWRDFKD",
        "IS_TITLEMOV",
        "IS_TITLSLCT",
        "SFX_SILENCE",
        "IS_TRAP",
        "IS_CAST1",
        "IS_CAST10",
        "IS_CAST12",
        "IS_CAST2",
        "IS_CAST3",
        "IS_CAST4",
        "IS_CAST5",
        "IS_CAST6",
        "IS_CAST7",
        "IS_CAST8",
        "IS_CAST9",
        "LS_HEALING",
        "IS_REPAIR",
        "LS_ACID",
        "LS_ACIDS",
        "LS_APOC",
        "LS_ARROWALL",
        "LS_BLODBOIL",
        "LS_BLODSTAR",
        "LS_BLSIMPT",
        "LS_BONESP",
        "LS_BSIMPCT",
        "LS_CALDRON",
        "LS_CBOLT",
        "LS_CHLTNING",
        "LS_DSERP",
        "LS_ELECIMP1",
        "LS_ELEMENTL",
        "LS_ETHEREAL",
        "LS_FBALL",
        "LS_FBOLT1",
        "LS_FBOLT2",
        "LS_FIRIMP1",
        "LS_FIRIMP2",
        "LS_FLAMWAVE",
        "LS_FLASH",
        "LS_FOUNTAIN",
        "LS_GOLUM",
        "LS_GOLUMDED",
        "LS_GSHRINE",
        "LS_GUARD",
        "LS_GUARDLAN",
        "LS_HOLYBOLT",
        "LS_HYPER",
        "LS_INFRAVIS",
        "LS_INVISIBL",
        "LS_INVPOT",
        "LS_LNING1",
        "LS_LTNING",
        "LS_MSHIELD",
        "LS_NOVA",
        "LS_PORTAL",
        "LS_PUDDLE",
        "LS_RESUR",
        "LS_SCURSE",
        "LS_SCURIMP",
        "LS_SENTINEL",
        "LS_SHATTER",
        "LS_SOULFIRE",
        "LS_SPOUTLOP",
        "LS_SPOUTSTR",
        "LS_STORM",
        "LS_TRAPDIS",
        "LS_TELEPORT",
        "LS_VTHEFT",
        "LS_WALLLOOP",
        "LS_WALLSTRT",
        "TSFX_BMAID1",
        "TSFX_BMAID2",
        "TSFX_BMAID3",
        "TSFX_BMAID4",
        "TSFX_BMAID5",
        "TSFX_BMAID6",
        "TSFX_BMAID7",
        "TSFX_BMAID8",
        "TSFX_BMAID9",
        "TSFX_BMAID10",
        "TSFX_BMAID11",
        "TSFX_BMAID12",
        "TSFX_BMAID13",
        "TSFX_BMAID14",
        "TSFX_BMAID15",
        "TSFX_BMAID16",
        "TSFX_BMAID17",
        "TSFX_BMAID18",
        "TSFX_BMAID19",
        "TSFX_BMAID20",
        "TSFX_BMAID21",
        "TSFX_BMAID22",
        "TSFX_BMAID23",
        "TSFX_BMAID24",
        "TSFX_BMAID25",
        "TSFX_BMAID26",
        "TSFX_BMAID27",
        "TSFX_BMAID28",
        "TSFX_BMAID29",
        "TSFX_BMAID30",
        "TSFX_BMAID31",
        "TSFX_BMAID32",
        "TSFX_BMAID33",
        "TSFX_BMAID34",
        "TSFX_BMAID35",
        "TSFX_BMAID36",
        "TSFX_BMAID37",
        "TSFX_BMAID38",
        "TSFX_BMAID39",
        "TSFX_BMAID40",
        "TSFX_SMITH1",
        "TSFX_SMITH2",
        "TSFX_SMITH3",
        "TSFX_SMITH4",
        "TSFX_SMITH5",
        "TSFX_SMITH6",
        "TSFX_SMITH7",
        "TSFX_SMITH8",
        "TSFX_SMITH9",
        "TSFX_SMITH10",
        "TSFX_SMITH11",
        "TSFX_SMITH12",
        "TSFX_SMITH13",
        "TSFX_SMITH14",
        "TSFX_SMITH15",
        "TSFX_SMITH16",
        "TSFX_SMITH17",
        "TSFX_SMITH18",
        "TSFX_SMITH19",
        "TSFX_SMITH20",
        "TSFX_SMITH21",
        "TSFX_SMITH22",
        "TSFX_SMITH23",
        "TSFX_SMITH24",
        "TSFX_SMITH25",
        "TSFX_SMITH26",
        "TSFX_SMITH27",
        "TSFX_SMITH28",
        "TSFX_SMITH29",
        "TSFX_SMITH30",
        "TSFX_SMITH31",
        "TSFX_SMITH32",
        "TSFX_SMITH33",
        "TSFX_SMITH34",
        "TSFX_SMITH35",
        "TSFX_SMITH36",
        "TSFX_SMITH37",
        "TSFX_SMITH38",
        "TSFX_SMITH39",
        "TSFX_SMITH40",
        "TSFX_SMITH41",
        "TSFX_SMITH42",
        "TSFX_SMITH43",
        "TSFX_SMITH44",
        "TSFX_SMITH45",
        "TSFX_SMITH46",
        "TSFX_SMITH47",
        "TSFX_SMITH48",
        "TSFX_SMITH49",
        "TSFX_SMITH50",
        "TSFX_SMITH51",
        "TSFX_SMITH52",
        "TSFX_SMITH53",
        "TSFX_SMITH54",
        "TSFX_SMITH55",
        "TSFX_SMITH56",
        "TSFX_COW1",
        "TSFX_COW2",
        "TSFX_DEADGUY",
        "TSFX_DRUNK1",
        "TSFX_DRUNK2",
        "TSFX_DRUNK3",
        "TSFX_DRUNK4",
        "TSFX_DRUNK5",
        "TSFX_DRUNK6",
        "TSFX_DRUNK7",
        "TSFX_DRUNK8",
        "TSFX_DRUNK9",
        "TSFX_DRUNK10",
        "TSFX_DRUNK11",
        "TSFX_DRUNK12",
        "TSFX_DRUNK13",
        "TSFX_DRUNK14",
        "TSFX_DRUNK15",
        "TSFX_DRUNK16",
        "TSFX_DRUNK17",
        "TSFX_DRUNK18",
        "TSFX_DRUNK19",
        "TSFX_DRUNK20",
        "TSFX_DRUNK21",
        "TSFX_DRUNK22",
        "TSFX_DRUNK23",
        "TSFX_DRUNK24",
        "TSFX_DRUNK25",
        "TSFX_DRUNK26",
        "TSFX_DRUNK27",
        "TSFX_DRUNK28",
        "TSFX_DRUNK29",
        "TSFX_DRUNK30",
        "TSFX_DRUNK31",
        "TSFX_DRUNK32",
        "TSFX_DRUNK33",
        "TSFX_DRUNK34",
        "TSFX_DRUNK35",
        "TSFX_HEALER1",
        "TSFX_HEALER2",
        "TSFX_HEALER3",
        "TSFX_HEALER4",
        "TSFX_HEALER5",
        "TSFX_HEALER6",
        "TSFX_HEALER7",
        "TSFX_HEALER8",
        "TSFX_HEALER9",
        "TSFX_HEALER10",
        "TSFX_HEALER11",
        "TSFX_HEALER12",
        "TSFX_HEALER13",
        "TSFX_HEALER14",
        "TSFX_HEALER15",
        "TSFX_HEALER16",
        "TSFX_HEALER17",
        "TSFX_HEALER18",
        "TSFX_HEALER19",
        "TSFX_HEALER20",
        "TSFX_HEALER21",
        "TSFX_HEALER22",
        "TSFX_HEALER23",
        "TSFX_HEALER24",
        "TSFX_HEALER25",
        "TSFX_HEALER26",
        "TSFX_HEALER27",
        "TSFX_HEALER28",
        "TSFX_HEALER29",
        "TSFX_HEALER30",
        "TSFX_HEALER31",
        "TSFX_HEALER32",
        "TSFX_HEALER33",
        "TSFX_HEALER34",
        "TSFX_HEALER35",
        "TSFX_HEALER36",
        "TSFX_HEALER37",
        "TSFX_HEALER38",
        "TSFX_HEALER39",
        "TSFX_HEALER40",
        "TSFX_HEALER41",
        "TSFX_HEALER42",
        "TSFX_HEALER43",
        "TSFX_HEALER44",
        "TSFX_HEALER45",
        "TSFX_HEALER46",
        "TSFX_HEALER47",
        "TSFX_PEGBOY1",
        "TSFX_PEGBOY2",
        "TSFX_PEGBOY3",
        "TSFX_PEGBOY4",
        "TSFX_PEGBOY5",
        "TSFX_PEGBOY6",
        "TSFX_PEGBOY7",
        "TSFX_PEGBOY8",
        "TSFX_PEGBOY9",
        "TSFX_PEGBOY10",
        "TSFX_PEGBOY11",
        "TSFX_PEGBOY12",
        "TSFX_PEGBOY13",
        "TSFX_PEGBOY14",
        "TSFX_PEGBOY15",
        "TSFX_PEGBOY16",
        "TSFX_PEGBOY17",
        "TSFX_PEGBOY18",
        "TSFX_PEGBOY19",
        "TSFX_PEGBOY20",
        "TSFX_PEGBOY21",
        "TSFX_PEGBOY22",
        "TSFX_PEGBOY23",
        "TSFX_PEGBOY24",
        "TSFX_PEGBOY25",
        "TSFX_PEGBOY26",
        "TSFX_PEGBOY27",
        "TSFX_PEGBOY28",
        "TSFX_PEGBOY29",
        "TSFX_PEGBOY30",
        "TSFX_PEGBOY31",
        "TSFX_PEGBOY32",
        "TSFX_PEGBOY33",
        "TSFX_PEGBOY34",
        "TSFX_PEGBOY35",
        "TSFX_PEGBOY36",
        "TSFX_PEGBOY37",
        "TSFX_PEGBOY38",
        "TSFX_PEGBOY39",
        "TSFX_PEGBOY40",
        "TSFX_PEGBOY41",
        "TSFX_PEGBOY42",
        "TSFX_PEGBOY43",
        "TSFX_PRIEST0",
        "TSFX_PRIEST1",
        "TSFX_PRIEST2",
        "TSFX_PRIEST3",
        "TSFX_PRIEST4",
        "TSFX_PRIEST5",
        "TSFX_PRIEST6",
        "TSFX_PRIEST7",
        "TSFX_STORY0",
        "TSFX_STORY1",
        "TSFX_STORY2",
        "TSFX_STORY3",
        "TSFX_STORY4",
        "TSFX_STORY5",
        "TSFX_STORY6",
        "TSFX_STORY7",
        "TSFX_STORY8",
        "TSFX_STORY9",
        "TSFX_STORY10",
        "TSFX_STORY11",
        "TSFX_STORY12",
        "TSFX_STORY13",
        "TSFX_STORY14",
        "TSFX_STORY15",
        "TSFX_STORY16",
        "TSFX_STORY17",
        "TSFX_STORY18",
        "TSFX_STORY19",
        "TSFX_STORY20",
        "TSFX_STORY21",
        "TSFX_STORY22",
        "TSFX_STORY23",
        "TSFX_STORY24",
        "TSFX_STORY25",
        "TSFX_STORY26",
        "TSFX_STORY27",
        "TSFX_STORY28",
        "TSFX_STORY29",
        "TSFX_STORY30",
        "TSFX_STORY31",
        "TSFX_STORY32",
        "TSFX_STORY33",
        "TSFX_STORY34",
        "TSFX_STORY35",
        "TSFX_STORY36",
        "TSFX_STORY37",
        "TSFX_STORY38",
        "TSFX_TAVERN0",
        "TSFX_TAVERN1",
        "TSFX_TAVERN2",
        "TSFX_TAVERN3",
        "TSFX_TAVERN4",
        "TSFX_TAVERN5",
        "TSFX_TAVERN6",
        "TSFX_TAVERN7",
        "TSFX_TAVERN8",
        "TSFX_TAVERN9",
        "TSFX_TAVERN10",
        "TSFX_TAVERN11",
        "TSFX_TAVERN12",
        "TSFX_TAVERN13",
        "TSFX_TAVERN14",
        "TSFX_TAVERN15",
        "TSFX_TAVERN16",
        "TSFX_TAVERN17",
        "TSFX_TAVERN18",
        "TSFX_TAVERN19",
        "TSFX_TAVERN20",
        "TSFX_TAVERN21",
        "TSFX_TAVERN22",
        "TSFX_TAVERN23",
        "TSFX_TAVERN24",
        "TSFX_TAVERN25",
        "TSFX_TAVERN26",
        "TSFX_TAVERN27",
        "TSFX_TAVERN28",
        "TSFX_TAVERN29",
        "TSFX_TAVERN30",
        "TSFX_TAVERN31",
        "TSFX_TAVERN32",
        "TSFX_TAVERN33",
        "TSFX_TAVERN34",
        "TSFX_TAVERN35",
        "TSFX_TAVERN36",
        "TSFX_TAVERN37",
        "TSFX_TAVERN38",
        "TSFX_TAVERN39",
        "TSFX_TAVERN40",
        "TSFX_TAVERN41",
        "TSFX_TAVERN42",
        "TSFX_TAVERN43",
        "TSFX_TAVERN44",
        "TSFX_TAVERN45",
        "TSFX_WITCH1",
        "TSFX_WITCH2",
        "TSFX_WITCH3",
        "TSFX_WITCH4",
        "TSFX_WITCH5",
        "TSFX_WITCH6",
        "TSFX_WITCH7",
        "TSFX_WITCH8",
        "TSFX_WITCH9",
        "TSFX_WITCH10",
        "TSFX_WITCH11",
        "TSFX_WITCH12",
        "TSFX_WITCH13",
        "TSFX_WITCH14",
        "TSFX_WITCH15",
        "TSFX_WITCH16",
        "TSFX_WITCH17",
        "TSFX_WITCH18",
        "TSFX_WITCH19",
        "TSFX_WITCH20",
        "TSFX_WITCH21",
        "TSFX_WITCH22",
        "TSFX_WITCH23",
        "TSFX_WITCH24",
        "TSFX_WITCH25",
        "TSFX_WITCH26",
        "TSFX_WITCH27",
        "TSFX_WITCH28",
        "TSFX_WITCH29",
        "TSFX_WITCH30",
        "TSFX_WITCH31",
        "TSFX_WITCH32",
        "TSFX_WITCH33",
        "TSFX_WITCH34",
        "TSFX_WITCH35",
        "TSFX_WITCH36",
        "TSFX_WITCH37",
        "TSFX_WITCH38",
        "TSFX_WITCH39",
        "TSFX_WITCH40",
        "TSFX_WITCH41",
        "TSFX_WITCH42",
        "TSFX_WITCH43",
        "TSFX_WITCH44",
        "TSFX_WITCH45",
        "TSFX_WITCH46",
        "TSFX_WITCH47",
        "TSFX_WITCH48",
        "TSFX_WITCH49",
        "TSFX_WITCH50",
        "TSFX_WOUND",
        "PS_MAGE1",
        "PS_MAGE2",
        "PS_MAGE3",
        "PS_MAGE4",
        "PS_MAGE5",
        "PS_MAGE6",
        "PS_MAGE7",
        "PS_MAGE8",
        "PS_MAGE9",
        "PS_MAGE10",
        "PS_MAGE11",
        "PS_MAGE12",
        "PS_MAGE13",
        "PS_MAGE14",
        "PS_MAGE15",
        "PS_MAGE16",
        "PS_MAGE17",
        "PS_MAGE18",
        "PS_MAGE19",
        "PS_MAGE20",
        "PS_MAGE21",
        "PS_MAGE22",
        "PS_MAGE23",
        "PS_MAGE24",
        "PS_MAGE25",
        "PS_MAGE26",
        "PS_MAGE27",
        "PS_MAGE28",
        "PS_MAGE29",
        "PS_MAGE30",
        "PS_MAGE31",
        "PS_MAGE32",
        "PS_MAGE33",
        "PS_MAGE34",
        "PS_MAGE35",
        "PS_MAGE36",
        "PS_MAGE37",
        "PS_MAGE38",
        "PS_MAGE39",
        "PS_MAGE40",
        "PS_MAGE41",
        "PS_MAGE42",
        "PS_MAGE43",
        "PS_MAGE44",
        "PS_MAGE45",
        "PS_MAGE46",
        "PS_MAGE47",
        "PS_MAGE48",
        "PS_MAGE49",
        "PS_MAGE50",
        "PS_MAGE51",
        "PS_MAGE52",
        "PS_MAGE53",
        "PS_MAGE54",
        "PS_MAGE55",
        "PS_MAGE56",
        "PS_MAGE57",
        "PS_MAGE58",
        "PS_MAGE59",
        "PS_MAGE60",
        "PS_MAGE61",
        "PS_MAGE62",
        "PS_MAGE63",
        "PS_MAGE64",
        "PS_MAGE65",
        "PS_MAGE66",
        "PS_MAGE67",
        "PS_MAGE68",
        "PS_MAGE69",
        "PS_MAGE69B",
        "PS_MAGE70",
        "PS_MAGE71",
        "PS_MAGE72",
        "PS_MAGE73",
        "PS_MAGE74",
        "PS_MAGE75",
        "PS_MAGE76",
        "PS_MAGE77",
        "PS_MAGE78",
        "PS_MAGE79",
        "PS_MAGE80",
        "PS_MAGE81",
        "PS_MAGE82",
        "PS_MAGE83",
        "PS_MAGE84",
        "PS_MAGE85",
        "PS_MAGE86",
        "PS_MAGE87",
        "PS_MAGE88",
        "PS_MAGE89",
        "PS_MAGE90",
        "PS_MAGE91",
        "PS_MAGE92",
        "PS_MAGE93",
        "PS_MAGE94",
        "PS_MAGE95",
        "PS_MAGE96",
        "PS_MAGE97",
        "PS_MAGE98",
        "PS_MAGE99",
        "PS_MAGE100",
        "PS_MAGE101",
        "PS_MAGE102",
        "PS_ROGUE1",
        "PS_ROGUE2",
        "PS_ROGUE3",
        "PS_ROGUE4",
        "PS_ROGUE5",
        "PS_ROGUE6",
        "PS_ROGUE7",
        "PS_ROGUE8",
        "PS_ROGUE9",
        "PS_ROGUE10",
        "PS_ROGUE11",
        "PS_ROGUE12",
        "PS_ROGUE13",
        "PS_ROGUE14",
        "PS_ROGUE15",
        "PS_ROGUE16",
        "PS_ROGUE17",
        "PS_ROGUE18",
        "PS_ROGUE19",
        "PS_ROGUE20",
        "PS_ROGUE21",
        "PS_ROGUE22",
        "PS_ROGUE23",
        "PS_ROGUE24",
        "PS_ROGUE25",
        "PS_ROGUE26",
        "PS_ROGUE27",
        "PS_ROGUE28",
        "PS_ROGUE29",
        "PS_ROGUE30",
        "PS_ROGUE31",
        "PS_ROGUE32",
        "PS_ROGUE33",
        "PS_ROGUE34",
        "PS_ROGUE35",
        "PS_ROGUE36",
        "PS_ROGUE37",
        "PS_ROGUE38",
        "PS_ROGUE39",
        "PS_ROGUE40",
        "PS_ROGUE41",
        "PS_ROGUE42",
        "PS_ROGUE43",
        "PS_ROGUE44",
        "PS_ROGUE45",
        "PS_ROGUE46",
        "PS_ROGUE47",
        "PS_ROGUE48",
        "PS_ROGUE49",
        "PS_ROGUE50",
        "PS_ROGUE51",
        "PS_ROGUE52",
        "PS_ROGUE53",
        "PS_ROGUE54",
        "PS_ROGUE55",
        "PS_ROGUE56",
        "PS_ROGUE57",
        "PS_ROGUE58",
        "PS_ROGUE59",
        "PS_ROGUE60",
        "PS_ROGUE61",
        "PS_ROGUE62",
        "PS_ROGUE63",
        "PS_ROGUE64",
        "PS_ROGUE65",
        "PS_ROGUE66",
        "PS_ROGUE67",
        "PS_ROGUE68",
        "PS_ROGUE69",
        "PS_ROGUE69B",
        "PS_ROGUE70",
        "PS_ROGUE71",
        "PS_ROGUE72",
        "PS_ROGUE73",
        "PS_ROGUE74",
        "PS_ROGUE75",
        "PS_ROGUE76",
        "PS_ROGUE77",
        "PS_ROGUE78",
        "PS_ROGUE79",
        "PS_ROGUE80",
        "PS_ROGUE81",
        "PS_ROGUE82",
        "PS_ROGUE83",
        "PS_ROGUE84",
        "PS_ROGUE85",
        "PS_ROGUE86",
        "PS_ROGUE87",
        "PS_ROGUE88",
        "PS_ROGUE89",
        "PS_ROGUE90",
        "PS_ROGUE91",
        "PS_ROGUE92",
        "PS_ROGUE93",
        "PS_ROGUE94",
        "PS_ROGUE95",
        "PS_ROGUE96",
        "PS_ROGUE97",
        "PS_ROGUE98",
        "PS_ROGUE99",
        "PS_ROGUE100",
        "PS_ROGUE101",
        "PS_ROGUE102",
        "PS_WARR1",
        "PS_WARR2",
        "PS_WARR3",
        "PS_WARR4",
        "PS_WARR5",
        "PS_WARR6",
        "PS_WARR7",
        "PS_WARR8",
        "PS_WARR9",
        "PS_WARR10",
        "PS_WARR11",
        "PS_WARR12",
        "PS_WARR13",
        "PS_WARR14",
        "PS_WARR14B",
        "PS_WARR14C",
        "PS_WARR15",
        "PS_WARR15B",
        "PS_WARR15C",
        "PS_WARR16",
        "PS_WARR16B",
        "PS_WARR16C",
        "PS_WARR17",
        "PS_WARR18",
        "PS_WARR19",
        "PS_WARR20",
        "PS_WARR21",
        "PS_WARR22",
        "PS_WARR23",
        "PS_WARR24",
        "PS_WARR25",
        "PS_WARR26",
        "PS_WARR27",
        "PS_WARR28",
        "PS_WARR29",
        "PS_WARR30",
        "PS_WARR31",
        "PS_WARR32",
        "PS_WARR33",
        "PS_WARR34",
        "PS_WARR35",
        "PS_WARR36",
        "PS_WARR37",
        "PS_WARR38",
        "PS_WARR39",
        "PS_WARR40",
        "PS_WARR41",
        "PS_WARR42",
        "PS_WARR43",
        "PS_WARR44",
        "PS_WARR45",
        "PS_WARR46",
        "PS_WARR47",
        "PS_WARR48",
        "PS_WARR49",
        "PS_WARR50",
        "PS_WARR51",
        "PS_WARR52",
        "PS_WARR53",
        "PS_WARR54",
        "PS_WARR55",
        "PS_WARR56",
        "PS_WARR57",
        "PS_WARR58",
        "PS_WARR59",
        "PS_WARR60",
        "PS_WARR61",
        "PS_WARR62",
        "PS_WARR63",
        "PS_WARR64",
        "PS_WARR65",
        "PS_WARR66",
        "PS_WARR67",
        "PS_WARR68",
        "PS_WARR69",
        "PS_WARR69B",
        "PS_WARR70",
        "PS_WARR71",
        "PS_WARR72",
        "PS_WARR73",
        "PS_WARR74",
        "PS_WARR75",
        "PS_WARR76",
        "PS_WARR77",
        "PS_WARR78",
        "PS_WARR79",
        "PS_WARR80",
        "PS_WARR81",
        "PS_WARR82",
        "PS_WARR83",
        "PS_WARR84",
        "PS_WARR85",
        "PS_WARR86",
        "PS_WARR87",
        "PS_WARR88",
        "PS_WARR89",
        "PS_WARR90",
        "PS_WARR91",
        "PS_WARR92",
        "PS_WARR93",
        "PS_WARR94",
        "PS_WARR95",
        "PS_WARR95B",
        "PS_WARR95C",
        "PS_WARR95D",
        "PS_WARR95E",
        "PS_WARR95F",
        "PS_WARR96B",
        "PS_WARR97",
        "PS_WARR98",
        "PS_WARR99",
        "PS_WARR100",
        "PS_WARR101",
        "PS_WARR102",
        "PS_NAR1",
        "PS_NAR2",
        "PS_NAR3",
        "PS_NAR4",
        "PS_NAR5",
        "PS_NAR6",
        "PS_NAR7",
        "PS_NAR8",
        "PS_NAR9",
        "PS_DIABLVLINT",
        "USFX_CLEAVER",
        "USFX_GARBUD1",
        "USFX_GARBUD2",
        "USFX_GARBUD3",
        "USFX_GARBUD4",
        "USFX_IZUAL1",
        "USFX_LACH1",
        "USFX_LACH2",
        "USFX_LACH3",
        "USFX_LAZ1",
        "USFX_LAZ2",
        "USFX_SKING1",
        "USFX_SNOT1",
        "USFX_SNOT2",
        "USFX_SNOT3",
        "USFX_WARLRD1",
        "USFX_WLOCK1",
        "USFX_ZHAR1",
        "USFX_ZHAR2",
        "USFX_DIABLOD",
    ]

    missile_id = {'MIS_NULL': 0x0, 'MIS_FIREBOLT': 0x1, 'MIS_GUARDIAN': 0x2, 'MIS_RNDTELEPORT': 0x3,
                  'MIS_LIGHTBALL': 0x4, 'MIS_FIREWALL': 0x5, 'MIS_FIREBALL': 0x6, 'MIS_LIGHTCTRL': 0x7,
                  'MIS_LIGHTNING': 0x8, 'MIS_MISEXP': 0x9, 'MIS_TOWN': 0xA, 'MIS_FLASH': 0xB, 'MIS_FLASH2': 0xC,
                  'MIS_MANASHIELD': 0xD, 'MIS_FIREMOVE': 0xE, 'MIS_CHAIN': 0xF, 'MIS_SENTINAL': 0x10,
                  'MIS_BLODSTAR': 0x11, 'MIS_BONE': 0x12, 'MIS_METLHIT': 0x13, 'MIS_RHINO': 0x14, 'MIS_MAGMABALL': 0x15,
                  'MIS_LIGHTCTRL2': 0x16, 'MIS_LIGHTNING2': 0x17, 'MIS_FLARE': 0x18, 'MIS_MISEXP2': 0x19,
                  'MIS_TELEPORT': 0x1A, 'MIS_FARROW': 0x1B, 'MIS_DOOMSERP': 0x1C, 'MIS_FIREWALLA': 0x1D,
                  'MIS_STONE': 0x1E, 'MIS_NULL_1F': 0x1F, 'MIS_INVISIBL': 0x20, 'MIS_GOLEM': 0x21,
                  'MIS_ETHEREALIZE': 0x22, 'MIS_BLODBUR': 0x23, 'MIS_BOOM': 0x24, 'MIS_HEAL': 0x25,
                  'MIS_FIREWALLC': 0x26, 'MIS_INFRA': 0x27, 'MIS_IDENTIFY': 0x28, 'MIS_WAVE': 0x29, 'MIS_NOVA': 0x2A,
                  'MIS_BLODBOIL': 0x2B, 'MIS_APOCA': 0x2C, 'MIS_REPAIR': 0x2D, 'MIS_RECHARGE': 0x2E, 'MIS_DISARM': 0x2F,
                  'MIS_FLAME': 0x30, 'MIS_FLAMEC': 0x31, 'MIS_FIREMAN': 0x32, 'MIS_KRULL': 0x33, 'MIS_CBOLT': 0x34,
                  'MIS_HBOLT': 0x35, 'MIS_RESURRECT': 0x36, 'MIS_TELEKINESIS': 0x37, 'MIS_LARROW': 0x38,
                  'MIS_ACID': 0x39, 'MIS_MISEXP3': 0x3A, 'MIS_ACIDPUD': 0x3B, 'MIS_HEALOTHER': 0x3C,
                  'MIS_ELEMENT': 0x3D, 'MIS_RESURRECTBEAM': 0x3E, 'MIS_BONESPIRIT': 0x3F, 'MIS_WEAPEXP': 0x40,
                  'MIS_RPORTAL': 0x41, 'MIS_BOOM2': 0x42, 'MIS_DIABAPOCA': 0x43}

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
            convert_exclusive_flag(conv_dict["sName"], spell_id),
            conv_dict["sManaCost"],
            convert_exclusive_flag(conv_dict["sType"], magic_type),
            # print(conv_dict["sNameText"]),
            f'P_("spell", "{get_string(m, conv_dict["sNameText"] - mem_offset)}")' if conv_dict[
                                                                                          "sNameText"] != 0 else "nullptr",
            f'P_("spell", "{get_string(m, conv_dict["sSkillText"] - mem_offset)}")' if conv_dict[
                                                                                           "sSkillText"] != 0 else "nullptr",
            twos_complement(conv_dict["sBookLvl"], 32),
            twos_complement(conv_dict["sStaffLvl"], 32),
            "true" if conv_dict["sTargeted"] != 0 else "false",
            "true" if conv_dict["sTownSpell"] != 0 else "false",
            twos_complement(conv_dict["sMinInt"], 32),
            sfx_id_list[conv_dict["sSFX"]],
            f'{{ {convert_exclusive_flag(twos_complement(conv_dict["sMissiles0"], 8), missile_id)}',
            f' {convert_exclusive_flag(twos_complement(conv_dict["sMissiles1"], 8), missile_id)}',
            f' {convert_exclusive_flag(twos_complement(conv_dict["sMissiles2"], 8), missile_id)} }}',
            conv_dict["sManaAdj"],
            conv_dict["sMinMana"],
            conv_dict["sStaffMin"],
            conv_dict["sStaffMax"],
            conv_dict["sBookCost"],
            conv_dict["sStaffCost"],
        ]

        conv_table.append(conv_row)
    # actual_label_order = [
    #     "iRnd",
    #     "iClass",
    #     "iLoc",
    #     "iCurs",
    #     "itype",
    #     "iItemId",
    #     "iName",
    #     "isName",
    #     "iMinMLvl",
    #     "iDurability",
    #     "iMinDam",
    #     "iMaxDam",
    #     "iMinAC",
    #     "iMaxAC",
    #     "iMinStr",
    #     "iMinMag",
    #     "iMinDex",
    #     "iFlags",
    #     "iMiscId",
    #     "iSpell",
    #     "iUsable",
    #     "iValue",
    # ]

    # print("; ".join(actual_label_order))
    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_missile_data(m):
    mem_start = 0x000937A8
    block_size = 28
    block_count = 68

    # data
    package = [("mName", 1),  # 0-3
               ("padding", 3),
               ("mAddProc", 4),
               ("mProc", 4),
               ("mDraw", 4),
               ("mType", 1),
               ("mResist", 1),
               ("mFileNum", 1),
               ("padding2", 1),
               ("mlSFX", 4),
               ("miSFX", 4),
               ]

    spell_id = {'SPL_NULL': 0x0, 'SPL_FIREBOLT': 0x1, 'SPL_HEAL': 0x2, 'SPL_LIGHTNING': 0x3, 'SPL_FLASH': 0x4,
                'SPL_IDENTIFY': 0x5, 'SPL_FIREWALL': 0x6, 'SPL_TOWN': 0x7, 'SPL_STONE': 0x8, 'SPL_INFRA': 0x9,
                'SPL_RNDTELEPORT': 0xA, 'SPL_MANASHIELD': 0xB, 'SPL_FIREBALL': 0xC, 'SPL_GUARDIAN': 0xD,
                'SPL_CHAIN': 0xE, 'SPL_WAVE': 0xF, 'SPL_DOOMSERP': 0x10, 'SPL_BLODRIT': 0x11, 'SPL_NOVA': 0x12,
                'SPL_INVISIBIL': 0x13, 'SPL_FLAME': 0x14, 'SPL_GOLEM': 0x15, 'SPL_BLODBOIL': 0x16, 'SPL_TELEPORT': 0x17,
                'SPL_APOCA': 0x18, 'SPL_ETHEREALIZE': 0x19, 'SPL_REPAIR': 0x1A, 'SPL_RECHARGE': 0x1B,
                'SPL_DISARM': 0x1C, 'SPL_ELEMENT': 0x1D, 'SPL_CBOLT': 0x1E, 'SPL_HBOLT': 0x1F, 'SPL_RESURRECT': 0x20,
                'SPL_TELEKINESIS': 0x21, 'SPL_HEALOTHER': 0x22, 'SPL_FLARE': 0x23, 'SPL_BONESPIRIT': 0x24,
                'SPL_INVALID': -1}

    magic_type = {'STYPE_FIRE': 0x0, 'STYPE_LIGHTNING': 0x1, 'STYPE_MAGIC': 0x2}

    sfx_id_list = [
        "PS_WALK1",
        "PS_WALK2",
        "PS_WALK3",
        "PS_WALK4",
        "PS_BFIRE",
        "PS_FMAG",
        "PS_TMAG",
        "PS_LGHIT",
        "PS_LGHIT1",
        "PS_SWING",
        "PS_SWING2",
        "PS_DEAD",
        "IS_QUESTDN",
        "IS_ARMRFKD",
        "IS_BARLFIRE",
        "IS_BARREL",
        "IS_BHIT",
        "IS_BHIT1",
        "IS_CHEST",
        "IS_DOORCLOS",
        "IS_DOOROPEN",
        "IS_FANVL",
        "IS_FAXE",
        "IS_FBLST",
        "IS_FBODY",
        "IS_FBOOK",
        "IS_FBOW",
        "IS_FCAP",
        "IS_FHARM",
        "IS_FLARM",
        "IS_FMAG",
        "IS_FMAG1",
        "IS_FMUSH",
        "IS_FPOT",
        "IS_FRING",
        "IS_FROCK",
        "IS_FSCRL",
        "IS_FSHLD",
        "IS_FSIGN",
        "IS_FSTAF",
        "IS_FSWOR",
        "IS_GOLD",
        "IS_HLMTFKD",
        "IS_IANVL",
        "IS_IAXE",
        "IS_IBLST",
        "IS_IBODY",
        "IS_IBOOK",
        "IS_IBOW",
        "IS_ICAP",
        "IS_IGRAB",
        "IS_IHARM",
        "IS_ILARM",
        "IS_IMUSH",
        "IS_IPOT",
        "IS_IRING",
        "IS_IROCK",
        "IS_ISCROL",
        "IS_ISHIEL",
        "IS_ISIGN",
        "IS_ISTAF",
        "IS_ISWORD",
        "IS_LEVER",
        "IS_MAGIC",
        "IS_MAGIC1",
        "IS_RBOOK",
        "IS_SARC",
        "IS_SHLDFKD",
        "IS_SWRDFKD",
        "IS_TITLEMOV",
        "IS_TITLSLCT",
        "SFX_SILENCE",
        "IS_TRAP",
        "IS_CAST1",
        "IS_CAST10",
        "IS_CAST12",
        "IS_CAST2",
        "IS_CAST3",
        "IS_CAST4",
        "IS_CAST5",
        "IS_CAST6",
        "IS_CAST7",
        "IS_CAST8",
        "IS_CAST9",
        "LS_HEALING",
        "IS_REPAIR",
        "LS_ACID",
        "LS_ACIDS",
        "LS_APOC",
        "LS_ARROWALL",
        "LS_BLODBOIL",
        "LS_BLODSTAR",
        "LS_BLSIMPT",
        "LS_BONESP",
        "LS_BSIMPCT",
        "LS_CALDRON",
        "LS_CBOLT",
        "LS_CHLTNING",
        "LS_DSERP",
        "LS_ELECIMP1",
        "LS_ELEMENTL",
        "LS_ETHEREAL",
        "LS_FBALL",
        "LS_FBOLT1",
        "LS_FBOLT2",
        "LS_FIRIMP1",
        "LS_FIRIMP2",
        "LS_FLAMWAVE",
        "LS_FLASH",
        "LS_FOUNTAIN",
        "LS_GOLUM",
        "LS_GOLUMDED",
        "LS_GSHRINE",
        "LS_GUARD",
        "LS_GUARDLAN",
        "LS_HOLYBOLT",
        "LS_HYPER",
        "LS_INFRAVIS",
        "LS_INVISIBL",
        "LS_INVPOT",
        "LS_LNING1",
        "LS_LTNING",
        "LS_MSHIELD",
        "LS_NOVA",
        "LS_PORTAL",
        "LS_PUDDLE",
        "LS_RESUR",
        "LS_SCURSE",
        "LS_SCURIMP",
        "LS_SENTINEL",
        "LS_SHATTER",
        "LS_SOULFIRE",
        "LS_SPOUTLOP",
        "LS_SPOUTSTR",
        "LS_STORM",
        "LS_TRAPDIS",
        "LS_TELEPORT",
        "LS_VTHEFT",
        "LS_WALLLOOP",
        "LS_WALLSTRT",
        "TSFX_BMAID1",
        "TSFX_BMAID2",
        "TSFX_BMAID3",
        "TSFX_BMAID4",
        "TSFX_BMAID5",
        "TSFX_BMAID6",
        "TSFX_BMAID7",
        "TSFX_BMAID8",
        "TSFX_BMAID9",
        "TSFX_BMAID10",
        "TSFX_BMAID11",
        "TSFX_BMAID12",
        "TSFX_BMAID13",
        "TSFX_BMAID14",
        "TSFX_BMAID15",
        "TSFX_BMAID16",
        "TSFX_BMAID17",
        "TSFX_BMAID18",
        "TSFX_BMAID19",
        "TSFX_BMAID20",
        "TSFX_BMAID21",
        "TSFX_BMAID22",
        "TSFX_BMAID23",
        "TSFX_BMAID24",
        "TSFX_BMAID25",
        "TSFX_BMAID26",
        "TSFX_BMAID27",
        "TSFX_BMAID28",
        "TSFX_BMAID29",
        "TSFX_BMAID30",
        "TSFX_BMAID31",
        "TSFX_BMAID32",
        "TSFX_BMAID33",
        "TSFX_BMAID34",
        "TSFX_BMAID35",
        "TSFX_BMAID36",
        "TSFX_BMAID37",
        "TSFX_BMAID38",
        "TSFX_BMAID39",
        "TSFX_BMAID40",
        "TSFX_SMITH1",
        "TSFX_SMITH2",
        "TSFX_SMITH3",
        "TSFX_SMITH4",
        "TSFX_SMITH5",
        "TSFX_SMITH6",
        "TSFX_SMITH7",
        "TSFX_SMITH8",
        "TSFX_SMITH9",
        "TSFX_SMITH10",
        "TSFX_SMITH11",
        "TSFX_SMITH12",
        "TSFX_SMITH13",
        "TSFX_SMITH14",
        "TSFX_SMITH15",
        "TSFX_SMITH16",
        "TSFX_SMITH17",
        "TSFX_SMITH18",
        "TSFX_SMITH19",
        "TSFX_SMITH20",
        "TSFX_SMITH21",
        "TSFX_SMITH22",
        "TSFX_SMITH23",
        "TSFX_SMITH24",
        "TSFX_SMITH25",
        "TSFX_SMITH26",
        "TSFX_SMITH27",
        "TSFX_SMITH28",
        "TSFX_SMITH29",
        "TSFX_SMITH30",
        "TSFX_SMITH31",
        "TSFX_SMITH32",
        "TSFX_SMITH33",
        "TSFX_SMITH34",
        "TSFX_SMITH35",
        "TSFX_SMITH36",
        "TSFX_SMITH37",
        "TSFX_SMITH38",
        "TSFX_SMITH39",
        "TSFX_SMITH40",
        "TSFX_SMITH41",
        "TSFX_SMITH42",
        "TSFX_SMITH43",
        "TSFX_SMITH44",
        "TSFX_SMITH45",
        "TSFX_SMITH46",
        "TSFX_SMITH47",
        "TSFX_SMITH48",
        "TSFX_SMITH49",
        "TSFX_SMITH50",
        "TSFX_SMITH51",
        "TSFX_SMITH52",
        "TSFX_SMITH53",
        "TSFX_SMITH54",
        "TSFX_SMITH55",
        "TSFX_SMITH56",
        "TSFX_COW1",
        "TSFX_COW2",
        "TSFX_DEADGUY",
        "TSFX_DRUNK1",
        "TSFX_DRUNK2",
        "TSFX_DRUNK3",
        "TSFX_DRUNK4",
        "TSFX_DRUNK5",
        "TSFX_DRUNK6",
        "TSFX_DRUNK7",
        "TSFX_DRUNK8",
        "TSFX_DRUNK9",
        "TSFX_DRUNK10",
        "TSFX_DRUNK11",
        "TSFX_DRUNK12",
        "TSFX_DRUNK13",
        "TSFX_DRUNK14",
        "TSFX_DRUNK15",
        "TSFX_DRUNK16",
        "TSFX_DRUNK17",
        "TSFX_DRUNK18",
        "TSFX_DRUNK19",
        "TSFX_DRUNK20",
        "TSFX_DRUNK21",
        "TSFX_DRUNK22",
        "TSFX_DRUNK23",
        "TSFX_DRUNK24",
        "TSFX_DRUNK25",
        "TSFX_DRUNK26",
        "TSFX_DRUNK27",
        "TSFX_DRUNK28",
        "TSFX_DRUNK29",
        "TSFX_DRUNK30",
        "TSFX_DRUNK31",
        "TSFX_DRUNK32",
        "TSFX_DRUNK33",
        "TSFX_DRUNK34",
        "TSFX_DRUNK35",
        "TSFX_HEALER1",
        "TSFX_HEALER2",
        "TSFX_HEALER3",
        "TSFX_HEALER4",
        "TSFX_HEALER5",
        "TSFX_HEALER6",
        "TSFX_HEALER7",
        "TSFX_HEALER8",
        "TSFX_HEALER9",
        "TSFX_HEALER10",
        "TSFX_HEALER11",
        "TSFX_HEALER12",
        "TSFX_HEALER13",
        "TSFX_HEALER14",
        "TSFX_HEALER15",
        "TSFX_HEALER16",
        "TSFX_HEALER17",
        "TSFX_HEALER18",
        "TSFX_HEALER19",
        "TSFX_HEALER20",
        "TSFX_HEALER21",
        "TSFX_HEALER22",
        "TSFX_HEALER23",
        "TSFX_HEALER24",
        "TSFX_HEALER25",
        "TSFX_HEALER26",
        "TSFX_HEALER27",
        "TSFX_HEALER28",
        "TSFX_HEALER29",
        "TSFX_HEALER30",
        "TSFX_HEALER31",
        "TSFX_HEALER32",
        "TSFX_HEALER33",
        "TSFX_HEALER34",
        "TSFX_HEALER35",
        "TSFX_HEALER36",
        "TSFX_HEALER37",
        "TSFX_HEALER38",
        "TSFX_HEALER39",
        "TSFX_HEALER40",
        "TSFX_HEALER41",
        "TSFX_HEALER42",
        "TSFX_HEALER43",
        "TSFX_HEALER44",
        "TSFX_HEALER45",
        "TSFX_HEALER46",
        "TSFX_HEALER47",
        "TSFX_PEGBOY1",
        "TSFX_PEGBOY2",
        "TSFX_PEGBOY3",
        "TSFX_PEGBOY4",
        "TSFX_PEGBOY5",
        "TSFX_PEGBOY6",
        "TSFX_PEGBOY7",
        "TSFX_PEGBOY8",
        "TSFX_PEGBOY9",
        "TSFX_PEGBOY10",
        "TSFX_PEGBOY11",
        "TSFX_PEGBOY12",
        "TSFX_PEGBOY13",
        "TSFX_PEGBOY14",
        "TSFX_PEGBOY15",
        "TSFX_PEGBOY16",
        "TSFX_PEGBOY17",
        "TSFX_PEGBOY18",
        "TSFX_PEGBOY19",
        "TSFX_PEGBOY20",
        "TSFX_PEGBOY21",
        "TSFX_PEGBOY22",
        "TSFX_PEGBOY23",
        "TSFX_PEGBOY24",
        "TSFX_PEGBOY25",
        "TSFX_PEGBOY26",
        "TSFX_PEGBOY27",
        "TSFX_PEGBOY28",
        "TSFX_PEGBOY29",
        "TSFX_PEGBOY30",
        "TSFX_PEGBOY31",
        "TSFX_PEGBOY32",
        "TSFX_PEGBOY33",
        "TSFX_PEGBOY34",
        "TSFX_PEGBOY35",
        "TSFX_PEGBOY36",
        "TSFX_PEGBOY37",
        "TSFX_PEGBOY38",
        "TSFX_PEGBOY39",
        "TSFX_PEGBOY40",
        "TSFX_PEGBOY41",
        "TSFX_PEGBOY42",
        "TSFX_PEGBOY43",
        "TSFX_PRIEST0",
        "TSFX_PRIEST1",
        "TSFX_PRIEST2",
        "TSFX_PRIEST3",
        "TSFX_PRIEST4",
        "TSFX_PRIEST5",
        "TSFX_PRIEST6",
        "TSFX_PRIEST7",
        "TSFX_STORY0",
        "TSFX_STORY1",
        "TSFX_STORY2",
        "TSFX_STORY3",
        "TSFX_STORY4",
        "TSFX_STORY5",
        "TSFX_STORY6",
        "TSFX_STORY7",
        "TSFX_STORY8",
        "TSFX_STORY9",
        "TSFX_STORY10",
        "TSFX_STORY11",
        "TSFX_STORY12",
        "TSFX_STORY13",
        "TSFX_STORY14",
        "TSFX_STORY15",
        "TSFX_STORY16",
        "TSFX_STORY17",
        "TSFX_STORY18",
        "TSFX_STORY19",
        "TSFX_STORY20",
        "TSFX_STORY21",
        "TSFX_STORY22",
        "TSFX_STORY23",
        "TSFX_STORY24",
        "TSFX_STORY25",
        "TSFX_STORY26",
        "TSFX_STORY27",
        "TSFX_STORY28",
        "TSFX_STORY29",
        "TSFX_STORY30",
        "TSFX_STORY31",
        "TSFX_STORY32",
        "TSFX_STORY33",
        "TSFX_STORY34",
        "TSFX_STORY35",
        "TSFX_STORY36",
        "TSFX_STORY37",
        "TSFX_STORY38",
        "TSFX_TAVERN0",
        "TSFX_TAVERN1",
        "TSFX_TAVERN2",
        "TSFX_TAVERN3",
        "TSFX_TAVERN4",
        "TSFX_TAVERN5",
        "TSFX_TAVERN6",
        "TSFX_TAVERN7",
        "TSFX_TAVERN8",
        "TSFX_TAVERN9",
        "TSFX_TAVERN10",
        "TSFX_TAVERN11",
        "TSFX_TAVERN12",
        "TSFX_TAVERN13",
        "TSFX_TAVERN14",
        "TSFX_TAVERN15",
        "TSFX_TAVERN16",
        "TSFX_TAVERN17",
        "TSFX_TAVERN18",
        "TSFX_TAVERN19",
        "TSFX_TAVERN20",
        "TSFX_TAVERN21",
        "TSFX_TAVERN22",
        "TSFX_TAVERN23",
        "TSFX_TAVERN24",
        "TSFX_TAVERN25",
        "TSFX_TAVERN26",
        "TSFX_TAVERN27",
        "TSFX_TAVERN28",
        "TSFX_TAVERN29",
        "TSFX_TAVERN30",
        "TSFX_TAVERN31",
        "TSFX_TAVERN32",
        "TSFX_TAVERN33",
        "TSFX_TAVERN34",
        "TSFX_TAVERN35",
        "TSFX_TAVERN36",
        "TSFX_TAVERN37",
        "TSFX_TAVERN38",
        "TSFX_TAVERN39",
        "TSFX_TAVERN40",
        "TSFX_TAVERN41",
        "TSFX_TAVERN42",
        "TSFX_TAVERN43",
        "TSFX_TAVERN44",
        "TSFX_TAVERN45",
        "TSFX_WITCH1",
        "TSFX_WITCH2",
        "TSFX_WITCH3",
        "TSFX_WITCH4",
        "TSFX_WITCH5",
        "TSFX_WITCH6",
        "TSFX_WITCH7",
        "TSFX_WITCH8",
        "TSFX_WITCH9",
        "TSFX_WITCH10",
        "TSFX_WITCH11",
        "TSFX_WITCH12",
        "TSFX_WITCH13",
        "TSFX_WITCH14",
        "TSFX_WITCH15",
        "TSFX_WITCH16",
        "TSFX_WITCH17",
        "TSFX_WITCH18",
        "TSFX_WITCH19",
        "TSFX_WITCH20",
        "TSFX_WITCH21",
        "TSFX_WITCH22",
        "TSFX_WITCH23",
        "TSFX_WITCH24",
        "TSFX_WITCH25",
        "TSFX_WITCH26",
        "TSFX_WITCH27",
        "TSFX_WITCH28",
        "TSFX_WITCH29",
        "TSFX_WITCH30",
        "TSFX_WITCH31",
        "TSFX_WITCH32",
        "TSFX_WITCH33",
        "TSFX_WITCH34",
        "TSFX_WITCH35",
        "TSFX_WITCH36",
        "TSFX_WITCH37",
        "TSFX_WITCH38",
        "TSFX_WITCH39",
        "TSFX_WITCH40",
        "TSFX_WITCH41",
        "TSFX_WITCH42",
        "TSFX_WITCH43",
        "TSFX_WITCH44",
        "TSFX_WITCH45",
        "TSFX_WITCH46",
        "TSFX_WITCH47",
        "TSFX_WITCH48",
        "TSFX_WITCH49",
        "TSFX_WITCH50",
        "TSFX_WOUND",
        "PS_MAGE1",
        "PS_MAGE2",
        "PS_MAGE3",
        "PS_MAGE4",
        "PS_MAGE5",
        "PS_MAGE6",
        "PS_MAGE7",
        "PS_MAGE8",
        "PS_MAGE9",
        "PS_MAGE10",
        "PS_MAGE11",
        "PS_MAGE12",
        "PS_MAGE13",
        "PS_MAGE14",
        "PS_MAGE15",
        "PS_MAGE16",
        "PS_MAGE17",
        "PS_MAGE18",
        "PS_MAGE19",
        "PS_MAGE20",
        "PS_MAGE21",
        "PS_MAGE22",
        "PS_MAGE23",
        "PS_MAGE24",
        "PS_MAGE25",
        "PS_MAGE26",
        "PS_MAGE27",
        "PS_MAGE28",
        "PS_MAGE29",
        "PS_MAGE30",
        "PS_MAGE31",
        "PS_MAGE32",
        "PS_MAGE33",
        "PS_MAGE34",
        "PS_MAGE35",
        "PS_MAGE36",
        "PS_MAGE37",
        "PS_MAGE38",
        "PS_MAGE39",
        "PS_MAGE40",
        "PS_MAGE41",
        "PS_MAGE42",
        "PS_MAGE43",
        "PS_MAGE44",
        "PS_MAGE45",
        "PS_MAGE46",
        "PS_MAGE47",
        "PS_MAGE48",
        "PS_MAGE49",
        "PS_MAGE50",
        "PS_MAGE51",
        "PS_MAGE52",
        "PS_MAGE53",
        "PS_MAGE54",
        "PS_MAGE55",
        "PS_MAGE56",
        "PS_MAGE57",
        "PS_MAGE58",
        "PS_MAGE59",
        "PS_MAGE60",
        "PS_MAGE61",
        "PS_MAGE62",
        "PS_MAGE63",
        "PS_MAGE64",
        "PS_MAGE65",
        "PS_MAGE66",
        "PS_MAGE67",
        "PS_MAGE68",
        "PS_MAGE69",
        "PS_MAGE69B",
        "PS_MAGE70",
        "PS_MAGE71",
        "PS_MAGE72",
        "PS_MAGE73",
        "PS_MAGE74",
        "PS_MAGE75",
        "PS_MAGE76",
        "PS_MAGE77",
        "PS_MAGE78",
        "PS_MAGE79",
        "PS_MAGE80",
        "PS_MAGE81",
        "PS_MAGE82",
        "PS_MAGE83",
        "PS_MAGE84",
        "PS_MAGE85",
        "PS_MAGE86",
        "PS_MAGE87",
        "PS_MAGE88",
        "PS_MAGE89",
        "PS_MAGE90",
        "PS_MAGE91",
        "PS_MAGE92",
        "PS_MAGE93",
        "PS_MAGE94",
        "PS_MAGE95",
        "PS_MAGE96",
        "PS_MAGE97",
        "PS_MAGE98",
        "PS_MAGE99",
        "PS_MAGE100",
        "PS_MAGE101",
        "PS_MAGE102",
        "PS_ROGUE1",
        "PS_ROGUE2",
        "PS_ROGUE3",
        "PS_ROGUE4",
        "PS_ROGUE5",
        "PS_ROGUE6",
        "PS_ROGUE7",
        "PS_ROGUE8",
        "PS_ROGUE9",
        "PS_ROGUE10",
        "PS_ROGUE11",
        "PS_ROGUE12",
        "PS_ROGUE13",
        "PS_ROGUE14",
        "PS_ROGUE15",
        "PS_ROGUE16",
        "PS_ROGUE17",
        "PS_ROGUE18",
        "PS_ROGUE19",
        "PS_ROGUE20",
        "PS_ROGUE21",
        "PS_ROGUE22",
        "PS_ROGUE23",
        "PS_ROGUE24",
        "PS_ROGUE25",
        "PS_ROGUE26",
        "PS_ROGUE27",
        "PS_ROGUE28",
        "PS_ROGUE29",
        "PS_ROGUE30",
        "PS_ROGUE31",
        "PS_ROGUE32",
        "PS_ROGUE33",
        "PS_ROGUE34",
        "PS_ROGUE35",
        "PS_ROGUE36",
        "PS_ROGUE37",
        "PS_ROGUE38",
        "PS_ROGUE39",
        "PS_ROGUE40",
        "PS_ROGUE41",
        "PS_ROGUE42",
        "PS_ROGUE43",
        "PS_ROGUE44",
        "PS_ROGUE45",
        "PS_ROGUE46",
        "PS_ROGUE47",
        "PS_ROGUE48",
        "PS_ROGUE49",
        "PS_ROGUE50",
        "PS_ROGUE51",
        "PS_ROGUE52",
        "PS_ROGUE53",
        "PS_ROGUE54",
        "PS_ROGUE55",
        "PS_ROGUE56",
        "PS_ROGUE57",
        "PS_ROGUE58",
        "PS_ROGUE59",
        "PS_ROGUE60",
        "PS_ROGUE61",
        "PS_ROGUE62",
        "PS_ROGUE63",
        "PS_ROGUE64",
        "PS_ROGUE65",
        "PS_ROGUE66",
        "PS_ROGUE67",
        "PS_ROGUE68",
        "PS_ROGUE69",
        "PS_ROGUE69B",
        "PS_ROGUE70",
        "PS_ROGUE71",
        "PS_ROGUE72",
        "PS_ROGUE73",
        "PS_ROGUE74",
        "PS_ROGUE75",
        "PS_ROGUE76",
        "PS_ROGUE77",
        "PS_ROGUE78",
        "PS_ROGUE79",
        "PS_ROGUE80",
        "PS_ROGUE81",
        "PS_ROGUE82",
        "PS_ROGUE83",
        "PS_ROGUE84",
        "PS_ROGUE85",
        "PS_ROGUE86",
        "PS_ROGUE87",
        "PS_ROGUE88",
        "PS_ROGUE89",
        "PS_ROGUE90",
        "PS_ROGUE91",
        "PS_ROGUE92",
        "PS_ROGUE93",
        "PS_ROGUE94",
        "PS_ROGUE95",
        "PS_ROGUE96",
        "PS_ROGUE97",
        "PS_ROGUE98",
        "PS_ROGUE99",
        "PS_ROGUE100",
        "PS_ROGUE101",
        "PS_ROGUE102",
        "PS_WARR1",
        "PS_WARR2",
        "PS_WARR3",
        "PS_WARR4",
        "PS_WARR5",
        "PS_WARR6",
        "PS_WARR7",
        "PS_WARR8",
        "PS_WARR9",
        "PS_WARR10",
        "PS_WARR11",
        "PS_WARR12",
        "PS_WARR13",
        "PS_WARR14",
        "PS_WARR14B",
        "PS_WARR14C",
        "PS_WARR15",
        "PS_WARR15B",
        "PS_WARR15C",
        "PS_WARR16",
        "PS_WARR16B",
        "PS_WARR16C",
        "PS_WARR17",
        "PS_WARR18",
        "PS_WARR19",
        "PS_WARR20",
        "PS_WARR21",
        "PS_WARR22",
        "PS_WARR23",
        "PS_WARR24",
        "PS_WARR25",
        "PS_WARR26",
        "PS_WARR27",
        "PS_WARR28",
        "PS_WARR29",
        "PS_WARR30",
        "PS_WARR31",
        "PS_WARR32",
        "PS_WARR33",
        "PS_WARR34",
        "PS_WARR35",
        "PS_WARR36",
        "PS_WARR37",
        "PS_WARR38",
        "PS_WARR39",
        "PS_WARR40",
        "PS_WARR41",
        "PS_WARR42",
        "PS_WARR43",
        "PS_WARR44",
        "PS_WARR45",
        "PS_WARR46",
        "PS_WARR47",
        "PS_WARR48",
        "PS_WARR49",
        "PS_WARR50",
        "PS_WARR51",
        "PS_WARR52",
        "PS_WARR53",
        "PS_WARR54",
        "PS_WARR55",
        "PS_WARR56",
        "PS_WARR57",
        "PS_WARR58",
        "PS_WARR59",
        "PS_WARR60",
        "PS_WARR61",
        "PS_WARR62",
        "PS_WARR63",
        "PS_WARR64",
        "PS_WARR65",
        "PS_WARR66",
        "PS_WARR67",
        "PS_WARR68",
        "PS_WARR69",
        "PS_WARR69B",
        "PS_WARR70",
        "PS_WARR71",
        "PS_WARR72",
        "PS_WARR73",
        "PS_WARR74",
        "PS_WARR75",
        "PS_WARR76",
        "PS_WARR77",
        "PS_WARR78",
        "PS_WARR79",
        "PS_WARR80",
        "PS_WARR81",
        "PS_WARR82",
        "PS_WARR83",
        "PS_WARR84",
        "PS_WARR85",
        "PS_WARR86",
        "PS_WARR87",
        "PS_WARR88",
        "PS_WARR89",
        "PS_WARR90",
        "PS_WARR91",
        "PS_WARR92",
        "PS_WARR93",
        "PS_WARR94",
        "PS_WARR95",
        "PS_WARR95B",
        "PS_WARR95C",
        "PS_WARR95D",
        "PS_WARR95E",
        "PS_WARR95F",
        "PS_WARR96B",
        "PS_WARR97",
        "PS_WARR98",
        "PS_WARR99",
        "PS_WARR100",
        "PS_WARR101",
        "PS_WARR102",
        "PS_NAR1",
        "PS_NAR2",
        "PS_NAR3",
        "PS_NAR4",
        "PS_NAR5",
        "PS_NAR6",
        "PS_NAR7",
        "PS_NAR8",
        "PS_NAR9",
        "PS_DIABLVLINT",
        "USFX_CLEAVER",
        "USFX_GARBUD1",
        "USFX_GARBUD2",
        "USFX_GARBUD3",
        "USFX_GARBUD4",
        "USFX_IZUAL1",
        "USFX_LACH1",
        "USFX_LACH2",
        "USFX_LACH3",
        "USFX_LAZ1",
        "USFX_LAZ2",
        "USFX_SKING1",
        "USFX_SNOT1",
        "USFX_SNOT2",
        "USFX_SNOT3",
        "USFX_WARLRD1",
        "USFX_WLOCK1",
        "USFX_ZHAR1",
        "USFX_ZHAR2",
        "USFX_DIABLOD",
    ]

    missile_resist = dict(
        MISR_NONE=0,
        MISR_FIRE=1,
        MISR_LIGHTNING=2,
        MISR_MAGIC=3,
        MISR_ACID=4,
    )

    missile_filenum = [
        "MFILE_ARROWS",
        "MFILE_FIREBA",
        "MFILE_GUARD",
        "MFILE_LGHNING",
        "MFILE_FIREWAL",
        "MFILE_MAGBLOS",
        "MFILE_PORTAL",
        "MFILE_BLUEXFR",
        "MFILE_BLUEXBK",
        "MFILE_MANASHLD",
        "MFILE_BLOOD",
        "MFILE_BONE",
        "MFILE_METLHIT",
        "MFILE_FARROW",
        "MFILE_DOOM",
        "MFILE_0F",
        "MFILE_BLODBUR",
        "MFILE_NEWEXP",
        "MFILE_SHATTER1",
        "MFILE_BIGEXP",
        "MFILE_INFERNO",
        "MFILE_THINLGHT",
        "MFILE_FLARE",
        "MFILE_FLAREEXP",
        "MFILE_MAGBALL",
        "MFILE_KRULL",
        "MFILE_MINILTNG",
        "MFILE_HOLY",
        "MFILE_HOLYEXPL",
        "MFILE_LARROW",
        "MFILE_FIRARWEX",
        "MFILE_ACIDBF",
        "MFILE_ACIDSPLA",
        "MFILE_ACIDPUD",
        "MFILE_ETHRSHLD",
        "MFILE_FIRERUN",
        "MFILE_RESSUR1",
        "MFILE_SKLBALL",
        "MFILE_RPORTAL",
        "MFILE_FIREPLAR",
        "MFILE_SCUBMISB",
        "MFILE_SCBSEXPB",
        "MFILE_SCUBMISC",
        "MFILE_SCBSEXPC",
        "MFILE_SCUBMISD",
        "MFILE_SCBSEXPD",
        "MFILE_NULL",
    ]

    missile_id = {'MIS_ARROW': 0x0, 'MIS_FIREBOLT': 0x1, 'MIS_GUARDIAN': 0x2, 'MIS_RNDTELEPORT': 0x3,
                  'MIS_LIGHTBALL': 0x4, 'MIS_FIREWALL': 0x5, 'MIS_FIREBALL': 0x6, 'MIS_LIGHTCTRL': 0x7,
                  'MIS_LIGHTNING': 0x8, 'MIS_MISEXP': 0x9, 'MIS_TOWN': 0xA, 'MIS_FLASH': 0xB, 'MIS_FLASH2': 0xC,
                  'MIS_MANASHIELD': 0xD, 'MIS_FIREMOVE': 0xE, 'MIS_CHAIN': 0xF, 'MIS_SENTINAL': 0x10,
                  'MIS_BLODSTAR': 0x11, 'MIS_BONE': 0x12, 'MIS_METLHIT': 0x13, 'MIS_RHINO': 0x14, 'MIS_MAGMABALL': 0x15,
                  'MIS_LIGHTCTRL2': 0x16, 'MIS_LIGHTNING2': 0x17, 'MIS_FLARE': 0x18, 'MIS_MISEXP2': 0x19,
                  'MIS_TELEPORT': 0x1A, 'MIS_FARROW': 0x1B, 'MIS_DOOMSERP': 0x1C, 'MIS_FIREWALLA': 0x1D,
                  'MIS_STONE': 0x1E, 'MIS_NULL_1F': 0x1F, 'MIS_INVISIBL': 0x20, 'MIS_GOLEM': 0x21,
                  'MIS_ETHEREALIZE': 0x22, 'MIS_BLODBUR': 0x23, 'MIS_BOOM': 0x24, 'MIS_HEAL': 0x25,
                  'MIS_FIREWALLC': 0x26, 'MIS_INFRA': 0x27, 'MIS_IDENTIFY': 0x28, 'MIS_WAVE': 0x29, 'MIS_NOVA': 0x2A,
                  'MIS_BLODBOIL': 0x2B, 'MIS_APOCA': 0x2C, 'MIS_REPAIR': 0x2D, 'MIS_RECHARGE': 0x2E, 'MIS_DISARM': 0x2F,
                  'MIS_FLAME': 0x30, 'MIS_FLAMEC': 0x31, 'MIS_FIREMAN': 0x32, 'MIS_KRULL': 0x33, 'MIS_CBOLT': 0x34,
                  'MIS_HBOLT': 0x35, 'MIS_RESURRECT': 0x36, 'MIS_TELEKINESIS': 0x37, 'MIS_LARROW': 0x38,
                  'MIS_ACID': 0x39, 'MIS_MISEXP3': 0x3A, 'MIS_ACIDPUD': 0x3B, 'MIS_HEALOTHER': 0x3C,
                  'MIS_ELEMENT': 0x3D, 'MIS_RESURRECTBEAM': 0x3E, 'MIS_BONESPIRIT': 0x3F, 'MIS_WEAPEXP': 0x40,
                  'MIS_RPORTAL': 0x41, 'MIS_BOOM2': 0x42, 'MIS_DIABAPOCA': 0x43}

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
            convert_exclusive_flag(conv_dict["mName"], missile_id),
            conv_dict["mAddProc"],
            conv_dict["mProc"],
            "true" if conv_dict["mDraw"] != 0 else "false",
            conv_dict["mType"],
            convert_exclusive_flag(conv_dict["mResist"], missile_resist),
            get_item_from_array(twos_complement(conv_dict["mFileNum"], 8), missile_filenum, "MFILE_NONE"),
            sfx_id_list[twos_complement(conv_dict["mlSFX"], 32)] if twos_complement(conv_dict["mlSFX"], 32) > 0 else -1,
            sfx_id_list[twos_complement(conv_dict["miSFX"], 32)] if twos_complement(conv_dict["miSFX"], 32) > 0 else -1,
        ]

        conv_table.append(conv_row)
    # actual_label_order = [
    #     "iRnd",
    #     "iClass",
    #     "iLoc",
    #     "iCurs",
    #     "itype",
    #     "iItemId",
    #     "iName",
    #     "isName",
    #     "iMinMLvl",
    #     "iDurability",
    #     "iMinDam",
    #     "iMaxDam",
    #     "iMinAC",
    #     "iMaxAC",
    #     "iMinStr",
    #     "iMinMag",
    #     "iMinDex",
    #     "iFlags",
    #     "iMiscId",
    #     "iSpell",
    #     "iUsable",
    #     "iValue",
    # ]

    # print("; ".join(actual_label_order))
    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_item_panel_data(m):
    mem_offset = 0x402200  # always this for Diablo 1.07
    mem_start = 0x000801B0  # start of look up, in binary
    block_size = 5  # length of structure in bytes (includes any padding)
    block_count = 34  # number of items in structure array

    # items to be looked up, label followed by size, in bytes
    package = [("ItemIdx", 1),
               ("PanelText", 4),
               ]

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single item in structure
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length

        # place memory info in correct order for row (for what is included in cpp files)
        conv_row = [
            conv_dict["ItemIdx"],
            f'"{get_string(m, conv_dict["PanelText"] - mem_offset)}"',
        ]

        conv_table.append(conv_row)

    # print info to console
    # adding ";" for formatting in .csv to fixed width formatter: https://www.convertcsv.com/csv-to-flat-file.htm

    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_monster_avail(m):
    mem_offset = 0x402200  # always this for Diablo 1.07
    mem_start = 0x0009A4F0  # start of look up, in binary
    block_size = 1  # length of structure in bytes (includes any padding)
    block_count = 0x70  # number of items in structure array

    # items to be looked up, label followed by size, in bytes
    package = [("availFlag", 1),
               ]

    avail_list = [
        "MAT_NEVER",
        "MAT_ALWAYS",
        "MAT_RETAIL",
    ]

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single item in structure
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length

        # place memory info in correct order for row (for what is included in cpp files)

        conv_table.append(avail_list[conv_dict["availFlag"]])

    # ', '.join(conv_table)
    # print(conv_table)

    for item in conv_table:
        print(f"{item},")

    # print info to console
    # adding ";" for formatting in .csv to fixed width formatter: https://www.convertcsv.com/csv-to-flat-file.htm

    # for row in conv_table:
    #     temp_string = "{"
    #     temp_row = [str(int) for int in row]
    #     x = ",; ".join(temp_row)
    #     temp_string += x
    #     temp_string += "},"
    #     print(temp_string)


def convert_anim_data(m):
    mem_offset = 0x402200  # always this for Diablo 1.07
    mem_start = 0x00079154  # start of look up, in binary
    block_size = 1  # length of structure in bytes (includes any padding)
    block_count = 256  # number of items in structure array

    # items to be looked up, label followed by size, in bytes
    package = [("AnimLength", 1),
               ]

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single item in structure
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length

        # place memory info in correct order for row (for what is included in cpp files)
        conv_table.append(conv_dict["AnimLength"])

        # conv_table.append(conv_row)

    # print info to console
    # adding ";" for formatting in .csv to fixed width formatter: https://www.convertcsv.com/csv-to-flat-file.htm

    print(", ".join(str(int) for int in conv_table))

    # for row in conv_table:
    #     temp_string = ""
    #     temp_row = [str(int) for int in row]
    #     x = ",; ".join(temp_row)
    #     temp_string += x
    #     # temp_string += "},"
    #     print(temp_string)


def convert_template_data(m):
    mem_offset = 0x402200  # always this for Diablo 1.07
    mem_start = 0x000801B0  # start of look up, in binary
    block_size = 5  # length of structure in bytes (includes any padding)
    block_count = 35  # number of items in structure array

    # items to be looked up, label followed by size, in bytes
    package = [("ItemIdx", 1),
               ("PanelText", 4),
               ]

    conv_dict = {}
    conv_table = []
    for mem_address in range(mem_start, mem_start + block_size * block_count, block_size):
        conv_dict.clear()
        cur_address = mem_address
        # pull memory info for single item in structure
        for name, length in package:
            conv_dict[name] = get_value(m, cur_address, length)
            cur_address = cur_address + length

        # place memory info in correct order for row (for what is included in cpp files)
        conv_row = [
            conv_dict["ItemIdx"],
            f'"{get_string(m, conv_dict["PanelText"] - mem_offset)}"',
        ]

        conv_table.append(conv_row)

    # print info to console
    # adding ";" for formatting in .csv to fixed width formatter: https://www.convertcsv.com/csv-to-flat-file.htm

    for row in conv_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ",; ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def convert_monster_resists():
    string_to_convert = r"""/* MT_MAGISTR */ { P_("monster", "Magistrate"),              "Mage\\Mage",       "Monsters\\Mage\\Mage%c%i.WAV",      "Monsters\\Mage\\Cnselg.TRN",        128,   2000, true,        false,       true,      { 12,  1, 20,  8, 28, 20 }, { 1, 1, 1, 1, 1, 1 },        26,       28,     27,     85,     85, MonsterAI::Counselor,                                                        MFLAG_CAN_OPEN_DOOR,    1,  100,      8,         10,         24,     0,       0,           0,           0,           0, MonsterClass::Demon,    RESIST_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40  , IMMUNE_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         4478 },
/* MT_CABALIST*/ { P_("monster", "Cabalist"),                "Mage\\Mage",       "Monsters\\Mage\\Mage%c%i.WAV",      "Monsters\\Mage\\Cnselgd.TRN",       128,   2000, true,        false,       true,      { 12,  1, 20,  8, 28, 20 }, { 1, 1, 1, 1, 1, 1 },        28,       30,     29,    120,    120, MonsterAI::Counselor,                                                        MFLAG_CAN_OPEN_DOOR,    2,  110,      8,         14,         30,     0,       0,           0,           0,           0, MonsterClass::Demon,    RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40  , IMMUNE_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         4929 },
/* MT_ADVOCATE*/ { P_("monster", "Advocate"),                "Mage\\Mage",       "Monsters\\Mage\\Mage%c%i.WAV",      "Monsters\\Mage\\Cnselbk.TRN",       128,   2000, true,        false,       true,      { 12,  1, 20,  8, 28, 20 }, { 1, 1, 1, 1, 1, 1 },        30,       30,     30,    145,    145, MonsterAI::Counselor,                                                        MFLAG_CAN_OPEN_DOOR,    3,  120,      8,         15,         25,     0,       0,           0,           0,           0, MonsterClass::Demon,    IMMUNE_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40  , IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         4968 },
/* MT_GOLEM   */ { P_("monster", "Golem"),                   "Golem\\Golem",     "Monsters\\Golem\\Golm%c%i.WAV",     nullptr,                              96,    386, true,        false,       false,     {  0, 16, 12,  0, 12, 20 }, { 1, 1, 1, 1, 1, 1 },         0,        0,     12,      1,      1, MonsterAI::Golem,                                                            MFLAG_CAN_OPEN_DOOR,    0,    0,      7,          1,          1,     0,       0,           0,           0,           1, MonsterClass::Demon,    0                                                               , 0                                                                 ,  0,                   0,            0 },
/* MT_DIABLO  */ { P_("monster", "The Dark Lord"),           "Diablo\\Diablo",   "Monsters\\Diablo\\Diablo%c%i.WAV",  nullptr,                             160,   2000, true,        true,        false,     { 16,  6, 16,  6, 16, 16 }, { 1, 1, 1, 1, 1, 1 },        50,       50,     45,   3333,   3333, MonsterAI::Diablo,                          MFLAG_KNOCKBACK | MFLAG_SEARCH | MFLAG_CAN_OPEN_DOOR,    3,  220,      4,         30,         60,     0,      11,           0,           0,          90, MonsterClass::Demon,    IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40  , IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,        31666 },
/* MT_DARKMAGE*/ { P_("monster", "The Arch-Litch Malignus"), "DarkMage\\Dmage",  "Monsters\\DarkMage\\Dmag%c%i.WAV",  nullptr,                             128,   1060, true,        false,       false,     {  6,  1, 21,  6, 23, 18 }, { 1, 1, 1, 1, 1, 1 },        40,       41,     30,    160,    160, MonsterAI::Counselor,                                                        MFLAG_CAN_OPEN_DOOR,    3,  120,      8,         20,         40,     0,       0,           0,           0,          70, MonsterClass::Demon,    RESIST_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40  , IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         4968 },
/* MT_HELLBOAR*/ { P_("monster", "Hellboar"),                "Fork\\Fork",       "Monsters\\newsfx\\HBoar%c%i.WAV",   nullptr,                             188,    800, false,       false,       false,     { 10, 10, 15,  6, 16,  0 }, { 2, 1, 1, 1, 1, 1 },        32,       35,     23,     80,    100, MonsterAI::SkeletonSword,                   MFLAG_KNOCKBACK | MFLAG_SEARCH                      ,    2,   70,      7,         16,         24,     0,       0,           0,           0,          60, MonsterClass::Demon,    0                                                               ,                RESIST_FIRE | RESIST_LIGHTNING                     ,  3,                   0,          750 },
/* MT_STINGER */ { P_("monster", "Stinger"),                 "Scorp\\Scorp",     "Monsters\\newsfx\\Stingr%c%i.WAV",  nullptr,                              64,    305, false,       false,       false,     { 10, 10, 12,  6, 15,  0 }, { 2, 1, 1, 1, 1, 1 },        32,       35,     22,     30,     40, MonsterAI::SkeletonSword,    0                                                                  ,    3,   85,      8,          1,         20,     0,       0,           0,           0,          50, MonsterClass::Animal,   0                                                               ,                              RESIST_LIGHTNING                     ,  1,                   0,          500 },
/* MT_PSYCHORB*/ { P_("monster", "Psychorb"),                "Eye\\Eye",         "Monsters\\newsfx\\psyco%c%i.WAV",   nullptr,                             156,    800, false,       false,       false,     { 12, 13, 13,  7, 21,  0 }, { 2, 1, 1, 1, 1, 1 },        32,       35,     22,     20,     30, MonsterAI::Psychorb,         0                                                                  ,    3,   80,      8,         10,         10,     0,       0,           0,           0,          40, MonsterClass::Animal,   0                                                               ,                RESIST_FIRE                                        ,  6,                   0,          450 },
/* MT_ARACHNON*/ { P_("monster", "Arachnon"),                "Spider\\Spider",   "Monsters\\newsfx\\SLord%c%i.WAV",   nullptr,                             148,    800, false,       false,       false,     { 12, 10, 15,  6, 20,  0 }, { 2, 1, 1, 1, 1, 1 },        32,       35,     22,     60,     80, MonsterAI::SkeletonSword,                                     MFLAG_SEARCH                      ,    3,   50,      8,          5,         15,     0,       0,           0,           0,          50, MonsterClass::Animal,   0                                                               ,                              RESIST_LIGHTNING                     ,  7,                   0,          500 },
/* MT_FELLTWIN*/ { P_("monster", "Felltwin"),                "TSneak\\TSneak",   "Monsters\\newsfx\\FTwin%c%i.WAV",   nullptr,                             128,    800, false,       false,       false,     { 13, 13, 15, 11, 16,  0 }, { 2, 1, 1, 1, 1, 1 },        32,       35,     22,     50,     70, MonsterAI::SkeletonSword,                                     MFLAG_SEARCH | MFLAG_CAN_OPEN_DOOR,    3,   70,      8,         10,         18,     0,       0,           0,           0,          50, MonsterClass::Demon,                                                    IMMUNE_NULL_40  ,                RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40    ,  3,                   0,          600 },
/* MT_VENMTAIL*/ { P_("monster", "Venomtail"),               "WScorp\\WScorp",   "Monsters\\newsfx\\Stingr%c%i.WAV",  nullptr,                              86,    305, false,       false,       false,     { 10, 10, 12,  6, 15,  0 }, { 2, 1, 1, 1, 1, 1 },        36,       39,     24,     40,     50, MonsterAI::SkeletonSword,    0                                                                  ,    3,   85,      8,          1,         30,     0,       0,           0,           0,          60, MonsterClass::Animal,                                RESIST_LIGHTNING                   ,                              IMMUNE_LIGHTNING                     ,  1,                   0,         1000 },
/* MT_NECRMORB*/ { P_("monster", "Necromorb"),               "Eye2\\Eye2",       "Monsters\\newsfx\\Psyco%c%i.WAV",   nullptr,                             140,    800, false,       false,       false,     { 12, 13, 13,  7, 21,  0 }, { 2, 1, 1, 1, 1, 1 },        36,       39,     24,     30,     40, MonsterAI::Necromorb,        0                                                                  ,    3,   80,      8,         20,         20,     0,       0,           0,           0,          50, MonsterClass::Animal,                  RESIST_FIRE                                      ,                IMMUNE_FIRE | RESIST_LIGHTNING                     ,  6,                   0,         1100 },
/* MT_SPIDLORD*/ { P_("monster", "Spider Lord"),             "bSpidr\\bSpidr",   "Monsters\\newsfx\\SLord%c%i.WAV",   nullptr,                             148,    800, true,        true,        false,     { 12, 10, 15,  6, 20, 10 }, { 2, 1, 1, 1, 1, 1 },        36,       39,     24,     80,    100, MonsterAI::AcidSpitter,                                       MFLAG_SEARCH                      ,    3,   60,      8,          8,         20,    75,       8,          10,          10,          60, MonsterClass::Animal,                                RESIST_LIGHTNING                   ,                RESIST_FIRE | IMMUNE_LIGHTNING                     ,  7,                   0,         1250 },
/* MT_LASHWORM*/ { P_("monster", "Lashworm"),                "Clasp\\Clasp",     "Monsters\\newsfx\\Lworm%c%i.WAV",   nullptr,                             176,    800, false,       false,       false,     { 10, 12, 15,  6, 16,  0 }, { 1, 1, 1, 1, 1, 1 },        36,       39,     20,     30,     30, MonsterAI::SkeletonSword,    0                                                                  ,    3,   90,      8,         12,         20,     0,       0,           0,           0,          50, MonsterClass::Animal,   0                                                               ,                RESIST_FIRE                                        ,  3,                   0,          600 },
/* MT_TORCHANT*/ { P_("monster", "Torchant"),                "AntWorm\\Worm",    "Monsters\\newsfx\\TchAnt%c%i.WAV",  nullptr,                             192,    800, false,       false,       false,     { 14, 12, 12,  6, 20,  0 }, { 2, 1, 1, 1, 1, 1 },        36,       39,     22,     60,     80, MonsterAI::HellBat,          0                                                                  ,    3,   75,      8,         20,         30,     0,       0,           0,           0,          70, MonsterClass::Animal,                  IMMUNE_FIRE                                      , RESIST_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING                     ,  7,                   0,         1250 },
/* MT_HORKDMN */ { P_("monster", "Hork Demon"),              "HorkD\\HorkD",     "Monsters\\newsfx\\HDemon%c%i.WAV",  nullptr,                             138,    800, true,        true,        false,     { 15,  8, 16,  6, 16,  9 }, { 2, 1, 1, 1, 1, 2 },        36,       37,     27,    120,    160, MonsterAI::SkeletonSword,    0                                                                  ,    3,   60,      8,         20,         35,    80,       8,           0,           0,          80, MonsterClass::Demon,                                 RESIST_LIGHTNING                   , RESIST_MAGIC |               IMMUNE_LIGHTNING                     ,  7,                   0,         2000 },
/* MT_DEFILER */ { P_("monster", "Hell Bug"),                "Hellbug\\Hellbg",  "Monsters\\newsfx\\Defile%c%i.WAV",  nullptr,                             198,    800, true,        true,        false,     {  8,  8, 14,  6, 14, 12 }, { 1, 1, 1, 1, 1, 1 },        38,       39,     30,    240,    240, MonsterAI::SkeletonSword,                                     MFLAG_SEARCH                      ,    3,  110,      8,         20,         30,    90,       8,          50,          60,          80, MonsterClass::Demon,    RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING                   , RESIST_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING                     ,  7,                   0,         5000 },
/* MT_GRAVEDIG*/ { P_("monster", "Gravedigger"),             "Gravdg\\Gravdg",   "Monsters\\newsfx\\GDiggr%c%i.WAV",  nullptr,                             124,    800, true,        true,        false,     { 24, 24, 12,  6, 16, 16 }, { 2, 1, 1, 1, 1, 1 },        40,       41,     26,    120,    240, MonsterAI::Scavenger,                                                        MFLAG_CAN_OPEN_DOOR,    3,   80,      6,          2,         12,     0,       0,           0,           0,          20, MonsterClass::Undead,                                IMMUNE_LIGHTNING  | IMMUNE_NULL_40 , RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  3,                   0,         2000 },
/* MT_TOMBRAT */ { P_("monster", "Tomb Rat"),                "Rat\\Rat",         "Monsters\\newsfx\\TmbRat%c%i.WAV",  nullptr,                             104,    550, false,       false,       false,     { 11,  8, 12,  6, 20,  0 }, { 2, 1, 1, 1, 1, 1 },        40,       43,     24,     80,    120, MonsterAI::SkeletonSword,    0                                                                  ,    3,  120,      8,         12,         25,     0,       0,           0,           0,          30, MonsterClass::Animal,   0                                                               ,                RESIST_FIRE | RESIST_LIGHTNING                     ,  3,                   0,         1800 },
/* MT_FIREBAT */ { P_("monster", "Firebat"),                 "Hellbat\\Helbat",  "Monsters\\newsfx\\HelBat%c%i.WAV",  nullptr,                              96,    550, false,       false,       false,     { 18, 16, 14,  6, 18, 11 }, { 2, 1, 1, 1, 1, 1 },        40,       43,     24,     60,     80, MonsterAI::FireBat,          0                                                                  ,    3,  100,      8,         15,         20,     0,       0,           0,           0,          70, MonsterClass::Animal,                  IMMUNE_FIRE                                      , RESIST_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING                     ,  7,                   0,         2400 },
/* MT_SKLWING */ { P_("monster", "Skullwing"),               "Demskel\\Demskl",  "Monsters\\newsfx\\SWing%c%i.WAV",   "Monsters\\Thin\\Thinv3.TRN",        128,   1740, true,        false,       false,     { 10,  8, 20,  6, 24, 16 }, { 3, 1, 1, 1, 1, 1 },        40,       43,     27,     70,     70, MonsterAI::SkeletonSword,    0                                                                  ,    0,   75,      7,         15,         20,    75,       9,          15,          20,          80, MonsterClass::Undead,                  RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40  ,                RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         3000 },
/* MT_LICH    */ { P_("monster", "Lich"),                    "Lich\\Lich",       "Monsters\\newsfx\\Lich%c%i.WAV",    nullptr,                              96,    800, false,       true,        false,     { 12, 10, 10,  7, 21,  0 }, { 2, 1, 1, 1, 2, 1 },        40,       43,     25,     80,    100, MonsterAI::Lich,             0                                                                  ,    3,  100,      8,         15,         20,     0,       0,           0,           0,          60, MonsterClass::Undead,                                RESIST_LIGHTNING | IMMUNE_NULL_40  , RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  3,                   0,         3000 },
/* MT_CRYPTDMN*/ { P_("monster", "Crypt Demon"),             "Bubba\\Bubba",     "Monsters\\newsfx\\Crypt%c%i.WAV",   nullptr,                             154,    800, false,       true,        false,     {  8, 18, 12,  8, 21,  0 }, { 3, 1, 1, 1, 1, 1 },        42,       45,     28,    200,    240, MonsterAI::SkeletonSword,    0                                                                  ,    3,  100,      8,         20,         40,     0,       0,           0,           0,          85, MonsterClass::Demon,    IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING                   , IMMUNE_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING                     ,  3,                   0,         3200 },
/* MT_HELLBAT */ { P_("monster", "Hellbat"),                 "Hellbat2\\bhelbt", "Monsters\\newsfx\\HelBat%c%i.WAV",  nullptr,                              96,    550, true,        false,       false,     { 18, 16, 14,  6, 18, 11 }, { 2, 1, 1, 1, 1, 1 },        44,       47,     29,    100,    140, MonsterAI::HellBat,          0                                                                  ,    3,  110,      8,         30,         30,     0,       0,           0,           0,          80, MonsterClass::Demon,    RESIST_MAGIC | IMMUNE_FIRE  | RESIST_LIGHTNING                  , RESIST_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING                     ,  7,                   0,         3600 },
/* MT_BONEDEMN*/ { P_("monster", "Bone Demon"),              "Demskel\\Demskl",  "Monsters\\newsfx\\SWing%c%i.WAV",   "Monsters\\Thin\\Thinv3.TRN",        128,   1740, true,        true,        false,     { 10,  8, 20,  6, 24, 16 }, { 3, 1, 1, 1, 1, 1 },        44,       47,     30,    240,    280, MonsterAI::BoneDemon,        0                                                                  ,    0,  100,      8,         40,         50,   160,      12,          50,          50,          50, MonsterClass::Undead,                  IMMUNE_FIRE  | IMMUNE_LIGHTNING | IMMUNE_NULL_40 ,                IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,         5000 },
/* MT_ARCHLICH*/ { P_("monster", "Arch Lich"),               "Lich2\\Lich2",     "Monsters\\newsfx\\Lich%c%i.WAV",    nullptr,                             136,    800, false,       true,        false,     { 12, 10, 10,  7, 21,  0 }, { 2, 1, 1, 1, 2, 1 },        44,       47,     30,    180,    200, MonsterAI::ArchLich,         0                                                                  ,    3,  120,      8,         30,         30,     0,       0,           0,           0,          75, MonsterClass::Undead,   RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING  | IMMUNE_NULL_40 , IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  3,                   0,         4000 },
/* MT_BICLOPS */ { P_("monster", "Biclops"),                 "Byclps\\Byclps",   "Monsters\\newsfx\\Biclop%c%i.WAV",  nullptr,                             180,    800, false,       false,       false,     { 10, 11, 16,  6, 16,  0 }, { 2, 1, 1, 1, 2, 1 },        44,       47,     30,    200,    240, MonsterAI::SkeletonSword,                   MFLAG_KNOCKBACK |                MFLAG_CAN_OPEN_DOOR,    3,   90,      8,         40,         50,     0,       0,           0,           0,          80, MonsterClass::Demon,                                 RESIST_LIGHTNING                   ,                RESIST_FIRE | RESIST_LIGHTNING                     ,  3,                   0,         4000 },
/* MT_REAPER  */ { P_("monster", "Reaper"),                  "Reaper\\Reap",     "Monsters\\newsfx\\Reaper%c%i.WAV",  nullptr,                             180,    800, false,       false,       false,     { 12, 10, 14,  6, 16,  0 }, { 2, 1, 1, 1, 1, 1 },        44,       47,     30,    260,    300, MonsterAI::SkeletonSword,    0                                                                  ,    3,  120,      8,         30,         35,     0,       0,           0,           0,          90, MonsterClass::Demon,    IMMUNE_MAGIC | IMMUNE_FIRE  | RESIST_LIGHTNING                  , IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING                     ,  3,                   0,         6000 },
// TRANSLATORS: Monster Block end
/* MT_NAKRUL  */ { P_("monster", "Na-Krul"),                 "Nkr\\Nkr",         "Monsters\\newsfx\\Nakrul%c%i.WAV",  nullptr,                             226,   1200, true,        true,        false,     {  2,  6, 16,  3, 16, 16 }, { 0, 0, 0, 0, 0, 0 },        60,       60,     40,   1332,   1332, MonsterAI::SkeletonSword,                   MFLAG_KNOCKBACK | MFLAG_SEARCH | MFLAG_CAN_OPEN_DOOR,    3,  150,      7,         40,         50,   150,      10,          40,          50,         125, MonsterClass::Demon,    IMMUNE_MAGIC | IMMUNE_FIRE  | RESIST_LIGHTNING | IMMUNE_NULL_40 , IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40    ,  7,                   0,        13333 },"""

    unique_string_to_convert =r"""	{  MT_NGOATMC,       P_("monster", "Gharbad the Weak"),                 "BSDB",                 4,       120, MonsterAI::Garbud,            3,           8,          16,                               IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_GARBUD1   },
	{  MT_SKING,         P_("monster", "Skeleton King"),                    "GENRL",                0,       240, MonsterAI::SkeletonKing,      3,           6,          16,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Independent,             0,                0, TEXT_NONE      },
	{  MT_COUNSLR,       P_("monster", "Zhar the Mad"),                     "GENERAL",              8,       360, MonsterAI::Zhar,              3,          16,          40,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_ZHAR1     },
	{  MT_BFALLSP,       P_("monster", "Snotspill"),                        "BNG",                  4,       220, MonsterAI::Snotspill,         3,          10,          18,                               RESIST_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_BANNER10  },
	{  MT_ADVOCATE,      P_("monster", "Arch-Bishop Lazarus"),              "GENERAL",              0,       600, MonsterAI::Lazarus,           3,          30,          50,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_VILE13    },
	{  MT_HLSPWN,        P_("monster", "Red Vex"),                          "REDV",                 0,       400, MonsterAI::LazarusHelpers,    3,          30,          50,  IMMUNE_MAGIC | RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_VILE13    },
	{  MT_HLSPWN,        P_("monster", "Black Jade"),                       "BLKJD",                0,       400, MonsterAI::LazarusHelpers,    3,          30,          50,  IMMUNE_MAGIC |               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_VILE13    },
	{  MT_RBLACK,        P_("monster", "Lachdanan"),                        "BHKA",                14,       500, MonsterAI::Lachdanan,         3,           0,           0,  0                                                             , UniqueMonsterPack::None,                    0,                0, TEXT_VEIL9     },
	{  MT_BTBLACK,       P_("monster", "Warlord of Blood"),                 "GENERAL",             13,       850, MonsterAI::Warlord,           3,          35,          50,  IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_WARLRD9   },
	{  MT_CLEAVER,       P_("monster", "The Butcher"),                      "GENRL",                0,       220, MonsterAI::Butcher,           3,           6,          12,                 RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_HORKDMN,       P_("monster", "Hork Demon"),                       "GENRL",               19,       300, MonsterAI::HorkDemon,         3,          20,          35,                               RESIST_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_DEFILER,       P_("monster", "The Defiler"),                      "GENRL",               20,       480, MonsterAI::SkeletonSword,     3,          30,          40,  RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_NAKRUL,        P_("monster", "Na-Krul"),                          "GENRL",                0,      1332, MonsterAI::SkeletonSword,     3,          40,          50,  IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_TSKELAX,       P_("monster", "Bonehead Keenaxe"),                 "BHKA",                 2,        91, MonsterAI::SkeletonSword,     2,           4,          10,  IMMUNE_MAGIC |                                  IMMUNE_NULL_40, UniqueMonsterPack::Leashed,               100,                0, TEXT_NONE      },
	{  MT_RFALLSD,       P_("monster", "Bladeskin the Slasher"),            "BSTS",                 2,        51, MonsterAI::Fallen,            0,           6,          18,                 RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,               45, TEXT_NONE      },
	{  MT_NZOMBIE,       P_("monster", "Soulpus"),                          "GENERAL",              2,       133, MonsterAI::Zombie,            0,           4,           8,                 RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_RFALLSP,       P_("monster", "Pukerat the Unclean"),              "PTU",                  2,        77, MonsterAI::Fallen,            3,           1,           5,                 RESIST_FIRE                                    , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_WSKELAX,       P_("monster", "Boneripper"),                       "BR",                   2,        54, MonsterAI::Bat,               0,           6,          15,  IMMUNE_MAGIC | IMMUNE_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NZOMBIE,       P_("monster", "Rotfeast the Hungry"),              "ETH",                  2,        85, MonsterAI::SkeletonSword,     3,           4,          12,  IMMUNE_MAGIC |                                  IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_DFALLSD,       P_("monster", "Gutshank the Quick"),               "GTQ",                  3,        66, MonsterAI::Bat,               2,           6,          16,                 RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_TSKELSD,       P_("monster", "Brokenhead Bangshield"),            "BHBS",                 3,       108, MonsterAI::SkeletonSword,     3,          12,          20,  IMMUNE_MAGIC |               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_YFALLSP,       P_("monster", "Bongo"),                            "BNG",                  3,       178, MonsterAI::Fallen,            3,           9,          21,  0                                                             , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BZOMBIE,       P_("monster", "Rotcarnage"),                       "RCRN",                 3,       102, MonsterAI::Zombie,            3,           9,          24,  IMMUNE_MAGIC |               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,               45, TEXT_NONE      },
	{  MT_NSCAV,         P_("monster", "Shadowbite"),                       "SHBT",                 2,        60, MonsterAI::SkeletonSword,     3,           3,          20,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_WSKELBW,       P_("monster", "Deadeye"),                          "DE",                   2,        49, MonsterAI::GoatArcher,        0,           6,           9,  IMMUNE_MAGIC | RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_RSKELAX,       P_("monster", "Madeye the Dead"),                  "MTD",                  4,        75, MonsterAI::Bat,               0,           9,          21,  IMMUNE_MAGIC | IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,               30, TEXT_NONE      },
	{  MT_BSCAV,         P_("monster", "El Chupacabras"),                   "GENERAL",              3,       120, MonsterAI::GoatMace,          0,          10,          18,                 RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_TSKELBW,       P_("monster", "Skullfire"),                        "SKFR",                 3,       125, MonsterAI::GoatArcher,        1,           6,          10,                 IMMUNE_FIRE                                    , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_SNEAK,         P_("monster", "Warpskull"),                        "TSPO",                 3,       117, MonsterAI::Sneak,             2,           6,          18,                 RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_GZOMBIE,       P_("monster", "Goretongue"),                       "PMR",                  3,       156, MonsterAI::SkeletonSword,     1,          15,          30,  IMMUNE_MAGIC |                                  IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_WSCAV,         P_("monster", "Pulsecrawler"),                     "BHKA",                 4,       150, MonsterAI::Scavenger,         0,          16,          20,                 IMMUNE_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,               45, TEXT_NONE      },
	{  MT_BLINK,         P_("monster", "Moonbender"),                       "GENERAL",              4,       135, MonsterAI::Bat,               0,           9,          27,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BLINK,         P_("monster", "Wrathraven"),                       "GENERAL",              5,       135, MonsterAI::Bat,               2,           9,          22,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_YSCAV,         P_("monster", "Spineeater"),                       "GENERAL",              4,       180, MonsterAI::Scavenger,         1,          18,          25,                               IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RSKELBW,       P_("monster", "Blackash the Burning"),             "BASHTB",               4,       120, MonsterAI::GoatArcher,        0,           6,          16,  IMMUNE_MAGIC | IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BFALLSD,       P_("monster", "Shadowcrow"),                       "GENERAL",              5,       270, MonsterAI::Sneak,             2,          12,          25,  0                                                             , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_LRDSAYTR,      P_("monster", "Blightstone the Weak"),             "BHKA",                 4,       360, MonsterAI::SkeletonSword,     0,           4,          12,  IMMUNE_MAGIC |               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                70,                0, TEXT_NONE      },
	{  MT_FAT,           P_("monster", "Bilefroth the Pit Master"),         "BFTP",                 6,       210, MonsterAI::Bat,               1,          16,          23,  IMMUNE_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NGOATBW,       P_("monster", "Bloodskin Darkbow"),                "BSDB",                 5,       207, MonsterAI::GoatArcher,        0,           3,          16,                 RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,               55, TEXT_NONE      },
	{  MT_GLOOM,         P_("monster", "Foulwing"),                         "DB",                   5,       246, MonsterAI::Rhino,             3,          12,          28,                 RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_XSKELSD,       P_("monster", "Shadowdrinker"),                    "SHDR",                 5,       300, MonsterAI::Sneak,             1,          18,          26,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,               45, TEXT_NONE      },
	{  MT_UNSEEN,        P_("monster", "Hazeshifter"),                      "BHKA",                 5,       285, MonsterAI::Sneak,             3,          18,          30,                               IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NACID,         P_("monster", "Deathspit"),                        "BFDS",                 6,       303, MonsterAI::AcidUnique,        0,          12,          32,                 RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RGOATMC,       P_("monster", "Bloodgutter"),                      "BGBL",                 6,       315, MonsterAI::Bat,               1,          24,          34,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BGOATMC,       P_("monster", "Deathshade Fleshmaul"),             "DSFM",                 6,       276, MonsterAI::Rhino,             0,          12,          24,  IMMUNE_MAGIC | RESIST_FIRE                                    , UniqueMonsterPack::None,                    0,               65, TEXT_NONE      },
	{  MT_WYRM,          P_("monster", "Warmaggot the Mad"),                "GENERAL",              6,       246, MonsterAI::Bat,               3,          15,          30,                               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_STORM,         P_("monster", "Glasskull the Jagged"),             "BHKA",                 7,       354, MonsterAI::Storm,             0,          18,          30,  IMMUNE_MAGIC | IMMUNE_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RGOATBW,       P_("monster", "Blightfire"),                       "BLF",                  7,       321, MonsterAI::Succubus,          2,          13,          21,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_GARGOYLE,      P_("monster", "Nightwing the Cold"),               "GENERAL",              7,       342, MonsterAI::Bat,               1,          18,          26,  IMMUNE_MAGIC |               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_GGOATBW,       P_("monster", "Gorestone"),                        "GENERAL",              7,       303, MonsterAI::GoatArcher,        1,          15,          28,                               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                70,                0, TEXT_NONE      },
	{  MT_BMAGMA,        P_("monster", "Bronzefist Firestone"),             "GENERAL",              8,       360, MonsterAI::MagmaDemon,        0,          30,          36,  IMMUNE_MAGIC | RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_INCIN,         P_("monster", "Wrathfire the Doomed"),             "WFTD",                 8,       270, MonsterAI::SkeletonSword,     2,          20,          30,  IMMUNE_MAGIC | RESIST_FIRE |  RESIST_LIGHTNING                , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NMAGMA,        P_("monster", "Firewound the Grim"),               "BHKA",                 8,       303, MonsterAI::MagmaDemon,        0,          18,          22,  IMMUNE_MAGIC | RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_MUDMAN,        P_("monster", "Baron Sludge"),                     "BSM",                  8,       315, MonsterAI::Sneak,             3,          25,          34,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,               75, TEXT_NONE      },
	{  MT_GGOATMC,       P_("monster", "Blighthorn Steelmace"),             "BHSM",                 7,       250, MonsterAI::Rhino,             0,          20,          28,                               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,               45, TEXT_NONE      },
	{  MT_RACID,         P_("monster", "Chaoshowler"),                      "GENERAL",              8,       240, MonsterAI::AcidUnique,        0,          12,          20,  0                                                             , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_REDDTH,        P_("monster", "Doomgrin the Rotting"),             "GENERAL",              8,       405, MonsterAI::Storm,             3,          25,          50,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_FLAMLRD,       P_("monster", "Madburner"),                        "GENERAL",              9,       270, MonsterAI::Storm,             0,          20,          40,  IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_LTCHDMN,       P_("monster", "Bonesaw the Litch"),                "GENERAL",              9,       495, MonsterAI::Storm,             2,          30,          55,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_MUDRUN,        P_("monster", "Breakspine"),                       "GENERAL",              9,       351, MonsterAI::Rhino,             0,          25,          34,                 RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_REDDTH,        P_("monster", "Devilskull Sharpbone"),             "GENERAL",              9,       444, MonsterAI::Storm,             1,          25,          40,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_STORM,         P_("monster", "Brokenstorm"),                      "GENERAL",              9,       411, MonsterAI::Storm,             2,          25,          36,                               IMMUNE_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RSTORM,        P_("monster", "Stormbane"),                        "GENERAL",              9,       555, MonsterAI::Storm,             3,          30,          30,                               IMMUNE_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_TOAD,          P_("monster", "Oozedrool"),                        "GENERAL",              9,       483, MonsterAI::Overlord,          3,          25,          30,                               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BLOODCLW,      P_("monster", "Goldblight of the Flame"),          "GENERAL",             10,       405, MonsterAI::Gargoyle,          0,          15,          35,  IMMUNE_MAGIC | IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,               80, TEXT_NONE      },
	{  MT_OBLORD,        P_("monster", "Blackstorm"),                       "GENERAL",             10,       525, MonsterAI::Rhino,             3,          20,          40,  IMMUNE_MAGIC |               IMMUNE_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,               90, TEXT_NONE      },
	{  MT_RACID,         P_("monster", "Plaguewrath"),                      "GENERAL",             10,       450, MonsterAI::AcidUnique,        2,          20,          30,  IMMUNE_MAGIC | RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RSTORM,        P_("monster", "The Flayer"),                       "GENERAL",             10,       501, MonsterAI::Storm,             1,          20,          35,  RESIST_MAGIC | RESIST_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_FROSTC,        P_("monster", "Bluehorn"),                         "GENERAL",             11,       477, MonsterAI::Rhino,             1,          25,          30,  IMMUNE_MAGIC | RESIST_FIRE                                    , UniqueMonsterPack::Leashed,                 0,               90, TEXT_NONE      },
	{  MT_HELLBURN,      P_("monster", "Warpfire Hellspawn"),               "GENERAL",             11,       525, MonsterAI::Fireman,           3,          10,          40,  RESIST_MAGIC | IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NSNAKE,        P_("monster", "Fangspeir"),                        "GENERAL",             11,       444, MonsterAI::SkeletonSword,     1,          15,          32,                 IMMUNE_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_UDEDBLRG,      P_("monster", "Festerskull"),                      "GENERAL",             11,       600, MonsterAI::Storm,             2,          15,          30,  IMMUNE_MAGIC |                                  IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_NBLACK,        P_("monster", "Lionskull the Bent"),               "GENERAL",             12,       525, MonsterAI::SkeletonSword,     2,          25,          25,  IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_COUNSLR,       P_("monster", "Blacktongue"),                      "GENERAL",             12,       360, MonsterAI::Counselor,         3,          15,          30,                 RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_DEATHW,        P_("monster", "Viletouch"),                        "GENERAL",             12,       525, MonsterAI::Gargoyle,          3,          20,          40,                               IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RSNAKE,        P_("monster", "Viperflame"),                       "GENERAL",             12,       570, MonsterAI::SkeletonSword,     1,          25,          35,                 IMMUNE_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BSNAKE,        P_("monster", "Fangskin"),                         "BHKA",                14,       681, MonsterAI::SkeletonSword,     2,          15,          50,  IMMUNE_MAGIC |               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_SUCCUBUS,      P_("monster", "Witchfire the Unholy"),             "GENERAL",             12,       444, MonsterAI::Succubus,          3,          10,          20,  IMMUNE_MAGIC | IMMUNE_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_BALROG,        P_("monster", "Blackskull"),                       "BHKA",                13,       750, MonsterAI::SkeletonSword,     3,          25,          40,  IMMUNE_MAGIC |               RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_UNRAV,         P_("monster", "Soulslash"),                        "GENERAL",             12,       450, MonsterAI::SkeletonSword,     0,          25,          25,  IMMUNE_MAGIC |                                  IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_VTEXLRD,       P_("monster", "Windspawn"),                        "GENERAL",             12,       711, MonsterAI::SkeletonSword,     1,          35,          40,  IMMUNE_MAGIC | IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_GSNAKE,        P_("monster", "Lord of the Pit"),                  "GENERAL",             13,       762, MonsterAI::SkeletonSword,     2,          25,          42,                 RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_RTBLACK,       P_("monster", "Rustweaver"),                       "GENERAL",             13,       400, MonsterAI::SkeletonSword,     3,           1,          60,  IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_HOLOWONE,      P_("monster", "Howlingire the Shade"),             "GENERAL",             13,       450, MonsterAI::SkeletonSword,     2,          40,          75,                 RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_MAEL,          P_("monster", "Doomcloud"),                        "GENERAL",             13,       612, MonsterAI::Storm,             1,           1,          60,                 RESIST_FIRE | IMMUNE_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_PAINMSTR,      P_("monster", "Bloodmoon Soulfire"),               "GENERAL",             13,       684, MonsterAI::SkeletonSword,     1,          15,          40,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_SNOWWICH,      P_("monster", "Witchmoon"),                        "GENERAL",             13,       310, MonsterAI::Succubus,          3,          30,          40,                               RESIST_LIGHTNING                 , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_VTEXLRD,       P_("monster", "Gorefeast"),                        "GENERAL",             13,       771, MonsterAI::SkeletonSword,     3,          20,          55,                 RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_RTBLACK,       P_("monster", "Graywar the Slayer"),               "GENERAL",             14,       672, MonsterAI::SkeletonSword,     1,          30,          50,                               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_MAGISTR,       P_("monster", "Dreadjudge"),                       "GENERAL",             14,       540, MonsterAI::Counselor,         1,          30,          40,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING                 , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_HLSPWN,        P_("monster", "Stareye the Witch"),                "GENERAL",             14,       726, MonsterAI::Succubus,          2,          30,          50,                 IMMUNE_FIRE                                    , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_BTBLACK,       P_("monster", "Steelskull the Hunter"),            "GENERAL",             14,       831, MonsterAI::SkeletonSword,     3,          40,          50,                               RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_RBLACK,        P_("monster", "Sir Gorash"),                       "GENERAL",             16,      1050, MonsterAI::SkeletonSword,     1,          20,          60,                                                  IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_CABALIST,      P_("monster", "The Vizier"),                       "GENERAL",             15,       850, MonsterAI::Counselor,         2,          25,          40,                 IMMUNE_FIRE                                    , UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_REALWEAV,      P_("monster", "Zamphir"),                          "GENERAL",             15,       891, MonsterAI::SkeletonSword,     2,          30,          50,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_HLSPWN,        P_("monster", "Bloodlust"),                        "GENERAL",             15,       825, MonsterAI::Succubus,          1,          20,          55,  IMMUNE_MAGIC |               IMMUNE_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_HLSPWN,        P_("monster", "Webwidow"),                         "GENERAL",             16,       774, MonsterAI::Succubus,          1,          20,          50,  IMMUNE_MAGIC | IMMUNE_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_SOLBRNR,       P_("monster", "Fleshdancer"),                      "GENERAL",             16,       999, MonsterAI::Succubus,          3,          30,          50,  IMMUNE_MAGIC | RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },
	{  MT_OBLORD,        P_("monster", "Grimspike"),                        "GENERAL",             19,       534, MonsterAI::Sneak,             1,          25,          40,  IMMUNE_MAGIC | RESIST_FIRE |                    IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
// TRANSLATORS: Unique Monster Block end
	{  MT_STORML,        P_("monster", "Doomlock"),                         "GENERAL",             28,       534, MonsterAI::Sneak,             1,          35,          55,  IMMUNE_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_NULL_40, UniqueMonsterPack::Leashed,                 0,                0, TEXT_NONE      },
	{  MT_INVALID,       nullptr,                                           nullptr,                0,         0, MonsterAI::Invalid,           0,           0,           0,  0                                                             , UniqueMonsterPack::None,                    0,                0, TEXT_NONE      },"""

    for line in unique_string_to_convert.split('\n'):
        repl = r"(.+,)(.+?,)( UniqueMonsterPack::.*)"
        r = re.search(repl, line)
        if r is not None:
            resist_string = "  { "
            resists = convert_resist_cell(r.group(2))
            resist_string += resists + "     "
            newline = re.sub(repl, r"\1" + resist_string + r"\3", line)
            print(newline)
        else:
            print(line)

    # for line in string_to_convert.split('\n'):
    #     r = re.search(r"(MonsterClass::.+?,)(.+?,)(.+?,)", line)
    #     if r is not None:
    #         resist_string = "  { " if "Demon" in r.group(1) else " { "
    #         normal_resists = convert_resist_cell(r.group(2))
    #         hell_resists = convert_resist_cell(r.group(3))
    #         resist_string += normal_resists + "   { " + normal_resists + "   { " + hell_resists + "       "
    #         newline = re.sub(r"(.*MonsterClass::.+?,)(.+?,)(.+?,)(.*)", r"\1" + resist_string + r"\4", line)
    #         print(newline)


def convert_resist_cell(text):
    return_text = ""
    if "MAGIC" in text:
        if "RESIST_MAGIC" in text:
            return_text += " 75,"
        else:
            return_text += "100,"
    else:
        return_text += "  0,"

    if "FIRE" in text:
        if "RESIST_FIRE" in text:
            return_text += " 75,"
        else:
            return_text += "100,"
    else:
        return_text += "  0,"

    if "LIGHTNING" in text:
        if "RESIST_LIGHTNING" in text:
            return_text += " 75,"
        else:
            return_text += "100,"
    else:
        return_text += "  0,"

    if "IMMUNE_ACID" in text:
        return_text +="100 },"
    else:
        return_text +="  0 },"
    
    return return_text


def main():
    with open("DIABLO.EXE", 'rb') as f:
        size_bytes = os.fstat(f.fileno()).st_size
        print(f"file size: {size_bytes}\n")
        m = mmap.mmap(f.fileno(), length=size_bytes, access=mmap.ACCESS_READ)

    # convert_monster_data(m)
    # convert_affix_data(m)
    # convert_unique_data(m)
    # convert_item_data(m)
    # convert_unique_monsters(m)
    # convert_spell_data(m)
    # convert_missile_data(m)
    # convert_item_panel_data(m)
    # convert_monster_avail(m)
    # convert_anim_data(m)
    convert_monster_resists()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
