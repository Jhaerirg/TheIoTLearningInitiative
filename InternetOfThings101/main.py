#!/usr/bin/python

import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time
import dweepy
import client as mqtt
import json
import uuid
import pyupm_grove as grove

from threading import Thread

from flask import Flask
from flask_restful import Api, Resource

#----------------------------------------------
macAddress = hex(uuid.getnode())[2:-1]
macAddress = format(long(macAddress, 16),'012x')
#remind the user of the mac address further down in code (post 'connecitng to QS')

#Set the variables for connecting to the Quickstart service
organization = "quickstart"
deviceType = "iotsample-gateway"
broker = ""
topic  = "iot-2/evt/status/fmt/json"
username = ""
password = ""

error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)

try:
	file_object = open("./device.cfg")
	for line in file_object:			
			readType, readValue = line.split("=")			
			if readType == "org":	
			        organization = readValue.strip()
			elif readType == "type": 
				deviceType = readValue.strip()
			elif readType == "id": 
				macAddress = readValue.strip()
			elif readType == "auth-method": 
				username = "use-token-auth"
			elif readType == "auth-token": 
				password = readValue.strip()
			else:
				print("please check the format of your config file") #will want to repeat this error further down if their connection fails?
	
	file_object.close()										
	print("Configuration file found - connecting to the registered service")
		
except error_to_catch:
	print("No config file found, connecting to the Quickstart service")
	print("MAC address: " + macAddress)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

DeviceID="SensorDeviceJR"

app = Flask(__name__)
api = Api(app)

class DataSensorRestApi(Resource):
    def get(self): 
        data = 'Data from a (simulated) sensor'
        return data

api.add_resource(DataSensorRestApi, '/sensor')

def functionApiWeather():
    data = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = data['location']['name']
    message = message + ", Temperature " + data['current_conditions']['temperature'] + " C"
    message = message + ", Atmospheric Pressure " + data['current_conditions']['barometer']['reading'][:-3] + " mbar"
    return message

def functionDataActuator(status):
    # Create the relay switch object using GPIO pin 0
    relay = grove.GroveRelay(0)
    # Close and then open the relay switch,
    # waiting one second each time.  The LED on the relay switch
    # will light up when the switch is on (closed).
    # The switch will also make a noise between transitions.
    if status in ['On', 'ON', 'on']:
        relay.on()
        if relay.isOn():
            print relay.name(), 'is on'
        time.sleep(1)
    elif status in ['Off', 'OFF', 'off']:
        relay.off()
        if relay.isOff():
            print relay.name(), 'is off'
        time.sleep(1)
    else:
        print "Wrong option %s" % status

#def functionDataActuator(status):
#    print "Data Actuator Status %s" % status

def functionDataActuatorMqttOnMessage(mosq, obj, msg):
    print "Data Sensor Mqtt Subscribe Message!"
    functionDataActuator(msg.payload)

def functionDataActuatorMqttSubscribe():
    mqttclient = paho.Client()
    mqttclient.on_message = functionDataActuatorMqttOnMessage
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/"+DeviceID+"/DataActuator", 0)
    while mqttclient.loop() == 0:
        pass

def functionDataSensor():
    # Create the light sensor object using AIO pin 0
    light = grove.GroveLight(0)
    # Read the input and print both the raw value and a rough lux value,
    # waiting one second between readings
    # while 1:
    data = light.name() + " rawval: %d" % light.raw_value() + " lux: %d" % light.value();
    return data

#time.sleep(1)

#def functionDataSensor():
#    netdata = psutil.net_io_counters()
#    data = netdata.packets_sent + netdata.packets_recv
#    return data

def functionDataSensorMqttOnPublish(mosq, obj, msg):
    print "Data Sensor Mqtt Published!"

def functionDataSensorMqttPublish():
    mqttclient = paho.Client()
    mqttclient.on_publish = functionDataSensorMqttOnPublish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        data = functionDataSensor()
        topic = "IoT101/"+DeviceID+"/DataSensor"
        mqttclient.publish(topic, data)
        time.sleep(1)

#--------------------------------------------------------------------
def functionIBMWatsonIoT():
    #Creating the client connection
    #Set clientID and broker
    clientID = "d:" + organization + ":" + deviceType + ":" + macAddress
    broker = organization + ".messaging.internetofthings.ibmcloud.com"

    mqttc = mqtt.Client(clientID)

    #Set authentication values, if connecting to registered service
    if username is not "":
	mqttc.username_pw_set(username, password=password)

    mqttc.connect(host=broker, port=1883, keepalive=60)

    #Publishing to IBM Internet of Things Foundation
    mqttc.loop_start() 

    while mqttc.loop() == 0:
	msg = json.JSONEncoder().encode({"d":{"datasensor":functionDataSensor()}})	
	mqttc.publish(topic, payload=msg, qos=0, retain=False)
	print "message published"
	time.sleep(5)
	pass

def functionServicesDweet():
    dweepy.dweet_for('InternetOfThings101Dweet', {'DataSensor':functionDataSensor()})

#--------------------------------------------------------------------

def functionSignalHandler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, functionSignalHandler)

    # app.run(host='0.0.0.0', debug=True)
    
    threadmqttpublish = Thread(target=functionDataSensorMqttPublish)
    threadmqttpublish.start()

    threadmqttsubscribe = Thread(target=functionDataActuatorMqttSubscribe)
    threadmqttsubscribe.start()    

    #-----------------------------------------------------------------
    threadibmwatsoniot = Thread(target=functionIBMWatsonIoT)
    threadibmwatsoniot.start()
    #-----------------------------------------------------------------        

    while True:
        print "Hello Internet of Things 101"
        # print "Data Sensor: %s " % functionDataSensor()        
        print "API Weather: %s " % functionApiWeather()
        functionServicesDweet()
        time.sleep(5)

# End of File
