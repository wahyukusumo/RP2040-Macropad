import time
import board
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


def handle_encoder(encoder, last_position, name):
    current_position = encoder.position
    if current_position != last_position:
        if current_position > last_position:
            print(f"{name}: Clockwise")
            mouse.move(wheel=1)
        else:
            print(f"{name}: Counterclockwise")
            mouse.move(wheel=-1)
    return current_position


kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

MEDIA = 1  # this can be for volume, media player, brightness etc.
KEY = 2  # Keyboard press
STRING = 3  # Text string
WRAPPED = 4
NEW_LINE = "NEW_LINE"


# This code is for buttons, currently moved to this function since it will be rewrite later.
def button_unused():
    # list of pins to use (skipping GP15 on Pico because it's funky)
    pins = [
        board.GP6,
        board.GP7,
        board.GP8,
        board.GP9,
        board.GP10,
        board.GP11,
        board.GP12,
        board.GP13,
        board.GP14,
        board.GP15,
        board.GP17,
        board.GP18,
    ]

    total_pins = len(pins)

    keymap = {
        (0): (KEY, [Keycode.TWO]),
        (1): (KEY, [Keycode.FIVE]),
        (2): (KEY, [Keycode.C]),
        (3): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.ONE]),
        (4): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.TWO]),
        (5): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.THREE]),
        (6): (KEY, [Keycode.M]),
        (7): (KEY, [Keycode.F]),
        (8): (KEY, [Keycode.I]),
        (9): (KEY, [Keycode.SPACE]),
        (10): (KEY, [Keycode.LEFT_CONTROL, Keycode.Z]),
        (11): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.Z]),
    }

    switches = [0] * total_pins

    for i in range(total_pins):
        switches[i] = DigitalInOut(pins[i])
        switches[i].direction = Direction.INPUT
        switches[i].pull = Pull.UP

    switch_state = [0] * total_pins

    while True:
        # Handle the 12 button switches
        for button in range(total_pins):
            if switch_state[button] == 0:
                if not switches[button].value:  # Button pressed
                    try:
                        if keymap[button][0] == KEY:
                            kbd.press(*keymap[button][1])
                        elif keymap[button][0] == STRING:
                            for letter in keymap[button][1][0]:
                                layout.write(letter)
                            if keymap[button][1][1] == NEW_LINE:
                                kbd.press(*[Keycode.RETURN])
                                kbd.release(*[Keycode.RETURN])
                        else:
                            cc.send(keymap[button][1][0])
                    except ValueError:  # deals with six-key limit
                        pass
                    switch_state[button] = 1

            if switch_state[button] == 1:
                if switches[button].value:  # Button released
                    try:
                        if keymap[button][0] == KEY:
                            kbd.release(*keymap[button][1])
                    except ValueError:
                        pass
                    switch_state[button] = 0


class RotaryEncoder:
    def __init__(self, name: str, pin_a, pin_b, pin_button):
        self.name = name
        self.encoder = rotaryio.IncrementalEncoder(pin_a, pin_b)
        self.last_position = self.encoder.position
        self.encoder_button = self.init_button(pin_button)
        self.button_state = 0

    def init_button(self, pin_button):
        button = DigitalInOut(pin_button)
        button.direction = Direction.INPUT
        button.pull = Pull.UP  # Pull-up resistor enabled
        return button

    def handle_button(self, keymap):
        if self.button_state == 0:
            if not self.encoder_button.value:
                try:
                    if keymap[0] == KEY:
                        kbd.press(*keymap[1])
                    elif keymap[0] == STRING:
                        for letter in keymap[1][0]:
                            layout.write(letter)
                        if keymap[1][1] == NEW_LINE:
                            kbd.press(*[Keycode.RETURN])
                            kbd.release(*[Keycode.RETURN])
                    else:
                        cc.send(keymap[1][0])
                except ValueError:  # deals with six-key limit
                    pass
                self.button_state = 1

        if self.button_state == 1:
            if self.encoder_button.value:
                try:
                    if keymap[0] == KEY:
                        kbd.release(*keymap[1])
                except ValueError:
                    pass
                self.button_state = 0

    def handle_encoder(self):
        current_position = self.encoder.position
        if current_position != self.last_position:
            if current_position > self.last_position:
                print(f"{self.name}: Clockwise")
                print(current_position)
                mouse.move(wheel=1)
            else:
                print(f"{self.name}: Counterclockwise")
                print(current_position)
                mouse.move(wheel=-1)
            self.last_position = current_position


encoder = RotaryEncoder("Encoder 1", board.GP0, board.GP1, board.GP5)

# encoder_1 = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
encoder_2 = rotaryio.IncrementalEncoder(board.GP2, board.GP3)
encoder_3 = rotaryio.IncrementalEncoder(board.GP4, board.GP5)

# last_position_1 = encoder_1.position
last_position_2 = encoder_2.position
last_position_3 = encoder_3.position

while True:
    encoder.handle_encoder()
    encoder.handle_button((KEY, [Keycode.LEFT_CONTROL, Keycode.Z]))

    # Handle Rotary Encoder 1 (track rotation and send arrow keys)
    # last_position_1 = handle_encoder(encoder_1, last_position_1, "Encoder 1")
    last_position_2 = handle_encoder(encoder_2, last_position_2, "Encoder 2")
    last_position_3 = handle_encoder(encoder_3, last_position_3, "Encoder 3")

    # Delay to prevent multiple fast triggers
    time.sleep(0.01)
