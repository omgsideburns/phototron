# app/lights.py
# Two MOSFET strips on GPIO13 and GPIO19, pigpio DMA PWM (independent channels)

import time
import threading
import random

try:
    import pigpio  # type: ignore

    _HAVE_PIGPIO = True
except Exception:
    pigpio = None  # type: ignore
    _HAVE_PIGPIO = False

PIN_L = 13
PIN_R = 19

# Mode levels (0.0..1.0)
ATTRACT_LEVEL = 0.2
PRE_LEVEL = 0.50
CAPTURE_LEVEL = 1.00

# PWM (DMA) config - keep freq*range <800_000 (pigpio DMA base)
# eg 5khz * 160 = 800k
PWM_FREQ = 5000 
PWM_RANGE = 160 
GAMMA = 1.2  # perceptual smoothing for low levels, set to 1.0 to disable

_pi = None
_pwm_ready = False
_anim_thread: threading.Thread | None = None
_anim_stop = threading.Event()


def _clamp(x: float) -> float:
    return 0.0 if x <= 0 else 1.0 if x >= 1 else x


def _dc(level: float) -> int:
    level = 0.0 if level <= 0 else 1.0 if level >= 1 else level
    if GAMMA and GAMMA != 1.0:
        level = level**GAMMA
    return int(level * PWM_RANGE)


def _ensure() -> bool:
    """Ensure pigpio is available and connected exactly once."""
    global _pi
    if not _HAVE_PIGPIO:
        if not hasattr(_ensure, "_warned"):
            print("[lights] pigpio not installed; lights disabled")
            _ensure._warned = True  # type: ignore[attr-defined]
        return False
    if _pi is None:
        _pi = pigpio.pi()
        if not _pi.connected:
            print("[lights] pigpiod not running (sudo systemctl enable --now pigpiod)")
            _pi = None
            return False
    return True


def _ensure_pwm_setup() -> bool:
    """Configure per-pin DMA PWM once."""
    global _pwm_ready
    if not _ensure():
        return False
    if not _pwm_ready:
        _pi.set_PWM_frequency(PIN_L, PWM_FREQ)
        _pi.set_PWM_frequency(PIN_R, PWM_FREQ)
        _pi.set_PWM_range(PIN_L, PWM_RANGE)
        _pi.set_PWM_range(PIN_R, PWM_RANGE)
        _pwm_ready = True
    return True


def init():
    if not _ensure_pwm_setup():
        return
    # sanity: see what pigpio set
    for pin in (PIN_L, PIN_R):
        print(
            f"[lights] pin{pin} freq={_pi.get_PWM_frequency(pin)} range={_pi.get_PWM_range(pin)}"
        )
    _pi.set_PWM_dutycycle(PIN_L, 0)
    _pi.set_PWM_dutycycle(PIN_R, 0)


def shutdown():
    attract_stop()
    if _pi:
        _pi.set_PWM_dutycycle(PIN_L, 0)
        _pi.set_PWM_dutycycle(PIN_R, 0)
        _pi.stop()


def set_left(level: float):
    if not _ensure_pwm_setup():
        return
    _pi.set_PWM_dutycycle(PIN_L, _dc(level))


def set_right(level: float):
    if not _ensure_pwm_setup():
        return
    _pi.set_PWM_dutycycle(PIN_R, _dc(level))


def set_both(level: float):
    if not _ensure_pwm_setup():
        return
    dc = _dc(level)
    _pi.set_PWM_dutycycle(PIN_L, dc)
    _pi.set_PWM_dutycycle(PIN_R, dc)


def fade_both(start: float, end: float, duration: float = 0.25, steps: int = 30):
    if steps < 1 or duration <= 0:
        set_both(end)
        return
    step = (end - start) / steps
    dt = duration / steps
    level = start
    for _ in range(steps):
        set_both(level)
        time.sleep(dt)
        level += step
    set_both(end)


# === Attract animation ===
def _attract_loop():
    if not _ensure_pwm_setup():
        return
    set_left(0.0)
    set_right(0.0)
    level = ATTRACT_LEVEL
    try:
        while not _anim_stop.is_set():
            # dominant dark time
            t_end = time.time() + random.uniform(1.2, 2.5)
            while not _anim_stop.is_set() and time.time() < t_end:
                time.sleep(0.02)
            if _anim_stop.is_set():
                break

            if random.random() < 0.6:
                # opposite fade ping-pong
                steps, half = 30, 0.6
                dt = half / steps
                for i in range(steps):
                    if _anim_stop.is_set():
                        break
                    a = i / (steps - 1)
                    set_left(level * a)
                    set_right(level * (1.0 - a))
                    time.sleep(dt)
                for i in range(steps):
                    if _anim_stop.is_set():
                        break
                    a = i / (steps - 1)
                    set_left(level * (1.0 - a))
                    set_right(level * a)
                    time.sleep(dt)
            else:
                # low-intensity ping-pong strobe
                pulses, on, gap = random.randint(3, 6), 0.045, 0.05
                for _ in range(pulses):
                    if _anim_stop.is_set():
                        break
                    set_left(level * 0.9)
                    set_right(0.0)
                    time.sleep(on)
                    set_left(0.0)
                    set_right(0.0)
                    time.sleep(gap)
                    set_left(0.0)
                    set_right(level * 0.9)
                    time.sleep(on)
                    set_left(0.0)
                    set_right(0.0)
                    time.sleep(gap)

            if _anim_stop.is_set():
                break
            fade_both(level * 0.2, 0.0, duration=0.4, steps=24)
            time.sleep(0.04)
    finally:
        set_left(0.0)
        set_right(0.0)


def attract_start():
    """Start attract animations (safe to call repeatedly)."""
    global _anim_thread
    if _anim_thread and _anim_thread.is_alive():
        return
    _anim_stop.clear()
    _anim_thread = threading.Thread(target=_attract_loop, daemon=True)
    _anim_thread.start()


def attract_stop():
    global _anim_thread
    if _anim_thread and _anim_thread.is_alive():
        _anim_stop.set()
        _anim_thread.join(timeout=0.8)
    _anim_thread = None


def mode_attract(animated: bool = True):
    if animated:
        attract_start()
    else:
        attract_stop()
        set_both(ATTRACT_LEVEL)


def mode_pre_capture(fade=True):
    attract_stop()
    fade_both(ATTRACT_LEVEL, PRE_LEVEL, duration=0.2) if fade else set_both(PRE_LEVEL)


def mode_capture(fade=False):
    attract_stop()
    fade_both(PRE_LEVEL, CAPTURE_LEVEL, duration=0.08) if fade else set_both(
        CAPTURE_LEVEL
    )


def mode_post_capture(fade=True):
    fade_both(CAPTURE_LEVEL, ATTRACT_LEVEL, duration=0.25) if fade else set_both(
        ATTRACT_LEVEL
    )
    attract_start()


# --- Compatibility aliases (so old calls don’t break) ---
def idle_start(*args, **kwargs):  # old name
    return attract_start()


def idle_stop(*args, **kwargs):  # old name
    return attract_stop()
