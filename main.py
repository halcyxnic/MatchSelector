from map_selector.map import MapPool
from map_selector.teams import PlayerPool

from map_selector import BO1_MAP_COUNT, BO3_MAP_COUNT, BO5_MAP_COUNT

import os
import argparse

def summary(players: PlayerPool, maps: MapPool):
    os.system('cls')

    # print teams and maps
    maps.print_maps()
    players.print_teams()

def save_state(players: PlayerPool, maps: MapPool, save_file: str = "match_data.txt"):
    # remove old save file
    if os.path.exists(save_file):
        os.remove(save_file)

    # print teams and maps to file
    with open(save_file, 'a') as f:
        maps.print_maps(output_file=f)
        players.print_teams(output_file=f)

    # let the user know data was saved
    print(f"\nMatch info has been saved to {save_file}.\n")

def bo1(players: PlayerPool):
    maps = MapPool(series_type=BO1_MAP_COUNT)
    maps.ban_phase(1, players.t1c, players.t2c)
    return maps

def bo3(players: PlayerPool):
    maps = MapPool(series_type=BO3_MAP_COUNT)
    maps.ban_phase(1, players.t1c, players.t2c)
    maps.pick_phase(2, players.t1c, players.t2c)
    maps.ban_phase(3, players.t1c, players.t2c)
    return maps

def bo5(players: PlayerPool):
    maps = MapPool(series_type=BO5_MAP_COUNT)
    maps.ban_phase(1, players.t1c, players.t2c)
    maps.pick_phase(2, players.t1c, players.t2c)
    maps.ban_phase(3, players.t1c, players.t2c)
    maps.pick_phase(4, players.t1c, players.t2c)
    maps.ban_phase(5, players.t1c, players.t2c)
    return maps

def parse_arguments():
    # declare initial argparser
    parser = argparse.ArgumentParser(
        prog="VALORANT Customs Lobby Setup",
        description="This program sets up a lobby for a VALORANT custom match"
    )

    # best of 1/3/5 selection argument
    parser.add_argument(
        "-s",
        "--series-type",
        type=int,
        choices=[1,3,5],
        required=True
    )

    # player selection method argument
    parser.add_argument(
        "-p",
        "--player-selection",
        choices=['snake', 'corerand', 'acs', 'trackerscore'],
        required=True
    )

    # return argparser
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # clear screen
    os.system('cls')

    # parse arguments
    args = parse_arguments()

    # initialize players and maps
    players = PlayerPool("playerlist.txt")
    if args.player_selection == "snake":
        players.captain_selection_manual()
        players.player_selection_snake()
    elif args.player_selection == "corerand":
        players.player_selection_corerand()
        players.captain_selection_auto()
    elif args.player_selection == "acs":
        players.player_selection_acscontrolswap()
        players.captain_selection_auto()
    elif args.player_selection == "trackerscore":
        players.player_selection_tsncontrolswap()
        players.captain_selection_auto()

    # print teams, prompt for continue
    os.system('cls')
    players.print_teams()
    input("Press ENTER to continue...")

    # map selection
    if args.series_type == 1:
        maps = bo1(players)
    elif args.series_type == 3:
        maps = bo3(players)
    elif args.series_type == 5:
        maps = bo5(players)

    # print summary
    summary(players, maps)
    save_state(players, maps)