version = "0.3.01"

from fnmatch import translate
import os
import logging
import sys
from tempfile import TemporaryFile
import time
import json

from datetime import datetime, timedelta

try:
    import pytz
except Exception as e:
    logging.error("failed to load custom pytz module: " + str(e))

try:
    import serial
except Exception as e:
    logging.error("failed to load custom serial module: " + str(e))

try:
    import module_find_usb as find_usb
except Exception as e:
    logging.error("failed to load custom find_usb module: " + str(e))    

    #possible we are locally testing, this will work then
    try:
        from . import module_find_usb as find_usb
        logging.warning("succesfull in loading module_find_usb.")
    except Exception as ex:
        logging.error("failed to load custom find_usb module: " + str(ex))

    find_usb = None

try:
    import module_env_var as env_var
except Exception as e:
    logging.error("failed to load custom env_var module: " + str(e))    

    #possible we are locally testing, this will work then
    try:
        from . import module_env_var as env_var
        logging.warning("succesfull in loading module_env_var.")
    except Exception as ex:
        logging.error("failed to load custom env_var module: " + str(ex))
        env_var = None

try:
    import module_influx as influx
except Exception as e:
    logging.error("failed to load custom influx module: " + str(e))

    #possible we are locally testing, this will work then
    try:
        from . import module_influx as influx
        logging.warning("succesfull in loading influx.")
    except Exception as ex:
        logging.error("failed to load custom influx module: " + str(ex))
        influx = None

try:
    import module_transform as transform
    transform.init_transform()
except Exception as e:
    logging.error("failed to load custom Transform module: " + str(e))

    #possible we are locally testing, this will work then
    try:
        from . import module_transform as transform
        logging.warning("succesfull in loading transform.")
    except Exception as ex:
        logging.error("failed to load custom transform module: " + str(ex))
        transform = None


time_format = '%Y-%m-%dT%H:%M:%SZ'

def new_log(str_message, an_exception = None):
    global do_trace

    module_name = "main_smart_meter.py, "

    if("ERROR" in str_message):
        logging.error( module_name + str_message)
        
        if not (an_exception is None):
            logging.error(str(an_exception))    
    elif("WARNING" in str_message):
        logging.warning( module_name + str_message)

        if not (an_exception is None):
            logging.warning(str(an_exception))   
    else:
        if do_trace:
            logging.info( module_name + str_message)

            if not (an_exception is None):
                logging.info(str(an_exception)) 

def get_influx():
    #this is for the enablement of unit testing functions like update_version
    return influx

def update_version(measurement, host):

    global time_format

    # Tags are fixed values, that are not time zone transformed
    # Hence for tags we need the current timezone
    #Else we get a timezone difference
    tz = pytz.timezone('Europe/Amsterdam')
    amsterdam_now = datetime.now(tz)

    # tag values that allows searching based on time tags
    current_year = str(amsterdam_now.strftime("%Y"))
    current_month_nr = str(amsterdam_now.strftime("%m"))
    current_week_nr = str(amsterdam_now.strftime("%U"))
    current_day_nr = str(amsterdam_now. strftime("%w"))

    #using point time to log things will ensure that everything uses the same time
    point_time = datetime.utcnow().strftime(time_format)

    current_day_of_year = amsterdam_now.timetuple().tm_yday

    if not (influx is None):
        influx.add_data_point(measurement, host , current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, "Version", version, point_time )

def get_modbus_device():
    global succes_var_modbus, baud, parity

    # was this module correctly loaded
    if (not (find_usb is None)) and succes_var_modbus:

        #check what parity to use
        if parity == "E":
            ser_parity=serial.PARITY_EVEN
        else:
            ser_parity=serial.PARITY_ODD

        #init
        find_usb.init_parameters(baud, ser_parity, serial.SEVENBITS, serial.STOPBITS_ONE, 0, 0, 20)

        #try to find usb device
        return find_usb.find_correct_usb("1-3:0.2.8")

    else:
        return None

def main_loop():

    time_in_between = 3600
    last_date_time = datetime.utcnow()

    #the variables that are loaded
    global is_local_test, do_trace, is_var_run
    global succes_var_modbus, auto_detect, device, baud, parity, variables

    #load system and modbus variables from the environment
    succes_var_sys, is_local_test, do_trace, is_var_run =  env_var.load_env_var_sys()
    succes_var_modbus, auto_detect, device, baud, parity, variables = env_var.load_env_var_modbus()

    if auto_detect:
        device = get_modbus_device()

    if succes_var_sys and succes_var_modbus and (not (device is None)):

        #parse the list of variables as defined in the environment
        list_of_var = transform.parse_variables(variables)

        # safety check: did we detect variables
        if (not (list_of_var is None)) and len(list_of_var) > 0:

            #load the variables
            global influx_url, influx_port, influx_org, influx_token, influx_bucket, influx_measurement, influx_host
            succes_var_influx, influx_url, influx_port, influx_org, influx_token, influx_bucket, influx_measurement, influx_host = env_var.load_env_var_influx()
          

            # load environment variables regarding influx
            if succes_var_influx:
                
                # init the influx connection
                #Influx.init_influx(influx_url, Influx_org, Influx_bucket, is_local_test, Influx_token, do_trace)
                influx.init_influx(influx_token=influx_token, in_host=influx_url, in_port=influx_port, influx_org=influx_org, in_bucket=influx_bucket, in_local_test=is_local_test, in_debug=do_trace)

                #pass the influx module on to transform
                transform.set_influx_module(influx, influx_measurement, influx_host)

                #Set COM port config
                ser = serial.Serial()
                
                ser.baudrate = baud
                ser.port= device

                if parity == "E":
                    ser.parity=serial.PARITY_EVEN
                else:
                    ser.parity=serial.PARITY_ODD

                #others
                ser.bytesize=serial.SEVENBITS              
                ser.stopbits=serial.STOPBITS_ONE
                ser.xonxoff=0
                ser.rtscts=0
                ser.timeout=20

                #Initialize p1_teller is mijn tellertje voor van 0 tot 20 te tellen
                try:
                    ser.open()
                except:
                    sys.exit ("Issue with opening serial port %s. Aaaaarch."  % ser.name)

                # run our program cotiniously
                while True:

                    # update the influx database on the version we are running
                    if (((datetime.utcnow() - last_date_time).total_seconds()) > time_in_between):
                        #update time
                        last_date_time = datetime.utcnow()
                        
                        #send version number to influx
                        update_version(influx_measurement, influx_host)
                
                    try:
                        p1_raw = ser.readline()
                        received = True
                    except Exception as e:
                        
                        new_log("WARNING: read eror", str(e))

                        #sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % s$
                        #print("receive error")
                        received = False

                    if received:

                        try:
                            p1_str=str(p1_raw.decode("utf-8"))
                            p1_line=p1_str.strip()
                        except:
                            p1_str=str(p1_raw)
                            p1_line=p1_str.strip()

                        new_log("OK: " + p1_line)

                        if "1-3:0.2.8" in p1_line:
                            transform.calculated_values()

                            time.sleep(3)

                        else:
                            transform.parse_line(p1_line, 10)

                    try:
                        influx.write_data()
                    except Exception as e:
                        new_log("ERROR: write error", str(e))

                    try:
                        transform.reset_stored()
                    except Exception as e:
                        new_log("ERROR: reset error", str(e))

if __name__ == '__main__':
    main_loop()