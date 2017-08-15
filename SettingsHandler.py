#!/usr/bin/python

# Version:      0.1
# Last changed: 06/08/17

import sys
import signal
import time
import pickle
from pathlib import Path

class SettingsHandler():

    def __init__( self, settings_file ):
        self.settings_file = settings_file
        if ( Path(settings_file).is_file() ):
            f = open( 'settings', 'rb' )
            self.settings = pickle.load(f)
            f.close()
        else:
            self.settings = {}

    def store( self, key, value ):
        self.settings[key] = value
        f = open( self.settings_file, 'wb' )
        pickle.dump( self.settings, f )
        f.close()
        return value

    def retrieve( self, key ):
        try:
            return self.settings[key]
        except KeyError:
            return None

    def set( self, key, default ):
        try:
            return self.settings[key]
        except KeyError:
            self.store( key, default )
            return default



def signal_handler( signal , frame ):
    global running
    running = False



if __name__ == '__main__':

    # add signal handler for SIGINT
    signal.signal( signal.SIGINT , signal_handler )

    # init stuff
    settings = SettingsHandler( "settings" )

    s_1 = settings.set("s_1", 10)
    s_2 = settings.set("s_2", 10.5)
    s_3 = settings.set("s_3", "test")
    s_4 = settings.set("s_4", False)

    print( settings.retrieve("s_1") )
    print( settings.retrieve("s_2") )
    print( settings.retrieve("s_3") )
    print( settings.retrieve("s_4") )

    s_1 = settings.store( "s_1", 20 )



    '''settings.store( "int", 10 )
    settings.store( "float", 10.4 )
    settings.store( "string", "test" )

    print( settings.retrieve("int") )
    print( settings.retrieve("float") )
    print( settings.retrieve("string") )'''

    # main program loop
    running = True
    while ( running ):
        pass
        time.sleep( 0.1 )

    # cleanup
    print( 'Closing program!' )
    sys.exit(0)
    