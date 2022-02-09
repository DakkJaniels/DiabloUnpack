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
                       ("secondary_attack_min_max_dmg", 2),
                       ("monster_ac", 1),
                       ("monster_type", 2),
                       ("resistances_immunities_norm_nm", 2),
                       ("resistances_immunities_hell", 2),
                       ("item_drop_specials", 2),
                       ("monster_selection_outline", 2),
                       ("xp", 4)
                       ]

    monster_start = 0x00096C70
    monster_size = 0x4C
    monster_count = 112

    monster_dict = {}
    cur_address = monster_start

    for name, length in monster_package:
        monster_dict[name] = get_value(m,cur_address,length)
        cur_address = cur_address + length

    # print(monster_dict)

    mem_offset = 0x402200

    for key in monster_dict:
        print(f"{key}: {(monster_dict[key])}")
        pointer_list = ["animation_pointer", "sounds_pointer", "color_trn_pointer", "monster_name_pointer"]
        resistance_list = ["resistances_immunities_norm_nm","resistances_immunities_hell"]
        if key in pointer_list and monster_dict[key] != 0:
            address = monster_dict[key] - mem_offset
            temp_string = ""
            while m[address] != 0:
                temp_string = temp_string + chr(m[address])
                address += 1
            print(f"\t{temp_string}")
        elif key in resistance_list:

            RESIST_MAGIC = 1 << 0
            RESIST_FIRE = 1 << 1
            RESIST_LIGHTNING = 1 << 2
            IMMUNE_MAGIC = 1 << 3
            IMMUNE_FIRE = 1 << 4
            IMMUNE_LIGHTNING = 1 << 5
            IMMUNE_NULL_40 = 1 << 6
            IMMUNE_ACID = 1 << 7

            resistance_string = ""
            res = monster_dict[key]
            if ((res & (RESIST_MAGIC | RESIST_FIRE | RESIST_LIGHTNING | IMMUNE_MAGIC | IMMUNE_FIRE | IMMUNE_LIGHTNING | IMMUNE_NULL_40 | IMMUNE_ACID)) == 0):
                resistance_string = "0"

            else:
                if ((res & RESIST_MAGIC) != 0):
                    resistance_string +="RESIST_MAGIC | "
                if ((res & RESIST_FIRE) != 0):
                    resistance_string +="RESIST_FIRE | "
                if ((res & RESIST_LIGHTNING) != 0):
                    resistance_string +="RESIST_LIGHTNING | "
                if ((res & IMMUNE_MAGIC) != 0):
                    resistance_string += "IMMUNE_MAGIC | "
                if ((res & IMMUNE_FIRE) != 0):
                    resistance_string += "IMMUNE_FIRE | "
                if ((res & IMMUNE_LIGHTNING) != 0):
                    resistance_string +="IMMUNE_LIGHTNING | "
                if ((res & IMMUNE_NULL_40) != 0):
                    resistance_string +="IMMUNE_NULL_40 | "
                if ((res & IMMUNE_ACID) != 0):
                    resistance_string += "IMMUNE_ACID"
                resistance_string = resistance_string.strip()
                resistance_string = resistance_string.strip("|")
            print(resistance_string)



    # start_pos = 0x00096C78
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
