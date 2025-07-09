class Deej:
    def __init__(self, programs: list):
        self.programs = programs  # Display name for program in list
        self.num_programs = len(programs)
        self.volumes = [50 for i in self.programs]
        self.current = 0
        self.display = self.refresh_display()

    def refresh_display(self):
        return f"{self.volumes[self.current]} - {self.programs[self.current]}"

    def cycle_programs(self, direction):
        # direction value is +1 or -1
        self.current = (self.current + direction) % self.num_programs
        # print(f"current = {self.current}")
        self.display = self.refresh_display()

    def clamp(self, val, min_val=0, max_val=100):
        return max(min_val, min(val, max_val))

    def change_volume(self, direction):
        # direction value is +2 or -2
        program_volume = self.volumes[self.current]
        self.volumes[self.current] = self.clamp(program_volume + direction)
        print(self.volumes)
        self.display = self.refresh_display()
