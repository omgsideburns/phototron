import time
import RPi.GPIO as GPIO
import board
import neopixel

# === Pin setup ===
FLASH_L_PIN = 13   # change to whatever GPIO you wired
FLASH_R_PIN = 19   # change to whatever GPIO you wired
NEO_PIN     = board.D18  # typical NeoPixel pin, check yours

NUM_PIXELS = 16   # adjust to match your ring
BRIGHTNESS = 0.2  # 0.0 - 1.0

# === Setup GPIO ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLASH_L_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(FLASH_R_PIN, GPIO.OUT, initial=GPIO.LOW)

# === Setup NeoPixel ===
pixels = neopixel.NeoPixel(NEO_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=True)

def test_flashes():
    print("Testing flash LEDs...")
    GPIO.output(FLASH_L_PIN, GPIO.HIGH)
    print("Left flash ON")
    time.sleep(1)
    GPIO.output(FLASH_L_PIN, GPIO.LOW)
    print("Left flash OFF")

    GPIO.output(FLASH_R_PIN, GPIO.HIGH)
    print("Right flash ON")
    time.sleep(1)
    GPIO.output(FLASH_R_PIN, GPIO.LOW)
    print("Right flash OFF")

def test_ring():
    print("Testing NeoPixel ring...")
    # red
    pixels.fill((255, 0, 0))
    time.sleep(1)
    # green
    pixels.fill((0, 255, 0))
    time.sleep(1)
    # blue
    pixels.fill((0, 0, 255))
    time.sleep(1)
    # off
    pixels.fill((0, 0, 0))
    print("Ring OFF")

try:
    while True:
        test_flashes()
        test_ring()
        time.sleep(2)

except KeyboardInterrupt:
    print("Cleaning up...")
    pixels.fill((0, 0, 0))
    GPIO.cleanup()