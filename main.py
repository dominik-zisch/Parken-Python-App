#!/usr/bin/python

import sys
import signal
import time
import threading
import socket
from multiprocessing import Queue
from SettingsHandler import SettingsHandler
from MQTTHandler import MQTTHandler
from OSCHandler import OSCHandler
from OpenCVHandler import OpenCVHandler
from envirophat import light, weather


##================================================================================//
##------------------------------------------------------------------------// Globals

settings = SettingsHandler( "settings" )

pi_id = 0
server_ip = '172.20.10.2'
broadcast_address = '172.20.10.15'

running = True
mqtt_broker = '172.20.10.2'
mqtt_port = 1883

osc_port = 5005 # change port from node

heartbeat_interval = settings.set( "heartbeat_interval", 5 )

sensor_interval = settings.set( "sensor_interval", 5 )
publish_mqtt_temperature = settings.set( "publish_mqtt_temperature", True )
broadcast_osc_temperature = settings.set( "broadcast_osc_temperature", False )
publish_mqtt_pressure = settings.set( "publish_mqtt_pressure", True )
broadcast_osc_pressure = settings.set( "broadcast_osc_pressure", False )
publish_mqtt_light = settings.set( "publish_mqtt_light", True )
broadcast_osc_light = settings.set( "broadcast_osc_light", False )
publish_mqtt_pedestrians = settings.set( "publish_mqtt_pedestrians", True )
broadcast_osc_pedestrians = settings.set( "broadcast_osc_pedestrians", False )

all_settings = str( sensor_interval )
all_settings += ',' + str( osc_port )
all_settings += ',' + str( int(publish_mqtt_temperature) ) + ',' + str( int(publish_mqtt_pressure) ) + ',' + str( int(publish_mqtt_light) ) + ',' + str( int(publish_mqtt_pedestrians) )
all_settings += ',' + str( int(broadcast_osc_temperature) ) + ',' + str( int(broadcast_osc_pressure) ) + ',' + str( int(broadcast_osc_light) ) + ',' + str( int(broadcast_osc_pedestrians) )

temperature = (0, 0)
pressure = (0, 0)
light = (0, 0)
pedestrians = (0, 0)

##------------------------------------------------------------------------// Globals
##--------------------------------------------------------------------------------//



##================================================================================//
##--------------------------------------------------------------// Utility functions

#------------------------------------------/
#---/ signal handler - cleanup
def signal_handler( signal , frame ):
    global running
    running = False

#------------------------------------------/
#---/get local ip address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((server_ip, 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

#------------------------------------------/
#---/ get current time in milliseconds
def current_milli_time():
    return int(round(time.time() * 1000))

#------------------------------------------/
#---/get RPi ID
def get_ID():
    return get_ip_address().split('.')[-1]

##--------------------------------------------------------------// Utility functions
##--------------------------------------------------------------------------------//



##================================================================================//
##---------------------------------------------------------------------// MQTT stuff

#------------------------------------------/
#---/ Build mqtt and osc topics
def build_topics():
    global heartbeat_topic, settings_topic
    global temperature_mqtt_topic, pressure_mqtt_topic, light_mqtt_topic, pedestrians_mqtt_topic
    global temperature_osc_topic, pressure_osc_topic, light_osc_topic, pedestrians_osc_topic

    global_mqtt_topic = 'parken/rpi/' + str(pi_id)

    heartbeat_topic = global_mqtt_topic + '/heartbeat'

    settings_topic = global_mqtt_topic + '/settings'

    temperature_mqtt_topic = global_mqtt_topic + '/temperature'
    temperature_osc_topic = '/' + temperature_mqtt_topic

    pressure_mqtt_topic = global_mqtt_topic + '/pressure'
    pressure_osc_topic = '/' + pressure_mqtt_topic

    light_mqtt_topic = global_mqtt_topic + '/light'
    light_osc_topic = '/' + light_mqtt_topic

    pedestrians_mqtt_topic = global_mqtt_topic + '/pedestrians'
    pedestrians_osc_topic = '/' + light_mqtt_topic

#------------------------------------------/
#---/ Settings
def set_settings( s ):
    global heartbeat_interval, sensor_interval, publish_mqtt_temperature, broadcast_osc_temperature, publish_mqtt_pressure, broadcast_osc_pressure, publish_mqtt_light, broadcast_osc_light, publish_mqtt_pedestrians, broadcast_osc_pedestrians

    s = s.split(',')

    heartbeat_interval = settings.store( "heartbeat_interval", int(s[0]))

    sensor_interval = settings.store( "sensor_interval", int(s[1]))
    publish_mqtt_temperature = settings.store( "publish_mqtt_temperature", bool(int(s[2])) )
    broadcast_osc_temperature = settings.store( "broadcast_osc_temperature", bool(int(s[3])) )
    publish_mqtt_pressure = settings.store( "publish_mqtt_pressure", bool(int(s[4])) )
    broadcast_osc_pressure = settings.store( "broadcast_osc_pressure", bool(int(s[5])) )
    publish_mqtt_light = settings.store( "publish_mqtt_light", bool(int(s[6])) )
    broadcast_osc_light = settings.store( "broadcast_osc_light", bool(int(s[7])) )
    publish_mqtt_pedestrians = settings.store( "publish_mqtt_pedestrians", bool(int(s[8])) )
    broadcast_osc_pedestrians = settings.store( "broadcast_osc_pedestrians", bool(int(s[9])) )

    # averaged values also
    # add sound stuff (amplitude, etc.)
    # direction of people walking? etc.

    all_settings = str( sensor_interval )
    all_settings += ',' + str( osc_port )
    all_settings += ',' + str( int(publish_mqtt_temperature) ) + ',' + str( int(publish_mqtt_pressure) ) + ',' + str( int(publish_mqtt_light) ) + ',' + str( int(publish_mqtt_pedestrians) )
    all_settings += ',' + str( int(broadcast_osc_temperature) ) + ',' + str( int(broadcast_osc_pressure) ) + ',' + str( int(broadcast_osc_light) ) + ',' + str( int(broadcast_osc_pedestrians) )

##---------------------------------------------------------------------// MQTT stuff
##--------------------------------------------------------------------------------//



##================================================================================//
##----------------------------------------------------------------------// Heartbeat

#------------------------------------------/
#---/ send heartbeat
def send_hearbeat():
    global running, mqtt_client
    next_frame = current_milli_time()
    while (running):
        if (current_milli_time() >= next_frame):
            next_frame += heartbeat_interval * 1000
            mqtt_client.publish_message( heartbeat_topic, all_settings )
        time.sleep(0.1)

##----------------------------------------------------------------------// Heartbeat
##--------------------------------------------------------------------------------//



##================================================================================//
##--------------------------------------------------------------------// Sensor data

#------------------------------------------/
#---/ get temperature
def get_temperature():
    return weather.temperature()

#------------------------------------------/
#---/ get pressure
def get_pressure():
    return weather.pressure()

#------------------------------------------/
#---/ get pressure
def get_light():
    return light.light()

#------------------------------------------/
#---/ get pressure
def get_pedestrians():
    return opencv.get_num_detected()

#------------------------------------------/
#---/ Sensor loop
def sensor_loop():
    global running, mqtt_client, osc_handler, opencv
    global temperature, pressure, light, pedestrians

    while (running):

        current_time = current_milli_time()

        # get temperature
        t = get_temperature()
        # if temperature changed or timer has passed, send
        if (t is not temperature[0] or current_time >= temperature[1]):
            if (publish_mqtt_temperature):
                mqtt_client.publish_message( temperature_mqtt_topic, t )

            if (broadcast_osc_temperature):
                osc_handler.send_message( temperature_osc_topic, t )

            temperature = (t, current_time + sensor_interval * 1000)

        # get pressure
        p = get_pressure()
        # if pressure changed or timer has passed, send
        if (p is not pressure[0] or current_time >= pressure[1]):
            if (publish_mqtt_pressure):
                mqtt_client.publish_message( pressure_mqtt_topic, p )

            if (broadcast_osc_pressure):
                osc_handler.send_message( pressure_osc_topic, p )

            pressure = (p, current_time + sensor_interval * 1000)

        # get light
        l = get_light()
        # if light changed or timer has passed, send
        if (l is not light[0] or current_time >= light[1]):
            if (publish_mqtt_light):
                mqtt_client.publish_message( light_mqtt_topic, l )

            if (broadcast_osc_light):
                osc_handler.send_message( light_osc_topic, l )

            light = (l, current_time + sensor_interval * 1000)

        # get pedestrians
        pe = get_pedestrians()
        # if pedestrians changed or timer has passed, send
        if (pe is not pedestrians[0] or current_time >= pedestrians[1]):
            if (publish_mqtt_pedestrians):
                mqtt_client.publish_message( pedestrians_mqtt_topic, pe )

            if (broadcast_osc_pedestrians):
                osc_handler.send_message( pedestrians_osc_topic, pe )

            pedestrians = (pe, current_time + sensor_interval * 1000)

        time.sleep(0.1)

##--------------------------------------------------------------------// Sensor data
##--------------------------------------------------------------------------------//



##================================================================================//
##-------------------------------------------------------------// Main program logic

def main():
    global running, pi_id, mqtt_client, osc_handler, opencv
    global temperature, pressure, light, pedestrians

    # add signal handler for SIGINT
    signal.signal( signal.SIGINT , signal_handler )

    # get IP for RPi (last digits in the IP address)
    pi_id = get_ID()
    print( "Raspberry Pi node with ID", pi_id, "starting..." )

    # build topics with id
    build_topics()

    # init timers
    temperature = (get_temperature(), current_milli_time())
    pressure = (get_pressure(), current_milli_time())
    light = (get_light(), current_milli_time())
    pedestrians = (opencv.get_num_detected(), current_milli_time())
    
    # Initialise MQTT thread
    q = Queue()
    mqtt_client = MQTTHandler( q, mqtt_broker, mqtt_port )
    mqtt_client.start()
    mqtt_client.subscribe( settings_topic )

    # Initialise OSC handler
    osc_handler = OSCHandler( broadcast_address, osc_port )

    # Initialise heartbeat thread
    heartbeat_thread = threading.Thread(target=send_hearbeat)
    heartbeat_thread.start()

    # Initialise OpenCV thread
    opencv = OpenCVHandler( 640, 480, 32 )
    opencv.start()

    # Initialise sensor thread
    sensor_thread = threading.Thread(target=sensor_loop)
    sensor_thread.start()

    # main program loop
    running = True
    while ( running ):
        if ( not q.empty() ):
            topic, msg = q.get()
            print( topic + " " + msg.decode() )

            # settings
            if (topic == settings_topic):
                set_settings( msg.decode() )

        time.sleep( 0.1 )

    # cleanup
    opencv.stop_thread()
    opencv.join()
    heartbeat_thread.join()
    sensor_thread.join()
    mqtt_client.stop()
    print( 'Closing program!' )
    sys.exit(0)


if __name__ == '__main__':
    main() 

##-------------------------------------------------------------// Main program logic
##--------------------------------------------------------------------------------//
