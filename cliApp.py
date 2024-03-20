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

scripts = {
    "Stochastic Tunneling": {"filename": "foo1.py", "args": ["--bar1", "--bar2"]},
    "Grid Search": {"filename": "BashScript-GridSearch", "args": ["--start", "--end", "--step"]},
    "CMA-ES": {"filename": "foo3.py", "args": ["--qux1", "--qux2"]},
}

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

def get_arguments(args):
    selected_arguments = []
    for arg in args:
        value = input(f"Value for {BOLD}{arg}{RESET} (leave empty if not used): ")
        if value:
            selected_arguments.append(arg)
            selected_arguments.append(value)
    return selected_arguments

def display_results(output, error, output_filename):
    print(BOLD + "Output:" + RESET)
    if not error:
        print(GREEN + "Monitoring output file (press Ctrl+C to stop):" + RESET)
        try:
            with open(output_filename, 'r') as file:
                while True:
                    lines = file.readlines()[-10:]  # Read last 10 lines of the file
                    print('\n'.join(lines))
                    time.sleep(1)  # Wait for 1 second before reading the file again
        except KeyboardInterrupt:
            print(BOLD + YELLOW + "\nStopped monitoring file." + RESET)
        except Exception as e:
            print(BOLD + RED + f"Error while reading file: {e}" + RESET)
    else:
        print(BOLD + RED + "Script Errors:" + RESET)
        print(RED + error + RESET)
    input("Press Enter to return to the menu...")  # Wait for user input to return to the menu

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
        print(f"\n{BOLD}{YELLOW}Running {script_name}...{RESET}")
        selected_arguments = get_arguments(script_args)
        command = [f'sbatch -N 1 -n 32 -p cpu_prod --qos=8nodespu --output={script_name}.txt {SCRIPT_DIR+script_filename}'] + selected_arguments
        #command = ["python3", script_filename] + selected_arguments
        result = subprocess.run(command, capture_output=True, text=True)
        #results are in a .txt file named script_name.txt. loop to read the file and print the results
        display_results(result.stdout, result.stderr, f"{script_name}.txt")
    else:
        print(BOLD + RED + "Invalid choice. Please try again." + RESET)