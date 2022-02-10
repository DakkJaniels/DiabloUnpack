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

def main():
    with open("DIABLO.EXE", 'rb') as f:
        size_bytes = os.fstat(f.fileno()).st_size
        print(f"file size: {size_bytes}\n")
        m = mmap.mmap(f.fileno(), length=size_bytes, access=mmap.ACCESS_READ)

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
    for monster_address in range(monster_start, monster_start+monster_size * monster_count, monster_size):
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
            f'\"{get_string(m, monster_dict["animation_pointer"] - mem_offset)}\"' if monster_dict["animation_pointer"] != 0 else "nullptr",
            f'\"{get_string(m, monster_dict["sounds_pointer"] - mem_offset)}\"' if monster_dict["sounds_pointer"] != 0 else "nullptr",
            f'\"{get_string(m, monster_dict["color_trn_pointer"] - mem_offset)}\"' if monster_dict["color_trn_pointer"] != 0 else "nullptr",
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
        temp_string ="{"
        temp_row = [str(int) for int in row]
        x = ", ".join(temp_row)
        temp_string += x
        temp_string +="},"
        print(temp_string)


    # for key in monster_dict:
    #
    #     print(f"{key}: {(monster_dict[key])}")
    #     pointer_list = ["animation_pointer", "sounds_pointer", "color_trn_pointer", "monster_name_pointer"]
    #     resistance_list = ["resistances_immunities_norm_nm", "resistances_immunities_hell"]
    #     if key in pointer_list and monster_dict[key] != 0:
    #         address = monster_dict[key] - mem_offset
    #         temp_string = ""
    #         while m[address] != 0:
    #             temp_string = temp_string + chr(m[address])
    #             address += 1
    #         print(f"\t{temp_string}")
    #     elif key in resistance_list:
    #
    #         RESIST_MAGIC = 1 << 0
    #         RESIST_FIRE = 1 << 1
    #         RESIST_LIGHTNING = 1 << 2
    #         IMMUNE_MAGIC = 1 << 3
    #         IMMUNE_FIRE = 1 << 4
    #         IMMUNE_LIGHTNING = 1 << 5
    #         IMMUNE_NULL_40 = 1 << 6
    #         IMMUNE_ACID = 1 << 7
    #
    #         resistance_string = ""
    #         res = monster_dict[key]
    #         if ((res & (
    #                 RESIST_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40 | IMMUNE_ACID)) == 0):
    #             resistance_string = "0"
    #
    #         else:
    #             if ((res & RESIST_MAGIC) != 0):
    #                 resistance_string += "RESIST_MAGIC | "
    #             if ((res & RESIST_FIRE) != 0):
    #                 resistance_string += "RESIST_FIRE | "
    #             if ((res & RESIST_LIGHTNING) != 0):
    #                 resistance_string += "RESIST_LIGHTNING | "
    #             if ((res & IMMUNE_MAGIC) != 0):
    #                 resistance_string += "IMMUNE_MAGIC | "
    #             if ((res & IMMUNE_FIRE) != 0):
    #                 resistance_string += "IMMUNE_FIRE | "
    #             if ((res & IMMUNE_LIGHTNING) != 0):
    #                 resistance_string += "IMMUNE_LIGHTNING | "
    #             if ((res & IMMUNE_NULL_40) != 0):
    #                 resistance_string += "IMMUNE_NULL_40 | "
    #             if ((res & IMMUNE_ACID) != 0):
    #                 resistance_string += "IMMUNE_ACID"
    #             resistance_string = resistance_string.strip()
    #             resistance_string = resistance_string.strip("|")
    #         print(resistance_string)
    #     elif key == "mAi":
    #         print(monster_ai_list[monster_dict[key]])
    #     elif key == "mFlags" and monster_dict[key] != 0:
    #         mflag_string = ""
    #         mflag = monster_dict[key]
    #         if ((mflag & MFLAG_HIDDEN) != 0):
    #             mflag_string += "MFLAG_HIDDEN | "
    #         if ((mflag & MFLAG_LOCK_ANIMATION) != 0):
    #             mflag_string += "MFLAG_LOCK_ANIMATION | "
    #         if ((mflag & MFLAG_ALLOW_SPECIAL) != 0):
    #             mflag_string += "MFLAG_ALLOW_SPECIAL | "
    #         if ((mflag & MFLAG_NOHEAL) != 0):
    #             mflag_string += "MFLAG_NOHEAL | "
    #         if ((mflag & MFLAG_TARGETS_MONSTER) != 0):
    #             mflag_string += "MFLAG_TARGETS_MONSTER | "
    #         if ((mflag & MFLAG_GOLEM) != 0):
    #             mflag_string += "MFLAG_GOLEM | "
    #         if ((mflag & MFLAG_QUEST_COMPLETE) != 0):
    #             mflag_string += "MFLAG_QUEST_COMPLETE | "
    #         if ((mflag & MFLAG_KNOCKBACK) != 0):
    #             mflag_string += "MFLAG_KNOCKBACK | "
    #         if ((mflag & MFLAG_SEARCH) != 0):
    #             mflag_string += "MFLAG_SEARCH | "
    #         if ((mflag & MFLAG_CAN_OPEN_DOOR) != 0):
    #             mflag_string += "MFLAG_CAN_OPEN_DOOR | "
    #         if ((mflag & MFLAG_NO_ENEMY) != 0):
    #             mflag_string += "MFLAG_NO_ENEMY | "
    #         if ((mflag & MFLAG_BERSERK) != 0):
    #             mflag_string += "MFLAG_BERSERK | "
    #         if ((mflag & MFLAG_NOLIFESTEAL) != 0):
    #             mflag_string += "MFLAG_NOLIFESTEAL | "
    #         mflag_string = mflag_string.strip()
    #         mflag_string = mflag_string.strip("|")
    #         print(mflag_string)
    #     elif key == "monster_type":
    #         print(monster_class_list[monster_dict[key]])
    #     elif key == "color_trn_pointer" and monster_dict[key] == 0:
    #         print("nullptr")
    #     elif key in bool_list:
    #         value = monster_dict[key]
    #         if value:
    #             print("true")
    #         else:
    #             print("false")
    #
    # # start_pos = 0x00096C78
    # end_pos = start_pos + 1
    # chunk = m[start_pos:end_pos]
    # print(chunk)
    # value_array = get_value(m, start_pos, 1)
    # print(value_array)
    # value = value_array[0]
    # print(hex(value))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
