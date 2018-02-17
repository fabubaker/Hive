# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import zmq
import numpy

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
rawCapture = PiRGBArray(camera, size=(640, 480))
FPS = 10

# allow the camera to warmup
time.sleep(0.1)
seqno=0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    print "Sending image %s ..." % seqno
    image = frame.array
    socket.send(topic, zmq.SNDMORE)
    socket.send(str(seqno), zmq.SNDMORE)
    send_array(socket, image)

    seqno += 1
    
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    time.sleep(float(1/FPS))
