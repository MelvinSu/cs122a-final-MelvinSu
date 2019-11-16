import smbus
import time
import RPi.GPIO as GPIO
from rpi_rf import RFDevice

bus = smbus.SMBus(1)
rf_device = RFDevice(17)
rf_device.enable_tx()

GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

while (1):
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])

    time.sleep(.5)

    data = bus.read_i2c_block_data(0x44, 0x00, 6)

    temp = data[0] * 256 + data[1]
    fTemp = -49 + (315 * temp/ 65535.0)
    humidity = (100 * data[3] * 256 + data[4]) / 65535.0

    print ("In Fahrenheit:", fTemp)
    print ("In Relative Humidity: %", humidity,"\n")
    
    if GPIO.input(19) == GPIO.HIGH:
        rf_device.tx_code(4281795, 1, 150)
        print("Activate switch")
    elif GPIO.input(26) == GPIO.HIGH:
        rf_device.tx_code(4281804, 1, 150)
        print("Deactivate switch")
    """
    
    if (fTemp > 79):
        rf_device.tx_code(4281795, 1, 150)
        print("Turn on")
    if (fTemp < 78):
        rf_device.tx_code(4281804, 1, 150)
        print("Turn off")

    """
    print('')

    time.sleep(1.5)
