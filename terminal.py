#!/usr/bin/env python3

import evdev
import threading
import os
import curses
import time
import sys
import random

def read_team_config():
    team_names = {}
    try:
        with open('team_config.txt', 'r') as config_file:
            for line in config_file:
                usb_id, team_name = line.strip().split(':')
                team_names[usb_id] = team_name
    except FileNotFoundError:
        print("ERROR: team_config.txt not found.")
        input("Press Enter to continue and run setup.sh")
        sys.exit()

    return team_names

def monitor_mouse_clicks(device, team_name, last_team, click_registered):
    for event in device.read_loop():
        if not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
            last_team[0] = team_name
            click_registered[0] = True

def display_scores(stdscr, last_team, click_registered, team_scores, quiz_round):
    stdscr.clear()

    # Add ASCII art title
    title = r"""
   _______          __       _____       _      ____        _       ___   ___ ___  ____
  / ____\ \        / /\     |  __ \     | |    / __ \      (_)     |__ \ / _ \__ \|___ \
 | (___  \ \  /\  / /  \    | |__) |   _| |__ | |  | |_   _ _ ____    ) | | | | ) | __) |
  \___ \  \ \/  \/ / /\ \   |  ___/ | | | '_ \| |  | | | | | |_  /   / /| | | |/ / |__ <
  ____) |  \  /\  / ____ \  | |   | |_| | |_) | |__| | |_| | |/ /   / /_| |_| / /_ ___) |
 |_____/    \/  \/_/    \_\ |_|    \__,_|_.__/ \___\_\\__,_|_/___| |____|\___/____|____/


    """
    stdscr.addstr(title)

    stdscr.addstr("\nFunctions:")
    stdscr.addstr("\n'Q' - Quit the game.")
    stdscr.addstr("\n'R' - Reset the game.\n")

    stdscr.addstr("\nScoreboard:\n")
    for team_name, total_score in team_scores.items():
        stdscr.addstr(f"{team_name}: {total_score} points\n")

    stdscr.addstr("\nTeam that clicked first: ")
    stdscr.addstr(f"{last_team[0]}\n" if click_registered[0] else "")

    if quiz_round[0] == 1:
        if click_registered[0]:
            stdscr.addstr("\nPress 'Enter' to start a new round.\n")
        else:
            stdscr.addstr("\nRound in progress. Waiting for a team to click.....\n")

    # Refresh the screen only when necessary
    stdscr.refresh()

def reset_game(team_scores, click_registered, last_team, quiz_round):
    team_scores.clear()
    click_registered[0] = False
    last_team[0] = None
    quiz_round[0] = 0

def cancel_restart_script():
    os.execl(sys.executable, sys.executable, *sys.argv)

def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(0)  # Non-blocking getch

    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = read_team_config()

    monitors = []
    team_scores = {name: 0 for name in team_names.values()}
    last_team = [None]
    quiz_round = [1]  # 0: Round not started, 1: Round in progress
    click_registered = [False]  # To track if a click has been registered in the current round

    for device, name in team_names.items():
        try:
            monitor = evdev.InputDevice(device)
            monitors.append((monitor, name))
        except:
            print(f"Failed to open device: {device}")

    if not monitors:
        print("No mice found or failed to open all devices.")
        return

    # Start a separate thread for each mouse to monitor mouse clicks
    mouse_threads = []
    for monitor, name in monitors:
        mouse_thread = threading.Thread(target=monitor_mouse_clicks, args=(monitor, name, last_team, click_registered))
        mouse_thread.daemon = True
        mouse_thread.start()
        mouse_threads.append(mouse_thread)

    while True:
        c = stdscr.getch()
        if c == ord('q') or c == ord('Q'):
            break
        elif c == ord('r') or c == ord('R'):  # Reset the game when 'R' key is pressed
            reset_game(team_scores, click_registered, last_team, quiz_round)
            cancel_restart_script()

        start_time = time.time()
        display_scores(stdscr, last_team, click_registered, team_scores, quiz_round)

        # Check if the 'Enter' key was pressed to start a new round
        if c == 10 and quiz_round[0] == 1 and click_registered[0]:
            click_registered[0] = False
            if last_team[0]:
                team_scores[last_team[0]] += 1
            last_team[0] = None

        # Refresh the screen only when necessary
        stdscr.refresh()

        # Sleep for a short duration to reduce flickering
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)