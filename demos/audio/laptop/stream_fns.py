import Vokaturi
import audioop

import numpy as np

# @args data -> byte audio stream. 
def get_amplitude(data):
    return audioop.rms(data, 2)

# @args buf -> byte audio stream.
# @args sockname -> print recv addr for logging.
def vokaturi_analyze(buf, sockname, cur_time):
    sample_rate = 44100
    samples = np.frombuffer(buf, dtype=np.int16)
    buffer_length = len(samples)
    c_buffer = Vokaturi.SampleArrayC(buffer_length)

    if samples.ndim == 1:  # mono
	c_buffer[:] = samples[:] / 32768.0
    else:  # stereo
	c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0

    voice = Vokaturi.Voice (sample_rate, buffer_length)
    voice.fill(buffer_length, c_buffer)

    quality = Vokaturi.Quality()
    emotionProbabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotionProbabilities)

    if quality.valid:
        print "===================================================="
        print cur_time, "Vokaturi results from " + sockname
	print ("Neutral: %.3f" % emotionProbabilities.neutrality)
	print ("Happy: %.3f" % emotionProbabilities.happiness)
	print ("Sad: %.3f" % emotionProbabilities.sadness)
	print ("Angry: %.3f" % emotionProbabilities.anger)
	print ("Fear: %.3f" % emotionProbabilities.fear)
        print "===================================================="

    voice.destroy()
