import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.ili9341 as ili9341

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BAUDRATE = 24000000

spi = board.SPI()

disp = ili9341.ILI9341(spi, rotation = 90, cs = cs_pin, dc = dc_pin, rst = reset_pin, baudrate = BAUDRATE)

if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height
image = Image.new('RGB', (width, height))

draw = ImageDraw.Draw(image)

draw.rectangle((0,0,width,height), outline = 0, fill = (0,0,0))
disp.image(image)

image = Image.open("blinka.jpg")

image_ratio = image.width / image.height
screen_ratio = width / height
if (screen_ratio < image_ratio):
    scaled_width = image.width * height // image.height
    scaled_height = height
else:
    scaled_width = width
    scaled_height = image.height * width // image.width
image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

x = scaled_width // 2 - width // 2
y = scaled_height // 2 - height // 2
image = image.crop((x, y, x + width, y + height))

disp.image(image)
