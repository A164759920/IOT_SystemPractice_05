#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT, initial= GPIO.HIGH)


try:
    while 1:
        GPIO.output(16, GPIO.HIGH)
except KeyboardInterrupt:
    pass
p.stop()
print("Ending")
GPIO.cleanup()
