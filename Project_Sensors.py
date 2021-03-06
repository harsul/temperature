import RPi.GPIO as GPIO
import dht11
import time
import datetime
from gpiozero import InputDevice

# initialize GPIO
GPIO.setwarnings(False)
# Use the GPIO BCM pin numbering scheme.
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pins
temp_hum = dht11.DHT11(pin=14)
no_rain = InputDevice(18)
soil=21
ldr=4

# Receive input signals through the pin.


while True:
    print("Last valid input: " + str(datetime.datetime.now()))
    GPIO.setup(soil, GPIO.IN)
    GPIO.setup(ldr,GPIO.IN)
    #temperature and humidity sensor readings
    result = temp_hum.read()
    if result.is_valid():
        temperature = result.temperature
        humidity = result.humidity
        print("Temperature: %d C" % temperature)
        print("Humidity: %d %%" % humidity)
		
	#soil measurement sensor readings
    if GPIO.input(soil):
	#'No water' = 1/True (sensor's microcontroller light is off).
        soil_data=0
        print("Soil: No water detected")
    else:
        soil_data=1
    #'Water' = 0/False (microcontroller light is on).
        print("Soil: Water detected!")
	
	#rain sensor readings
    if not no_rain.is_active:
        rain_data=1
        print("Rain: Rain detected")
    else:
        rain_data=0
        print("Rain: No rain detected")
        
	#ldr sensor reading
    if GPIO.input(ldr):
        light_data=0
        print ("Light: No")
    else:
        light_data=1
        print ("Light: Yes")
		
    time.sleep(5)
