import tempfile

from PIL import Image, ImageDraw, ImageFont

white = (255, 255, 255)
black = (0, 0, 0)
reddit_red = (255, 69, 0)
font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 24)
title_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 50)
line_spacing = 10
title_width = [50.0, 175.0]
HEIGHT, WIDTH = 600, 800


def _wrap_text(text, font, max_text_width, background_drawer):
    lines = []
    words = text.split(' ')

    current_line = ""  # Counter to track when to wrap every other line

    for idx, word in enumerate(words, start=1):
        test_line = current_line + word + " "

        # Get the bounding box for the current test line
        bbox = background_drawer.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]  # Width of the text

        if text_width <= max_text_width:
            current_line = test_line
        else:
            if idx % 2 == 0:
                # Append the current line only every other time
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                # Join this line with the previous to simulate every-other-line wrapping
                current_line += word + " "
    # Increase the counter only on wrapping decisions

    if current_line:
        lines.append(current_line.strip())

    return lines


def create_reddit_image(username, text):
    reddit_post = Image.open("media/ai_reddit.jpg").convert("RGBA")
    reddit_drawer = ImageDraw.Draw(reddit_post)
    reddit_drawer.text((125, 40), f"u/{username}", font=font, fill=black)

    wrapped_text = _wrap_text(text, font, HEIGHT, reddit_drawer)

    x, y = (55, 150)
    for line in wrapped_text:
        reddit_drawer.text((x, y), line, font=font, fill=black)
        y += font.size + line_spacing

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        reddit_post.save(temp_file.name)  # Save the image to the temp file
        temp_filename = temp_file.name  # Store the temp file's name

    return temp_filename
