import os
from pathlib import Path
from smanim.constants import ORIGIN
from smanim.utils.color import BLACK, ManimColor

__all__ = ["Config", "CONFIG"]

already_created = False


class Config:
    def __init__(
        self,
        pixel_height: float = 900,
        frame_height: float = 8,
        aspect_ratio: float = 16 / 9,
        frame_center: float = ORIGIN,
        bg_color: ManimColor = BLACK,
        save_file_dir: Path | None = Path(os.getcwd()) / "media",
        # FUTURE: testing vs in browser paths
    ):
        global already_created
        if already_created:
            raise Exception("Can only created one config")
        already_created = True
        self.ph = pixel_height
        self.pw = pixel_height * aspect_ratio
        self.fh = frame_height
        self.fw = frame_height * aspect_ratio
        self.aspect_ratio = aspect_ratio
        self.fc = frame_center
        self.bg_color = bg_color
        self.save_file_dir = save_file_dir
        self.mk_dir_attempted = False

    def mk_save_dir_if_not_exists(self):
        if self.mk_dir_attempted:
            return
        self.save_file_dir.mkdir(parents=True, exist_ok=True)
        self.mk_dir_attempted = True


CONFIG = Config()
