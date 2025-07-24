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
from adafruit_display_text import label


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

ENCODERS = [
    {  # Encoder 1
        "actions": (
            lambda: SCREEN.change_brightness(-1),
            lambda: SCREEN.change_brightness(+1),
        ),
        "button": {"pin": 1, "actions": (BiT.KEY, [key.ONE])},
    },
    {  # Encoder 2
        "actions": (
            lambda: DEEJ.change_volume(-5),
            lambda: DEEJ.change_volume(+5),
        ),
        "button": {"pin": 0, "actions": (BiT.KEY, [key.TWO])},
    },
    {  # Encoder 3
        "actions": (lambda: hid.MOUSE.move(wheel=-1), lambda: hid.MOUSE.move(wheel=1)),
        "button": {"pin": 3, "actions": (BiT.KEY, [key.THREE])},
    },
    {  # Encoder 4
        "actions": (
            lambda: hid.KBD.send(key.CONTROL, key.LEFT_BRACKET),
            lambda: hid.KBD.send(key.CONTROL, key.RIGHT_BRACKET),
        ),
        "button": {"pin": 2, "actions": (BiT.KEY, [key.FOUR])},
    },
    {  # Encoder 5
        "actions": (
            lambda: hid.KBD.send(key.CONTROL, key.Z),
            lambda: hid.KBD.send(key.CONTROL, key.SHIFT, key.Z),
        ),
        "button": {"pin": 4, "actions": (BiT.KEY, [key.FIVE])},
    },
    {  # Encoder 6
        "actions": (
            lambda: hid.KBD.send(key.I),
            lambda: hid.KBD.send(key.J),
        ),
        "button": {"pin": 5, "actions": (BiT.KEY, [key.SIX])},
    },
]

KEYPADS = [
    [
        (BiT.CUSTOM, lambda: DEEJ.cycle_programs(-1)),
        (BiT.MEDIA, cc_code.SCAN_PREVIOUS_TRACK),
        (BiT.MEDIA, cc_code.PLAY_PAUSE),
        (BiT.MEDIA, cc_code.SCAN_NEXT_TRACK),
        (BiT.CUSTOM, lambda: DEEJ.cycle_programs(+1)),
    ],
    [
        (BiT.KEY, [key.F]),
        (BiT.KEY, [key.G]),
        (BiT.KEY, [key.H]),
        (BiT.KEY, [key.I]),
        (BiT.KEY, [key.J]),
    ],
    [
        (BiT.KEY, [key.K]),
        (BiT.KEY, [key.L]),
        (BiT.KEY, [key.M]),
        (BiT.KEY, [key.N]),
        (BiT.KEY, [key.O]),
    ],
    [
        (BiT.KEY, [key.P]),
        (BiT.KEY, [key.Q]),
        (BiT.KEY, [key.R]),
        (BiT.KEY, [key.S]),
        (BiT.KEY, [key.T]),
    ],
]


def init_expander(scl, sda):
    i2c = busio.I2C(scl, sda)
    # Wait for I2C to be ready
    while not i2c.try_lock():
        pass
    i2c.unlock()
    return i2c


def init_encoders(encoders_num):

    dual_encoders = []
    for i in range(0, encoders_num * 2, 4):
        pins = [getattr(board, f"GP{j}") for j in range(i, i + 4)]
        init_dual_encoder = DualIncrementalEncoder(*pins)
        dual_encoders.append(init_dual_encoder)

    encoders = []
    for i in range(encoders_num):
        group = i // 2  # integer division groups every two items
        local_index = i % 2  # 0 or 1
        split_encoder = SplitRotaryEncoder(
            name=f"Encoder {i}",
            encoder=dual_encoders[group],
            index=local_index,
            actions=ENCODERS[config.ROTARY_ENCODERS_ORDER[i] - 1]["actions"],
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

    labels = init_volumes_label()
    # slideshow = display.Slideshow(SCREEN.images_group)
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
        # slideshow.update()
        # gif.update_gif()

        time.sleep(0.01)


if __name__ == "__main__":
    main()
