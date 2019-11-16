import RPi.GPIO as GPIO
from rpi_rf import RFDevice

rfdevice = RFDevice(17)
rfdevice.enable_tx()

GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

while (1):
    if GPIO.input(19) == GPIO.HIGH:
        rfdevice.tx_code(4281795, 1, 150)
        print("On button")
        
    elif GPIO.input(26) == GPIO.HIGH:
        rfdevice.tx_code(4281804, 1, 150)
        print("Off button")
