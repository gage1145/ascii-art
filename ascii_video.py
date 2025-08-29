import cv2
import os
import sys
import time
from PIL import Image

# ascii characters used to build the output text
ASCII_CHARS = [i for i in """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft\|(1}[?-_+~<i!lI;:,"^'. """][::-1]
ASCII_CHARS_SHORT = [i for i in "@#$%?*+;:,. "][::-1]


# convert video into list of PIL images
def convert_video(file):
    cap = cv2.VideoCapture(file)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        frames.append(pil_image)
    cap.release()
    cv2.destroyAllWindows()
    return frames


# resize image according to a new width
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / (1.9 * width)
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image


def change_contrast(img, level=100):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


# convert each pixel to grayscale
def grayify(image):
    return image.convert("L")


# convert pixels to a string of ascii characters
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS_SHORT[pixel // 22] for pixel in pixels])
    return characters


def image_to_ascii(image, new_width=75, contrast=0):
    # convert image to ascii    
    new_image_data = pixels_to_ascii(
        grayify(
            change_contrast(
                resize_image(image, new_width=new_width),
                contrast
            )
        )
    )

    # format
    pixel_count = len(new_image_data)
    ascii_image = "\n".join(
        [new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)]
    )

    return ascii_image


if __name__ == "__main__":
    nargs = len(sys.argv)
    if nargs != 2:
        raise ValueError(f"Expected only 1 argument. Received {nargs}")
    file = sys.argv[1]
    if not os.path.exists(file):
        raise ValueError(f"File {file} does not exist.")

    # grab frames directly in memory
    frames = convert_video(file)

    # convert all frames to ascii strings
    movie = [image_to_ascii(frame, 100, 0) for frame in frames]

    # play ascii animation
    for ascii_frame in movie:
        os.system("cls" if os.name == "nt" else "clear")
        print(ascii_frame)
        time.sleep(0.0167)  # ~60 fps
