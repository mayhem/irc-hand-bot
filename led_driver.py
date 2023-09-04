#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 4        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



class LEDDriver:

    def __init__(self):
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.next_update = None

    def update(self):
        pass

    def idle(self, wait_ms=20, iterations=1):
        self.strip.setPixelColor(0, Color(  0, 180, 5))
        self.strip.setPixelColor(1, Color(  0, 180, 5))
        self.strip.setPixelColor(2, Color(255, 50, 0))
        self.strip.setPixelColor(3, Color(255, 50, 0))
        self.strip.show()

    def rainbow(self):

        def wheel(pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

if __name__ == '__main__':
    d = LEDDriver()
#    d.rainbow(iterations=9999999)
    d.idle()
