import time
import cv2
import zmq
import numpy as np
import io
import cv2
import sys
import time
from datetime import datetime

def timenow():
        return datetime.now().strftime("%I:%M:%S.%f")

NUM = int(sys.argv[1])
BASEPORT = 9000
PORTS = map(lambda x: str(BASEPORT + x), range(0, NUM))
FILE  = "data.pack"
TOPIC = "VIDEO"
context = zmq.Context()
sockets = []

for i, port in enumerate(PORTS):
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)
    sockets.append(socket)

frame = open(FILE, 'rb').read()
count = 1    
while True:
    time.sleep(0.001)

    for i,socket in enumerate(sockets):
        print len(frame)
        socket.send_multipart([TOPIC, frame, timenow()])
        print "Sending data %d" % count
    
    count = count + 1

    if count > 400:
        exit()
        
