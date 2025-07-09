import os


class Deej:
    def __init__(self, programs: list):
        self.current = 0
        self.programs = programs  # Display name for program in list
        self.num_programs = len(programs)
        self.volumes = self.create_or_get_volumes()
        self.display = self.refresh_display()

    def create_or_get_volumes(self):
        filename = "deej.csv"
        if filename not in os.listdir("."):
            with open(filename, "w") as f:
                data = [50 for i in range(self.num_programs)]
                f.write(",".join(str(v) for v in data))
        else:
            with open(filename, "r") as file:
                data = file.readline().strip().split(",")

        return data

    def refresh_display(self):
        return f"{self.volumes[self.current]}\n{self.programs[self.current]}"

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


if __name__ == "__main__":
    programs = ["Master", "Firefox", "Spotify", "Discord", "Apex Legends"]
    deej = Deej(programs)
    print(deej.volumes)
