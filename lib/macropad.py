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


class HIDType:
    KBD = Keyboard(usb_hid.devices)
    MOUSE = Mouse(usb_hid.devices)
    CC = ConsumerControl(usb_hid.devices)
    CC_CODE = ConsumerControlCode
    LAYOUT = KeyboardLayoutUS(KBD)


class ButtonInputType:
    MEDIA = 1  # this can be for volume, media player, brightness etc.
    KEY = 2  # Keyboard press
    LETTER = 3  # Text string
    NEW_LINE = "NEW_LINE"


class Button:
    def __init__(self, pin_button, actions, pin_interupt=None):
        self.button = self.init_button(pin_button)
        self.button_state = False
        self.actions = actions
        if pin_interupt:
            self.pin_interupt = self.init_button(pin_interupt)

    def init_button(self, button):
        # Button type string is for matrix
        if type(button) == str:
            return button
        # This is for button that use gpio in pico
        elif isinstance(button, microcontroller.Pin):
            button = DigitalInOut(button)
            button.direction = Direction.INPUT
            button.pull = Pull.UP  # Pull-up resistor enabled
        # And this for pin in expander like PCF8574
        else:
            button.switch_to_input(pull=Pull.UP)

        return button

    def button_action(self, is_pressed=None):
        # If bool is_pressed not set in argument
        # detect button straight from the pin
        if is_pressed == None:
            is_pressed = self.button.value

        keymap = self.actions

        if self.button_state == False and not is_pressed:  # Button pressed
            try:
                if keymap[0] == ButtonInputType.KEY:
                    HIDType.KBD.press(*keymap[1])
                elif keymap[0] == ButtonInputType.LETTER:
                    for letter in keymap[1][0]:
                        HIDType.LAYOUT.write(letter)
                    if keymap[1][1] == ButtonInputType.NEW_LINE:
                        HIDType.KBD.press(*[Keycode.RETURN])
                        HIDType.KBD.release(*[Keycode.RETURN])
                elif keymap[0] == ButtonInputType.MEDIA:
                    HIDType.CC.send(keymap[1][0])

                # print("Button pressed")
            except ValueError:  # deals with six-key limit
                pass
            self.button_state = True

        if self.button_state == True and is_pressed:  # Button released
            try:
                if keymap[0] == ButtonInputType.KEY:
                    HIDType.KBD.release(*keymap[1])
            except ValueError:
                pass
            self.button_state = False
            # print("Button released")

    def button_action_with_interupt(self):
        try:
            # if not self.pin_interupt.value:
            self.button_action()
        except OSError as e:
            print(e)


# Original Rotary Encoder
class RotaryEncoder(Button):
    def __init__(
        self,
        name: str,
        pin_a: board.Pin,
        pin_b: board.Pin,
        actions: tuple[callable, ...],
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

    def handle_button_encoder(self):
        self.button_action()
        self.handle_encoder()


class SplitRotaryEncoder:
    def __init__(self, name, encoder, index, actions):
        self.name = name
        self.encoder = encoder
        self.index = index
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


# This button matrix used PCF8574 for columns.
# Columns is the input and rows the output
class ButtonMatrix:
    def __init__(self, rows, columns, actions, expander):
        self.actions = actions
        self.expander = expander
        self.rows = self.init_matrix_by_gpio(rows)
        self.columns = self.init_matrix_by_expander(columns)
        self.buttons = self.init_button_matrix()

    def button_name(self, r, c):
        return f"R{r}C{c}"  # output: R0C0

    # This is input
    def init_matrix_by_expander(self, pin_list):
        pins = [self.expander.get_pin(i) for i in pin_list]
        for pin in pins:
            pin.switch_to_input()
        return pins

    # This is output
    def init_matrix_by_gpio(self, pin_list):
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
