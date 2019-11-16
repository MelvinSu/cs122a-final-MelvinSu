import smbus
import time

#init function
bus = smbus.SMBus(1)

#???
bus.write_i2c_block_data(0x44, 0x2C, [0x06])

#Most likely needs time to process
time.sleep(.5)

#0x44 is device address
#Unsure how 0x00 is data read back
#6 bytes of data will be received
#returns temp msb, temp lsb, temp crc, humid msb, humit lsb, humid crc in array format
data = bus.read_i2c_block_data(0x44, 0x00, 6)

#all conversions
temp = data[0] * 256 + data[1]
cTemp = -45 + (175 * temp/ 65535.0)
fTemp = -49 + (315 * temp/ 65535.0)
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

#all outputs
print ("In Celsius:",cTemp)
print ("In Fahrenheit:",fTemp)
print ("In Relative Humidity: %",humidity)
