import io
import os
from spyparty.ReplayParser import ReplayParser


class Mission:
    def __init__(self):
        self.missions = {
            "Bug Ambassador": 0,
            "Contact Double Agent": 0,
            "Transfer Microfilm": 0,
            "Swap Statue": 0,
            "Inspect Statues": 0,
            "Seduce Target": 0,
            "Purloin Guest List": 0,
            "Fingerprint Ambassador": 0
        }

    def complete_mission(self, completed_missions):
        for mission in completed_missions:
            if mission in self.missions:
                self.missions[mission] += 1


class Venue:
    def __init__(self, name):
        self.name = name
        self.total_game_count = 0
        self.results = {"Civilian Shot": 0, "Missions Win": 0, "Spy Shot": 0, "Time Out": 0}
        self.spy_results = {"Civilian Shot": 0, "Missions Win": 0, "Spy Shot": 0, "Time Out": 0}
        self.sniper_results = {"Civilian Shot": 0, "Missions Win": 0, "Spy Shot": 0, "Time Out": 0}
        self.spy_game_count = 0
        self.sniper_game_count = 0
        self.spy_missions = Mission()
        self.sniper_missions = Mission()
        self.duration = {"spy_win": 0, "spy_loss": 0, "sniper_win": 0, "sniper_loss": 0}

    def get_win_rates(self):
        spy_win_rate = 0
        sniper_win_rate = 0
        if self.spy_game_count > 0:
            spy_wins = self.spy_results.get("Missions Win", 0) + self.spy_results.get("Civilian Shot", 0)
            spy_win_rate = (spy_wins / self.spy_game_count) * 100

        if self.sniper_game_count > 0:
            sniper_wins = self.sniper_results.get("Spy Shot", 0) + self.sniper_results.get("Time Out", 0)
            sniper_win_rate = (sniper_wins / self.sniper_game_count) * 100

        return spy_win_rate, sniper_win_rate

    def count_game(self, result, role, duration):
        if role.lower() == "spy":
            self.spy_game_count += 1
            if result in self.spy_results:
                self.spy_results[result] += 1
                if result in ["Missions Win", "Civilian Shot"]:
                    self.duration['spy_win'] += duration
                else:
                    self.duration['spy_loss'] += duration
        elif role.lower() == "sniper":
            self.sniper_game_count += 1
            if result in self.sniper_results:
                self.sniper_results[result] += 1
                if result == "Spy Shot":
                    self.duration['sniper_win'] += duration
                else:
                    self.duration['sniper_loss'] += duration

    def print_average_durations(self, capture):
        # For Spy Win
        self._print_average_duration('spy_win', "Spy Win", "spy", "Missions Win", "Civilian Shot", capture=capture)

        # For Spy Loss
        self._print_average_duration('spy_loss', "Spy Loss", "spy", "Spy Shot", "Time Out", capture=capture)

        # For Sniper Win
        self._print_average_duration('sniper_win', "Sniper Win", "sniper", "Spy Shot", capture=capture)

        # For Sniper Loss
        self._print_average_duration('sniper_loss', "Sniper Loss", "sniper", "Missions Win", "Civilian Shot",
                                     "Time Out", capture=capture)

    def _print_average_duration(self, duration_key, label, role, *result_keys, capture):
        if role.lower() == "spy":
            total_results = sum(self.spy_results.get(key, 0) for key in result_keys)
        elif role.lower() == "sniper":
            total_results = sum(self.sniper_results.get(key, 0) for key in result_keys)
        else:
            message = f"Invalid role specified: {role}"
            print(message)
            capture.write(message + '\n')  # Write to StringIO object
            return

        if total_results > 0:
            average_duration_seconds = self.duration[duration_key] / total_results
            average_minutes = int(average_duration_seconds // 60)
            average_seconds = int(average_duration_seconds % 60)
            message = f" Average {label} Duration for {self.name}: {average_minutes}:{average_seconds:02d}"
            print(message)
            capture.write(message + '\n')
        else:
            message = f"No {label.lower()} recorded for {self.name}."
            print(message)
            capture.write(message + '\n')

    def print_mission_percentages(self, capture):
        # Calculate total missions for Spy and Sniper
        total_spy_missions = sum(self.spy_missions.missions.values())
        total_sniper_missions = sum(self.sniper_missions.missions.values())

        message = f"Mission Occurrence Percentages for {self.name}:"
        print(message)
        capture.write(message + '\n')

        if total_spy_missions > 0:
            print("  Spy Missions:")
            capture.write("  Spy Missions:" + '\n')
            max_length = max(len(mission) for mission in self.spy_missions.missions)
            for mission, count in self.spy_missions.missions.items():
                percentage = (count / total_spy_missions) * 100
                message = f"    {mission.ljust(max_length)}: {percentage:.2f}%"
                print(message)
                capture.write(message + '\n')
        else:
            print("  No Spy Missions recorded.")
            capture.write("  No Spy Missions recorded." + '\n')

        if total_sniper_missions > 0:
            print("  Sniper Missions:")
            capture.write("  Sniper Missions:" + '\n')
            for mission, count in self.sniper_missions.missions.items():
                max_length = max(len(mission) for mission in self.spy_missions.missions)
                percentage = (count / total_sniper_missions) * 100
                print(f"    {mission.ljust(max_length)}: {percentage:.2f}%")
                capture.write(f"    {mission.ljust(max_length)}: {percentage:.2f}%" + '\n')
        else:
            print("  No Sniper Missions recorded.")
            capture.write("  No Sniper Missions recorded." + '\n')

    def print_win_percentages(self, capture):
        # Calculate the total number of games played as Spy and Sniper
        total_spy_games = sum(self.spy_results.values())
        total_sniper_games = sum(self.sniper_results.values())

        # Calculate win conditions for Spy and Sniper
        spy_wins = self.spy_results.get("Missions Win", 0) + self.spy_results.get("Civilian Shot", 0)
        sniper_wins = self.sniper_results.get("Time Out", 0) + self.sniper_results.get("Spy Shot", 0)

        # Calculate win percentages
        if total_spy_games > 0:
            spy_win_percentage = (spy_wins / total_spy_games) * 100
            print(f"Spy Win Percentage for {self.name}: {spy_win_percentage:.2f}% | {spy_wins}/{total_spy_games}")
            capture.write(f"Spy Win Percentage for {self.name}: {spy_win_percentage:.2f}% | {spy_wins}/{total_spy_games}" + '\n')

        else:
            print(f"No Spy games recorded for {self.name}.")
            capture.write(f"No Spy games recorded for {self.name}." + '\n')

        if total_sniper_games > 0:
            sniper_win_percentage = (sniper_wins / total_sniper_games) * 100
            print(f"Sniper Win Percentage for {self.name}: {sniper_win_percentage:.2f}% | {sniper_wins}/{total_sniper_games}")
            capture.write(f"Sniper Win Percentage for {self.name}: {sniper_win_percentage:.2f}% | {sniper_wins}/{total_sniper_games}" + '\n')
        else:
            print(f"No Sniper games recorded for {self.name}.")
            capture.write(f"No Sniper games recorded for {self.name}." + '\n')

    def print_game_counts_as_percentages(self, capture):
        # Calculate the total number of games played as Spy and Sniper
        total_spy_games = sum(self.spy_results.values())
        total_sniper_games = sum(self.sniper_results.values())

        print(f"Game Outcome Percentages for {self.name}:")
        capture.write(f"Game Outcome Percentages for {self.name}:" + '\n')

        # Print Spy results
        print("  Spy Results:")
        capture.write("  Spy Results:" + '\n')

        if total_spy_games > 0:
            for outcome, count in self.spy_results.items():
                max_length = max(len(outcome) for outcome in self.spy_results)
                percentage = (count / total_spy_games) * 100
                print(f"    {outcome.ljust(max_length)}: {percentage:.2f}%")
                capture.write(f"    {outcome.ljust(max_length)}: {percentage:.2f}%" + '\n')

        else:
            print("    No Spy games recorded.")
            capture.write("    No Spy games recorded." + '\n')


        # Print Sniper results
        print("  Sniper Results:")
        capture.write("  Sniper Results:" + '\n')

        if total_sniper_games > 0:
            for outcome, count in self.sniper_results.items():
                max_length = max(len(outcome) for outcome in self.sniper_results)
                percentage = (count / total_sniper_games) * 100
                print(f"    {outcome.ljust(max_length)}: {percentage:.2f}%")
                capture.write(f"    {outcome.ljust(max_length)}: {percentage:.2f}%" + '\n')

        else:
            print("    No Sniper games recorded.")
            capture.write("    No Sniper games recorded." + '\n')

    def __str__(self):
        missions_str = f"Spy Missions: {self.spy_missions.missions}\n Sniper Missions: {self.sniper_missions.missions}"
        return f"{self.name}:\n Results: {self.results}\n Game Counts: Spy: {self.spy_game_count} Sniper: {self.sniper_game_count}\n Durations: {self.duration}\n {missions_str}"


def iterate_folders_files(root_folder, player):
    for dirpath, _, filenames in os.walk(root_folder):
        if "Practice" in dirpath.split(os.sep):
            continue
        for filename in filenames:
            if not filename.endswith('.replay'):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                parser = ReplayParser(filepath)
                replay_data = parser.parse()
                valid = process_replay(replay_data, player)
                if not valid: break
            except Exception as e:
                print(f"Error processing {filepath}: {e}")


def process_replay(replay_data, player_search):
    if replay_data.get("result") == "In_Progress":
        print("In_Progress replay")
        return False

    spy, sniper = replay_data["spy_displayname"], replay_data["sniper_displayname"]
    if not any(player in [spy, sniper] for player in player_search):  # Check if any alias matches
        print(f'None of the aliases found in {spy} vs {sniper}')
        return False

    if any(opponent in [spy, sniper] for player in player_search) or bypassOpponentSearch:
        print(f'Opponent found in {spy} vs {sniper}')
    else:
        print(f'Opponent not found in in {spy} vs {sniper}')
        return False

    venue_name = replay_data.get("level")
    print(f'{spy} vs {sniper}: {venue_name}')
    current_venue = next((v for v in venues_list if v.name == venue_name), None)
    if current_venue:
        role = "spy" if any(player == spy for player in player_search) else "sniper"
        missions = current_venue.spy_missions if role == "spy" else current_venue.sniper_missions
        missions.complete_mission(replay_data.get("completed_missions", []))
        current_venue.count_game(replay_data.get("result"), role, replay_data.get("duration"))
    return True


#
# Main method
#
venues = ["Aquarium", "Balcony", "Ballroom", "Courtyard", "Gallery", "High-Rise", "Library", "Moderne", "Redwoods",
          "Teien", "Terrace", "Veranda"]
venues_list = [Venue(name) for name in venues]

folder_path = r'Replays\\Example-Replays'

player_search = ["martini/steam"]
opponent = "OpiWrites/steam"
bypassOpponentSearch = False

iterate_folders_files(folder_path, player_search)
output_capture = io.StringIO()

total_games = 0
equals_separator = "========================================================="
for venue in venues_list:
    print(equals_separator)
    output_capture.write(f'{equals_separator}\n')
    game_count = venue.sniper_game_count + venue.spy_game_count
    total_games += game_count
    print(f'{venue.name} : {game_count}')
    output_capture.write(f'{venue.name} : {game_count}\n')

    venue.print_win_percentages(output_capture)
    print(equals_separator)
    output_capture.write(f'{equals_separator}\n')

    venue.print_average_durations(output_capture)
    venue.print_mission_percentages(output_capture)
    venue.print_game_counts_as_percentages(output_capture)

print(f'Total Games: {total_games}')
output_capture.write(f'Total Games: {total_games}\n')

venue_win_rates = []
for venue in venues_list:
    venue.total_game_count = venue.spy_game_count + venue.sniper_game_count
    total_game_count = venue.total_game_count
    spy_win_rate, sniper_win_rate = venue.get_win_rates()
    venue_win_rates.append((venue.name, total_game_count, spy_win_rate, sniper_win_rate))

# Sort by venue names
venue_win_rates.sort(key=lambda x: x[0])
max_venue_name_length = max(len(venue.name) for venue in venues_list)

print("Venue Win Rates:")
output_capture.write("Venue Win Rates:\n")
for venue_name, total_game_count, spy_win_rate, sniper_win_rate in venue_win_rates:
    print(f"{venue_name.ljust(max_venue_name_length)} |{total_game_count:4.0f}: Spy Win Rate: {spy_win_rate:5.2f}%, Sniper Win Rate: {sniper_win_rate:5.2f}%")
    output_capture.write(f"{venue_name.ljust(max_venue_name_length)} |{total_game_count:4.0f}: Spy Win Rate: {spy_win_rate:5.2f}%, Sniper Win Rate: {sniper_win_rate:5.2f}%\n")
#
# Printout of the stats columns
#
# Step 1: Create a new list with mean win rate included
venue_win_rates_with_mean = []
for venue in venue_win_rates:
    venue_name, total_game_count, spy_win_rate, sniper_win_rate = venue
    mean_win_rate = (spy_win_rate + sniper_win_rate) / 2
    venue_with_mean = (venue_name, total_game_count, spy_win_rate, sniper_win_rate, mean_win_rate)
    venue_win_rates_with_mean.append(venue_with_mean)

# Step 2: Sort venues by Spy Win Rate, Sniper Win Rate, and Mean Win Rate
sorted_by_spy_win_rate = sorted(venue_win_rates_with_mean, key=lambda x: x[2], reverse=True)
sorted_by_sniper_win_rate = sorted(venue_win_rates_with_mean, key=lambda x: x[3], reverse=True)
sorted_by_mean_win_rate = sorted(venue_win_rates_with_mean, key=lambda x: x[4], reverse=True)

# Step 3: Determine the maximum venue name length for formatting
max_venue_name_length = max(len(venue[0]) for venue in venue_win_rates_with_mean)

# Set a fixed width for percentages
percentage_width = 6  # e.g., "58.23%"
print('\n')
output_capture.write("\n")

# Print header
header_venue_format = f"{{:<{max_venue_name_length}}}"
header_percentage_format = f"{{:>{percentage_width + 1}}}"  # +1 for the space before the percentage
header = (header_venue_format + header_percentage_format) * 3
header = header.format('Spy Rate:', '           ', 'Sniper Rate:', '        ', 'Mean Rate:', '')
print(header)  # Trim the trailing separator
output_capture.write(f'{header}\n')

# Iterate and print the rankings side by side
for i in range(len(venue_win_rates_with_mean)):
    spy_venue_name, _, spy_win_rate, _, _ = sorted_by_spy_win_rate[i]
    sniper_venue_name, _, _, sniper_win_rate, _ = sorted_by_sniper_win_rate[i]
    mean_venue_name, _, _, _, mean_win_rate = sorted_by_mean_win_rate[i]

    # Format each line
    line_format = header_venue_format + f" {{:>{percentage_width}.2f}}%   "
    spy_column = line_format.format(spy_venue_name, spy_win_rate)
    sniper_column = line_format.format(sniper_venue_name, sniper_win_rate)
    mean_column = line_format.format(mean_venue_name, mean_win_rate)

    print(f"{spy_column}{sniper_column}{mean_column}")
    output_capture.write(f"{spy_column}{sniper_column}{mean_column}\n")

# gonna save it to a .txt file now
base_file_name = '-'.join([name.replace('/steam', '') for name in player_search])
file_directory = r'Stats-Text-Files'
file_extension = '.txt'
file_number = 0  # Starting number

# Full path for the initial file
file_path = os.path.join(file_directory, f"{base_file_name}{file_extension}")

# Check if the file exists and increment the file number until finding an available filename
while os.path.exists(file_path):
    file_number += 1  # Increment the number
    # Generate a new file path with the incremented number
    file_path = os.path.join(file_directory, f"{base_file_name}_{file_number}{file_extension}")

# Create a .txt file with the concatenated names as the filename
with open(file_path, 'w') as file:
    # Write data to the file
    file.write(output_capture.getvalue())

print(f"File '{file_path}' created successfully and data written to it.")
