import subprocess


class Video:
    def __init__(self):
        self.location = ""
        self.name = ""

    def find_video_location(self):
        output = subprocess.run(
            ['zenity --file-selection --title="Select a File"'],
            shell=True,
            capture_output=True,
        )

        location_with_appendages = str(output).split(",")[2]
        location = location_with_appendages[10:-3]

        self.location = location

    def find_video_name(self):
        pass
