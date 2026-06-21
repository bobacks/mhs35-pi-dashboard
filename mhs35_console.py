#!/usr/bin/env python3
import time
import spidev
import gpiod
from gpiod.line import Direction, Value
from PIL import Image, ImageDraw, ImageFont

DC = 24
RST = 25
W, H = 480, 320

class MHS35:
    def __init__(self):
        self.req = gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="mhs35-console",
            config={
                DC: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
                RST: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE),
            },
        )

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 16000000
        self.spi.mode = 0
        self.spi.bits_per_word = 8

        self.image = Image.new("RGB", (W, H), "black")
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)

        self.init_panel()

    def dc(self, v):
        self.req.set_value(DC, Value.ACTIVE if v else Value.INACTIVE)

    def rst(self, v):
        self.req.set_value(RST, Value.ACTIVE if v else Value.INACTIVE)

    def reset(self):
        self.rst(1)
        time.sleep(0.05)
        self.rst(0)
        time.sleep(0.12)
        self.rst(1)
        time.sleep(0.15)

    def cmd(self, c, *data):
        self.dc(0)
        self.spi.xfer2([0x00, c & 0xff])
        if data:
            self.dc(1)
            out = []
            for x in data:
                out.extend([0x00, x & 0xff])
            self.spi.xfer2(out)

    def init_panel(self):
        self.reset()
        self.cmd(0xF1, 0x36, 0x04, 0x00, 0x3C, 0x0F, 0x8F)
        self.cmd(0xF2, 0x18, 0xA3, 0x12, 0x02, 0xB2, 0x12, 0xFF, 0x10, 0x00)
        self.cmd(0xF8, 0x21, 0x04)
        self.cmd(0xF9, 0x00, 0x08)
        self.cmd(0x36, 0x08)
        self.cmd(0xB4, 0x00)
        self.cmd(0xC1, 0x41)
        self.cmd(0xC5, 0x00, 0x91, 0x80, 0x00)
        self.cmd(0xE0, 0x0F, 0x1F, 0x1C, 0x0C, 0x0F, 0x08, 0x48, 0x98, 0x37, 0x0A, 0x13, 0x04, 0x11, 0x0D, 0x00)
        self.cmd(0xE1, 0x0F, 0x32, 0x2E, 0x0B, 0x0D, 0x05, 0x47, 0x75, 0x37, 0x06, 0x10, 0x03, 0x24, 0x20, 0x00)
        self.cmd(0x3A, 0x55)
        self.cmd(0x11)
        time.sleep(0.12)
        self.cmd(0x36, 0x28)
        time.sleep(0.05)
        self.cmd(0x29)
        time.sleep(0.05)

    def set_window(self, x0, y0, x1, y1):
        self.cmd(0x2A, x0 >> 8, x0 & 255, x1 >> 8, x1 & 255)
        self.cmd(0x2B, y0 >> 8, y0 & 255, y1 >> 8, y1 & 255)
        self.cmd(0x2C)

    def clear(self, colour="black"):
        self.draw.rectangle((0, 0, W, H), fill=colour)

    def text(self, msg, x, y, colour="white", size=None):
        font = self.font if size is None else ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size
        )
        self.draw.text((x, y), str(msg), fill=colour, font=font)

    def show(self):
        img = self.image.convert("RGB")
        px = img.load()
        for y in range(H):
            self.set_window(0, y, W - 1, y)
            self.dc(1)
            row = []
            for x in range(W):
                r, g, b = px[x, y]
                c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                row.extend([(c >> 8) & 255, c & 255])
            self.spi.xfer2(row)

    def display_off(self):
        self.clear("black")
        self.show()

    def display_on(self):
        self.cmd(0x11)
        time.sleep(0.12)
        self.cmd(0x29)
        time.sleep(0.05)

    def close(self):
        self.spi.close()
        self.req.release()

if __name__ == "__main__":
    d = MHS35()
    try:
        d.clear("black")
        d.text("MHS35 Console Online", 20, 20, "lime", 24)
        d.text("Debian Trixie + Pi 4B", 20, 60, "white")
        d.text("SPI custom text mode", 20, 95, "cyan")
        d.text(time.strftime("%Y-%m-%d %H:%M:%S"), 20, 135, "yellow")
        d.show()
    finally:
        d.close()
