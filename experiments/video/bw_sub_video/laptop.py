# import the necessary packages
import time
import cv2
import zmq
import numpy as np
import io
import sys
from datetime import datetime

def percentile(n, arr):
    list.sort(arr)
    nper = int(len(arr) * float(5)/100)
    return arr[nper: len(arr) - nper]


def timenow():
    return datetime.now()


def get_amplitude(data):
    return audioop.rms(data, 2)


TOPIC = "VIDEO"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')

NUM = int(sys.argv[1])
BASEPORT = 9000
BASEIP = "127.0.0.1:"

ip = map(lambda x: BASEIP + str(BASEPORT + x), range(0, 1))[0]
sockets = []

for i in range(NUM):
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s" % ip)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    sockets.append(socket)

time.sleep(1)
count = 1

avg = []

while True:
    times = {}
    readable, writable, exceptional = zmq.select(sockets, [], [])
    for socket in readable:
        topic_recv = socket.recv()
        data = socket.recv()
        stamp = socket.recv()
        timestamp = timenow() - datetime.strptime(stamp, "%I:%M:%S.%f")
            
        times[socket] = timestamp.microseconds/float(1000)

    avg.append(times[times.keys()[0]])

    print ">>>" + str(count)
    count += 1
