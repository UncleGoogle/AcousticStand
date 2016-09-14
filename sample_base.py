BITS = 16
RESOLUTION = 2**BITS
VOLTAGE = 3.3
STEP = VOLTAGE/RESOLUTION

with open('sample_base.txt', 'x') as f:
    for i in range(1, RESOLUTION+1):
        f.write("%.6f" % (STEP*i))
        f.write(' ')
