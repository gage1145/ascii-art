import PIL.Image
import os

# resize image according to a new width
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / (2.8 * width)
    print(ratio)
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
def pixels_to_ascii(image, simple=True):
    pixels = image.getdata()
    if simple:
        ASCII_CHARS = [i for i in "@#$%?*+;:,. "][::-1]
        characters = "".join([ASCII_CHARS[pixel//22] for pixel in pixels])
    else:
        ASCII_CHARS = [i for i in """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft\|(1}[?-_+~<i!lI;:,"^'. """][::-1]
        characters = "".join([ASCII_CHARS[pixel//4] for pixel in pixels])
    return(characters)    

def main(new_width=100, contrast=100, simple=True):
    # attempt to open image from user-input
    for file in os.listdir():
        if file.endswith(".jpg"):
            path = file
    try:
        image = PIL.Image.open(path)
    except:
        print(path, " is not a valid pathname to an image.")
        return
  
    # convert image to ascii    
    new_image_data = pixels_to_ascii(grayify(change_contrast(resize_image(image, new_width=new_width), contrast)), simple=simple)
    
    # format
    pixel_count = len(new_image_data)  
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    
    # print result
    print(ascii_image)
    
    # save result to "ascii_image.txt"
    with open("ascii_image.txt", "w") as f:
        f.write(ascii_image)
 
# run program
main(200, 300, False)