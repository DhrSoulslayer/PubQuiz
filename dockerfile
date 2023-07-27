# syntax=docker/dockerfile:1

FROM ubuntu22.04
COPY requirements.txt requirements.txt
RUN apt update
RUN apt install -y python3 python3-pip ttyd
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod +x ./terminal.py
RUN ttyd -p 80 ./terminal.py