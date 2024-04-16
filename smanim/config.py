import os
from pathlib import Path
from smanim.constants import LOW_RES, ORIGIN
from smanim.utils.color import BLACK, ManimColor


__all__ = ["Config", "CONFIG"]

already_created = False


class Config:

    def __init__(
        self,
        density: float = LOW_RES,
        # uses 16:9 aspect ratio by default
        frame_height: float = 8,
        frame_width: float = 14.222,
        frame_center: float = ORIGIN,
        bg_color: ManimColor | None = BLACK,
        save_file_dir: Path | None = Path(os.getcwd()) / "media",
        # FUTURE: testing vs in browser paths
    ):
        global already_created
        if already_created:
            raise Exception("Can only created one config")
        already_created = True

        self.density = density
        self.pw = int(frame_width * density)  # pixel width
        self.ph = int(frame_height * density)  # pixel height
        self.fw = frame_width
        self.fh = frame_height
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
