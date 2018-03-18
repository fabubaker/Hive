# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import zmq
import numpy as np
import io

def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype = str(A.dtype),
        shape = A.shape,
    )
    socket.send_json(md, flags|zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)


# zmq port details
PORT = "9999"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % PORT)
topic = "/video"

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 64
rawCapture = io.BytesIO()
FPS = 0.03 # second per image

# allow the camera to warmup
time.sleep(0.1)
seqno=0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="jpeg", use_video_port=True, quality=10):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    data = frame.getvalue()
    print "Sending image %s with size %d ..." % (seqno, len(data))
    socket.send(topic, zmq.SNDMORE)
    socket.send(str(seqno), zmq.SNDMORE)
    socket.send(data)
    seqno += 1
    
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    rawCapture.seek(0)
    time.sleep(FPS)
