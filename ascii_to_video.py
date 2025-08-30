import cv2
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ASCII characters (densest to lightest)
ASCII_CHARS_SHORT = [i for i in "@#$%?*+;:,. "][::-1]


def resize_image(image, new_width=100):
    """Resize image preserving aspect ratio, adjusted for ASCII font ratio."""
    width, height = image.size
    ratio = height / (1.9 * width)
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def change_contrast(img, level=100):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c): return 128 + factor * (c - 128)
    return img.point(contrast)


def grayify(image):
    return image.convert("L")


def pixels_to_ascii(image):
    pixels = image.getdata()
    return "".join([ASCII_CHARS_SHORT[pixel // 22] for pixel in pixels])


def image_to_ascii(image, new_width=100, contrast=100):
    """Convert a PIL image to ASCII string."""
    new_image_data = pixels_to_ascii(
        grayify(
            change_contrast(
                resize_image(image, new_width=new_width),
                contrast
            )
        )
    )
    pixel_count = len(new_image_data)
    ascii_image = "\n".join(
        [new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)]
    )
    return ascii_image


def calc_output_size(ascii_str, font):
    """Calculate output size for a monospace font."""
    lines = ascii_str.split("\n")
    num_lines = len(lines)
    max_chars = max(len(line) for line in lines)

    # width/height of one character cell
    bbox = font.getbbox("M")
    char_width = bbox[2] - bbox[0]
    line_height = bbox[3] - bbox[1]

    out_w = char_width * max_chars
    out_h = line_height * num_lines
    return (out_w, out_h)


def ascii_to_image(ascii_str, size, font, font_size=12):
    """Render ASCII text into a fixed-size PIL image."""
    lines = ascii_str.split("\n")
    bbox = font.getbbox("M")
    line_height = bbox[3] - bbox[1]

    img = Image.new("RGB", size, "black")
    draw = ImageDraw.Draw(img)

    y = 0
    for line in lines:
        draw.text((0, y), line, fill="white", font=font)
        y += line_height
        if y >= size[1]:
            break
    return img


def video_to_ascii_video(input_file, output_file="ascii_output.mp4",
                         new_width=120, contrast=0, fps=30,
                         font_path=None, font_size=12):

    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file {input_file}")

    # load a monospace font
    if font_path is None:
        # fallback: DejaVuSansMono (Linux/Mac) or Consolas (Windows)
        if os.name == "nt":
            font_path = "C:\\Windows\\Fonts\\consola.ttf"
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

    font = ImageFont.truetype(font_path, font_size)

    # read first frame to determine output size
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Could not read first frame")

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    ascii_str = image_to_ascii(pil_image, new_width, contrast)

    # calculate proper size
    out_size = calc_output_size(ascii_str, font)

    # setup VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, out_size)

    # process first frame
    ascii_img = ascii_to_image(ascii_str, out_size, font, font_size)
    frame_out = cv2.cvtColor(np.array(ascii_img), cv2.COLOR_RGB2BGR)
    out.write(frame_out)

    # process remaining frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        ascii_str = image_to_ascii(pil_image, new_width, contrast)
        ascii_img = ascii_to_image(ascii_str, out_size, font, font_size)

        frame_out = cv2.cvtColor(np.array(ascii_img), cv2.COLOR_RGB2BGR)
        out.write(frame_out)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Saved ASCII video to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Usage: python ascii_video.py <input_video>")
    file = sys.argv[1]
    if not os.path.exists(file):
        raise ValueError(f"File {file} does not exist.")

    video_to_ascii_video(file,
                         output_file="ascii_output.mp4",
                         new_width=200,
                         contrast=100,
                         fps=30,
                         font_size=12)
