#!/usr/bin/env python3

from threading import Thread
from time import sleep, monotonic

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme

class ButtonPoller(Thread):

    def __init__(self, hand_bot):
        Thread.__init__(self)
        self.button0_pin = 4
        self.button1_pin = 17
        self.hand_bot = hand_bot

        self.button0_last_down = 0
        self.button1_last_down = 0

        GPIO.setup(self.button0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def run(self):

        while True:
            button0 = GPIO.input(self.button0_pin)
            if button0 == 0:
                if monotonic() - self.button0_last_down > .25:
                    self.hand_bot.button_0_pressed()
                    self.button0_last_down = monotonic()

            button1 = GPIO.input(self.button1_pin)
            if button1 == 0:
                if monotonic() - self.button1_last_down > .25:
                    self.hand_bot.button_1_pressed()
                    self.button1_last_down = monotonic()

            sleep(.01)


if __name__ == '__main__':
    d = ButtonPoller()
    d.start()
    while True:
        sleep(1)
