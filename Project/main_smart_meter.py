version = "0.2.00"

from fnmatch import translate
import os
import logging
import sys
from tempfile import TemporaryFile
import time
import json

from datetime import datetime, timedelta

try:
    import module_env_var as env_var
except Exception as e:
    logging.error("failed to load custom env_var module: " + str(e))    

try:
    import pytz
except Exception as e:
    logging.error("failed to load custom pytz module: " + str(e))

try:
    import serial
except Exception as e:
    logging.error("failed to load custom serial module: " + str(e))

try:
    import module_influx as influx
except Exception as e:
    logging.error("failed to load custom influx module: " + str(e))

try:
    import module_transform as transform
    transform.init_transform()
except Exception as e:
    logging.error("failed to load custom Transform module: " + str(e))


class meter():

    time_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self):
        print("init smartmeter")


    def update_version(self, measurement, host):

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
            point_time = datetime.utcnow().strftime(self.time_format)

            current_day_of_year = amsterdam_now.timetuple().tm_yday

            influx.add_data_point(measurement, host , current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, "Version", version, point_time )


    def main_loop(self):

        time_in_between = 3600
        last_date_time = datetime.utcnow()

        #the variables that are loaded
        global is_local_test, do_trace, is_var_run
        global device, baud, parity, variables

        #load system and modbus variables from the environment
        succes_var_sys, is_local_test, do_trace, is_var_run =  env_var.load_env_var_sys()
        succes_var_modbus, device, baud, parity, variables = env_var.load_env_var_modbus()

        #parse the list of variables as defined in the environment
        list_of_var = transform.parse_variables(variables)

        # safety check: did we detect variables
        if (not (list_of_var is None)) and len(list_of_var) > 0:

            #load the variables
            global influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host
            succes_var_influx, influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host = env_var.load_env_var_influx()

            # load environment variables regarding influx
            if succes_var_influx:
                
                # init the influx connection
                #Influx.init_influx(influx_url, Influx_org, Influx_bucket, is_local_test, Influx_token, do_trace)
                influx.init_influx(influx_user, influx_password, influx_url, influx_port, influx_database, is_local_test, do_trace)

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
                        self.update_version(influx_measurement, influx_host)
              
                    try:
                        p1_raw = ser.readline()
                        received = True
                    except Exception as e:
                        print(e)
                        print("read eror")
                        #sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % s$
                        #print("receive error")
                        received = False

                    if received:
                        p1_str=str(p1_raw)
                        p1_line=p1_str.strip()

                        logging.warning(p1_line)

                        if "1-3:0.2.8" in p1_line:
                            transform.calculated_values()

                            time.sleep(3)

                        else:
                            transform.parse_line(p1_line, 10)

                    try:
                        influx.write_data()
                        transform.reset_stored()
                    except Exception as e:
                        print(e)
                        print("write error")


if __name__ == '__main__':
    Meterclass = meter()
    Meterclass.main_loop()
