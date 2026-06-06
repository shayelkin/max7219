"""
Python max7219 cascadable 8x8 LED matrix driver, ported from
https://github.com/mcauser/micropython-max7219

SPDX-License-Identifier: MIT

Copyright (c) 2026 Shay Elkin
Copyright (c) 2017 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import spidev
from PIL import Image, ImageDraw, ImageFont

def const(obj):
    return obj

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Matrix8x8:
    def __init__(
        self,
        num: int,
        spi_bus: int = 0,
        spi_device: int = 0,
        flip: bool = False
    ) -> None:
        """
        Driver for cascading MAX7219 8x8 LED matrices.

        Args:
            spi_bus: SPI bus number.
            spi_device: SPI chip-select device number.
            num: Number of cascaded 8x8 matrices.
            flip: if true, transpose the display by 180 degrees.

        >>> import max7219
        >>> display = max7219.Matrix8x8(num=4)
        >>> display.init()
        >>> display.text("Hi!", 0, 0, 1)
        >>> display.show()
        >>> display.close()
        """
        self.num = num
        self._transpose = Image.Transpose.ROTATE_180 if flip else None

        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = 1_000_000
        self._spi.mode = 0

        self._image = Image.new("1", (8 * num, 8), 0)
        self._draw = ImageDraw.Draw(self._image)
        self._font: ImageFont.ImageFont | None = None

        # Provide methods for accessing Image and ImageDraw primitives, similar to how
        # the MicroPython version does for FrameBuffer graphics primitives.
        self.getpixel = self._image.getpixel
        self.putpixel = self._image.putpixel
        self.line = self._draw.line
        self.rectangle = self._draw.rectangle
        self.paste = self._image.paste

        self.init()

    def _write(self, command: int, data: int) -> None:
        for m in range(self.num):
            self._spi.xfer2([command, data])

    def init(self) -> None:
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value: int) -> None:
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    def show(self) -> None:
        buffer = self._pack_image()
        for y in range(8):
            for m in range(self.num):
                self._spi.xfer2([_DIGIT0 + y, buffer[y * self.num + m]])

    def _pack_image(self) -> bytearray:
        # Pack the PIL 1-bit image into MONO_HLSB-style row bytes, where each
        # byte holds 8 horizontally adjacent pixels with the MSB on the left.
        image = self._image
        if self._transpose is not None:
            image = image.copy().transpose(self._transpose)

        pixels = image.load()
        if pixels is None:
            raise RuntimeError("image.load() returned empty response")

        buffer = bytearray(8 * self.num)
        for y in range(8):
            for m in range(self.num):
                byte = 0
                base_x = m * 8
                for bit in range(8):
                    if pixels[base_x + bit, y]:
                        byte |= 1 << (7 - bit)
                buffer[y * self.num + m] = byte
        return buffer

    def text(self, string: str, x: int, y: int, col: int = 1) -> None:
        if self._font is None:
            self._font = ImageFont.load_default()
        # PIL's default TTF font reserves ascender space above the cap line;
        # subtract the font bbox offset so (x, y) is the visible top-left.
        left, top, _, _ = self._font.getbbox(string)
        self._draw.text((x - left, y - top), string, fill=col, font=self._font)

    def close(self) -> None:
        self._spi.close()
