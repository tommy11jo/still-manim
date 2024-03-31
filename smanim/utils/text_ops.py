from pathlib import Path
from PIL import ImageFont


# in browser, can use foreign objects
# https://stackoverflow.com/questions/4991171/auto-line-wrapping-in-svg-text
# FUTURE: This will probably be its own text class, WText() "Web Text"
# locally, must implement text wrap manually, like I did below
# https://stackoverflow.com/questions/26276125/how-to-manipulate-svg-foreign-object-html-text-wrapping-and-positioning
def wrap_text(
    text: str,
    font_path: Path,
    font_size: int,
    max_width_in_pixels: int,
):
    # Getting the bbox takes ~0.0006 seconds locally (166 ops per 0.1 seconds)
    words = text.split(" ")
    text_tokens = []
    dims = []  # tracks dimensions of each text token
    font = ImageFont.truetype(font_path, font_size)
    x_size = font.getlength("x")
    approx_num_chars_per_line = int(max_width_in_pixels / x_size)
    if approx_num_chars_per_line == 0:
        raise ValueError("Approx num chars must be > 0")

    def get_dim_lens(text):
        left, top, right, bottom = font.getbbox(text)
        width = right - left
        height = bottom - top
        return width, height

    to_process = text
    word_ind = 0

    while word_ind < len(words):
        remaining_words = words[word_ind:]
        to_process = " ".join(remaining_words)
        width, height = get_dim_lens(to_process)
        if width < max_width_in_pixels:
            text_tokens.append(to_process)
            dims.append((width, height))
            break
        cur_ind = word_ind  # index in `words` of end of `cur_text`, exclusive
        cur_text = ""
        for word in remaining_words:
            if len(cur_text + word) <= approx_num_chars_per_line:
                cur_text += word
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
            width, height = get_dim_lens(one_back)
            text_tokens.append(one_back)
            dims.append((width, height))
            word_ind = cur_ind
        else:
            while width > max_width_in_pixels:
                cur_ind -= 1
                if cur_ind == 0:
                    # choosing to show the whole word and not wrap it, if it's too big for it's own line
                    cur_ind = 1
                    break

                cur_text = " ".join(words[word_ind:cur_ind])
                width, height = get_dim_lens(cur_text)

            text_tokens.append(cur_text)
            width, height = get_dim_lens(cur_text)
            dims.append((width, height))
            word_ind = cur_ind
    return text_tokens, dims
