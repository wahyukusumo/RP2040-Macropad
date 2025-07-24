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
