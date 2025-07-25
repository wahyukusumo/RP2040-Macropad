import time
import board
import digitalio
import usb_hid
import rotaryio
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from rp2pio_dualincrementalencoder import DualIncrementalEncoder


# HID Type Tupple
class HIDType:
    KBD = Keyboard(usb_hid.devices)
    MOUSE = Mouse(usb_hid.devices)
    CC = ConsumerControl(usb_hid.devices)
    CC_CODE = ConsumerControlCode
    LAYOUT = KeyboardLayoutUS(KBD)


# Input Type Tupple
class ButtonInputType:
    MEDIA = 1  # this can be for volume, media player, brightness etc.
    KEY = 2  # Normal keyboard press & release
    CUSTOM = 3  # run lambda function


class Button:
    def __init__(
        self,
        pin_button: board.Pin | str,
        actions: tuple[ButtonInputType, callable],
        pin_interupt: board.Pin = None,
    ):
        self.button = self.init_button(pin_button)
        self.button_state = False
        self.actions = actions  # (ButtonInputType.args , [Keycode.A, Keycode.B])
        if pin_interupt:
            self.pin_interupt = self.init_button(pin_interupt)

    def init_button(self, button: board.Pin | str):
        # Button type string is for matrix
        if type(button) == str:
            return button

        # This is for button that use gpio in pico
        elif isinstance(button, microcontroller.Pin):
            button = DigitalInOut(button)
            button.direction = Direction.INPUT
            button.pull = Pull.UP  # Pull-up resistor enabled

        # And this for pin (PCF8574.get_pin) in expander like PCF8574
        else:
            button.switch_to_input(pull=digitalio.Pull.UP)

        return button

    def button_action(self, is_pressed: bool = None):
        # If bool is_pressed not set in argument
        # detect button straight from the pin
        if is_pressed == None:
            is_pressed = self.button.value

        input_type, keymap = self.actions

        if self.button_state == False and not is_pressed:  # Button pressed
            try:
                if input_type == ButtonInputType.KEY:
                    HIDType.KBD.press(*keymap)
                elif input_type == ButtonInputType.MEDIA:
                    HIDType.CC.send(keymap)
                elif input_type == ButtonInputType.CUSTOM:
                    keymap()

                # print("Button pressed")
            except ValueError:  # deals with six-key limit
                pass
            self.button_state = True

        if self.button_state == True and is_pressed:  # Button released
            try:
                if input_type == ButtonInputType.KEY:
                    HIDType.KBD.release(*keymap)
            except ValueError:
                pass
            self.button_state = False
            # print("Button released")

    def button_press(self):
        pass

    def button_action_with_interupt(self):
        try:
            # if not self.pin_interupt.value:
            self.button_action()
        except OSError as e:
            print(e)


# Original Rotary Encoder
class RotaryEncoder:
    def __init__(
        self,
        name: str,
        pin_a: board.Pin,
        pin_b: board.Pin,
        actions: tuple[callable, ...],
    ):
        super().__init__()
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
                # print(f"{self.name}: Clockwise")
                if num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[0]()
            else:
                # print(f"{self.name}: Counterclockwise")
                if num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[1]()

            self.last_position = current_position


class SplitRotaryEncoder:
    def __init__(
        self,
        name: str,
        encoder: rotaryio.IncrementalEncoder | DualIncrementalEncoder,
        index: int,
        actions: callable,
    ):
        self.name = name
        self.encoder = encoder  # use DualIncrementalEncoder
        self.index = index  # since using DualIncrementalEncoder require 4 pins and it split into 2 positions = (0,0)
        self.last_position = encoder.positions[index]
        self.actions = actions
        self.num_actions = len(actions)

    def encoder_action(self):
        current_position = self.encoder.positions[self.index]
        index = current_position % self.num_actions

        if current_position != self.last_position:
            # Clockwise action
            if current_position > self.last_position:
                # print(f"{self.name}: Clockwise")
                if self.num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[0]()

            # Counterclokwise action
            else:
                # print(f"{self.name}: Counterclockwise")
                if self.num_actions > 2:
                    self.actions[index]()
                else:
                    self.actions[1]()

            self.last_position = current_position
            return True


# This button matrix used PCF8574 for columns.
# Columns is the input and rows the output
class ButtonMatrix:
    def __init__(
        self, rows: list[board.Pin], columns: list[int], actions: callable, expander
    ):
        self.actions = actions
        self.expander = expander
        self.rows = self.init_matrix_by_gpio(rows)
        self.columns = self.init_matrix_by_expander(columns)
        self.buttons = self.init_button_matrix()

    def button_name(self, r, c):
        return f"R{r}C{c}"  # output: R0C0

    # This is input
    def init_matrix_by_expander(self, pin_list: list[int]):
        pins = [self.expander.get_pin(i) for i in pin_list]
        for pin in pins:
            pin.switch_to_input()
        return pins

    # This is output
    def init_matrix_by_gpio(self, pin_list: list[board.Pin]):
        pins = []

        for pin in pin_list:
            p = digitalio.DigitalInOut(pin)
            p.direction = digitalio.Direction.OUTPUT
            p.value = True
            pins.append(p)

        return pins

    def init_button_matrix(self):
        buttons = {}
        for r in range(len(self.rows)):
            for c in range(len(self.columns)):
                label = f"R{r}C{c}"  # output: R0C0
                buttons[label] = Button(pin_button=label, actions=self.actions[r][c])

        return buttons

    # Put this in while loop
    def matrix_scanning(self):
        for row_idx, row in enumerate(self.rows):
            for r in self.rows:
                r.value = True  # deactivate all rows
            row.value = False  # activate current row
            time.sleep(0.001)

            for col_idx, col in enumerate(self.columns):
                label = f"R{row_idx}C{col_idx}"
                is_pressed = not col.value  # return False
                button = self.buttons[label]

                if is_pressed != button.button_state:
                    button.button_action(is_pressed=not is_pressed)
