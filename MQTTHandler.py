#!/usr/bin/python

# Version:      0.1
# Last changed: 06/08/17

import sys
import signal
import time
from multiprocessing import Queue
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_publish

class MQTTHandler():

    def __init__( self, queue, host, port ):
        self.queue = queue
        self.running = True
        self.host = host
        self.port = port

        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message

    def start( self ):
        print("Connecting to MQTT Broker.")
        self.mqtt_client.connect( self.host, self.port, 60 )
        self.mqtt_client.loop_start()

    def stop( self ):
        print("Disconnecting from MQTT Broker.")
        self.mqtt_client.loop_stop( force=False )
        self.mqtt_client.disconnect()

    def on_connect( self, client, userdata, flags, rc ):
        print( "Connected with result code " + str(rc) )

    def on_disconnect( self, client, userdata, rc ):
        print( "Disconnected with result code " + str(rc) )

    def subscribe( self, topic ):
        self.mqtt_client.subscribe( topic )

    def unsubscribe( self, topic ):
        self.mqtt_client.unsubscribe( topic )

    def on_message( self, client, userdata, msg ):
        #print( msg.topic + " " + str(msg.payload) )
        self.queue.put( (msg.topic, msg.payload) )

    def publish_message( self, topic, msg ):
        mqtt_publish.single( topic, msg, hostname=self.host )



def signal_handler( signal , frame ):
    global running
    running = False



if __name__ == '__main__':

    # add signal handler for SIGINT
    signal.signal( signal.SIGINT , signal_handler )

    # init stuff
    q = Queue()
    mqtt_client = MQTTHandler( q, "localhost", 1883 )
    mqtt_client.start()

    mqtt_client.subscribe( "test" )
    mqtt_client.publish_message( "test", "Test no 2" )

    # main program loop
    running = True
    while ( running ):
        if ( not q.empty() ):
            topic, msg = q.get()
            print( topic + " " + str(msg) )
        time.sleep( 0.1 )

    # cleanup
    mqtt_client.stop()
    print( 'Closing program!' )
    sys.exit(0)
    