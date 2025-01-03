# SOURCE: https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in3f.py
# *****************************************************************************
# * | File        :	  epd7in3f.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2022-10-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from .base import Display
from .edpconfig import RaspberryPi

from PIL import Image

# Display resolution
EPD_WIDTH = 800
EPD_HEIGHT = 480

logger = logging.getLogger("uvicorn.error")


class EPD7IN3F(Display):
    """e-Paper 7.3" (800x480) display driver
    Wiki: https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(F)
    """

    def __init__(self):
        super().__init__(EPD_WIDTH, EPD_HEIGHT)
        self.driver = RaspberryPi()
        self.reset_pin = self.driver.RST_PIN
        self.dc_pin = self.driver.DC_PIN
        self.busy_pin = self.driver.BUSY_PIN
        self.cs_pin = self.driver.CS_PIN
        self.BLACK = 0x000000  #   0000  BGR
        self.WHITE = 0xFFFFFF  #   0001
        self.GREEN = 0x00FF00  #   0010
        self.BLUE = 0xFF0000  #   0011
        self.RED = 0x0000FF  #   0100
        self.YELLOW = 0x00FFFF  #   0101
        self.ORANGE = 0x0080FF  #   0110

    # Hardware reset
    def reset(self):
        self.driver.digital_write(self.reset_pin, 1)
        self.driver.delay_ms(20)
        self.driver.digital_write(self.reset_pin, 0)  # module reset
        self.driver.delay_ms(2)
        self.driver.digital_write(self.reset_pin, 1)
        self.driver.delay_ms(20)

    def send_command(self, command):
        self.driver.digital_write(self.dc_pin, 0)
        self.driver.digital_write(self.cs_pin, 0)
        self.driver.spi_writebyte([command])
        self.driver.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.driver.digital_write(self.dc_pin, 1)
        self.driver.digital_write(self.cs_pin, 0)
        self.driver.spi_writebyte([data])
        self.driver.digital_write(self.cs_pin, 1)

    # send a lot of data
    def send_data2(self, data):
        self.driver.digital_write(self.dc_pin, 1)
        self.driver.digital_write(self.cs_pin, 0)
        self.driver.spi_writebyte2(data)
        self.driver.digital_write(self.cs_pin, 1)

    def ReadBusyH(self):
        logger.debug("e-Paper busy H")
        while self.driver.digital_read(self.busy_pin) == 0:  # 0: busy, 1: idle
            self.driver.delay_ms(5)
        logger.debug("e-Paper busy H release")

    def TurnOnDisplay(self):
        self.send_command(0x04)  # POWER_ON
        self.ReadBusyH()

        self.send_command(0x12)  # DISPLAY_REFRESH
        self.send_data(0x00)
        self.ReadBusyH()

        self.send_command(0x02)  # POWER_OFF
        self.send_data(0x00)
        self.ReadBusyH()

    def init(self):
        if self.driver.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()
        self.ReadBusyH()
        self.driver.delay_ms(30)

        self.send_command(0xAA)  # CMDH
        self.send_data(0x49)
        self.send_data(0x55)
        self.send_data(0x20)
        self.send_data(0x08)
        self.send_data(0x09)
        self.send_data(0x18)

        self.send_command(0x01)
        self.send_data(0x3F)
        self.send_data(0x00)
        self.send_data(0x32)
        self.send_data(0x2A)
        self.send_data(0x0E)
        self.send_data(0x2A)

        self.send_command(0x00)
        self.send_data(0x5F)
        self.send_data(0x69)

        self.send_command(0x03)
        self.send_data(0x00)
        self.send_data(0x54)
        self.send_data(0x00)
        self.send_data(0x44)

        self.send_command(0x05)
        self.send_data(0x40)
        self.send_data(0x1F)
        self.send_data(0x1F)
        self.send_data(0x2C)

        self.send_command(0x06)
        self.send_data(0x6F)
        self.send_data(0x1F)
        self.send_data(0x1F)
        self.send_data(0x22)

        self.send_command(0x08)
        self.send_data(0x6F)
        self.send_data(0x1F)
        self.send_data(0x1F)
        self.send_data(0x22)

        self.send_command(0x13)  # IPC
        self.send_data(0x00)
        self.send_data(0x04)

        self.send_command(0x30)
        self.send_data(0x3C)

        self.send_command(0x41)  # TSE
        self.send_data(0x00)

        self.send_command(0x50)
        self.send_data(0x3F)

        self.send_command(0x60)
        self.send_data(0x02)
        self.send_data(0x00)

        self.send_command(0x61)
        self.send_data(0x03)
        self.send_data(0x20)
        self.send_data(0x01)
        self.send_data(0xE0)

        self.send_command(0x82)
        self.send_data(0x1E)

        self.send_command(0x84)
        self.send_data(0x00)

        self.send_command(0x86)  # AGID
        self.send_data(0x00)

        self.send_command(0xE3)
        self.send_data(0x2F)

        self.send_command(0xE0)  # CCSET
        self.send_data(0x00)

        self.send_command(0xE6)  # TSSET
        self.send_data(0x00)
        return 0

    def get_buffer(self, image: Image) -> list[int]:
        buf_7color = bytearray(image.tobytes("raw"))

        # PIL does not support 4 bit color, so pack the 4 bits of color
        # into a single byte to transfer to the panel
        buf = [0x00] * int(self.width * self.height / 2)
        idx = 0
        for i in range(0, len(buf_7color), 2):
            buf[idx] = (buf_7color[i] << 4) + buf_7color[i + 1]
            idx += 1

        return buf

    def display(self, image_data: list[int]):
        self.send_command(0x10)
        self.send_data2(image_data)
        self.TurnOnDisplay()

    def clear(self, color=0x11):
        self.send_command(0x10)
        self.send_data2([color] * int(self.height) * int(self.width / 2))

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)

        self.driver.delay_ms(2000)
        self.driver.module_exit()


### END OF FILE ###
