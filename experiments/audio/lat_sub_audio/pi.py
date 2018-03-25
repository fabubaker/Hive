#!/usr/bin/env python

import sys
import socket
import pyaudio
import wave
import zmq
import time
from datetime import datetime

def timenow():
        return datetime.now().strftime("%I:%M:%S.%f")

NUM = 1
BASEPORT = 9000
PORTS = map(lambda x: str(BASEPORT + x), range(0, NUM))
FILE  = "sound.wav"
TOPIC = "AUDIO"
context = zmq.Context()

sockets = []
wf = None

for i, port in enumerate(PORTS):
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)
    sockets.append(socket)

wf = wave.open(FILE, 'rb')
    
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

framecount = 1
while True:
    time.sleep(0.001)
    framecount += 1
    data = wf.readframes(CHUNK)

    for i,socket in enumerate(sockets):
        if len(data) > 0:        
            socket.send_multipart([TOPIC, data, timenow()])
            print "Sending data %d" % framecount
        




