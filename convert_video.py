import cv2
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ASCII characters (densest to lightest)
ASCII_CHARS = "@#$%?*+;:,. "[::-1]

def video_to_ascii_video(input_file, output_file="ascii_output.mp4",
                         new_width=120, fps=30, fill = "#fff",
                         font_path="fonts/COUR.TTF", font_size=12):

    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open input video: {input_file}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ofps = int(cap.get(cv2.CAP_PROP_FPS))

    if fps > 30 or fps < 1: raise ValueError("fps can not be greater than 30 or less than 1.")
    new_frame_count = frame_count // (ofps // fps)
    frame_ratio = frame_count // new_frame_count

    # Load monospace font
    font = ImageFont.truetype(font_path, font_size)

    # Precompute font metrics
    bbox = font.getbbox("M")
    char_width = bbox[2] - bbox[0]
    ascent, descent = font.getmetrics()
    line_height = ascent + descent

    # ASCII lookup table
    lut = np.array(list(ASCII_CHARS), dtype="<U1")
    step = 256 // len(ASCII_CHARS)

    # Read first frame to determine output size
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Could not read first frame")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aspect_ratio = gray.shape[0] / gray.shape[1]
    new_height = int(new_width * aspect_ratio * 0.5)  # adjust for character aspect ratio
    resized = cv2.resize(gray, (new_width, new_height))

    ascii_arr = lut[np.clip(resized // step, 0, len(lut) - 1)]
    ascii_block = "\n".join("".join(row) for row in ascii_arr)

    # Calculate proper output size
    out_size = (char_width * new_width, line_height * new_height)

    # Setup VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, out_size)

    # Write first frame
    img = Image.new("RGB", out_size, "black")
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), ascii_block, fill=fill, font=font)
    out.write(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))

    # Process remaining frames
    frame_idx = 1
    new_frame_idx = 1
    while True:
        ret, frame = cap.read()
        if not ret: break

        if frame_idx % frame_ratio == 1:
            print(f"Exporting frame {new_frame_idx} of {new_frame_count}", end="\r")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (new_width, new_height))

            # Vectorized ASCII mapping
            ascii_arr = lut[np.clip(resized // step, 0, len(lut) - 1)]
            ascii_block = "\n".join("".join(row) for row in ascii_arr)

            img = Image.new("RGB", out_size, "black")
            draw = ImageDraw.Draw(img)
            draw.text((0, 0), ascii_block, fill=fill, font=font)

            frame_out = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame_out)
            new_frame_idx += 1

        frame_idx += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"\n✅ Saved ASCII video to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Usage: python ascii_video.py <input_video>")
    file = sys.argv[1]
    if not os.path.exists(file):
        raise ValueError(f"File {file} does not exist.")

    video_to_ascii_video(
        file,
        output_file="ascii_output.mp4",
        new_width=400,
        fps=15,
        fill="#95ffaf",
        font_path="fonts/CONSOLA.TTF",
        font_size=12
    )
