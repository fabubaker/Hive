# import the necessary packages
import time
import cv2
import zmq
import numpy

# zmq port details
PORT = "9999"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topic = "/video"
socket.connect("tcp://10.42.0.53:%s" % PORT)
socket.setsockopt(zmq.SUBSCRIBE, topic)

def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = buffer(msg)
    A = numpy.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])

orb = cv2.ORB()

while True:
    topic_recv = socket.recv()
    seqno      = socket.recv()
    image      = recv_array(socket)

    print "Message %s received..." % seqno

    # kp = orb.detect(image,None)
    # kp, des = orb.compute(image, kp)
    # img2 = cv2.drawKeypoints(image,kp,color=(0,255,0), flags=0)
    img2 = image

    # show the frame
    cv2.imshow("Frame", img2)
    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break



                                                        
