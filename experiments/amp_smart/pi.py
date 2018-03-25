#!/usr/bin/env python

import sys
import socket
import pyaudio
import wave
import zmq
import time
from datetime import datetime

PORTS = ["9991", "9992", "9993", "9994"]
FILES = ["pi_1.wav", "pi_2.wav", "pi_3.wav", "pi_4.wav"]
TOPIC = "AUDIO"
context = zmq.Context()

sockets = []
wfs = []

for i, port in enumerate(PORTS):
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)
    sockets.append(socket)
    wf = wave.open(FILES[i], 'rb')
    wfs.append(wf)
    
CHUNK = 8192/2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

time.sleep(0.1)
framecount = 1
while True:
    framecount += 1
    for i,socket in enumerate(sockets):
        data = wfs[i].readframes(CHUNK)

        if len(data) > 0:
            print "Sending data %d" % framecount
            socket.send(TOPIC, zmq.SNDMORE)
            socket.send(data)
        




