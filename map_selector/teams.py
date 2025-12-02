import random
import os
from tabulate import tabulate
import math
import textwrap
import sys

delimiter = "================================================"

class Player:
    def __init__(self, name, acs, tracker_score, tracker_score_normalized):
        # assign initial parameters
        self.name = name
        self.acs = acs
        self.ts = tracker_score
        self.tsn = tracker_score_normalized

    def __str__(self):
        return self.name

class PlayerPool:
    def __init__(self, playerlist="playerlist.txt"):
        # create player list
        self.player_pool = []
        self.team1 = []
        self.team2 = []
        
        # read file with players
        with open(playerlist, 'r') as f:
            for _, line in enumerate(f, 1):
                row = line.strip().split(',')
                player_name = row[0]
                player_acs = int(row[1])
                player_ts = int(row[2])
                player_tsn = 19.6 * math.log(player_ts / 50, 1.8)
                player = Player(player_name, player_acs, player_ts, player_tsn)
                self.player_pool.append(player)

    def captain_selection_manual(self):
        # MANUAL CAPTAIN SELECTION SHOULD BE DONE BEFORE SELECTING TEAMS

        # print all players
        print(delimiter)
        print("Captain Selection:")
        print(delimiter)
        self.print_player_pool()
        print(delimiter)

        # select captains
        self.t1c = self.player_pool[int(input("Team 1 Captain: ")) - 1]
        self.t2c = self.player_pool[int(input("Team 2 Captain: ")) - 1]

        # remove captains from player pool
        self.player_pool.remove(self.t1c)
        self.player_pool.remove(self.t2c)

        # flip a coin
        coinflip_winner = random.choice([self.t1c, self.t2c])
        if coinflip_winner != self.t1c:
            self.t1c, self.t2c = self.t2c, self.t1c
        
        # add captains to team list
        self.team1.append(self.t1c)
        self.team2.append(self.t2c)

        # indicate which captain picks first
        print(f"First Pick: {self.t1c}")
        print(f"Second Pick: {self.t2c}")

    def captain_selection_auto(self):
        # AUTOMATIC CAPTAIN SELECTION WILL BE DONE AFTER TEAMS ARE POPULATED

        # randomly assign captain to team 1
        self.t1c = random.choice(self.team1)
        self.t2c = random.choice(self.team2)
    
    def player_selection_snake(self):
        # error check
        if self.t1c is None and self.t2c is None:
            print("Error; please select captains first.")
            return
        if len(self.player_pool) != 8:
            print("Error; player pool must be exactly 10.")
            return

        # start with team 1 captain; pick count starts at 1 (max. 2, resets to 0)
        curr_captain = self.t1c
        pick_count = 1

        # while players are still in pool, select players
        while self.player_pool:
            # clear screen and print captains
            os.system('cls')
            print(delimiter)
            self.print_captains()

            # print player list
            print(delimiter)
            print("Available Players:")
            self.print_player_pool()
            print(delimiter)

            # print teams
            self.print_teams()

            # current captain selects
            print(delimiter)
            curr_player = self.player_pool[int(input(f"{curr_captain} select: ")) - 1]
            if curr_captain == self.t1c:
                self.team1.append(curr_player)
            else:
                self.team2.append(curr_player)
            self.player_pool.remove(curr_player)

            # increment pick count, flip current captain if needed
            pick_count += 1
            if pick_count == 2:
                curr_captain = self.t2c if curr_captain == self.t1c else self.t1c
                pick_count = 0
    
    def player_selection_corerand(self):
        # error check
        if len(self.player_pool) != 10:
            print("Error; player pool must be exactly 10.")

        # sort players in order of ACS
        sorted_players = sorted(self.player_pool, key=lambda p: p.acs, reverse=True)

        # split core seed from randomized
        core_seed = sorted_players[:4]
        randomized_seed = sorted_players[4:]

        # --- STEP 1: Core Seed Balancing ---

        # Snake draft-style balancing for the core seed
        self.team1.append(core_seed[0])
        self.team1.append(core_seed[3])
        self.team2.append(core_seed[1])
        self.team2.append(core_seed[2])

        # --- STEP 2: Random Seed Balancing ---

        # create a list of lists representing the pairs
        pairs = []
        for i in range(0, len(randomized_seed), 2):
            pair = randomized_seed[i:i+2]
            if pair:
                pairs.append(pair)
        
        # randomly assign each pair to a team
        for i, pair in enumerate(pairs):
            # randomly select players from each pair
            p1 = random.choice(pair)
            pair.remove(p1)
            p2 = pair[0]

            # assign players to each team
            self.team1.append(p1)
            self.team2.append(p2)

    def player_selection_acscontrolswap(self, variation: int = 5, swap_attempts: int = 100):
        # error check
        if len(self.player_pool) != 10:
            print("Error; player pool must be exactly 10.")

        # --- STEP 1: Initialize Selection Parameters ---

        # create a list of players, sorted by ACS (index 0 = highest ACS)
        sorted_players = sorted(self.player_pool, key=lambda p: p.acs, reverse=True)

        # determine ACS parameters
        total_acs = sum(p.acs for p in sorted_players)
        max_acs_delta = total_acs * (variation / 100.0)

        # --- STEP 2: Initial Seeding ---

        # iterate through sorted players and alternate team assignments
        for i, player in enumerate(sorted_players):
            if i % 2 == 0:
                self.team1.append(player)
            else:
                self.team2.append(player)

        # --- STEP 3: Controlled Random Swaps ---

        # swap execution loop
        for attempt in range(swap_attempts):
            # choose two random players from each team
            p1 = random.choice(self.team1)
            p2 = random.choice(self.team2)

            # calculate the current and expected ACS totals for each team
            t1_acs_preswap, t2_acs_preswap = self.get_team_acs()

            # calculate the expected ACS totals if p1 and p2 swap
            t1_acs_postswap = t1_acs_preswap - p1.acs + p2.acs
            t2_acs_postswap = t2_acs_preswap - p2.acs + p1.acs
            acs_delta = abs(t1_acs_postswap - t2_acs_postswap)

            # check if the ACS difference is less than max variation
            if acs_delta < max_acs_delta:
                # acs delta is less than max variation; swap
                self.team1.remove(p1)
                self.team2.remove(p2)
                self.team1.append(p2)
                self.team2.append(p1)

                # debug print
                # print(f"Swap {attempt}: {p1} (ACS: {p1.acs}) and {p2} (ACS: {p2.acs})")

    def player_selection_tsncontrolswap(self, variation: int = 5, swap_attempts: int = 100):
        # tracker score normalized (tsn) based control swap

        # error check
        if len(self.player_pool) != 10:
            print("Error; player pool must be exactly 10.")

        # --- STEP 1: Initialize Selection Parameters ---
        
        # create a list of players sorted by normalized TS (index 0 = highest ACS)
        sorted_players = sorted(self.player_pool, key=lambda p: p.tsn, reverse=True)

        # determine TS parameters
        total_tsn = sum(p.tsn for p in sorted_players)
        max_tsn_delta = total_tsn * (variation / 100.0)

        # --- STEP 2: Initial Seeding ---
        
        # iterate through sorted players and alternate team assignments
        for i, player in enumerate(sorted_players):
            if i % 2 == 0:
                self.team1.append(player)
            else:
                self.team2.append(player)

        # --- STEP 3: Controlled Random Swaps ---

        # swap execution loop
        for attempt in range(swap_attempts):
            # choose two random players from each team
            p1 = random.choice(self.team1)
            p2 = random.choice(self.team2)

            # calculate the current and expected TSN totals for each team
            t1_tsn_preswap, t2_tsn_preswap = self.get_team_tsn()

            # calculate jthe expected TSN totals if p1 and p2 swap
            t1_tsn_postswap = t1_tsn_preswap - p1.tsn + p2.tsn
            t2_tsn_postswap = t2_tsn_preswap - p2.tsn + p1.tsn
            tsn_delta = abs(t1_tsn_postswap - t2_tsn_postswap)

            # check if the TSN difference is less than max variation
            if tsn_delta < max_tsn_delta:
                # tsn delta is less than max variation; swap
                self.team1.remove(p1)
                self.team2.remove(p2)
                self.team1.append(p2)
                self.team2.append(p1)

                # debug print
                # print(f"Swap {attempt}: {p1} (TSN: {p1.tsn}) and {p2} (TSN: {p2.tsn})")
    
    def print_captains(self):
        print(f"[ Team 1 Captain: {self.t1c} // Team 2 Captain: {self.t2c} ]")

    def print_player_pool(self):
        counter = 1
        for name in self.player_pool:
            print(f'[{counter}] {name}')
            counter += 1

    def print_teams(self, output_file=sys.stdout):
        # if captains aren't assigned, randomly assign
        if not hasattr(self, 't1c') or not hasattr(self, 't2c'):
            self.captain_selection_auto()

        # create a row for the tabulate table
        rows_list = []
        for i in range(5):
            row = []
            if i < len(self.team1):
                row.append(self.team1[i])
            else:
                row.append("")
            if i < len(self.team2):
                row.append(self.team2[i])
            else:
                row.append("")
            rows_list.append(row)

        # append team metadata
        team1_acs, team2_acs = self.get_team_acs()
        team1_tsn, team2_tsn = self.get_team_tsn()

        # create column headers
        team1_column_header = textwrap.dedent(f"""\
            Team 1 ({self.t1c})
            Total ACS: {team1_acs}
            Total TSN: {int(round(team1_tsn,0))}\
        """)
        team2_column_header = textwrap.dedent(f"""\
            Team 2 ({self.t2c})
            Total ACS: {team2_acs}
            Total TSN: {int(round(team2_tsn,0))}\
        """)
        
        columns_list = [team1_column_header, team2_column_header]

        # tabulate and print
        tabulated_teams = tabulate(rows_list, columns_list, tablefmt="grid")
        print(tabulated_teams, file=output_file)

    # helper function to calculate the ACS for team1 and team2, returned as a tuple
    def get_team_acs(self):
        return (sum(p.acs for p in self.team1), sum(p.acs for p in self.team2))
    
    # helper function to calcualte the TSN (tracker score normalized) for team1 and team2, returned as a tuple
    def get_team_tsn(self):
        return (sum(p.tsn for p in self.team1), sum(p.tsn for p in self.team2))