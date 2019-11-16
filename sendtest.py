import time
from RPi import GPIO

def __init__( gpio):
    gpio = 17
    tx_enabled = True

    tx_pulselength = 150

    tx_repeat = 10
    tx_length = 24
    
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(self.gpio, GPIO.OUT)

    rawcode = format(4281795, '#0{}b'.format(self.tx_length + 2))[2:]

    for _ in range (0, tx_repeat):
        for byte in range(0, tx_length):
            if rawcode[byte] == '0':
                GPIO.output(17, GPIO.HIGH)
                self._sleep((highpulses * tx_pulselength) / 1000000)
                GPIO.output(17, GPIO.LOW)
                self._sleep((lowpulses * tx_pulselength)/ 1000000)
            else:

