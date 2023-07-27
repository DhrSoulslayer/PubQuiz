#!/usr/bin/env python3

import evdev
import threading
import os
import time
import random
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
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
            mouse_names[device.fn] = fun_team_names[i]
    return mouse_names

@app.route('/')
def index():
    return render_template('index.html', team_scores=team_scores, last_team=last_team[0], click_registered=click_registered[0], quiz_round=quiz_round[0])

@socketio.on('connect')
def handle_connect():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = assign_fun_team_names(devices)

    monitors = []
    global team_scores, last_team, quiz_round, click_registered
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

    @socketio.on('start_new_round')
    def start_new_round():
        click_registered[0] = False
        if last_team[0]:
            team_scores[last_team[0]] += 1
        last_team[0] = None

    def monitor_mouse_clicks():
        while True:
            for monitor, name in monitors:
                event = monitor.read_one()
                if event:
                    if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
                        last_team[0] = name
                        click_registered[0] = True

    threading.Thread(target=monitor_mouse_clicks, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)