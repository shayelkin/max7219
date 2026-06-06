# Python MAX7219 8x8 LED Matrix

A Python library for the MAX7219 8x8 LED matrix driver over SPI, for use on the
Raspberry Pi and other Linux devices with an SPI interface. Supports cascading
and uses [Pillow (PIL)](https://pillow.readthedocs.io/) for drawing.

Ported from [mcauser's micropython-max7219](https://github.com/mcauser/micropython-max7219).

## Requirements

* A Linux device with an SPI interface (e.g. Raspberry Pi) with SPI enabled.
* [spidev](https://pypi.org/project/spidev/)
* [Pillow](https://pypi.org/project/Pillow/)

## Usage

The constructor opens the SPI device and initialises the display. The chip
select is handled by the kernel, so only the SPI bus and device numbers are
needed. Call `close()` when done to release the SPI device.

**Single 8x8 LED Matrix**

```python
import max7219

display = max7219.Matrix8x8(num=1)
display.text('1', 0, 0, 1)
display.show()
display.close()
```

**Chain of 4x 8x8 LED Matrices**

```python
import max7219

display = max7219.Matrix8x8(num=4)
display.text('1234', 0, 0, 1)
display.show()
display.close()
```

**Selecting an SPI bus/device and flipping the display**

```python
import max7219

# SPI bus 0, chip-select device 1, rotated 180 degrees.
display = max7219.Matrix8x8(num=4, spi_bus=0, spi_device=1, flip=True)
display.brightness(0)  # 0 (dim) to 15 (bright)
display.text('1234', 0, 0, 1)
display.show()
display.close()
```

**Drawing shapes and text**

The display exposes [Pillow](https://pillow.readthedocs.io/) primitives. The
backing image is 1-bit (`8 * num` wide, 8 tall); use `1` to set a pixel and `0`
to clear it.

```python
display.putpixel((0, 0), 1)
display.putpixel((1, 1), 1)
display.line((8, 0, 16, 8), fill=1)
display.rectangle((17, 1, 23, 7), outline=1)
display.rectangle((25, 1, 31, 7), fill=1)
display.show()

# Clear the display.
display.rectangle((0, 0, 8 * display.num - 1, 7), fill=0)
display.text('dead', 0, 0, 1)
display.show()
display.close()
```

## Connections

The chip select is driven by the kernel; pick the device with `spi_device`
(`CE0` is device `0`, `CE1` is device `1`).

The connections differ by the SPI interface use. The following is an example only for connection to
Raspberry Pi on the SPI0, CE0 interface:

Raspberry Pi (SPI0, CE0)         | max7219 8x8 LED Matrix
---------------------------------|-----------------------
5V (pin 2)                       | VCC
GND (pin 6)                      | GND
MOSI / GPIO10 (pin 19)           | DIN
CE0 / GPIO8 (pin 24)             | CS
SCLK / GPIO11 (pin 23)           | CLK

## Links

* Ported from [mcauser's micropython-max7219](https://github.com/mcauser/micropython-max7219)
* Originally based on [deshipu's max7219.py](https://bitbucket.org/thesheep/micropython-max7219/src)
* [Pillow documentation](https://pillow.readthedocs.io/)
* [spidev documentation](https://pypi.org/project/spidev/)

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).
