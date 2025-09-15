# app/lights_test_modes.py
import time
import lights

lights.init()
try:
    lights.mode_attract()
    time.sleep(1.0)
    lights.mode_pre_capture()
    time.sleep(1.0)
    lights.mode_capture()
    time.sleep(0.6)
    lights.mode_post_capture()
    time.sleep(1.0)
finally:
    lights.shutdown()
