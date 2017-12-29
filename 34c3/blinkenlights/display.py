import pygame
import struct

WIDTH = 16
HEIGHT = 16
SCALE = 16

pygame.init()
win = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE))
pix = pygame.PixelArray(win)

f = open('out.bin', 'rb')

while True:
    for y in range(16):
        for x in range(16):
            r,g,b = struct.unpack('<BBB', f.read(3))
            pygame.draw.rect(win, (r, g, b),(x*SCALE, y*SCALE, SCALE, SCALE))
    pygame.display.update()
