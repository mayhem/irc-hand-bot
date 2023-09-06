#!/usr/bin/env python3
from colorsys import hsv_to_rgb
from threading import Thread
from time import sleep
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 4        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



class LEDDriver(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.strip.setBrightness(255)
        self.next_update = None
        self.rainbow_hue_index = 0.0
        self.raised_hue_index = 0.0
        self.raised_increment = None
        self.acked_hue_index = 0.0
        self.acked_increment = None

        self.startup()

    def startup(self):
        for i in range(5):
            self.strip.setPixelColor(0, Color(255, 60, 0))
            self.strip.setPixelColor(1, Color(255, 60, 0))
            self.strip.setPixelColor(2, Color(255, 0, 255))
            self.strip.setPixelColor(3, Color(255, 0, 255))
            self.strip.show()
            sleep(.2)

            self.strip.setPixelColor(0, Color(255, 0, 255))
            self.strip.setPixelColor(1, Color(255, 0, 255))
            self.strip.setPixelColor(2, Color(255, 60, 0))
            self.strip.setPixelColor(3, Color(255, 60, 0))
            self.strip.show()
            sleep(.2)

    def idle(self, wait_ms=20, iterations=1):
        self.strip.setBrightness(255)
        self.strip.setPixelColor(2, Color(  0, 32, 0))
        self.strip.setPixelColor(3, Color(  0, 32, 0))
        self.strip.setPixelColor(0, Color(64, 18, 0))
        self.strip.setPixelColor(1, Color(64, 18, 0))
        return .1 

    def short_dim(self):
        increment = 5
        brightness = 255
        while brightness > 64:
            brightness = max(0, brightness - increment)
            self.strip.setBrightness(brightness)
            self.strip.show()
            sleep(.005)
        while brightness < 255:
            brightness = min(255, brightness + increment)
            self.strip.setBrightness(brightness)
            self.strip.show()
            sleep(.005)


    def raised(self):
        hue_begin = 0.0
        hue_end = .03
        hue_jitter = .01
        steps = 50

        self.strip.setBrightness(255)
        if self.raised_increment is None:
            self.raised_increment = (hue_end - hue_begin) / steps

        self.raised_hue_index += self.raised_increment
        if self.raised_hue_index > hue_end:
            self.raised_hue_index = hue_end - self.raised_increment
            self.raised_increment = -self.raised_increment
        elif self.raised_hue_index < hue_begin:
            self.raised_hue_index = hue_begin - self.raised_increment
            self.raised_increment = -self.raised_increment

        order = (0, 2, 1, 3)
        for i in range(4):
            r, g, b = hsv_to_rgb(self.raised_hue_index + (hue_jitter * order[i]), 1.0, 1.0)
            self.strip.setPixelColor(i, Color(int(r * 255), int(g * 255), int(b * 255)))

        return .01 

    def acked(self):
        hue_begin = 0.60
        hue_end = 0.75
        hue_jitter = .03
        steps = 100

        self.strip.setBrightness(96)
        if self.acked_increment is None:
            self.acked_increment = (hue_end - hue_begin) / steps

        self.acked_hue_index += self.acked_increment
        if self.acked_hue_index > hue_end:
            self.acked_hue_index = hue_end - self.acked_increment
            self.acked_increment = -self.acked_increment
        elif self.acked_hue_index < hue_begin:
            self.acked_hue_index = hue_begin - self.acked_increment
            self.acked_increment = -self.acked_increment

        order = (0, 2, 1, 3)
        for i in range(4):
            r, g, b = hsv_to_rgb(self.acked_hue_index + (hue_jitter * order[i]), 1.0, 1.0)
            self.strip.setPixelColor(i, Color(int(r * 255), int(g * 255), int(b * 255)))

        return .02 

    def rainbow(self):
        self.strip.setBrightness(128)
        r, g, b = hsv_to_rgb(self.rainbow_hue_index, 1.0, 1.0)
        for i in range(4):
            self.strip.setPixelColor(i, Color(int(r * 255), int(g * 255), int(b * 255)))
        self.rainbow_hue_index += .001

        return .01

    def set_pattern(self, pattern):
        if pattern not in ("idle", "raised", "rainbow", "acked"):
            return
        self.pattern = pattern

    def run(self):

        self.pattern = "idle"
        while True:
            if self.pattern == "idle":
                delay = self.idle()
            elif self.pattern == "raised":
                delay = self.raised()
            elif self.pattern == "rainbow":
                delay = self.rainbow()
            elif self.pattern == "acked":
                delay = self.acked()

            self.strip.show()
            sleep(delay)


if __name__ == '__main__':
    d = LEDDriver()
    d.start()
    d.set_pattern("acked")
    while True:
        sleep(1)
