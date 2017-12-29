#import pygame
import struct

WIDTH = 16
HEIGHT = 16

def readsamples():
    curpos = 0
    with open('data.csv.bak') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if '#' in line:
                continue
            parts = line.split(',')
            delay = int(parts[0])
            value = int(parts[1])

            yield delay-curpos, value
            curpos = delay

def bitstream():
    for dt, val in readsamples():
        if val == 1:
            if dt > 1000:
                yield (True, None)
        else:
            if dt < 10:
                yield (None, 0)
            elif dt > 20:
                yield (None, 1)
            else:
                raise 'wut'

def lines():
    data = []
    for line, bit in bitstream():
        if line == True:
            yield data[:]
            data = []
        else:
            data.append(bit)

def frames():
    for line in lines():
        if len(line) != 6144:
            print('weird length...')
            continue

        frame = []
        for i in range(0, 6144, 24):
            pixel = line[i:i+24]
            g, r, b = pixel[:8], pixel[8:16], pixel[16:]
            r = int(''.join(str(rr) for rr in r[::-1]), 2)
            g = int(''.join(str(rr) for rr in g[::-1]), 2)
            b = int(''.join(str(rr) for rr in b[::-1]), 2)
            frame.append((r, g, b))
        yield frame

out = open('out.bin', 'wb')

frameout = [0 for _ in range(256)]
for fnum, frame in enumerate(frames()):
    print(fnum)
    invert = False
    for x in range(WIDTH):
        for y in range(HEIGHT):
            invert = not invert
            x2 = x
            if invert:
                x2 = 15 - x
            y2 = 15 - y
            pixel = frame[y * WIDTH + x2]
            frameout[y * 16 + x] = pixel

    for y in range(HEIGHT):
        for x in range(WIDTH):
            dat = struct.pack('<BBB', *frameout[y * 16 + x])
            out.write(dat)
