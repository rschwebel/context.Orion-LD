#!/usr/bin/env .venv/bin/python
# -*- coding: latin-1 -*-
# Copyright 2019 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of Orion Context Broker.
#
# Orion Context Broker is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Orion Context Broker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.
#
# For those usages not covered by this license please contact with
# iot_support at tid dot es


# Copyright 2020 FIWARE Foundation e.V.
#
# This file is part of Orion-LD Context Broker.
#
# Orion-LD Context Broker is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Orion-LD Context Broker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion-LD Context Broker. If not, see http://www.gnu.org/licenses/.
#
# For those usages not covered by this license please contact with
# orionld at fiware dot org


# -----------------------------------------------------------------------------
#
# Imports
#
import paho.mqtt.client as mqtt
from getopt import getopt, GetoptError
from os.path import basename
from sys import argv
import json


# -----------------------------------------------------------------------------
#
# log file
#
logFile = open("/tmp/mqttTestClient.log", "w")
logFile.write("mqttTestClient.py has started\n")
logFile.flush()


# -----------------------------------------------------------------------------
#
# Dump file
#
dumpFile = open("/tmp/mqttTestClient.dump", "w")
dumpFile.flush()


# -----------------------------------------------------------------------------
#
# usage -
#
def usage():
    """
    Print usage message
    """

    print('Usage: %s --mqttBrokerIp <broker ip> --mqttBrokerPort <portNo> --pretty-print --mqttTopic <topic> -v -u'
          % basename(__file__))
    print('')
    print('Parameters:')
    print("  --mqttBrokerIp <MQTT Broker IP-address>: (default is 'localhost')")
    print("  --mqttBrokerPort <port number>: MQTT broker port (default is 1883)")
    print("  --mqttTopic <topic>: MQTT topic to subscribe to (default is 'notification')")
    print("  --pretty-print: pretty print mode")
    print("  -v: verbose mode")
    print("  -u: print this usage message")


# -----------------------------------------------------------------------------
#
# Command Line Arguments
#
pretty = False
verbose = 0
mqttBrokerIp = "localhost"
mqttBrokerPort = 1883
mqttTopic = "notification"
qos = 0

logFile.write("Parsing Command Line Arguments\n")
logFile.flush()

try:
    opts, args = getopt(argv[1:], 'vu', ['mqttBrokerIp=', 'mqttBrokerPort=', 'mqttTopic=', 'pretty-print'])

    for opt, arg in opts:
        if opt == '-u':
            usage()
            exit(0)
        elif opt == '-v':
            verbose = 1
        elif opt == '--pretty-print':
            pretty = True
        elif opt == '--mqttBrokerIp':
            mqttBrokerIp = arg
        elif opt == '--mqttBrokerPort':
            try:
                mqttBrokerPort = int(arg)
            except ValueError:
                print('the "--mqttBrokerPort" value must be an integer')
                exit(1)
        elif opt == '--mqttTopic':
            mqttTopic = arg
        else:
            print("no such command-line argument: " + opt)
            exit(1)
except GetoptError:
    print('Invalid command-line argument\n')
    usage()
    exit(1)


logFile.write("Parsed Command Line Arguments\n")
logFile.flush()


# -----------------------------------------------------------------------------
#
#
#
notifications = 0
notificationAcc = ""


# -----------------------------------------------------------------------------
#
# on_connect - MQTT callback for CONNACK response from the server.
#
def on_connect(client, userdata, flags, rc):
    global notifications, notificationAcc
    notifications = 0
    notificationAcc = ""


# -----------------------------------------------------------------------------
#
# The callback for when a PUBLISH message is received from the server.
#
def on_message(client, userdata, msg):
    global notifications, notificationAcc
    global logFile, dumpFile

    payload = msg.payload.decode("utf-8")

    logFile.write("-----------------------------------------------------------------------------------------\n")
    logFile.write("Topic:   " + msg.topic + "\n" + "Payload: " + payload + "\n")
    logFile.flush()

    if (payload == 'dump'):
        logFile.write("Dumping received notifications to dump-file\n")
        logFile.flush()
        dumpFile.write("Notifications: " + str(notifications) + "\n")
        dumpFile.write(notificationAcc + "\n")
        dumpFile.flush()
    elif (payload == 'ping'):
        logFile.write("I'm Alive\n")
        logFile.flush()
    elif (payload == 'exit'):
        logFile.write("EXIT command received - I die\n")
        logFile.flush()
        exit(0)
    elif (payload == 'reset'):
        logFile.write("Resetting dump file\n")
        logFile.flush()
        notifications   = 0
        notificationAcc = ""
        dumpFile.close()
        dumpFile = open("/tmp/mqttTestClient.dump", "w")
        dumpFile.flush()
    else:
        logFile.write("Got a notification:\n")
        logFile.flush()

        if pretty:
            logFile.write("pretty-printing\n")
            logFile.flush()
            try:
                logFile.write("before loads\n")
                logFile.flush()
                json_obj = json.loads(msg.payload)
                logFile.write("after loads\n")
                logFile.flush()
                out = json.dumps(json_obj, indent=2, sort_keys=True)
                logFile.write("after dumps\n")
                logFile.flush()
            except ValueError as e:
                out = str(e)
            except:
                out = payload;
        else:
            out = payload

        logFile.write("Pretty payload:\n")
        logFile.write(out + "\n\n")
        logFile.flush()
        notifications = notifications + 1
        notificationAcc += str(out) + "\n"
        notificationAcc += "=======================================\n"


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

logFile.write("MQTT Test Client connecting to " + mqttBrokerIp + ":" + str(mqttBrokerPort) + "\n")
logFile.flush()

client.connect(mqttBrokerIp, mqttBrokerPort, 60)
logFile.write("MQTT Test Client connected to " + mqttBrokerIp + ":" + str(mqttBrokerPort) + "\n")
client.subscribe(mqttTopic, qos)
logFile.write("MQTT Test Client subscribes to '" + mqttTopic + "'\n")

#
# Await notifications and commands (dump, reset, ping ...)
#
client.loop_forever()
