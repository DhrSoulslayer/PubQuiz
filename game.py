from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Assign fun team names to connected mice
def assign_fun_team_names():
    fun_team_names = [
        "Thunderbolts", "Moonwalkers", "Fire Dragons", "Super Strikers", "Fantastic Falcons",
        "Turtle Ninjas", "Cosmic Comets", "Rainbow Unicorns", "Daring Dolphins", "Mighty Martians"
    ]
    return fun_team_names

# Initialize team scores
team_names = assign_fun_team_names()
team_scores = {name: 0 for name in team_names}
last_team = ""
click_registered = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('mouse_click')
def handle_mouse_click(team_name):
    global click_registered, last_team

    if not click_registered:
        click_registered = True
        last_team = team_name
        team_scores[team_name] += 1
        emit('update_scoreboard', team_scores, broadcast=True)
        emit('update_last_team', last_team, broadcast=True)
        click_registered = False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
