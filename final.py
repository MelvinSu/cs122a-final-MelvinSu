import smbus2
import time
import RPi.GPIO as GPIO
from threading import Thread
import bluetooth
import queue
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

default_temp_median = 77
default_humid_median = 60

FONTSIZE = 22
width = 320
height = 240

send_output_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(send_output_pin, GPIO.OUT)
on_cmd = '010000010101010111000011'
off_cmd = '010000010101010111001100'

bus = smbus2.SMBus(1)
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = ili9341.ILI9341(spi, rotation = 90, cs = cs_pin, dc = dc_pin, rst = reset_pin, baudrate=BAUDRATE)

image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', FONTSIZE)

def sleep_timer(delay, delay_increment):
    end_timer = time.time() + delay - delay_increment
    while time.time() < end_timer:
        time.sleep(delay_increment)

def send_command(code):
    for t in range(5):
        for i in code:
            if i == '1':
                GPIO.output(send_output_pin, 1)
                sleep_timer(.00045, .0000045)
                GPIO.output(send_output_pin, 0)
                sleep_timer(.00015, .0000015)
            else:
                GPIO.output(send_output_pin, 1)
                sleep_timer(.00015, .0000015)
                GPIO.output(send_output_pin, 0)
                sleep_timer(.00045, .0000045)
        GPIO.output(send_output_pin, 1)
        sleep_timer(.00015, .0000015)
        GPIO.output(send_output_pin, 0)
        sleep_timer(.00465, .0000465)

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
        
        if (temp_queue.empty() is False):
            temp_desired = temp_queue.get_nowait()
            print ("Changing temperature to ", temp_desired)
        if (humid_queue.empty() is False):
            humid_desired = humid_queue.get_nowait()
            print ("Changing humidity to ", humid_desired)

        if (humidity < humid_desired):
            if (fTemp > temp_desired - 10 and fTemp < temp_desired + 10):
                send_command(on_cmd)
                last_command = 1
                print("Turn on")
        elif (humidity > humid_desired + 10 or fTemp < temp_desired - 20 or fTemp > temp_desired + 20):
            send_command(off_cmd)
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

        print ("Desired temperature:", temp_desired, "\nDesired humidity:", humid_desired)
        print ("In Fahrenheit:", fTemp)
        print ("In Relative Humidity: %", humidity,"\n")



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
                        print(var)
                        temp_queue.put(int(var))
                        print ("Received temperature:", var)
                    elif ("change humid" in conv_data):
                        var = conv_data.partition("change humid")[2]
                        print (var)
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
