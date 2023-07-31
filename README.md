# PubQuiz
Python Scripts for hosting a pubquiz System using mice as game buzzers

The Mouse Quiz Game is a simple interactive game that allows teams to compete by clicking their mice. Each team's score is displayed on the terminal, and the first team that clicked their mouse is shown after each round.
Additionally the terminal can be shown on a webpage using a terminal to webpage package such as ttyd.

## Requirements

- Python 3 (install using `apt install python3`)
- Python 3 Pip (install using `apt install python3-pip`)
- evdev library (install using `pip install evdev`)

## Setting Up
For the scoring system to work correctly the mice ID's need to be configured for the teams.
The setup the mice and team names run the script setup.sh from the commandline as root.
Please make sure that the mice are labeled so you can seperate them from each other.

Setup the team names by executing the setup script:

   ```bash
   ./setup.sh

## How to Play

1. Make sure all the mice you want to use for the game are connected to the computer.

2. Make sure that the setup.sh program has run and the team_config.txt file is present.

3. Run the game by executing the Python script `terminal.py`:

   ```bash
   ./terminal.py
