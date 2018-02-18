# import the necessary packages
import time
import cv2
import zmq
import numpy as np


# zmq port details
PORT = "9999"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topic = "/video"
#socket.connect("tcp://10.42.0.53:%s" % PORT) ## nsl-shared ip
socket.connect("tcp://192.168.1.139:%s" % PORT) ## hive ip
socket.setsockopt(zmq.SUBSCRIBE, topic)

def convertToRGB(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def detect_faces(f_cascade, colored_img, scaleFactor = 1.1):
    img_copy = np.copy(colored_img)
    #convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    
    #let's detect multiscale (some images may be closer to camera than others) images
    faces = f_cascade.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=5);

    print('Faces found: %d' % len(faces))
    
    #go over list of faces and draw them as rectangles on original colored img
    for (x, y, w, h) in faces:
        cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
    return img_copy

def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = buffer(msg)
    print len(buf)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])

if __name__ == "__main__":
    lbp_face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')
    
    while True:
        topic_recv = socket.recv()
        seqno      = socket.recv()
        image      = recv_array(socket)

        print "Message %s received..." % seqno

        faces_detected_img = detect_faces(lbp_face_cascade, image)
        
        # show the frame
        cv2.imshow("Frame", faces_detected_img)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break



                                                        
