import PIL.Image
import cv2
import os
import sys
import time



# ascii characters used to build the output text
ASCII_CHARS = [i for i in """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft\|(1}[?-_+~<i!lI;:,"^'. """][::-1]
ASCII_CHARS_SHORT = [i for i in "@#$%?*+;:,. "][::-1]

# Convert video frames to individual images
def convert_video(file):
    cap = cv2.VideoCapture(file)
    try:
        if not os.path.exists("images"):
            os.makedirs("images")
    except OSError:
        print("Error: Creating directory of images.")
    
    current_frame = 1
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Saves image of the current frame in jpg file
        name = "./images/frame" + "_" + str(current_frame) + ".jpg"
        try:
            cv2.imwrite(name, frame)
            print("Creating..." + name, end="\r")
            current_frame += 1
        except:
            break
    cap.release()
    cv2.destroyAllWindows()

# resize image according to a new width
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / (1.9 * width)
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return(resized_image)

def change_contrast(img, level=100):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)

# convert each pixel to grayscale
def grayify(image):
    grayscale_image = image.convert("L")
    return(grayscale_image)
    
# convert pixels to a string of ascii characters
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS_short[pixel//22] for pixel in pixels])
    return(characters)    

def main(path, new_width=100, contrast=100):
    try:
        image = PIL.Image.open(path)
    except:
        print(path, " is not a valid pathname to an image.")
        return
  
    # convert image to ascii    
    new_image_data = pixels_to_ascii(grayify(change_contrast(resize_image(image, new_width=new_width), contrast)))
    
    # format
    pixel_count = len(new_image_data)  
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    
    # Return result
    return ascii_image

if __name__ == "__main__":
    nargs = len(sys.argv)
    if nargs != 2:
        raise ValueError(f"Expected only 1 argument. Received {nargs}")
    file = sys.argv[1]
    if not os.listdir("images"):
        if not os.path.exists(file):
            raise ValueError(f"File {file} does not exist. ")
        convert_video(file)

    movie = []
    images = os.listdir("images")
    for i in range(len(images)):
        image = os.path.join("images", images[i])
        movie.append(main(image, 200, 0))

    for i in range(len(images)):
        os.system("cls")
        print(movie[i])
        time.sleep(0.0167)
