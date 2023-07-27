from flask import Flask, render_template
import evdev
import time
import random

app = Flask(__name__)

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

def monitor_mouse_clicks(device, team_name, team_scores, last_team, quiz_round, click_registered):
    for event in device.read_loop():
        if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
            last_team[0] = team_name
            click_registered[0] = True

@app.route('/')
def index():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    team_names = assign_fun_team_names(devices)

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
        return "No mice found or failed to open all devices."

    while True:
        time.sleep(0.05)

        for monitor, name in monitors:
            event = monitor.read_one()
            if event:
                if quiz_round[0] == 1 and not click_registered[0] and event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT and event.value == 1:
                    last_team[0] = name
                    click_registered[0] = True
                    if last_team[0]:
                        team_scores[last_team[0]] += 1
                    last_team[0] = None
                    click_registered[0] = False

        return render_template('index.html', team_scores=team_scores, last_team=last_team, quiz_round=quiz_round, click_registered=click_registered)

if __name__ == "__main__":
    app.run()
