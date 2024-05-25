import os
from pathlib import Path
from smanim.constants import DEFAULT_FONT_SIZE, LOW_RES, ORIGIN
from smanim.utils.color import BLACK, WHITE, ManimColor


__all__ = ["Config", "CONFIG"]

already_created = False


class Config:

    def __init__(
        self,
        density: float | None = None,
        frame_height: float | None = None,
        frame_width: float | None = None,
        frame_center: float | None = None,
        bg_color: ManimColor | None = None,
        save_file_dir: Path | None = None,
    ):
        global already_created
        if already_created:
            raise Exception("Can only create one config")
        already_created = True
        self.reset_config(
            density=density,
            frame_height=frame_height,
            frame_width=frame_width,
            frame_center=frame_center,
            bg_color=bg_color,
            save_file_dir=save_file_dir,
        )

    def reset_config(
        self,
        density: float | None = None,
        # uses 16:9 aspect ratio by default
        frame_height: float | None = None,
        frame_width: float | None = None,
        frame_center: float | None = None,
        bg_color: ManimColor | None = None,
        save_file_dir: Path | None = None,
        default_text_color: ManimColor = WHITE,
        default_text_font_size: int = DEFAULT_FONT_SIZE,
        default_text_font_family: str = "computer-modern",
    ):
        DEFAULT_DENSITY = LOW_RES
        DEFAULT_FRAME_HEIGHT = 8
        DEFAULT_FRAME_WIDTH = 14.222
        DEFAULT_FRAME_CENTER = ORIGIN
        DEFAULT_BG_COLOR = BLACK

        self.density = density if density is not None else DEFAULT_DENSITY
        self.fw = frame_width if frame_width is not None else DEFAULT_FRAME_WIDTH
        self.fh = frame_height if frame_height is not None else DEFAULT_FRAME_HEIGHT
        self.fc = frame_center if frame_center is not None else DEFAULT_FRAME_CENTER
        self.bg_color = bg_color if bg_color is not None else DEFAULT_BG_COLOR
        self.save_file_dir = (
            save_file_dir if save_file_dir is not None else Path(os.getcwd()) / "media"
        )

        # Calculate pixel dimensions based on the density
        self.pw = int(self.fw * self.density)  # pixel width
        self.ph = int(self.fh * self.density)  # pixel height
        self.mk_dir_attempted = False

        self.default_text_color = default_text_color
        self.default_text_font_size = default_text_font_size
        self.default_text_font_family = default_text_font_family

    def mk_save_dir_if_not_exists(self):
        if self.mk_dir_attempted:
            return
        self.save_file_dir.mkdir(parents=True, exist_ok=True)
        self.mk_dir_attempted = True


CONFIG = Config()
