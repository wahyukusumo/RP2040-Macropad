import time
import board
import busio
import display
from macropad import (
    HIDType as hid,
    ButtonInputType as BiT,
    Button,
    SplitRotaryEncoder,
    ButtonMatrix,
)
from adafruit_pcf8574 import PCF8574
from adafruit_hid.keycode import Keycode as kc
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
        "actions": (
            lambda: SCREEN.change_brightness(-1),
            lambda: SCREEN.change_brightness(+1),
        ),
        "button": {"pin": 1, "actions": (BiT.KEY, [kc.ONE])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(kc.A),
            lambda: hid.KBD.send(kc.B),
        ),
        "button": {"pin": 0, "actions": (BiT.KEY, [kc.TWO])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(kc.C),
            lambda: hid.KBD.send(kc.D),
        ),
        "button": {"pin": 3, "actions": (BiT.KEY, [kc.THREE])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(kc.E),
            lambda: hid.KBD.send(kc.F),
        ),
        "button": {"pin": 2, "actions": (BiT.KEY, [kc.FOUR])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(kc.G),
            lambda: hid.KBD.send(kc.H),
        ),
        "button": {"pin": 4, "actions": (BiT.KEY, [kc.FIVE])},
    },
    {
        "actions": (
            lambda: hid.KBD.send(kc.I),
            lambda: hid.KBD.send(kc.J),
        ),
        "button": {"pin": 5, "actions": (BiT.KEY, [kc.SIX])},
    },
]

KEYPADS = [
    [
        (BiT.KEY, [kc.A]),
        (BiT.KEY, [kc.B]),
        (BiT.KEY, [kc.C]),
        (BiT.KEY, [kc.D]),
        (BiT.KEY, [kc.E]),
    ],
    [
        (BiT.KEY, [kc.F]),
        (BiT.KEY, [kc.G]),
        (BiT.KEY, [kc.H]),
        (BiT.KEY, [kc.I]),
        (BiT.KEY, [kc.J]),
    ],
    [
        (BiT.KEY, [kc.K]),
        (BiT.KEY, [kc.L]),
        (BiT.KEY, [kc.M]),
        (BiT.KEY, [kc.N]),
        (BiT.KEY, [kc.O]),
    ],
    [
        (BiT.KEY, [kc.P]),
        (BiT.KEY, [kc.Q]),
        (BiT.KEY, [kc.R]),
        (BiT.KEY, [kc.S]),
        (BiT.KEY, [kc.T]),
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
    for i in range(0, 12, 4):
        pin_1, pin_2, pin_3, pin_4 = [getattr(board, f"GP{j}") for j in range(i, i + 4)]
        init_dual_encoder = DualIncrementalEncoder(pin_1, pin_2, pin_3, pin_4)
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


def main():
    i2c = init_expander()

    encoders = init_encoders()
    encoder_buttons = init_button_encoders(i2c)

    keypad = ButtonMatrix(
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

        for button in encoder_buttons:
            button.button_action()

        keypad.matrix_scanning()

        time.sleep(0.01)


if __name__ == "__main__":
    main()
    # check_i2c_address()
