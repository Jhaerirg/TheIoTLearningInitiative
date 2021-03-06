#!/usr/bin/python

import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time

from threading import Thread

from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

DeviceID="SensorDeviceJR"

class SensorRestApi(Resource)
    def get(self):
        data = 'Data from a (simulated) sensor'
        return data

def functionApiWeather():
    data = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = data['location']['name']
    message = message + ", Temperature " + data['current_conditions']['temperature'] + " C"
    message = message + ", Atmospheric Pressure " + data['current_conditions']['barometer']['reading'][:-3] + " mbar"
    return message

def functionDataActuator(status):
    print "Data Actuator Status %s" % status

def functionDataActuatorMqttOnMessage(mosq, obj, msg):
    print "Data Sensor Mqtt Subscribe Message!"
    functionDataActuator(msg.payload)

def functionDataActuatorMqttSubscribe():
    mqttclient = paho.Client()
    mqttclient.on_message = functionDataActuatorMqttOnMessage
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/SensorDeviceJR/DataActuator", 0)
    while mqttclient.loop() == 0:
        pass

def functionDataSensor():
    app.run(host='0.0.0.0', debug=True)
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
        topic = "IoT101/SensorDeviceJR/DataSensor"
        mqttclient.publish(topic, data)
        time.sleep(1)

def functionSignalHandler(signal, frame):
    sys.exit(0)

api.add_resource(SensorRestApi, '/sensor')

if __name__ == '__main__':

    signal.signal(signal.SIGINT, functionSignalHandler)

    threadSimulatedSensor

    threadmqttpublish = Thread(target=functionDataSensorMqttPublish)
    threadmqttpublish.start()

    threadmqttsubscribe = Thread(target=functionDataActuatorMqttSubscribe)
    threadmqttsubscribe.start()

    while True:
        print "Hello Internet of Things 101"
        print "Data Sensor: %s " % functionDataSensor()
        print "API Weather: %s " % functionApiWeather()
        time.sleep(5)

# End of File
