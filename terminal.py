#!/usr/bin/env python3

import evdev
import threading
import os
import curses
import time
import sys
import random
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

def assign_fun_team_names(devices):
    fun_team_names = [
        "Thunderbolts", "Moonwalkers", "Fire Dragons", "Super Strikers", "Fantastic Falcons",
        "Turtle Ninjas", "Cosmic Comets", "Rainbow Unicorns", "Daring Dolphins", "Mighty Martians"
    ]
    random.shuffle(fun_team_names)

    mouse_names = {}
    for i, device in enumerate(devices):
        if i < len(fun_team_names) and "mouse" in device.name.lower():
            mouse_names[device.path] = fun_team_names[i]
    return mouse_names

def monitor_mouse_clicks(device_path, team_name, team_scores, last_team, quiz_round, click_registered):
    device = evdev.InputDevice(device_path)
    for event in device.read_loop():
        if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
            last_team[0] = team_name
            click_registered[0] = True
            emit('mouse_click', {'team_name': team_name}, namespace='/')  # Emit the mouse click event to all connected clients
            break

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
            stdscr.addstr("\nRound in progress. Waiting for a team to click first.\n")

    # Refresh the screen only when necessary
    stdscr.refresh()

def reset_game(team_scores, click_registered, last_team, quiz_round):
    team_scores.clear()
    click_registered[0] = False
    last_team[0] = None
    quiz_round[0] = 0

def cancel_restart_script():
    os.execl(sys.executable, sys.executable, *sys.argv)

@socketio.on('start_new_round')
def start_new_round():
    global quiz_round, click_registered
    if quiz_round[0] == 0:
        quiz_round[0] = 1
        click_registered[0] = False
        emit('new_round_start', broadcast=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    curses.wrapper(main)
    #socketio.run(app, host='0.0.0.0', port=5000)
