import time
import random
import board
import neopixel
import RPi.GPIO as GPIO
from config import LIGHTS_CONFIG

class LightController:
    def __init__(self):
        self.flash_enabled = LIGHTS_CONFIG.get("enable_flash", False)
        self.flash_pin = LIGHTS_CONFIG.get("flash_pin", 17)
        self.flash_mode = LIGHTS_CONFIG.get("flash_mode", "flash")

        self.pixel_enabled = LIGHTS_CONFIG.get("enable_neopixel", False)
        self.pixel_pin = LIGHTS_CONFIG.get("neopixel_pin", 18)
        self.pixel_count = LIGHTS_CONFIG.get("neopixel_count", 16)
        self.pixel_brightness = LIGHTS_CONFIG.get("neopixel_brightness", 0.5)

        if self.flash_enabled:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.flash_pin, GPIO.OUT)

        if self.pixel_enabled:
            self.pixels = neopixel.NeoPixel(
                getattr(board, f"D{self.pixel_pin}"),
                self.pixel_count,
                brightness=self.pixel_brightness,
                auto_write=False
            )

    def flash_on(self):
        if self.flash_enabled:
            GPIO.output(self.flash_pin, GPIO.HIGH)

    def flash_off(self):
        if self.flash_enabled:
            GPIO.output(self.flash_pin, GPIO.LOW)

    def flash_burst(self, duration=0.25):
        self.flash_on()
        time.sleep(duration)
        self.flash_off()

    def animate_flash_ring(self):
        if self.pixel_enabled:
            for i in range(self.pixel_count):
                self.pixels[i] = (255, 255, 255)
            self.pixels.show()
            time.sleep(0.1)
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

    def animate_rainbow_cycle(self, wait=0.01, cycles=1):
        if self.pixel_enabled:
            def wheel(pos):
                if pos < 85:
                    return (pos * 3, 255 - pos * 3, 0)
                elif pos < 170:
                    pos -= 85
                    return (255 - pos * 3, 0, pos * 3)
                else:
                    pos -= 170
                    return (0, pos * 3, 255 - pos * 3)

            for _ in range(cycles):
                for j in range(256):
                    for i in range(self.pixel_count):
                        pixel_index = (i * 256 // self.pixel_count + j) & 255
                        self.pixels[i] = wheel(pixel_index)
                    self.pixels.show()
                    time.sleep(wait)

    def animate_breathing(self, color=(0, 0, 255), steps=20, pause=0.03, cycles=2):
        if self.pixel_enabled:
            for _ in range(cycles):
                for i in range(steps):
                    self.pixels.brightness = i / steps
                    self.pixels.fill(color)
                    self.pixels.show()
                    time.sleep(pause)
                for i in range(steps, 0, -1):
                    self.pixels.brightness = i / steps
                    self.pixels.fill(color)
                    self.pixels.show()
                    time.sleep(pause)
            self.pixels.brightness = self.pixel_brightness

    def animate_police_strobe(self, flashes=5, delay=0.1):
        if self.pixel_enabled:
            for _ in range(flashes):
                self.pixels.fill((255, 0, 0))
                self.pixels.show()
                time.sleep(delay)
                self.pixels.fill((255, 255, 0))
                self.pixels.show()
                time.sleep(delay)
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

    def animate_theater_chase(self, color=(127, 127, 127), delay=0.05, cycles=3):
        if self.pixel_enabled:
            for _ in range(cycles):
                for q in range(3):
                    for i in range(0, self.pixel_count, 3):
                        self.pixels[i + q % 3] = color
                    self.pixels.show()
                    time.sleep(delay)
                    for i in range(0, self.pixel_count, 3):
                        self.pixels[i + q % 3] = (0, 0, 0)

    def animate_twinkle(self, color=(255, 255, 255), count=10, delay=0.05):
        if self.pixel_enabled:
            for _ in range(count):
                i = random.randint(0, self.pixel_count - 1)
                self.pixels[i] = color
                self.pixels.show()
                time.sleep(delay)
                self.pixels[i] = (0, 0, 0)
                self.pixels.show()

    def animate_party_mode(self, flashes=20, delay=0.05):
        if self.pixel_enabled:
            for _ in range(flashes):
                for i in range(self.pixel_count):
                    self.pixels[i] = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    )
                self.pixels.show()
                time.sleep(delay)
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

    def set_error(self):
        if self.pixel_enabled:
            self.pixels.fill((255, 0, 0))
            self.pixels.show()

    def set_idle(self):
        if self.pixel_enabled:
            self.pixels.fill((0, 0, 50))
            self.pixels.show()

    def cleanup(self):
        if self.flash_enabled:
            GPIO.cleanup()