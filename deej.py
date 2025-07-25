import os

DEFAULT_DIGITAL_VOLUME = 50
MIN_DIGITAL_VOLUME = 0
MAX_DIGITAL_VOLUME = 100
MAX_ANALOG_VOLUME = 1023


class Deej:
    def __init__(self, programs: list):
        self.programs = programs  # Display name for program in list
        self.num_programs = len(programs)
        self.volumes = [DEFAULT_DIGITAL_VOLUME for i in self.programs]
        self.current = 0
        self.display = self.refresh_display()

    def create_or_get_volumes(self):
        filename = "deej.csv"
        if filename not in os.listdir("/"):
            with open(filename, "w") as f:
                data = ",".join(str(DEFAULT_DIGITAL_VOLUME) for i in self.num_programs)
                f.write(data)
        else:
            with open(filename, "r") as file:
                self.volumes = file.strip().split(",")

    def refresh_display(self):
        return f"{self.volumes[self.current]}\n{self.programs[self.current]}"

    def cycle_programs(self, direction: int):
        # direction value is +1 or -1
        self.current = (self.current + direction) % self.num_programs
        # print(f"current = {self.current}")
        self.display = self.refresh_display()

    def clamp(self, val, min_val=MIN_DIGITAL_VOLUME, max_val=MAX_DIGITAL_VOLUME):
        return max(min_val, min(val, max_val))

    def analog_value(self, value: int):
        return round(value * MAX_ANALOG_VOLUME / MAX_DIGITAL_VOLUME)

    def send_to_serial(self):
        analog_value = [self.analog_value(v) for v in self.volumes]
        volumes = map(str, analog_value)
        serialize = "|".join(volumes)
        print(serialize)

    def change_volume(self, direction: int):
        # direction value is +2 or -2
        program_volume = self.volumes[self.current]
        self.volumes[self.current] = self.clamp(program_volume + direction)
        self.send_to_serial()
        self.display = self.refresh_display()
