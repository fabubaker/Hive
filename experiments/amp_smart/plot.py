import matplotlib.pyplot as plt
import numpy as np
import wave
import sys


spf = wave.open(sys.argv[1],'r')

#Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, 'Int16')


plt.figure(1)
plt.title('Signal Wave...')
plt.plot(signal)
plt.show()
