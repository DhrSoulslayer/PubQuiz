#!/usr/bin/env python3

import evdev
import threading
import os
import curses
import time
import sys
import random

def assign_fun_team_names(devices):
    fun_team_names = [
        "Thunderbolts", "Moonwalkers", "Fire Dragons", "Super Strikers", "Fantastic Falcons",
        "Turtle Ninjas", "Cosmic Comets", "Rainbow Unicorns", "Daring Dolphins", "Mighty Martians"
    ]
    random.shuffle(fun_team_names)

    mouse_names = {}
    for i, device in enumerate(devices):
        if i < len(fun_team_names) and "mouse" in device.name.lower():
            mouse_names[device.fn] = fun_team_names[i]
    return mouse_names

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
    stdscr.addstr("\n'R' - Reset the game.")
    stdscr.addstr("\n'P' - Replay the current round (only if the round is completed).")
    stdscr.addstr("\n'Enter' - Start the next round.\n")

    stdscr.addstr("\nScoreboard (Points):\n")
    for team_name, total_score in team_scores.items():
        stdscr.addstr(f"{team_name}: {total_score} points\n")

    stdscr.addstr("\nLast team that clicked: ")
    stdscr.addstr(f"{last_team[0]}\n" if click_registered[0] else "")

    if quiz_round[0] == 1:
        if click_registered[0]:
            stdscr.addstr("\nPress 'Enter' to start a new round.\n")
        else:
            stdscr.addstr("\nRound in progress. Teams can click their mice.\n")
    elif quiz_round[0] == 2:
        stdscr.addstr("\nRound has been completed.")
        stdscr.addstr("\nPress 'Enter' to start the next round or 'P' to replay this round (only if completed).\n")

    # Refresh the screen only when necessary
    stdscr.refresh()

def reset_game(team_scores, click_registered, last_team, quiz_round):
    team_scores.clear()
    click_registered[0] = False
    last_team[0] = None
    quiz_round[0] = 0

def replay_round(click_registered, quiz_round):
    click_registered[0] = False
    quiz_round[0] = 1

def cancel_restart_script():
    os.execl(sys.executable, sys.executable, *sys.argv)

def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(0)  # Non-blocking getch

    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = assign_fun_team_names(devices)

    monitors = []
    team_scores = {name: 0 for name in team_names.values()}
    last_team = [None]
    quiz_round = [0]  # 0: Round not started, 1: Round in progress, 2: Round completed
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

    while True:
        c = stdscr.getch()
        if c == ord('q') or c == ord('Q'):
            break
        elif c == ord('r') or c == ord('R'):  # Reset the game when 'R' key is pressed
            reset_game(team_scores, click_registered, last_team, quiz_round)
            cancel_restart_script()
        elif c == ord('p') or c == ord('P'):  # Replay the current round when 'P' key is pressed
            if quiz_round[0] == 2:  # Only allow replay if the round is completed
                replay_round(click_registered, quiz_round)

        start_time = time.time()
        display_scores(stdscr, last_team, click_registered, team_scores, quiz_round)

        # Check if the 'Enter' key was pressed to start a new round
        if c == 10 and quiz_round[0] == 1 and click_registered[0]:
            click_registered[0] = False
            if last_team[0]:
                team_scores[last_team[0]] += 1
            last_team[0] = None
            quiz_round[0] = 2  # Mark the round as completed

        # Check if the 'Enter' key was pressed to start the next round after completing a round
        if c == 10 and quiz_round[0] == 2:
            quiz_round[0] = 1  # Start the next round
            click_registered[0] = False

        for monitor, name in monitors:
            event = monitor.read_one()
            if event:
                if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
                    last_team[0] = name
                    click_registered[0] = True

        # Refresh the screen only when necessary
        stdscr.refresh()

        # Sleep for a short duration to reduce flickering
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
