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


class ButtonInputType:
    MEDIA = 1  # this can be for volume, media player, brightness etc.
    KEY = 2  # Keyboard press
    LETTER = 3  # Text string
    NEW_LINE = "NEW_LINE"


class Button:
    def __init__(
        self,
        pin_button: tuple[board.Pin, tuple[ButtonInputType, list]],
    ):
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
                    if keymap[0] == ButtonInputType.KEY:
                        kbd.press(*keymap[1])
                    elif keymap[0] == ButtonInputType.LETTER:
                        for letter in keymap[1][0]:
                            layout.write(letter)
                        if keymap[1][1] == ButtonInputType.NEW_LINE:
                            kbd.press(*[Keycode.RETURN])
                            kbd.release(*[Keycode.RETURN])
                    elif keymap[0] == ButtonInputType.MEDIA:
                        cc.send(keymap[1][0])
                except ValueError:  # deals with six-key limit
                    pass
                self.button_state = 1

        if self.button_state == 1:
            if self.button.value:  # Button released
                try:
                    if keymap[0] == ButtonInputType.KEY:
                        kbd.release(*keymap[1])
                except ValueError:
                    pass
                self.button_state = 0


class RotaryEncoder(Button):
    def __init__(
        self,
        name: str,
        pin_a: board.Pin,
        pin_b: board.Pin,
        actions: tuple[callable, callable],
        pin_button: tuple[board.Pin, tuple[ButtonInputType, list]],
    ):
        super().__init__(pin_button)
        self.name = name
        self.actions = actions
        self.encoder = rotaryio.IncrementalEncoder(pin_a, pin_b)
        self.last_position = self.encoder.position

    def handle_encoder(self):
        num_actions = len(self.actions)

        current_position = self.encoder.position
        index = current_position % num_actions

        if current_position != self.last_position:
            if current_position > self.last_position:
                print(f"{self.name}: Clockwise")
                if num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[0]()
            else:
                print(f"{self.name}: Counterclockwise")
                if num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[1]()

            self.last_position = current_position

    def handle_button_encoder(self):
        self.handle_button()
        self.handle_encoder()


def main():

    encoder_1 = RotaryEncoder(
        "Encoder 1",
        pin_a=board.GP0,
        pin_b=board.GP1,
        actions=(lambda: mouse.move(wheel=-1), lambda: mouse.move(wheel=1)),
        pin_button=(board.GP5, (ButtonInputType.KEY, [Keycode.TWO])),
    )

    encoder_2 = RotaryEncoder(
        "Encoder 2",
        pin_a=board.GP3,
        pin_b=board.GP4,
        actions=(
            lambda: kbd.send(Keycode.CONTROL, Keycode.LEFT_BRACKET),
            lambda: kbd.send(Keycode.CONTROL, Keycode.RIGHT_BRACKET),
        ),
        pin_button=(board.GP2, (ButtonInputType.KEY, [Keycode.FIVE])),
    )

    encoder_3 = RotaryEncoder(
        "Encoder 3",
        pin_a=board.GP16,
        pin_b=board.GP17,
        actions=(
            lambda: kbd.send(Keycode.RIGHT_BRACKET),
            lambda: kbd.send(Keycode.LEFT_BRACKET),
        ),
        pin_button=(board.GP15, (ButtonInputType.KEY, [Keycode.SPACE])),
    )

    encoder_4 = RotaryEncoder(
        "Encoder 4",
        pin_a=board.GP12,
        pin_b=board.GP13,
        actions=(
            lambda: kbd.send(Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.ONE),
            lambda: kbd.send(Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.TWO),
            lambda: kbd.send(Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.THREE),
        ),
        pin_button=(board.GP14, (ButtonInputType.KEY, [Keycode.FORWARD_SLASH])),
    )

    while True:
        # Call handle_encoder() for each encoder, one after the other
        encoder_1.handle_button_encoder()
        encoder_2.handle_button_encoder()
        encoder_3.handle_button_encoder()
        encoder_4.handle_button_encoder()

        # Delay to prevent multiple fast triggers
        time.sleep(0.01)


if __name__ == "__main__":
    main()
