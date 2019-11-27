import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import adafruit_rgb_display.st7789 as st7789        # pylint: disable=unused-import
import adafruit_rgb_display.hx8357 as hx8357        # pylint: disable=unused-import
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
import adafruit_rgb_display.ssd1351 as ssd1351      # pylint: disable=unused-import
import adafruit_rgb_display.ssd1331 as ssd1331      # pylint: disable=unused-import
 
# First define some constants to allow easy resizing of shapes.
BORDER = 20
FONTSIZE = 24
 
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000
 
# Setup SPI bus using hardware SPI:
spi = board.SPI()
 
# pylint: disable=line-too-long
# Create the display:
#disp = st7789.ST7789(spi, rotation=90                             # 2.0" ST7789
#disp = st7789.ST7789(spi, height=240, y_offset=80, rotation=90    # 1.3", 1.54" ST7789
#disp = st7789.ST7789(spi, rotation=90, width=135, height=240, x_offset=53, y_offset=40, # 1.14" ST7789
#disp = hx8357.HX8357(spi, rotation=180,                           # 3.5" HX8357
#disp = st7735.ST7735R(spi, rotation=90,                           # 1.8" ST7735R
#disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,   # 1.44" ST7735R
#disp = st7735.ST7735R(spi, rotation=90, bgr=True,                 # 0.96" MiniTFT ST7735R
#disp = ssd1351.SSD1351(spi, rotation=180,                         # 1.5" SSD1351
#disp = ssd1351.SSD1351(spi, height=96, y_offset=32, rotation=180, # 1.27" SSD1351
#disp = ssd1331.SSD1331(spi, rotation=180,                         # 0.96" SSD1331
disp = ili9341.ILI9341(spi, rotation=90,                           # 2.2", 2.4", 2.8", 3.2" ILI9341
                       cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)
# pylint: enable=line-too-long
 
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width   # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width   # we swap height/width to rotate it to landscape!
    height = disp.height
 
image = Image.new('RGB', (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
i = 0
while(1):
    # Draw a green filled box as the background
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    

    # Load a TTF Font
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONTSIZE)
 

    # Draw Some Text

    text1 = "Desired Temperature:" + str(i)
    text2 = "Desired Humidity: " + str(i)
    text3 = "Current Temperature:" + str(i)
    text4 = "Current Humidity: " + str(i)
    i = i + 1
    draw.text((0, 0),
            text1, font=font, fill=(255, 255, 0))
    draw.text((0, 40),
            text2, font=font, fill=(255, 255, 255))
    draw.text((0, 80),
            text3, font=font, fill=(0, 255, 255))
    draw.text((0, 120),
            text4, font=font, fill=(255, 0, 255))
    print(width)
    print(width//2)
    print(width/2)
# Display image.
    disp.image(image)
