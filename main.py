import mmap
import os
import struct


def get_value(m, start_pos, size):
    # note - last value is not pulled
    chunk = m[start_pos:start_pos + size]
    unpack_string = "<"
    if size == 1:
        unpack_string = unpack_string + "B"
    elif size == 2:
        unpack_string = unpack_string + "H"
    elif size == 4:
        unpack_string = unpack_string + "I"
    elif size == 8:
        unpack_string = unpack_string + "Q"
    else:
        print("error, get value size incorrect")
        return 0
    # print(unpack_string)
    return struct.unpack(unpack_string, chunk)[0]


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
        "AI_INVALID"
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
        x = ", ".join(temp_row)
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

def twos_complement(hexstr,bits):
    value = int(hexstr)
    if value & (1 << (bits-1)):
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

    # print(monster_dict)

    mem_offset = 0x402200
    affix_start = 0x0007AAF8
    affix_size = 48
    affix_count = 180

    affix_dict = {}
    cur_address = affix_start
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
            affix_dict["PLMinVal"],
            affix_dict["PLMaxVal"],
            # str(affix_dict["PLMultVal"])
            twos_complement(str(affix_dict["PLMultVal"]),32),
        ]
        # print(monster_row)
        affix_table.append(affix_row)

    for row in affix_table:
        temp_string = "{"
        temp_row = [str(int) for int in row]
        x = ", ".join(temp_row)
        temp_string += x
        temp_string += "},"
        print(temp_string)


def main():
    with open("DIABLO.EXE", 'rb') as f:
        size_bytes = os.fstat(f.fileno()).st_size
        print(f"file size: {size_bytes}\n")
        m = mmap.mmap(f.fileno(), length=size_bytes, access=mmap.ACCESS_READ)

    # convert_monster_data(m)
    convert_affix_data(m)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
