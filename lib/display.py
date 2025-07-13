import busio
import displayio
import pwmio
import os
import terminalio
import gifio
import time
from fourwire import FourWire
from adafruit_st7789 import ST7789
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label


class DisplayScreen:
    def __init__(
        self, pin_clock, pin_mosi, pin_cs, pin_dc, pin_reset, pin_bl, rotation=0
    ):
        self.rotation = rotation
        self.current = 3  # default brightness level
        self.levels = [
            0,
            6553,
            13107,
            19660,
            26214,
            32767,
            39321,
            45874,
            52428,
            58981,
        ]
        self.brightness = None
        self.display = self.init_display(
            pin_clock, pin_mosi, pin_cs, pin_dc, pin_reset, pin_bl
        )
        self.group = displayio.Group()
        self.images_group = displayio.Group()
        self.texts_group = displayio.Group()

    def change_brightness(self, direction):
        # direction value is +1 or -1
        index = self.current + direction
        self.current = index % 10
        self.brightness.duty_cycle = self.levels[self.current]

    def init_spi_bus(self, pin_clock, pin_mosi):
        spi = busio.SPI(clock=pin_clock, MOSI=pin_mosi)
        while not spi.try_lock():
            pass
        spi.configure(baudrate=24000000)
        spi.unlock()
        return spi

    def init_display(self, pin_clock, pin_mosi, pin_cs, pin_dc, pin_reset, pin_bl):
        displayio.release_displays()

        spi = self.init_spi_bus(pin_clock, pin_mosi)

        self.brightness = pwmio.PWMOut(pin_bl, frequency=5000, duty_cycle=0)
        self.brightness.duty_cycle = self.levels[self.current]

        display_bus = FourWire(spi, command=pin_dc, chip_select=pin_cs, reset=pin_reset)
        display = ST7789(
            display_bus,
            width=240,
            height=240,
            rowstart=80,
            bgr=True,
            invert=True,
            rotation=self.rotation,
        )
        return display

    def show_image(self, image_file):
        bitmap = displayio.OnDiskBitmap(f"{image_file}")
        # Create tile grid to hold image
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        self.images_group.append(tile_grid)

    def show_icons(self, icon_file):
        icon = displayio.OnDiskBitmap(f"/media/Icons/{icon_file}")  # 1-bit or 8-bit BMP

        # Make a TileGrid using the bitmap's pixel shader (palette)
        tile = displayio.TileGrid(icon, pixel_shader=icon.pixel_shader, x=150, y=50)

        # Make the background color transparent (assumes index 0 is background)
        icon.pixel_shader.make_transparent(0)

        # Show it
        self.group.append(tile)

    def gif_io(self):
        odg = gifio.OnDiskGif("media/tako.gif")

        start = time.monotonic()
        next_delay = odg.next_frame()  # Load the first frame
        end = time.monotonic()
        overhead = end - start

        face = displayio.TileGrid(
            odg.bitmap,
            pixel_shader=displayio.ColorConverter(
                input_colorspace=displayio.Colorspace.RGB565_SWAPPED
            ),
        )
        self.group.append(face)
        # self.display.root_group = self.group
        self.display.refresh()

        return odg, next_delay, overhead

        # Display repeatedly.
        # while True:
        # Sleep for the frame delay specified by the GIF,
        # minus the overhead measured to advance between frames.
        # time.sleep(max(0, next_delay - overhead))
        # next_delay = odg.next_frame()

    def show_screen(self):
        self.group.append(self.images_group)
        self.group.append(self.texts_group)
        self.display.root_group = self.group

    def label(self, text, x, y):
        # Set text, font, and color
        font = bitmap_font.load_font("fonts/LexendDeca-Regular-17.pcf")
        # font = terminalio.FONT
        text_area = label.Label(
            font=font,
            text=text,
            color=0x88363E,
            # outline_color=0xFFFFFF,
            # outline_size=1,
            x=x,
            y=y,
            scale=1,
        )
        self.texts_group.append(text_area)
        return text_area


class Slideshow:
    def __init__(self, group):
        folder = "/media"
        self.group = group
        self.dwell = 60
        self.images = [
            folder + "/" + f
            for f in os.listdir(folder)
            if (not f.startswith(".") and (f.endswith(".bmp")))
        ]
        self.num_images = len(self.images)
        self.last_time = time.monotonic()
        self.index = 0
        self.show_image(self.images[self.index])

    def show_image(self, image_file):
        bitmap = displayio.OnDiskBitmap(image_file)
        # Create tile grid to hold image
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        self.group.append(tile_grid)

    def clamp(self):
        self.index = (self.index + 1) % self.num_images

    def advance(self):
        self.clamp()
        self.group.pop()
        self.show_image(self.images[self.index])

    def update(self) -> bool:
        """Updates the slideshow to the next image."""
        now = time.monotonic()
        if now - self.last_time >= self.dwell:
            # return True
            self.last_time = now
            return self.advance()
