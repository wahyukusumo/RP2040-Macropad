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

MEDIA = 1  # this can be for volume, media player, brightness etc.
KEY = 2
STRING = 3
NEW_LINE = "NEW_LINE"

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

encoder_1 = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
encoder_2 = rotaryio.IncrementalEncoder(board.GP2, board.GP3)
encoder_3 = rotaryio.IncrementalEncoder(board.GP4, board.GP5)

last_position_1 = encoder_1.position
last_position_2 = encoder_2.position
last_position_3 = encoder_3.position

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

    # Handle Rotary Encoder 1 (track rotation and send arrow keys)
    last_position_1 = handle_encoder(encoder_1, last_position_1, "Encoder 1")
    last_position_2 = handle_encoder(encoder_2, last_position_2, "Encoder 2")
    last_position_3 = handle_encoder(encoder_3, last_position_3, "Encoder 3")

    # Delay to prevent multiple fast triggers
    time.sleep(0.01)
