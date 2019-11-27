import smbus2
import time
import RPi.GPIO as GPIO
from rpi_rf import RFDevice
from threading import Thread
import bluetooth
import queue
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341


check_temp = 1
check_humid = 0

default_temp_median = 77
default_humid_median = 50

FONTSIZE = 24
i = 0

bus = smbus2.SMBus(1)
rf_device = RFDevice(17)
rf_device.enable_tx()

GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = ili9341.ILI9341(spi, rotation = 90, cs = cs_pin, dc = dc_pin, rst = reset_pin, baudrate=BAUDRATE)

if (disp.rotation % 180 == 90):
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONTSIZE)



def get_readings(temp_queue, humid_queue):
    temp_desired = temp_queue.get_nowait()
    humid_desired = humid_queue.get_nowait()
    last_command = 0
    while (1):
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])

        time.sleep(.5)

        data = bus.read_i2c_block_data(0x44, 0x00, 6)

        temp = data[0] * 256 + data[1]
        fTemp = -49 + (315 * temp/ 65535.0)
        humidity = (100 * data[3] * 256 + data[4]) / 65535.0

        print ("Desired temperature:", temp_desired, "\nDesired humidity:", humid_desired)
        print ("In Fahrenheit:", fTemp)
        print ("In Relative Humidity: %", humidity,"\n")
        
        if (temp_queue.empty() is False):
            temp_desired = temp_queue.get_nowait()
            print ("Changing temperature to ", temp_desired)
        if (humid_queue.empty() is False):
            humid_desired = humid_queue.get_nowait()
            print ("Changing humidity to ", humid_desired)
        if (fTemp > temp_desired + 2):
            rf_device.tx_code(4281795, 1, 150)
            last_command = 1
            print("Turn on")
        if (fTemp < temp_desired - 2):
            rf_device.tx_code(4281804, 1, 150)
            last_command = 0
            print("Turn off")

        draw.rectangle((0,0,width,height), fill=(0,0,0))
        str1 = "Desired Temp: " + str(temp_desired) + "°F"
        str2 = "Desired Humidity: " + str(humid_desired) + "%"
        str3 = "Current Temp: " + str('%.2f'%(fTemp)) + "°F"
        str4 = "Current Humidity: " + str('%.2f'%(humidity)) + "%"
        if (last_command == 1):
            str5 = "Humidifier is on"
        else:
            str5 = "Humidifier is off"
        draw.text((0,0), str1, font=font, fill= (255,255,255))
        draw.text((0,40), str2, font=font, fill= (255,255,255))
        draw.text((0,80), str3, font=font, fill= (255,255,255))
        draw.text((0,120), str4, font=font, fill= (255,255,255))
        draw.text((0, 200), str5, font=font, fill= (255,255,255))
        disp.image(image)

        time.sleep(1.5)

def bluetooth_change_values(temp_queue, humid_queue):
    while (1):
        try:
            server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            port = 1
            server_socket.bind(("",port))
            server_socket.listen(1)

            client_socket, addr = server_socket.accept()
            print ("Client connected")

            while(1):
                data = client_socket.recv(1024)
                conv_data = data.decode()
                if (conv_data):
                    if ("change temp" in conv_data):
                        var = conv_data.partition("change temp")[2]
                        temp_queue.put(int(var))
                        print ("Received temperature:", var)
                    if ("change humid percent " in conv_data):
                        var = conv_data.partition("change humid percent")[2]
                        humid_queue.put(int(var))
                        print ("Receieved humidity:", var)
                else:
                    print ("Data received: ", conv_data)
                
        except:
            server_socket.close()
            print("Lost connection to client, restarting bluetooth service...")

if __name__ == '__main__':
    temp_queue = queue.Queue()
    humid_queue = queue.Queue()
    temp_queue.put(default_temp_median)
    humid_queue.put(default_humid_median)
    Thread(target = get_readings, args=(temp_queue, humid_queue,)).start()
    Thread(target = bluetooth_change_values, args = (temp_queue, humid_queue,)).start()
