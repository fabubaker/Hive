import select, socket, sys
import wave, pyaudio
import Vokaturi
import numpy as np
import audioop

from datetime import datetime
from stream_fns import *
from ctypes import *

def timenow():
    return datetime.now().strftime("%I:%M:%S.%f") + ":"

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
      return

# ---------------- MAIN --------------- #
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "server_output.wav"
WIDTH = 2

HOST = '0.0.0.0'     # Symbolic name meaning all available interfaces
PORT = 50007           # Arbitrary non-privileged port

# Setup server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((HOST, PORT))
server.listen(5)
inputs = [server]
outputs = []
message_list = {}
audio_handlers = {}
amps     = {}

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary("/usr/lib/x86_64-linux-gnu/libasound.so.2")
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)
# Pyaudio init
Vokaturi.load("./Vokaturi_linux64.so")

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

stream.start_stream()

try:
    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        for s in readable:
	    if s is server:
	        connection, client_addr = s.accept()
                
                print timenow(), 'Connected to', client_addr 
                
                connection.setblocking(0)
	        inputs.append(connection)                

                amps[connection]     = None
            
	    else:
	        data = s.recv(CHUNK)
                if data:
                    #print timenow(), str(len(data)), ' bytes received from ', str(s.getpeername())

                    message_list[s] = data

                    # Get amplitude of stream.
                    amps[s] = get_amplitude(data)
                
                else:
                    # Interpret empty result as closed connection
                    #print timenow(), 'closing', s.getsockname(), 'after reading no data'
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    s.close()                    


#        print amps
        # # Get max amplitude and analyze it.
        max_amp  = -1
        max_conn = -1
        for conn, ampval in amps.items():
            if ampval > max_amp:
                max_amp = ampval
                max_conn = conn

        if max_amp > 0:
            # analyze and playback the highest amplitude stream
            print "Audio stream from %s" % max_conn.getpeername()[0]
            stream.write(data) # Output audio
            vokaturi_analyze(message_list[max_conn], max_conn.getpeername()[0], timenow())
    
except KeyboardInterrupt:
    # Cleanup
    map(lambda s: s.close(), inputs)
    stream.stop_stream()
    stream.close()
    p.terminate()
    server.close()

