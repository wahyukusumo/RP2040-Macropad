import time
import board
import busio
import display
from macropad import HIDType, ButtonInputType, Button, SplitRotaryEncoder, ButtonMatrix
from adafruit_pcf8574 import PCF8574
from adafruit_hid.keycode import Keycode
from rp2pio_dualincrementalencoder import DualIncrementalEncoder


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


SCREEN = display.DisplayScreen(
    pin_clock=board.GP18,
    pin_mosi=board.GP19,
    pin_cs=board.GP20,
    pin_dc=board.GP21,
    pin_reset=board.GP22,
    pin_bl=board.GP23,
)

ENCODERS = [
    {
        "name": "Encoder 1",  # Encoder 1 (Top Left)
        "pins": (board.GP0, board.GP1),
        "actions": (
            lambda: SCREEN.change_brightness(-1),
            lambda: SCREEN.change_brightness(+1),
        ),
        "button": {"pin": 0, "actions": ()},
    },
    {
        "name": "Encoder 2",
        "pins": (board.GP2, board.GP3),
        "actions": (
            lambda: HIDType.MOUSE.move(wheel=-1),
            lambda: HIDType.MOUSE.move(wheel=1),
        ),
        "button": {"pin": 1, "actions": ()},
    },
    {
        "name": "Encoder 3",
        "pins": (board.GP4, board.GP5),
        "actions": (
            lambda: HIDType.MOUSE.move(wheel=-1),
            lambda: HIDType.MOUSE.move(wheel=1),
        ),
        "button": {"pin": 2, "actions": ()},
    },
    {
        "name": "Encoder 4",
        "pins": (board.GP6, board.GP7),
        "actions": (
            lambda: HIDType.MOUSE.move(wheel=-1),
            lambda: HIDType.MOUSE.move(wheel=1),
        ),
        "button": {"pin": 3, "actions": ()},
    },
    {
        "name": "Encoder 5",
        "pins": (board.GP8, board.GP9),
        "actions": (
            lambda: HIDType.MOUSE.move(wheel=-1),
            lambda: HIDType.MOUSE.move(wheel=1),
        ),
        "button": {"pin": 4, "actions": ()},
    },
    {
        "name": "Encoder 6",
        "pins": (board.GP10, board.GP11),
        "actions": (
            lambda: HIDType.MOUSE.move(wheel=-1),
            lambda: HIDType.MOUSE.move(wheel=1),
        ),
        "button": {"pin": 5, "actions": ()},
    },
]

KEYPADS = [
    [
        (ButtonInputType.KEY, [Keycode.A]),
        (ButtonInputType.KEY, [Keycode.B]),
        (ButtonInputType.KEY, [Keycode.C]),
        (ButtonInputType.KEY, [Keycode.D]),
        (ButtonInputType.KEY, [Keycode.E]),
    ],
    [
        (ButtonInputType.KEY, [Keycode.F]),
        (ButtonInputType.KEY, [Keycode.G]),
        (ButtonInputType.KEY, [Keycode.H]),
        (ButtonInputType.KEY, [Keycode.I]),
        (ButtonInputType.KEY, [Keycode.J]),
    ],
    [
        (ButtonInputType.KEY, [Keycode.K]),
        (ButtonInputType.KEY, [Keycode.L]),
        (ButtonInputType.KEY, [Keycode.M]),
        (ButtonInputType.KEY, [Keycode.N]),
        (ButtonInputType.KEY, [Keycode.O]),
    ],
    [
        (ButtonInputType.KEY, [Keycode.P]),
        (ButtonInputType.KEY, [Keycode.Q]),
        (ButtonInputType.KEY, [Keycode.R]),
        (ButtonInputType.KEY, [Keycode.S]),
        (ButtonInputType.KEY, [Keycode.T]),
    ],
]


def init_expander():
    i2c = busio.I2C(scl=board.GP13, sda=board.GP12)  # SCL, SDA
    # Wait for I2C to be ready
    while not i2c.try_lock():
        pass
    i2c.unlock()
    return i2c


def init_encoders():
    dual_encoders = []
    for i in range(0, len(ENCODERS), 2):
        pin_1, pin_2, pin_3, pin_4 = ENCODERS[i]["pins"] + ENCODERS[i + 1]["pins"]
        init_dual_encoder = DualIncrementalEncoder(pin_1, pin_2, pin_3, pin_4)
        dual_encoders.append(init_dual_encoder)

    encoders = []
    for i, encoder in enumerate(ENCODERS):
        group = i // 2  # integer division groups every two items
        local_index = i % 2  # 0 or 1
        split_encoder = SplitRotaryEncoder(
            name=encoder["name"],
            encoder=dual_encoders[group],
            index=local_index,
            actions=encoder["actions"],
        )
        encoders.append(split_encoder)

    return encoders


def main():
    i2c = init_expander()

    encoders = init_encoders()

    matrix = ButtonMatrix(
        actions=KEYPADS,
        expander=PCF8574(i2c, address=0x25),
        rows=[board.GP14, board.GP15, board.GP17, board.GP24],
        columns=[0, 1, 2, 3, 4],
    )

    SCREEN.show_image("berry.bmp")
    SCREEN.show_screen()

    while True:
        for encoder in encoders:
            encoder.encoder_action()

        matrix.matrix_scanning()


if __name__ == "__main__":
    main()
    # check_i2c_address()
