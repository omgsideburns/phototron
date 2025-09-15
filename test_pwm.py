# pwm_dual_test.py — pigpio hardware PWM on GPIO13 & GPIO19
import time, pigpio

PIN_L = 13
PIN_R = 19
FREQ = 20_000  # 20 kHz


def d(u):
    return max(0, min(1_000_000, u))  # clamp 0..1_000_000


pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError(
        "pigpio daemon not running. Try: sudo systemctl enable --now pigpiod"
    )

try:
    # 1) sanity: both 20% → both 80% → off
    for duty in (200_000, 800_000, 0):
        pi.hardware_PWM(PIN_L, FREQ, d(duty))
        pi.hardware_PWM(PIN_R, FREQ, d(duty))
        print("Both duty:", duty / 10_000, "%")
        time.sleep(1.5)

    # 2) contrast: left high / right low, then swap
    pairs = [(800_000, 200_000), (200_000, 800_000)]
    for _ in range(2):
        for dl, dr in pairs:
            pi.hardware_PWM(PIN_L, FREQ, d(dl))
            pi.hardware_PWM(PIN_R, FREQ, d(dr))
            print(f"L:{dl / 10_000:.0f}%  R:{dr / 10_000:.0f}%")
            time.sleep(1.5)

    # 3) fade: left up while right down, then reverse
    step = 25_000  # smoothness
    duty = 0

    # up
    while duty <= 1_000_000:
        pi.hardware_PWM(PIN_L, FREQ, d(duty))
        pi.hardware_PWM(PIN_R, FREQ, d(1_000_000 - duty))
        time.sleep(0.01)
        duty += step

    # down
    duty = 1_000_000  # reset so we start exactly at max
    while duty >= 0:
        pi.hardware_PWM(PIN_L, FREQ, d(duty))
        pi.hardware_PWM(PIN_R, FREQ, d(1_000_000 - duty))
        time.sleep(0.01)
        duty -= step

except KeyboardInterrupt:
    pass
finally:
    pi.hardware_PWM(PIN_L, 0, 0)
    pi.hardware_PWM(PIN_R, 0, 0)
    pi.stop()
