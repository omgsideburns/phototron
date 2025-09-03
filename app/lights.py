# app/lights.py
# simple version: one trigger per event

class StubFlash:
    def on(self):  print("[flash] on (stub)")
    def off(self): print("[flash] off (stub)")
    def pulse(self, ms=100): print(f"[flash] pulse {ms}ms (stub)")

class StubNeoPixel:
    def set_effect(self, name, **kwargs):
        print(f"[neopixel] effect={name} kwargs={kwargs} (stub)")
    def clear(self): print("[neopixel] clear (stub)")

# make the stub devices
flash = StubFlash()
neo   = StubNeoPixel()

# light triggers.. use names that make sense, idiot. 

def idle():
    print("[lights] idle()")
    neo.set_effect("idle_breathe")
    # later: add more light actions here

def countdown():
    print("[lights] countdown()")
    neo.set_effect("countdown", ticks=3, speed="fast")
    flash.pulse(60)
    # later: add more actions

def capture():
    print("[lights] capture()")
    flash.on()
    neo.set_effect("capture_arm")
    # later: add more actions, like turning off at end

def success():
    print("[lights] success()")
    neo.set_effect("success_chase")

def error():
    print("[lights] error()")
    neo.set_effect("error_pulse")