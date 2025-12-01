import board

IO_EXPANDER_PINS = {"SDA": board.GP12, "SCL": board.GP13}
MATRIX_IO_EXPANDER_ADDRESS = 0x25
BUTTON_IO_EXPANDER_ADDRESS = 0x20
DEEJ_PROGRAMS = ["Master", "Firefox", "Spotify", "Discord", "Apex"]

USE_DEEJ = False
DISPLAY_PINS = {
    "CLOCK": board.GP18,
    "MOSI": board.GP19,
    "CS": board.GP20,
    "DC": board.GP21,
    "RESET": board.GP22,
    "BL": board.GP23,
    "ROTATION": 180,
}

MATRIX_ROW_PINS = [board.GP14, board.GP15, board.GP17, board.GP24]
MATRIX_COL_PINS = [0, 1, 2, 3, 4]

ROTARY_ENCODERS_NUM = 6
ROTARY_ENCODERS_PHYSICAL_ORDER = [1, 6, 4, 2, 5, 3]
"""This is for physical order of rotary encoder, in practice your physical 
rotary encoder position must same as gpio pin, like:

|ENC1 (gpio 0, gpio 1)|ENC2 (gpio 2, gpio 3)|
|ENC3 (gpio 4, gpio 5)|ENC4 (gpio 6, gpio 7)|
|ENC5 (gpio 8, gpio 9)|ENC6 (gpio 10, gpio 11)|

but if your wiring not in order, you still can reorder it
without changing the wiring.
"""


def input_map(screen, deej, BiT, key, hid, cc_code):
    ENCODERS = [
        {  # Encoder 1
            "actions": (
                # lambda: SCREEN.change_brightness(-1),
                # lambda: SCREEN.change_brightness(+1),
                lambda: hid.KBD.send(key.CONTROL, key.Z),
                lambda: hid.KBD.send(key.CONTROL, key.SHIFT, key.Z),
            ),
            "button": {"pin": 1, "actions": (BiT.KEY, [key.ONE])},
        },
        {  # Encoder 2
            "actions": (
                # lambda: DEEJ.change_volume(-5),
                # lambda: DEEJ.change_volume(+5),
                lambda: SCREEN.change_brightness(-1),
                lambda: SCREEN.change_brightness(+1),
            ),
            "button": {"pin": 0, "actions": (BiT.KEY, [key.TWO])},
        },
        {  # Encoder 3
            "actions": (
                lambda: hid.MOUSE.move(wheel=-1),
                lambda: hid.MOUSE.move(wheel=1),
            ),
            "button": {"pin": 3, "actions": (BiT.KEY, [key.TWO])},
        },
        {  # Encoder 4
            "actions": (
                lambda: hid.KBD.send(key.CONTROL, key.LEFT_BRACKET),
                lambda: hid.KBD.send(key.CONTROL, key.RIGHT_BRACKET),
            ),
            "button": {"pin": 2, "actions": (BiT.KEY, [key.FIVE])},
        },
        {  # Encoder 5
            "actions": (
                lambda: hid.KBD.send(key.CONTROL, key.Z),
                lambda: hid.KBD.send(key.CONTROL, key.SHIFT, key.Z),
            ),
            "button": {"pin": 4, "actions": (BiT.KEY, [key.FIVE])},
        },
        {  # Encoder 6
            "actions": (
                lambda: hid.KBD.send(key.CONTROL, key.ALT, key.ONE),
                lambda: hid.KBD.send(key.CONTROL, key.ALT, key.TWO),
                lambda: hid.KBD.send(key.CONTROL, key.ALT, key.THREE),
            ),
            "button": {"pin": 5, "actions": (BiT.KEY, [key.FORWARD_SLASH])},
        },
    ]

    KEYPADS = [
        [  # Row 1
            (BiT.CUSTOM, lambda: DEEJ.cycle_programs(-1)),
            (BiT.MEDIA, cc_code.SCAN_PREVIOUS_TRACK),
            (BiT.MEDIA, cc_code.PLAY_PAUSE),
            (BiT.MEDIA, cc_code.SCAN_NEXT_TRACK),
            (BiT.CUSTOM, lambda: DEEJ.cycle_programs(+1)),
        ],
        [  # Row 2
            (BiT.KEY, [key.INSERT]),
            (BiT.KEY, [key.SHIFT, key.DELETE]),
            (BiT.KEY, [key.CONTROL, key.ALT, key.SHIFT, key.V]),
            (BiT.KEY, [key.CONTROL, key.T]),
            (BiT.KEY, [key.CONTROL, key.SHIFT, key.A]),
        ],
        [  # Row 3
            (BiT.KEY, [key.SPACE]),
            (BiT.KEY, [key.B]),
            (BiT.KEY, [key.M]),
            (BiT.KEY, [key.N]),
            (BiT.KEY, [key.O]),
        ],
        [  # Row 4
            (BiT.KEY, [key.SHIFT]),
            (BiT.KEY, [key.CONTROL]),
            (BiT.KEY, [key.R]),
            (BiT.KEY, [key.S]),
            (BiT.KEY, [key.T]),
        ],
    ]

    return ENCODERS, KEYPADS
