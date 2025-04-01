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

kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

MEDIA = 1  # this can be for volume, media player, brightness etc.
KEY = 2  # Keyboard press
STRING = 3  # Text string
WRAPPED = 4
NEW_LINE = "NEW_LINE"


def handle_input_action():
    pass


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


class Button:
    def __init__(self, pin_button: board.Pin):
        # def __init__(self, pin_button: board.Pin):
        self.button = self.init_button(pin_button)
        self.button_state = 0

    def init_button(self, pin_button: board.Pin):
        button = DigitalInOut(pin_button)
        button.direction = Direction.INPUT
        button.pull = Pull.UP  # Pull-up resistor enabled
        return button

    def handle_button(self, keymap: tuple):
        if self.button_state == 0:
            if not self.button.value:
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
            if self.button.value:
                try:
                    if keymap[0] == KEY:
                        kbd.release(*keymap[1])
                except ValueError:
                    pass
                self.button_state = 0


class RotaryEncoder(Button):
    def __init__(
        self, name: str, pin_a: board.Pin, pin_b: board.Pin, pin_button: board.Pin
    ):
        super().__init__(pin_button)
        self.name = name
        self.encoder = rotaryio.IncrementalEncoder(pin_a, pin_b)
        self.last_position = self.encoder.position

    def handle_encoder(self):
        current_position = self.encoder.position
        if current_position != self.last_position:
            if current_position > self.last_position:
                print(f"{self.name}: Clockwise")
                mouse.move(wheel=1)
            else:
                print(f"{self.name}: Counterclockwise")
                mouse.move(wheel=-1)
            self.last_position = current_position


def main():
    # Initialize your encoders
    # encoder_1 = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
    encoder_2 = rotaryio.IncrementalEncoder(board.GP3, board.GP4)
    encoder_3 = rotaryio.IncrementalEncoder(board.GP12, board.GP13)
    encoder_4 = rotaryio.IncrementalEncoder(board.GP16, board.GP17)

    # Track positions separately
    # last_position_1 = encoder_1.position
    last_position_2 = encoder_2.position
    last_position_3 = encoder_3.position
    last_position_4 = encoder_4.position

    encoder = RotaryEncoder("Encoder 1", board.GP0, board.GP1, board.GP5)
    print(type(encoder.button))

    while True:
        # Call handle_encoder() for each encoder, one after the other
        # last_position_1 = handle_encoder(encoder_1, last_position_1, "Encoder 1")
        encoder.handle_encoder()
        encoder.handle_button((KEY, [Keycode.C]))
        last_position_2 = handle_encoder(encoder_2, last_position_2, "Encoder 2")
        last_position_3 = handle_encoder(encoder_3, last_position_3, "Encoder 3")
        last_position_4 = handle_encoder(encoder_4, last_position_4, "Encoder 4")

        # Delay to prevent multiple fast triggers
        time.sleep(0.01)


if __name__ == "__main__":
    main()
