#!/usr/bin/env python

import sys
import wave, pyaudio
import numpy as np
import audioop
import zmq
import time
import math
import scipy.io.wavfile
import operator
from datetime import datetime

def percentile(n, arr):
        list.sort(arr)
        nper = int(len(arr) * float(5)/100)
        return arr[nper : len(arr) - nper]

def timenow():
        return datetime.now()

def get_amplitude(data):
    return audioop.rms(data, 2)

TOPIC = "AUDIO"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')

NUM = int(sys.argv[1]) # number of subscribers
BASEPORT = 9000
BASEIP   = "127.0.0.1:"

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

ip = map(lambda x: BASEIP + str(BASEPORT + x), range(0, 1))[0]
sockets = []

for i in range(NUM):
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
            amps = {}
            slab = {}
            times = {}
            total = {}
            readable, writable, exceptional = zmq.select(sockets, [], [])
            for socket in readable:                
                topic = socket.recv()
                data  = socket.recv()
                stamp = socket.recv()
                timestamp = timenow() - datetime.strptime(stamp, "%I:%M:%S.%f")

                times[socket] = timestamp.microseconds/float(1000)
                amps[socket] = 20 * math.log10(get_amplitude(data) / float(2**15))
                slab[socket] = data
                total[socket] = len(topic) + len(data) + len(stamp)

            maxkey = max(amps.iteritems(), key=operator.itemgetter(1))[0]
            f.write("%s \t %f \n" % (count, times[maxkey]))
            avg.append(times[maxkey])

            print ">>>" + str(count)
            count += 1

            
except KeyboardInterrupt:
        avg = percentile(90, avg)
        f.write("%f \t %f \n" % (np.mean(avg), np.var(avg)))
        f.close()
    
