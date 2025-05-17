.readme

# Phototron

A custom photo booth system built to replace the now-abandoned `pibooth` — because it doesn’t support current versions of Raspberry Pi OS, and honestly, it was starting to get a little clunky.

This is a homebrew solution using Node.js, Socket.IO, and whatever else I feel like bolting on. Designed to be touchscreen-friendly, print stuff reliably, and eventually support things like QR downloads and remote config.

---

## Current Status

Under development.  Not working.

Currently building on OSX, but planning for it to work on a raspi 4. Should work on both.

Currently capturing the photos from the preview video feed.  Actually a bit snappier than using a separate service for capture.

Still need to finish adding features listed in the chart.

Need to format all of the html/css. Super ugly placeholders all over the place. 

Need to put build some output templates.

Need to build config page, gallery page, yada yada yada..

---

## Flow Overview

![Flowchart Overview](docs/chart.svg)

> Full planning chart showing navigation and module structure.

---

More to come. This is mostly planning while I get the modules together.

---

## License

Phototron is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).  
You can use and remix it, but **credit me**, **don’t sell it**, and **share your changes** under the same terms.