import time
import board
import busio
import display
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


def check_i2c_address():
    # Initialize I2C (e.g., I2C0: GP0 = SDA, GP1 = SCL)
    i2c = busio.I2C(scl=board.GP13, sda=board.GP12)  # SCL, SDA

    while not i2c.try_lock():
        pass

    try:
        devices = i2c.scan()
        if devices:
            print("I2C devices found:")
            for device in devices:
                print(" - Address: 0x{:02X}".format(device))
        else:
            print("No I2C devices found.")
    finally:
        i2c.unlock()


DEEJ = Deej(["Master", "Firefox", "Spotify", "Discord", "Apex"])

SCREEN = display.DisplayScreen(
    pin_clock=board.GP18,
    pin_mosi=board.GP19,
    pin_cs=board.GP20,
    pin_dc=board.GP21,
    pin_reset=board.GP22,
    pin_bl=board.GP23,
    rotation=180,
)

ENCODERS = [
    {
        "actions": (
            lambda: SCREEN.change_brightness(-1),
            lambda: SCREEN.change_brightness(+1),
        ),
        "button": {"pin": 1, "actions": (BiT.KEY, [key.ONE])},
    },
    {
        "actions": (
            lambda: DEEJ.change_volume(-5),
            lambda: DEEJ.change_volume(+5),
        ),
        "button": {"pin": 0, "actions": (BiT.KEY, [key.TWO])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(key.C),
            lambda: hid.KBD.send(key.D),
        ),
        "button": {"pin": 3, "actions": (BiT.KEY, [key.THREE])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(key.E),
            lambda: hid.KBD.send(key.F),
        ),
        "button": {"pin": 2, "actions": (BiT.KEY, [key.FOUR])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(key.G),
            lambda: hid.KBD.send(key.H),
        ),
        "button": {"pin": 4, "actions": (BiT.KEY, [key.FIVE])},
    },
    {
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
        (BiT.KEY, []),
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


def init_encoders():

    dual_encoders = []
    for i in range(0, 12, 4):
        pins = [getattr(board, f"GP{j}") for j in range(i, i + 4)]
        init_dual_encoder = DualIncrementalEncoder(*pins)
        dual_encoders.append(init_dual_encoder)

    # Encoder position on macropad hardware, order based on pin
    orders = [1, 6, 4, 2, 5, 3]
    encoders = []
    for i in range(6):
        group = i // 2  # integer division groups every two items
        local_index = i % 2  # 0 or 1
        split_encoder = SplitRotaryEncoder(
            name=f"Encoder {i}",
            encoder=dual_encoders[group],
            index=local_index,
            actions=ENCODERS[orders[i] - 1]["actions"],
        )
        encoders.append(split_encoder)

    return encoders


def init_button_encoders(i2c):
    expander = PCF8574(i2c, address=0x20)
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
    i2c = init_expander(scl=board.GP13, sda=board.GP12)

    encoders = init_encoders()
    encoder_buttons = init_button_encoders(i2c)

    keypad = ButtonMatrix(
        actions=KEYPADS,
        expander=PCF8574(i2c, address=0x25),
        rows=[board.GP14, board.GP15, board.GP17, board.GP24],
        columns=[0, 1, 2, 3, 4],
    )

    SCREEN.show_image("media/lize.bmp")

    labels = init_volumes_label()
    SCREEN.show_screen()

    while True:
        for encoder in encoders:
            enc = encoder.encoder_action()

            if enc == True:
                labels[DEEJ.current].text = DEEJ.display

        for button in encoder_buttons:
            button.button_action()

        keypad.matrix_scanning()

        time.sleep(0.01)


if __name__ == "__main__":
    main()
    # check_i2c_address()
