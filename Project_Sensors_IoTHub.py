from base64 import b64encode, b64decode
from hashlib import sha256
from urllib import quote_plus, urlencode
from hmac import HMAC
import requests
import json
import os
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
GPIO.setup(soil, GPIO.IN)
GPIO.setup(ldr,GPIO.IN)

# Azure IoT Hub
URI = 'YOUR_IOT_HUB_NAME.azure-devices.net'
KEY = 'YOUR_IOT_HUB_PRIMARY_KEY'
IOT_DEVICE_ID = 'YOUR_REGISTED_IOT_DEVICE_ID'
POLICY = 'iothubowner'

def generate_sas_token():
    expiry=3600
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((quote_plus(URI)), int(ttl))
    signature = b64encode(HMAC(b64decode(KEY), sign_key, sha256).digest())

    rawtoken = {
        'sr' :  URI,
        'sig': signature,
        'se' : str(int(ttl))
    }

    rawtoken['skn'] = POLICY

    return 'SharedAccessSignature ' + urlencode(rawtoken)

#send message to IoT Hub
def send_message(token, message):
	url = 'https://{0}/devices/{1}/messages/events?api-version=2016-11-14'.format(URI, IOT_DEVICE_ID)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
	#make json format of message
    data = json.dumps(message)
    print (data)
    response = requests.post(url, data=data, headers=headers)

#Generate SAS Token
token = generate_sas_token()

while True:
	print ("Reading data from sensors...")
	#temperature and humidity sensor readings
    result = temp_hum.read()
    if result.is_valid():
		temperature=result.temperature
		humidity=result.humidity
        print("Last valid input: " + str(datetime.datetime.now()))
        print("Temperature: %d C" % temperature)
        print("Humidity: %d %%" % humidity)
		
	#soil measurement sensor readings
	if GPIO.input(soil):
	#'No water' = 1/True (sensor's microcontroller light is off).
		soil=0
		print("Soil: No water detected")
	else:
		soil=1
    #'Water' = 0/False (microcontroller light is on).
		print("Soil: Water detected!")
	
	#rain sensor readings
	if not no_rain.is_active:
		rain=1
        print("Rain: Rain detected")
	else:	
		rain=0
		print("Rain: No rain detected")
        
	#ldr sensor readings
	if GPIO.input(ldr):
		light=1
		print ("Light: Yes")
	else:
		light=0
		print ("Light: No")
	
	message = { "temp": str(temperature),
		"humy":str(humidity),
		"rain":str(rain),
		"soil":str(soil),
		"ldr":str(ldr)}
	print("Sending data to IoT Hub...")
    send_message(token, message)
		
    time.sleep(5)