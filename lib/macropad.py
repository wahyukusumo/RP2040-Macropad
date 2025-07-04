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


class HIDType:
    KBD = Keyboard(usb_hid.devices)
    MOUSE = Mouse(usb_hid.devices)
    CC = ConsumerControl(usb_hid.devices)
    LAYOUT = KeyboardLayoutUS(KBD)


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
                        HIDType.KBD.press(*keymap[1])
                    elif keymap[0] == ButtonInputType.LETTER:
                        for letter in keymap[1][0]:
                            layout.write(letter)
                        if keymap[1][1] == ButtonInputType.NEW_LINE:
                            HIDType.KBD.press(*[Keycode.RETURN])
                            HIDType.KBD.release(*[Keycode.RETURN])
                    elif keymap[0] == ButtonInputType.MEDIA:
                        cc.send(keymap[1][0])
                except ValueError:  # deals with six-key limit
                    pass
                self.button_state = 1

        if self.button_state == 1:
            if self.button.value:  # Button released
                try:
                    if keymap[0] == ButtonInputType.KEY:
                        HIDType.KBD.release(*keymap[1])
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
