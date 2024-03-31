from smanim.constants import ORIGIN
from smanim.utils.color import BLACK, ManimColor


class Config:
    def __init__(
        self,
        pixel_height: float = 900,
        frame_height: float = 8,
        aspect_ratio: float = 16 / 9,
        frame_center: float = ORIGIN,
        bg_color: ManimColor = BLACK,
        save_file_dir: str = "/Users/tommyjoseph/Desktop/projects/still-manim/examples/media/",
    ):
        self.ph = pixel_height
        self.pw = pixel_height * aspect_ratio
        self.fh = frame_height
        self.fw = frame_height * aspect_ratio
        self.aspect_ratio = aspect_ratio
        self.fc = frame_center
        self.bg_color = bg_color
        self.save_file_dir = save_file_dir


CONFIG = Config()
