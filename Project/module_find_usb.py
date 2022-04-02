import serial
import sys
from datetime import datetime, timedelta
import logging

from os import listdir, system

def init_parameters(in_baud, in_par, in_byte, in_stop_bits, in_onoff, in_rtscts, in_timeout):
    global ser 

    # set COM port config
    ser = serial.Serial()

    ser.baudrate = in_baud
    ser.parity= in_par

    #others
    ser.bytesize= in_byte             
    ser.stopbits= in_stop_bits
    ser.xonxoff= in_onoff
    ser.rtscts= in_rtscts
    ser.timeout= in_timeout


def find_correct_usb(in_identifier):

    global ser

    # start with device index 0
    device_option_index = 0

    # we have not found the device yet
    correct_device_found = False

    # only test for x seconds per device
    time_in_between = 30  

    # list all the USB devices
    options = []

    try:
        for dev_device in listdir("/dev"):
            if "ttyUSB" in dev_device:
                options.append("/dev/" + dev_device)
    except Exception as e:
        logging.error("module_find_usb.py: ERROR: unable to locate /dev folder")
        return None

    #     (correct device not found )     (we still have devices to test    )
    while (not(correct_device_found)) and (device_option_index < len(options)):

        #port
        ser.port= options[device_option_index]

        #start time of a test run
        last_date_time = datetime.utcnow()

        try:
            ser.open()

            # did we receive a message?
            received = False

            #     ( test for a pre-defined limited amount of time                           )                              
            while (((datetime.utcnow() - last_date_time).total_seconds()) <= time_in_between):

                #Initialize p1_teller is mijn tellertje voor van 0 tot 20 te tellen
                try:
                    p1_raw = ser.readline()
                    received = True 
                except Exception as e:
                    print(e)
                    print("init read eror")
                    received = False

                if(received):
                    p1_str=str(p1_raw)
                    p1_line=p1_str.strip()

                    if in_identifier in p1_line:
                        correct_device_found = True
                        print("device is found: "  + options[device_option_index])
                        return options[device_option_index]

        except:
            print("could not open this port: " + options[device_option_index])
            break

        try:
            ser.close()
            print("serial is closed again")
        
        except:
            print("could not close this port: " + options[device_option_index])

        #increase device index
        device_option_index += 1

    return None