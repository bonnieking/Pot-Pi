#!/usr/bin/env python
import os
import pygame
import sys
import time

from pygame.locals import *

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'



import sys, random, pygame
from pygame.locals import *

pygame.init()

w = 640
h = 480

screen = pygame.display.set_mode((w,h))
morphingShape = pygame.Surface((20,20))
morphingShape.fill((255, 137, 0)) #random colour for testing
morphingRect = morphingShape.get_rect()

# clock object that will be used to make the animation
# have the same speed on all machines regardless
# of the actual machine speed.
clock = pygame.time.Clock()

def ShapeSizeChange(shape, x, screen):
    w = shape.get_width()
    h = shape.get_height()
    shape = pygame.transform.smoothscale(shape, (x, x))
    shape.fill((255, 137, 0))
    rect = shape.get_rect()
    screen.blit(shape, rect)
    return shape

x = 10 

while True:
    screen.fill( (0,0,0) )
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # we'll assume that the pot didn't move
    trim_pot_changed = False

    # read the analog pin
    trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    # how much has it changed since the last read?
    pot_adjust = abs(trim_pot - last_read)

    if DEBUG:
        print "trim_pot:", trim_pot
        print "pot_adjust:", pot_adjust
        print "last_read", last_read

    if ( pot_adjust > tolerance ):
           trim_pot_changed = True

    if ( trim_pot_changed ):
            x = int(trim_pot)
            morphingShape = ShapeSizeChange(morphingShape, x, screen)
            pygame.display.update()

    # save the potentiometer reading for the next loop
    last_read = trim_pot
