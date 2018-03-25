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

def get_amplitude(data):
    return audioop.rms(data, 2)

TOPIC = "AUDIO"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')

PORT = "9999"
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

str_ip = ["127.0.0.1:9991", "127.0.0.1:9992", "127.0.0.1:9993", "127.0.0.1:9994"]
sockets = []

for ip in str_ip:
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s" % ip)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    sockets.append(socket)

time.sleep(1)
count = 1

f = open("results.dat", "w+")
f.write("time \t pi1 \t pi2 \t pi3 \t pi4 \t hive \n")

final = ""
try:
        while True:
            amps = {}
            slab = {}
            readable, writable, exceptional = zmq.select(sockets, [], [])
            for socket in readable:                
                topic = socket.recv()
                data  = socket.recv()
                print "-----"
                print get_amplitude(data)

                amps[socket] = 20 * math.log10(get_amplitude(data) / float(2**15))
                slab[socket] = data
                
            print "============="
            print ">>>>>" + str(count)
            print amps.values()
            maxamp = max(amps.values())
            print maxamp
            
            if len(amps.values()) == 4:
                f.write("%s \t %f \t %f \t %f \t %f \t %f\n" % (count * 0.1, amps.values()[0], amps.values()[1], amps.values()[2], amps.values()[3], max(amps.values())))
                maxkey = max(amps.iteritems(), key=operator.itemgetter(1))[0]
                final += slab[maxkey] 
            print "============="

            count += 1
            
except KeyboardInterrupt:
    final = np.fromstring(final, dtype=np.int32)
    scipy.io.wavfile.write('final.wav', 44100, final)
    f.close()

