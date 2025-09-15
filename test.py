from picamera2 import Picamera2, Preview
from libcamera import Transform
import time

picam2 = Picamera2()
picam2.start_preview(
    Preview.QTGL, 
    x=100, 
    y=200, 
    width=800, 
    height=600, 
    transform=Transform(rotation=90)
)
picam2.start()
time.sleep(5)