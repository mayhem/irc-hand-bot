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
        self.next_update = None
        self.rainbow_hue_index = 0.0
        self.raised_hue_index = 0.0
        self.raised_increment = None

        self.startup()

    def startup(self):
        for i in range(3):
            self.strip.setPixelColor(0, Color(  0, 180, 5))
            self.strip.setPixelColor(1, Color(  0, 180, 5))
            self.strip.setPixelColor(2, Color(255, 50, 0))
            self.strip.setPixelColor(3, Color(255, 50, 0))
            self.strip.show()
            sleep(.100)

            self.strip.setPixelColor(0, Color(255, 50, 0))
            self.strip.setPixelColor(1, Color(255, 50, 0))
            self.strip.setPixelColor(2, Color(  0, 180, 5))
            self.strip.setPixelColor(3, Color(  0, 180, 5))
            self.strip.show()
            sleep(.100)

    def idle(self, wait_ms=20, iterations=1):
        self.strip.setPixelColor(0, Color(  0, 32, 0))
        self.strip.setPixelColor(1, Color(  0, 32, 0))
        self.strip.setPixelColor(2, Color(64, 18, 0))
        self.strip.setPixelColor(3, Color(64, 18, 0))
        return .1 

    def raised(self):
        hue_begin = 0.0
        hue_end = .03
        steps = 50

        if self.raised_increment is None:
            self.raised_increment = (hue_end - hue_begin) / steps

        self.raised_hue_index += self.raised_increment
        if self.raised_hue_index > hue_end:
            self.raised_hue_index = hue_end - self.raised_increment
            self.raised_increment = -self.raised_increment
        elif self.raised_hue_index < hue_begin:
            self.raised_hue_index = hue_begin - self.raised_increment
            self.raised_increment = -self.raised_increment

        r, g, b = hsv_to_rgb(self.raised_hue_index, 1.0, 1.0)
        for i in range(4):
            self.strip.setPixelColor(i, Color(int(r * 255), int(g * 255), int(b * 255)))

        return .015 

    def rainbow(self):
        r, g, b = hsv_to_rgb(self.rainbow_hue_index, 1.0, 1.0)
        for i in range(4):
            self.strip.setPixelColor(i, Color(int(r * 255), int(g * 255), int(b * 255)))
        self.rainbow_hue_index += .001

        return .01

    def set_pattern(self, pattern):
        if pattern not in ("idle", "raised", "rainbow"):
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

            self.strip.show()
            sleep(delay)


if __name__ == '__main__':
    d = LEDDriver()
    d.start()
    d.set_pattern("raised")
    while True:
        sleep(1)
