import sys
import numpy as np

def percentile(n, arr):
        list.sort(arr)
        nper = int(len(arr) * float(5)/100)
        return arr[nper : len(arr) - nper]

f = open(sys.argv[1])
bws = []


for line in f.readlines():
    bw = float(line.split(" ")[0])
    bws.append(bw/1000)
    

avg = percentile(90, bws)
print "%s\t%s\t%s" % (num, np.mean(avg), np.var(avg))
