#!/usr/bin/env python3

import evdev
import threading
import os
import time
import random
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app, async_mode='threading')  # Use threading as the async mode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def assign_fun_team_names(devices):
    fun_team_names = [
        "Thunderbolts", "Moonwalkers", "Fire Dragons", "Super Strikers", "Fantastic Falcons",
        "Turtle Ninjas", "Cosmic Comets", "Rainbow Unicorns", "Daring Dolphins", "Mighty Martians",
        "Galactic Guardians", "Laser Legends", "Meteor Mavericks", "Quantum Quasars", "Celestial Centurions",
        "Starship Strikers", "Nebula Knights", "Astral Avengers", "Supernova Surfers", "Interstellar Invincibles"
    ]
    random.shuffle(fun_team_names)

    mouse_names = {}
    for i, device in enumerate(devices):
        if i < len(fun_team_names) and "mouse" in device.name.lower():
            mouse_names[device.path] = fun_team_names[i]  # Use device.path instead of device.fn
    return mouse_names

# Add a lock for proper synchronization
global_lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = assign_fun_team_names(devices)

    monitors = []
    global team_scores, quiz_round, click_registered, team_names_input
    team_scores = {name: 0 for name in team_names.values()}
    quiz_round = [1]  # 0: Round not started, 1: Round in progress
    click_registered = [False]  # To track if a click has been registered in the current round
    team_names_input = {}  # To store team names entered by teams

    for device, name in team_names.items():
        try:
            monitor = evdev.InputDevice(device)
            monitors.append((monitor, name))
        except:
            logger.error(f"Failed to open device: {device}")

    if not monitors:
        logger.error("No mice found or failed to open all devices.")
        return

    def monitor_mouse_clicks(monitors, lock):
        last_clicked_team = None

        while True:
            for monitor, name in monitors:
                event = monitor.read_one()
                if event:
                    if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
                        with lock:
                            last_clicked_team = name
                            click_registered[0] = True
                            logger.info(f"Mouse click detected for {name}")

            if last_clicked_team:
                # Use socketio object to emit the event within the Flask-SocketIO context
                socketio.emit('mouse_click', {'team_name': last_clicked_team}, namespace='/')
                last_clicked_team = None

    threading.Thread(target=monitor_mouse_clicks, args=(monitors, global_lock), daemon=True).start()

@socketio.on('start_new_round')
def start_new_round():
    global click_registered, team_names_input

    with global_lock:
        click_registered[0] = False  # Reset click_registered to False for each new round

        # Reset last_team to None for each round
        last_team = None

        # Emit the event to start a new round and prompt teams to enter their names
        emit('new_round_start', namespace='/', broadcast=True)

@socketio.on('team_name_entered')
def team_name_entered(data):
    global team_scores, last_team, team_names_input

    with global_lock:
        # Check if a team clicked in the previous round and update its score
        if last_team is not None:
            if last_team in team_scores:
                team_scores[last_team] += 1
            else:
                logger.warning(f"Received mouse click for an unknown team: {last_team}")

        # Update the team name with the name entered by the team
        team_name = data['team_name']
        team_names_input[request.sid] = team_name

        # Store the team name that clicked for updating scores in the next round
        last_team = team_name

        # Emit the event with updated scores to all connected clients, including all team scores
        emit('update_scores', {'team_scores': team_scores, 'last_team': last_team, 'click_registered': click_registered[0], 'quiz_round': quiz_round[0], 'team_names_input': team_names_input}, namespace='/', broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)