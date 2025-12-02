import random
import os
import sys

from map_selector import BO3_MAP_COUNT

map_list = [
    "Bind",
    "Haven",
    "Split",
    "Ascent",
    "Icebox",
    "Breeze",
    "Fracture",
    "Pearl",
    "Lotus",
    "Sunset",
    "Abyss",
    "Corrode"
]

delimiter = "================================================"

class MapPool:
    def __init__(self, series_type=BO3_MAP_COUNT):
        # create a list of all maps and maps selected for this match
        self.all_maps = map_list
        self.available_maps = []
        self.selected_maps = []

        # initialize selected maps list
        for _ in range(series_type):
            map = random.choice(map_list)
            self.available_maps.append(map)
            self.all_maps.remove(map)

    def ban_phase(self, phase_number, t1_cap, t2_cap):
        # print a header for the current phase
        os.system('cls')
        print(delimiter)
        print(f"[ Phase {phase_number} // BAN ]")
        print(delimiter)
        print("Available Maps:")
        self.print_pool()
        print(delimiter)

        # prompt for ban inputs
        ban_1 = self.available_maps[int(input(f"{t1_cap} BAN: ")) - 1]
        ban_2 = self.available_maps[int(input(f"{t2_cap} BAN: ")) - 1]

        # remove maps from list
        self.available_maps.remove(ban_1)
        self.available_maps.remove(ban_2)

        # check if there's only 1 map left; if so, add it to the pool
        if len(self.available_maps) == 1:
            self.selected_maps.append(self.available_maps[0])
            self.available_maps.remove(self.available_maps[0])

    def pick_phase(self, phase_number, t1_cap, t2_cap):
        # print a header for the current phase
        os.system('cls')
        print(delimiter)
        print(f"[ Phase {phase_number} // PICK ]")
        print(delimiter)
        print("Available Maps:")
        self.print_pool()
        print(delimiter)

        # prompt for pick inputs
        ban_1 = self.available_maps[int(input(f"{t1_cap} PICK: ")) - 1]
        ban_2 = self.available_maps[int(input(f"{t2_cap} PICK: ")) - 1]

        # add maps to final list
        self.available_maps.remove(ban_1)
        self.selected_maps.append(ban_1)
        self.available_maps.remove(ban_2)
        self.selected_maps.append(ban_2)

    def print_pool(self):
        counter = 1
        for map in self.available_maps:
            print(f"[{counter}] {map}")
            counter += 1

    def print_maps(self, output_file=sys.stdout):
        # concatenate maps into string
        printed_string = "MAP SELECTION: [ "
        for map in self.selected_maps:
            printed_string += f"{map}"
            if map != self.selected_maps[-1]:
                printed_string += " // "
            else:
                printed_string += " ]\n"

        # print the header/selected maps
        print(printed_string, file=output_file)