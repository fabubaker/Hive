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

str_ip = map(lambda x: BASEIP + str(BASEPORT + x), range(0, 1))
sockets = []

for ip in str_ip:
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s" % ip)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    sockets.append(socket)

time.sleep(1)
count = 1

f = open("results%d.dat" % NUM, "w+")
f.write("time \t latency\n")

avg = []

try:
    while True:
        times = {}
        readable, writable, exceptional = zmq.select(sockets, [], [])
        for socket in readable:
            topic_recv = socket.recv()
            data = socket.recv()
            stamp = socket.recv()
            timestamp = timenow() - datetime.strptime(stamp, "%I:%M:%S.%f")
            
            times[socket] = timestamp.microseconds/float(1000)

        f.write("%s \t %f \n" % (count, times[times.keys()[0]]))
        avg.append(times[times.keys()[0]])

        print ">>>" + str(count)
        count += 1

except KeyboardInterrupt:
    avg = percentile(90, avg)
    f.write("%f \t %f\n" % (np.mean(avg), np.var(avg)))
    f.close()
