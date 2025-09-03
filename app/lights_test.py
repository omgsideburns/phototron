# test_lights.py
import time
from app.lights import LightController

def main():
    print("Initializing LightController...")
    lights = LightController()

    print("Testing flash burst...")
    lights.flash_burst()
    time.sleep(1)

    print("Testing animate_flash_ring...")
    lights.animate_flash_ring()
    time.sleep(1)

    print("Testing animate_rainbow_cycle...")
    lights.animate_rainbow_cycle(wait=0.005, cycles=1)

    print("Testing animate_breathing...")
    lights.animate_breathing(color=(0, 255, 0), steps=30, pause=0.01, cycles=1)

    print("Testing animate_police_strobe...")
    lights.animate_police_strobe(flashes=3, delay=0.1)

    print("Testing animate_theater_chase...")
    lights.animate_theater_chase(color=(0, 255, 255), delay=0.05, cycles=2)

    print("Testing animate_twinkle...")
    lights.animate_twinkle(color=(255, 0, 255), count=15, delay=0.05)

    print("Testing animate_party_mode...")
    lights.animate_party_mode(flashes=10, delay=0.05)

    print("Testing set_error...")
    lights.set_error()
    time.sleep(1)

    print("Testing set_idle...")
    lights.set_idle()
    time.sleep(1)

    print("Cleaning up GPIO...")
    lights.cleanup()

    print("Done.")

if __name__ == "__main__":
    main()