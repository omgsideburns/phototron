# Phototron

A custom photo booth system built to replace the now-abandoned `pibooth` — because it doesn’t support current versions of Raspberry Pi OS, and honestly, it was starting to get a little clunky.

This is a homebrew solution using whatever. Designed to be touchscreen-friendly, print stuff reliably, and eventually support things like QR downloads and remote config.

I am rebooting this specifically for Pi's at the moment because I'm in a time crunch to get it ready for an event...

---

## Current Status

Under development again but not working yet...

I will push gits WAY too many times when I'm doing tests on a pi.  It's just so much easier to `git pull` updates rather than trying to transfer them directly between devices. 

Currently building in macos for Pi 4 or Pi 5.. hopefully will add crossplatform compatibility for funsies..

---

## Flow Overview

![Flowchart Overview](docs/chart.svg)

> Full planning chart showing navigation and module structure.

---

More to come. This is mostly planning while I get the modules together.

---

# 💡 Phototron Light Animations

All animations live in `lights.py` under the `LightController` class. You can call them like this:

```python
from app.lights import LightController

lights = LightController()
lights.animate_party_mode()
```

---

## ✨ Animation Reference

| Method | Description |
|--------|-------------|
| `flash_on()` | Turns the relay flash ON |
| `flash_off()` | Turns the relay flash OFF |
| `flash_burst(duration=0.25)` | Turns flash ON briefly, then OFF |
| `animate_flash_ring()` | Quick white ring flash |
| `animate_rainbow_cycle(wait=0.01, cycles=1)` | Continuous rainbow animation |
| `animate_breathing(color, steps, pause, cycles)` | Fades in/out like breathing |
| `animate_police_strobe(flashes=5, delay=0.1)` | Red/Yellow strobe alert |
| `animate_theater_chase(color, delay, cycles)` | Marching lights theater style |
| `animate_twinkle(color, count, delay)` | Random sparkles |
| `animate_party_mode(flashes, delay)` | Colorful chaotic blinking |
| `set_error()` | Solid red |
| `set_idle()` | Dim blue idle glow |
| `cleanup()` | Call before shutdown to clean GPIO |

You can change default colors, counts, and delays in `LIGHTS_CONFIG` from your config file.

---

## License

Phototron is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).  
You can use and remix it, but **credit me**, **don’t sell it**, and **share your changes** under the same terms.