import time, board, neopixel_spi as neopixel

spi = board.SPI()  # uses MOSI (GPIO10)

p = neopixel.NeoPixel_SPI(board.SPI(), 16, bpp=4, brightness=0.5, auto_write=True, pixel_order=neopixel.RGBW)
p.fill((255, 0, 0))
time.sleep(1)
p.fill((0, 255, 0))
time.sleep(1)
p.fill((0, 0, 255))
time.sleep(1)
p.fill((0, 0, 0))
