import os
import sys
import subprocess
import time

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"
WIDTH = 80  # Width of the menu

SCRIPT_DIR = "iso3dfd-st7/BashScripts"

#TODO: add the nb nodes as a parameter to the bash scripts
#TODO: rename the bash scripts to remove the "BashScript-" prefix, and add the extension ".sh"


scripts = {
    "Stochastic Tunneling": {
        "filename": "BashScript-StochasticTunneling",
        "args": ["--num_starters", "--step_size", "--temperature_initial", "--max_iteration", "--max_k"],
        "default_args": ["3", "2", "1000", "50", "5"]
    },
    "Grid Search": {
        "filename": "BashScript-GridSearch",
        "args": ["--start", "--end", "--step"],
        "default_args": ["32", "256", "32"]
    },
    "Hill Climbing": {
        "filename": "BashScript-HillClimbing",
        "args": ["--max_stable_runs", "--step_size"],
        "default_args": ["4", "2"]
    },
    "Guided Hill Climbing": {
        "filename": "BashScript-GuidedHillClimbing",
        "args": ["--max_stable_runs", "--step_size"],
        "default_args": ["4", "2"]
    },
    "CMA-ES": {
        "filename": "BashScript-CMA-ES",
        "args": ["--sigma", '--compilation', '--seed'],
        "default_args": ["8", "O3", "42"]
    },
}

BOLD = "\033[1m"
RESET = "\033[0m"

def get_arguments(args, default_args):
    selected_arguments = []
    for arg, default_value in zip(args, default_args):
        value = input(f"Value for {BOLD}{arg}{RESET} (default: {default_value}): ")
        if value:
            selected_arguments.append(arg)
            selected_arguments.append(value)
        else:
            selected_arguments.append(arg)
            selected_arguments.append(default_value)
    return selected_arguments

def display_header():
    # Define color codes
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    print(BOLD)
    print("=" * WIDTH + RESET+"\n")
    art1 = [
        f'{YELLOW}M""MMMMM""MM MM"""""""`YM MM\'""""\'YMM{RESET}        {CYAN}{BOLD}ST7 Project by:{RESET}',
        f'{YELLOW}M  MMMMM  MM MM  mmmmm  M M\' .mmm. `M{RESET}        {GREEN}Lucas Martins{RESET}',
        f'{YELLOW}M         `M M\'        .M M  MMMMMooM{RESET}        {GREEN}João Pedro Regazzi{RESET}',
        f'{YELLOW}M  MMMMM  MM MM  MMMMMMMM M  MMMMMMMM{RESET}        {GREEN}Mateus Goto{RESET}',
        f'{YELLOW}M  MMMMM  MM MM  MMMMMMMM M. `MMM\' .M{RESET}        {GREEN}Benjamin Feldman{RESET}',
        f'{YELLOW}M  MMMMM  MM MM  MMMMMMMM MM.     .dM{RESET}        {CYAN}Supervised by Stéphane Vialle{RESET}',
        f'{YELLOW}MMMMMMMMMMMM MMMMMMMMMMMM MMMMMMMMMMM{RESET}        {MAGENTA}2024 CentraleSupélec{RESET}'
    ]

    # Print ASCII art for "HPC" with colors
    for line in art1:
        print(line)
    print(RESET)



# Function to display the menu and get user input
def display_menu():
    display_header()
    print("=" * WIDTH + RESET)
    print(BOLD + "Cache Blocking Optimization Methods" + RESET)
    print("=" * WIDTH + RESET)
    print("Available Methods:")
    for index, script in enumerate(scripts, start=1):
        print(f"{GREEN}{index}. {script}{RESET}")
    print(f"{RED}0. Exit{RESET}")
    choice = input("Enter the number of the script to run: ")
    return choice

def get_sbatch_parameters():
    nodes = input(f"Enter the number of nodes (default: 8): ") or "8"
    tasks_per_node = str(int(nodes)*32)
    partition = input(f"Enter the partition (default: cpu_prod): ") or "cpu_prod"
    qos = input(f"Enter the QOS (default: 8nodespu): ") or "8nodespu"
    return nodes, tasks_per_node, partition, qos

def get_arguments(args, default_args):
    selected_arguments = []
    for arg, default_value in zip(args, default_args):
        value = input(f"Value for {BOLD}{arg}{RESET} (default: {default_value}): ")
        if value:
            selected_arguments.append(arg)
            selected_arguments.append(value)
        else:
            selected_arguments.append(arg)
            selected_arguments.append(default_value)
    return selected_arguments

def display_results(output, error, output_filename):
    output_filename = output_filename.replace(" ", "")
    print(BOLD + "Output:" + RESET)
    if not error:
        print(GREEN + "Monitoring output file (press Ctrl+C to stop):" + RESET)
        last_line_count = 0
        waiting_message_printed = False
        try:
            while True:
                try:
                    with open(output_filename, 'r') as file:
                        lines = file.readlines()
                        if len(lines) > last_line_count:
                            new_lines = lines[last_line_count:]
                            print(''.join(new_lines), end='')
                            last_line_count = len(lines)
                except FileNotFoundError:
                    if not waiting_message_printed:
                        print(YELLOW + f"Waiting for the slurm process to start..." + RESET)
                        waiting_message_printed = True
                time.sleep(0.1)  # Wait for 1 second before reading the file again
        except KeyboardInterrupt:
            print(BOLD + YELLOW + "\nStopped monitoring file." + RESET)
        except Exception as e:
            print(BOLD + RED + f"Error while reading file: {e}" + RESET)
    else:
        print(BOLD + RED + "Script Errors:" + RESET)
        print(RED + error + RESET)
    input("Press Enter to return to the menu...")  # Wait for user input to return to the menu

def main():
    while True:
        choice = display_menu()
        if choice == "0":
            print(BOLD + RED + "Exiting..." + RESET)
            break
        elif choice in [str(i) for i in range(1, len(scripts) + 1)]:
            script_index = int(choice) - 1
            script_info = list(scripts.values())[script_index]
            script_filename = script_info['filename']
            script_name = list(scripts.keys())[script_index]
            script_args = script_info['args']
            script_default_args = script_info['default_args']
            print(f"\n{BOLD}{YELLOW}Running {script_name}...{RESET}")
            selected_arguments = get_arguments(script_args, script_default_args)
            nodes, tasks_per_node, partition, qos = get_sbatch_parameters()
            script_path = os.path.join(SCRIPT_DIR, script_filename)
            # delete the output file if it exists
            try:
                os.remove(f"{script_name.replace(' ', '')}.txt")
            except FileNotFoundError:
                pass
            command = ['sbatch', '-N', nodes, '-n', tasks_per_node, '-p', partition, f'--qos={qos}',
                    f'--output={script_name.replace(" ", "")}.txt', script_path, '--nodes', nodes] + selected_arguments

            try:
                result = subprocess.run(command, capture_output=True, text=True, shell=False)
                display_results(result.stdout, result.stderr, f"{script_name.replace(' ', '')}.txt")
            except Exception as e:
                print(f"An error occurred while trying to execute the script: {e}")
        else:
            print(BOLD + RED + "Invalid choice. Please try again." + RESET)

if __name__ == "__main__":
    main()