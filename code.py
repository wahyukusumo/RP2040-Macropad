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


class InputType:
    MEDIA = 1  # this can be for volume, media player, brightness etc.
    KEY = 2  # Keyboard press
    LETTER = 3  # Text string
    WRAPPED = 4
    NEW_LINE = "NEW_LINE"


class Button:
    def __init__(
        self,
        pin_button: tuple[board.Pin, tuple[InputType, list]],
    ):
        # def __init__(self, pin_button: board.Pin):
        self.pin_button = pin_button
        self.button = self.init_button(pin_button[0])
        self.button_state = 0

    def init_button(self, pin_button: board.Pin):
        button = DigitalInOut(pin_button)
        button.direction = Direction.INPUT
        button.pull = Pull.UP  # Pull-up resistor enabled
        return button

    def handle_button(self):
        keymap = self.pin_button[1]
        if self.button_state == 0:
            if not self.button.value:  # Button pressed
                try:
                    if keymap[0] == InputType.KEY:
                        kbd.press(*keymap[1])
                    elif keymap[0] == InputType.LETTER:
                        for letter in keymap[1][0]:
                            layout.write(letter)
                        if keymap[1][1] == InputType.NEW_LINE:
                            kbd.press(*[Keycode.RETURN])
                            kbd.release(*[Keycode.RETURN])
                    elif keymap[0] == InputType.MEDIA:
                        cc.send(keymap[1][0])
                except ValueError:  # deals with six-key limit
                    pass
                self.button_state = 1

        if self.button_state == 1:
            if self.button.value:  # Button released
                try:
                    if keymap[0] == InputType.KEY:
                        kbd.release(*keymap[1])
                except ValueError:
                    pass
                self.button_state = 0


class RotaryEncoder(Button):
    def __init__(
        self,
        name: str,
        pin_a: tuple[board.Pin, callable],
        pin_b: tuple[board.Pin, callable],
        pin_button: tuple[board.Pin, tuple[InputType, list]],
    ):
        super().__init__(pin_button)
        self.name = name
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.encoder = rotaryio.IncrementalEncoder(pin_a[0], pin_b[0])
        self.last_position = self.encoder.position

    def handle_encoder(self):
        current_position = self.encoder.position
        if current_position != self.last_position:
            if current_position > self.last_position:
                print(f"{self.name}: Clockwise")
                self.pin_a[1]()
            else:
                print(f"{self.name}: Counterclockwise")
                self.pin_b[1]()
            self.last_position = current_position

    def handle_button_encoder(self):
        self.handle_button()
        self.handle_encoder()


def main():
    # Initialize your encoders
    # encoder_1 = board.GP0, board.GP1
    # encoder_2 = board.GP3, board.GP4
    # encoder_3 = board.GP12, board.GP13
    # encoder_4 = board.GP16, board.GP17

    encoder = RotaryEncoder(
        "Encoder 1",
        pin_a=(board.GP0, lambda: mouse.move(wheel=1)),
        pin_b=(board.GP1, lambda: mouse.move(wheel=-1)),
        pin_button=(board.GP5, (InputType.KEY, [Keycode.C])),
    )

    while True:
        # Call handle_encoder() for each encoder, one after the other
        encoder.handle_button_encoder()

        # Delay to prevent multiple fast triggers
        time.sleep(0.01)


if __name__ == "__main__":
    main()
