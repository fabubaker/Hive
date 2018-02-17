import socket
import pyaudio
from datetime import datetime
from motion import *

def timenow():
        return datetime.datetime.now().strftime("%I:%M:%S.%f") + ":"

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

HOST = '10.42.0.83'    # The remote host
PORT = 50007             # The same port as used by the server

p = pyaudio.PyAudio()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

MOTION = False
last_detected = datetime.datetime.now()

def callback(in_data, frame_count, time_info, status):
    if MOTION:
        s.send(in_data)
    return (None, pyaudio.paContinue)

# start Recording
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)

stream1 = getStreamImage(True)
while True:
    stream2 = getStreamImage(True)
    
    if checkForMotion(stream1, stream2):
        last_detected = datetime.datetime.now()
        print("\n*_ %s >Motion detected..." % (timenow()))
        MOTION = True
    else:
        delta = datetime.datetime.now() - last_detected
        print("\n*_ %s >No motion detected..." % (timenow()))
        if delta.total_seconds() >= 15.00:
            MOTION = False
            print("\n*_>No motion detected for 15 seconds, stopping stream...")

    stream1=stream2


