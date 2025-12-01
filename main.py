import time
import board
import busio
import display
import config
from deej import Deej
from macropad import (
    HIDType as hid,
    ButtonInputType as BiT,
    Button,
    SplitRotaryEncoder,
    ButtonMatrix,
)
from adafruit_pcf8574 import PCF8574
from adafruit_hid.keycode import Keycode as key
from rp2pio_dualincrementalencoder import DualIncrementalEncoder
from adafruit_hid.consumer_control_code import ConsumerControlCode as cc_code


DEEJ = Deej(config.DEEJ_PROGRAMS)

SCREEN = display.DisplayScreen(
    pin_clock=config.DISPLAY_PINS["CLOCK"],
    pin_mosi=config.DISPLAY_PINS["MOSI"],
    pin_cs=config.DISPLAY_PINS["CS"],
    pin_dc=config.DISPLAY_PINS["DC"],
    pin_reset=config.DISPLAY_PINS["RESET"],
    pin_bl=config.DISPLAY_PINS["BL"],
    rotation=config.DISPLAY_PINS["ROTATION"],
)

ENCODERS, KEYPADS = config.input_map(SCREEN, DEEJ, BiT, key, hid, cc_code)


def init_expander(scl, sda):
    i2c = busio.I2C(scl, sda)
    # Wait for I2C to be ready
    while not i2c.try_lock():
        pass
    i2c.unlock()
    return i2c


def init_encoders(encoders_num):
    """This loop is for looping through encoders pin and .
    So if there's 6 rotary encoders, encoders_num = 6
    (0, 6 * 2, 4) mean we start from 0, and since each encoder have 2 pins, multiplied by 2.
    DualIncrementalEncoder require 4 pins so we split it by 4
    and it will append to dual_encoders as 3 object of DualIncrementalEncoder
    """
    dual_encoders = []
    for i in range(0, encoders_num * 2, 4):
        pins = [getattr(board, f"GP{j}") for j in range(i, i + 4)]
        init_dual_encoder = DualIncrementalEncoder(*pins)
        dual_encoders.append(init_dual_encoder)

    """ After we get DualIncrementalEncoders we need to get value of each encoder and
    apply action of the encoders
    """
    encoders = []
    for i in range(encoders_num):
        group = i // 2  # integer division groups every two items
        local_index = i % 2  # 0 or 1
        split_encoder = SplitRotaryEncoder(
            name=f"Encoder {i}",
            encoder=dual_encoders[group],
            index=local_index,
            actions=ENCODERS[config.ROTARY_ENCODERS_PHYSICAL_ORDER[i] - 1]["actions"],
        )
        encoders.append(split_encoder)

    return encoders


def init_button_encoders(i2c):
    expander = PCF8574(i2c, address=config.BUTTON_IO_EXPANDER_ADDRESS)
    buttons = []

    for encoder in ENCODERS:
        button_pin = expander.get_pin(encoder["button"]["pin"])
        button = Button(pin_button=button_pin, actions=encoder["button"]["actions"])
        buttons.append(button)
    return buttons


def init_volumes_label():
    labels = []
    for i in range(DEEJ.num_programs):
        y = 50 + (i - 1) * 25
        text = f"{DEEJ.volumes[i]} - {DEEJ.programs[i]}"
        label = SCREEN.label(text, x=15, y=y)
        labels.append(label)
    return labels


def main():
    i2c = init_expander(
        scl=config.IO_EXPANDER_PINS["SCL"], sda=config.IO_EXPANDER_PINS["SDA"]
    )

    encoders = init_encoders(config.ROTARY_ENCODERS_NUM)
    encoder_buttons = init_button_encoders(i2c)

    keypad = ButtonMatrix(
        actions=KEYPADS,
        expander=PCF8574(i2c, address=config.MATRIX_IO_EXPANDER_ADDRESS),
        rows=config.MATRIX_ROW_PINS,
        columns=config.MATRIX_COL_PINS,
    )

    if config.USE_DEEJ:
        labels = init_volumes_label()

    slideshow = display.Slideshow(SCREEN.images_group)
    # gif = display.PlayGif("media/mon.gif", SCREEN.gif_group, SCREEN.display)
    SCREEN.show_screen()

    while True:
        for encoder in encoders:
            turned = encoder.encoder_action()

            if turned and config.USE_DEEJ:
                labels[DEEJ.current].text = DEEJ.display

        for button in encoder_buttons:
            button.button_action()

        keypad.matrix_scanning()
        slideshow.update()
        # gif.update_gif()

        time.sleep(0.01)


if __name__ == "__main__":
    main()
