from pathlib import Path
from typing import List, Tuple
from PIL import ImageFont

# in browser, can use foreign objects
# https://stackoverflow.com/questions/4991171/auto-line-wrapping-in-svg-text
# FUTURE: This will probably be its own text class, WText() "Web Text"
# locally, must implement text wrap manually, like I did below
# https://stackoverflow.com/questions/26276125/how-to-manipulate-svg-foreign-object-html-text-wrapping-and-positioning


# FUTURE: Consider using fonttools to get raw glyph width and height
# https://gist.github.com/nitely/62b281dcfd15490e1ed21296d6be3113
# Actually this takes a lot more time, up to 0.18 seconds vs 0.05 seconds. The time is from loading the font. Unless if I load the font ahead of time, this won't work.
def wrap_text(
    text: str,
    font_path: Path,
    font_size: int,
    max_width_in_pixels: int,
) -> Tuple[List[str], List[Tuple[float, float]]]:
    """
    Returns a list where each element is the contents of a new line and a corresponding list containing (width, height) dimensions per line
    """
    # this entire function takes 0.006 seconds on 22 words, 4 lines wrapping
    words = text.split(" ")
    text_tokens = []
    dims = []  # tracks dimensions of each text token
    font = ImageFont.truetype(str(font_path), font_size)
    x_size = font.getlength("x")
    approx_num_chars_per_line = int(max_width_in_pixels / x_size)
    if approx_num_chars_per_line == 0:
        approx_num_chars_per_line += 1
        # raise ValueError("Approx num chars must be > 0")

    def get_dim_lens(text):
        # Getting the bbox takes ~0.0006 seconds locally (166 ops per 0.1 seconds)
        # Note: "aG" has different height than "aa"
        left, top, right, bottom = font.getbbox(text)
        width = right - left
        height = bottom - top

        # TODO: Fix bug. Why is width not working for getbbox or getlength
        # width = font.getlength(text)
        return width, height

    to_process = text
    word_ind = 0

    while word_ind < len(words):
        remaining_words = words[word_ind:]
        to_process = " ".join(remaining_words)
        width, height = get_dim_lens(to_process)
        if len(remaining_words) == 1 or width < max_width_in_pixels:
            text_tokens.append(to_process)
            dims.append((width, height))
            break
        cur_ind = word_ind  # index in `words` of end of `cur_text`, exclusive
        cur_text, *remaining_words = remaining_words
        for word in remaining_words:
            if len(cur_text + word) <= approx_num_chars_per_line:
                cur_text += " " + word
                cur_ind += 1
            else:
                break
        width, height = get_dim_lens(cur_text)
        if width < max_width_in_pixels:
            while width < max_width_in_pixels:
                cur_ind += 1
                if cur_ind > len(words):
                    break
                cur_text = " ".join(words[word_ind:cur_ind])
                width, height = get_dim_lens(cur_text)

            cur_ind -= 1
            one_back = " ".join(words[word_ind:cur_ind])
            # add extra space for copying and pasting smoothness, if not the last word
            if cur_ind != len(words):
                one_back += " "
            width, height = get_dim_lens(one_back)
            text_tokens.append(one_back)
            dims.append((width, height))
            word_ind = cur_ind
        else:
            while width > max_width_in_pixels:
                cur_ind -= 1
                # add extra space for copying and pasting smoothness, guaranteed not the last word
                cur_text = " ".join(words[word_ind:cur_ind]) + " "
                width, height = get_dim_lens(cur_text)
                if cur_ind == word_ind:
                    # choosing to show the whole word and not wrap it, if it's too big for it's own line
                    cur_ind = word_ind + 1
                    break

            text_tokens.append(cur_text)
            width, height = get_dim_lens(cur_text)
            dims.append((width, height))
            word_ind = cur_ind
    return text_tokens, dims
