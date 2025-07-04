import time
import board
import macropad
from adafruit_hid.keycode import Keycode


def main():

    encoder_1 = macropad.RotaryEncoder(
        "Encoder 1",
        pin_a=board.GP0,
        pin_b=board.GP1,
        actions=(
            lambda: macropad.HIDType.MOUSE.move(wheel=-1),
            lambda: macropad.HIDType.MOUSE.move(wheel=1),
        ),
        pin_button=(board.GP5, (macropad.ButtonInputType.KEY, [Keycode.TWO])),
    )

    encoder_2 = macropad.RotaryEncoder(
        "Encoder 2",
        pin_a=board.GP3,
        pin_b=board.GP4,
        actions=(
            lambda: macropad.HIDType.KBD.send(Keycode.CONTROL, Keycode.LEFT_BRACKET),
            lambda: macropad.HIDType.KBD.send(Keycode.CONTROL, Keycode.RIGHT_BRACKET),
        ),
        pin_button=(board.GP2, (macropad.ButtonInputType.KEY, [Keycode.FIVE])),
    )

    encoder_3 = macropad.RotaryEncoder(
        "Encoder 3",
        pin_a=board.GP16,
        pin_b=board.GP17,
        actions=(
            lambda: macropad.HIDType.KBD.send(Keycode.RIGHT_BRACKET),
            lambda: macropad.HIDType.KBD.send(Keycode.LEFT_BRACKET),
        ),
        pin_button=(board.GP15, (macropad.ButtonInputType.KEY, [Keycode.SPACE])),
    )

    encoder_4 = macropad.RotaryEncoder(
        "Encoder 4",
        pin_a=board.GP12,
        pin_b=board.GP13,
        actions=(
            lambda: macropad.HIDType.KBD.send(
                Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.ONE
            ),
            lambda: macropad.HIDType.KBD.send(
                Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.TWO
            ),
            lambda: macropad.HIDType.KBD.send(
                Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.THREE
            ),
        ),
        pin_button=(
            board.GP14,
            (macropad.ButtonInputType.KEY, [Keycode.FORWARD_SLASH]),
        ),
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
