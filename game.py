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

@socketio.on('connect')
def handle_connect():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = assign_fun_team_names(devices)

    monitors = []
    global team_scores, last_team, quiz_round, click_registered
    team_scores = {name: 0 for name in team_names.values()}
    last_team = [None]  # Initialize last_team as None
    quiz_round = [1]  # 0: Round not started, 1: Round in progress
    click_registered = [False]  # To track if a click has been registered in the current round

    for device, name in team_names.items():
        try:
            monitor = evdev.InputDevice(device)
            monitors.append((monitor, name))
        except:
            logger.error(f"Failed to open device: {device}")

    if not monitors:
        logger.error("No mice found or failed to open all devices.")
        return

    @socketio.on('start_new_round')
    def start_new_round():
        global last_team, click_registered

        click_registered[0] = False
        if last_team[0] is not None and last_team[0] in team_scores:
            team_scores[last_team[0]] += 1
            emit('team_click', {'team_name': last_team[0]}, broadcast=True)  # Emit the team_click event to all connected clients

        last_team[0] = None  # Reset last_team to None for each round
        emit('update_scores', {'team_scores': team_scores, 'last_team': last_team[0], 'click_registered': click_registered[0], 'quiz_round': quiz_round[0]}, broadcast=True)  # Emit the event with updated scores to all connected clients

    def monitor_mouse_clicks(monitors):
        last_clicked_team = None

        while True:
            for monitor, name in monitors:
                event = monitor.read_one()
                if event:
                    if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
                        last_clicked_team = name
                        click_registered[0] = True
                        logger.info(f"Mouse click detected for {name}")

            if last_clicked_team:
                emit('mouse_click', {'team_name': last_clicked_team}, namespace='/')  # Emit the mouse click event to all connected clients
                last_clicked_team = None

    threading.Thread(target=monitor_mouse_clicks, args=(monitors,), daemon=True).start()

@app.route('/')
def index():
    global team_scores, last_team, click_registered, quiz_round
    return render_template('index.html', team_scores=team_scores, last_team=last_team[0], click_registered=click_registered[0], quiz_round=quiz_round[0])

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)