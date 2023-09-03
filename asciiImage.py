import modules.scripts as scripts
import gradio as gr
from PIL import Image, ImageDraw, ImageFont

from modules import images
from modules.processing import process_images, Processed
from modules.shared import opts, cmd_opts, state

ASCII_CHARS = ["@", "B", "%", "8", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", "\"", "^", "`", "'", ".", " "]

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width)
    return image.resize((new_width, new_height))

def image_to_greyscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return ascii_str

def image_to_ascii(image, new_width):
    image = resize_image(image, new_width)
    greyscale_image = image_to_greyscale(image)
    ascii_pixels = pixels_to_ascii(greyscale_image)
    ascii_image = "\n".join([ascii_pixels[i: i + greyscale_image.width] for i in range(0, len(ascii_pixels), greyscale_image.width)])
    return ascii_image

def ascii_to_image(ascii_str, block_size=10, kerning=0, font=ImageFont.load_default(), bg_color="white"):
    lines = ascii_str.split("\n")
    width = len(lines[0]) * block_size
    height = len(lines) * block_size

    # Map color names to RGB values
    color_map = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "cyan": (0, 255, 255),
    "brown": (139, 69, 19),
    "gray": (128, 128, 128),
    "lime": (0, 255, 0),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238),
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
    "beige": (245, 245, 220),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "maroon": (128, 0, 0)
    }

    # Set default background color if none is selected
    if not bg_color:
        bg_color = "white"

    # Get the RGB value for the background color
    bg_color_rgb = color_map.get(bg_color, (255, 255, 255))

    # Set text color based on background color
    text_color = (0, 0, 0) if bg_color != "black" else (255, 255, 255)

    img = Image.new("RGB", (width, height), color=color_map.get(bg_color, (255, 255, 255)))
    draw = ImageDraw.Draw(img)

    y = 0
    for line in lines:
        x = 0
        for char in line:
            draw.text((x + kerning, y), char, font=font, fill=text_color)
            x += block_size + kerning
        y += block_size

    return img

class Script(scripts.Script):

    def title(self):
        return "Convert to ASCII Art Image"

    def show(self, is_img2img):
        return is_img2img

    def ui(self, is_img2img):
        width = gr.Slider(minimum=50, maximum=200, step=1, value=100, label="ASCII Width")
        kerning = gr.Slider(minimum=0, maximum=10, step=1, value=0, label="Letter Spacing")
        font_size = gr.Slider(minimum=8, maximum=20, step=1, value=12, label="Font Size")
        font_type = gr.Dropdown(choices=["default", "Arial", "Courier New", "Times New Roman", "Comic Sans MS", "Verdana"], label="Font Type")
        bg_color = gr.Dropdown(choices=["white", "black", "red", "green", "blue", "yellow", "purple", "orange", "pink", "cyan", "brown", "gray", "lime", "indigo", "violet", "gold", "silver", "beige", "teal", "navy", "maroon"], label="Background Color")
        return [width, kerning, font_size, font_type, bg_color]

    def run(self, p, width, kerning, font_size, font_type, bg_color):
        proc = process_images(p)

        # Initialize font to a default value
        font = ImageFont.load_default()

        try:
            if font_type == "default":
                font = ImageFont.load_default()
            elif font_type == "Arial":
                font = ImageFont.truetype("arial.ttf", font_size)
            elif font_type == "Courier New":
                font = ImageFont.truetype("cour.ttf", font_size)
            elif font_type == "Times New Roman":
                font = ImageFont.truetype("times.ttf", font_size)
            elif font_type == "Comic Sans MS":
                font = ImageFont.truetype("comic.ttf", font_size)
            elif font_type == "Verdana":
                font = ImageFont.truetype("verdana.ttf", font_size)
        except IOError:
            print(f"Font {font_type} not found. Using default font.")
            font = ImageFont.load_default()

        for i in range(len(proc.images)):
            ascii_art = image_to_ascii(proc.images[i], width)
            ascii_img = ascii_to_image(ascii_art, block_size=font_size, kerning=kerning, font=font, bg_color=bg_color)
            proc.images[i] = ascii_img

        return proc
