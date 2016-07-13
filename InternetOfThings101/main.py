#!/usr/bin/python

import paho.mqtt.client as paho
import psutil
import signal
import sys
import time

from threading import Thread

def functionDataActuator():
    print "Data Actuator"

def functionDataSensor():
    netdata = psutil.net_io_counters()
    data = netdata.packets_sent + netdata.packets_recv
    return data

def functionDataSensorMqttOnPublish(mosq, obj, msg):
    print "Data Sensor Mqtt Published!"

def functionDataSensorMqttPublish():
    mqttclient = paho.Client()
    mqttclient.on_publish = functionDataSensorMqttOnPublish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        data = functionDataSensor()
        topic = "IoT101/DataSensor"
        mqttclient.publish(topic, data)
        time.sleep(1)

def functionSignalHandler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, functionSignalHandler)

    threadmqttpublish = Thread(target=functionDataSensorMqttPublish)
    threadmqttpublish.start()

    while True:
        print "Hello Internet of Things 101"
        print "Data Sensor: %s " % functionDataSensor()
        time.sleep(5)

# End of File
