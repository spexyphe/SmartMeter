version = "0.1.10"

import os
import logging
import sys
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

    def new_log(self, str_message, an_exception = None):
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

    def load_env_var_sys(self):
        global do_trace, is_local_test, is_var_run
        
        #by default we are do_trace-ing
        is_local_test = False
        do_trace = True 
        is_var_run = True
        
        try: #do_trace
            do_trace_str = os.environ['do_trace']

            if do_trace_str == "True":
                do_trace = True
            else:
                do_trace = False

            self.new_log("OK: succesfully loaded environment variable for system 'do_trace'")
        except Exception as e:
            self.new_log("ERROR: environment variable for system 'do_trace' FAILED", e)

        try: #is_local_test
            is_local_test_str = os.environ['is_local_test']

            if is_local_test_str == "True":
                is_local_test = True
            else:
                is_local_test = False

            self.new_log("OK: succesfully loaded environment variable for system 'is_local_test': " + str(is_local_test))
        except Exception as e:
            self.new_log("ERROR: environment variable for system 'is_local_test' FAILED", e)

        try: #is_var_run
            is_var_run_str = os.environ['is_var_run']

            if is_var_run_str == "True":
                is_var_run = True
            else:
                is_var_run = False

            self.new_log("OK: succesfully loaded environment variable for system 'is_var_run'")
        except Exception as e:
            self.new_log("ERROR: environment variable for system 'is_var_run' FAILED", e)

    def load_env_var_modbus(self):

        global device, baud, parity, variables

        device = "/dev/ttyUSB0"
        baud = 115200
        parity = "E" 
        variables = ""

        try: #modbus_device
            device = os.environ['modbus_device']
            self.new_log("OK: succesfully loaded environment variable for modbus 'modbus_device'")
        except Exception as e:
            self.new_log("ERROR: environment variable for modbus 'modbus_device' FAILED", e)

        try: #modbus_baud
            baud = int(os.environ['modbus_baud'])
            self.new_log("OK: succesfully loaded environment variable for modbus 'modbus_baud'")
        except Exception as e:
            self.new_log("ERROR: environment variable for modbus 'modbus_baud' FAILED", e)
        
        try: #modbus_parity
            parity = os.environ['modbus_parity']
            self.new_log("OK: succesfully loaded environment variable for modbus 'modbus_parity'")
        except Exception as e:
            self.new_log("ERROR: environment variable for modbus 'modbus_parity' FAILED", e)

        try: #modbus_variables
            variables = os.environ['modbus_variables']
            self.new_log("OK: succesfully loaded environment variable for modbus 'modbus_variables'")
        except Exception as e:
            self.new_log("ERROR: environment variable for modbus 'modbus_variables' FAILED", e)

    def parse_variables(self, in_variables):
        out_variables = None

        try:
            out_variables = in_variables.split(",")    
        except Exception as e:
            self.new_log("ERROR, parse_variables Failed", e)
        
        return out_variables

    def load_env_var_influx(self):
        global influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host

        env_var_influx_success = True
        
        try: #influx_url
            influx_url = os.environ['influx_url']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_url'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_url' FAILED", e)
            env_var_influx_success = False

        try: #influx_port
            influx_port = int(os.environ['influx_port'])
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_port'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_port' FAILED", e)
            env_var_influx_success = False

        try: #influx_user
            influx_user = os.environ['influx_user']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_user'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_user' FAILED", e)
            env_var_influx_success = False

        try: #influx_password
            influx_password = os.environ['influx_password']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_password'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_password' FAILED", e)
            env_var_influx_success = False

        try: #influx_database
            influx_database = os.environ['influx_database']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_database'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_database' FAILED", e)
            env_var_influx_success = False

        try: #influx_measurement
            influx_measurement = os.environ['influx_measurement']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_measurement'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_measurement' FAILED", e)
            env_var_influx_success = False

        try: #INFLUX_host
            influx_host = os.environ['influx_host']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_host'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_host' FAILED", e)
            env_var_influx_success = False

        return env_var_influx_success

    #dashboards don't always like boolean values, convert to int
    def bool_to_influx(self, input):

        if type(input)==bool:
            if input == True:
                return "true"
            else:
                return "false"
        else:
            return None

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

    def create_raw_point_locally(self, measurement, host, line_nr, value):

            #using point time to log things will ensure that everything uses the same time
            point_time = datetime.utcnow().strftime(self.time_format)

            influx.add_raw_point(measurement, host, line_nr, "Raw", value, point_time)


    def create_data_point_locally(self, measurement, host, value_name, value, phase=None):
        ### mk: measurement and host should not be needed as input


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
            
            current_day_of_year = amsterdam_now.timetuple().tm_yday

            #using point time to log things will ensure that everything uses the same time
            point_time = datetime.utcnow().strftime(self.time_format)

            influx.add_data_point(measurement, host, current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, value_name, value, point_time, phase)

    def parse_line(self, in_line):
        out_line = None

        try:
            if in_line.count('*') > 0:
                if in_line.count(')') == 2:
                    out_line = float(in_line[in_line.index(')')+2:in_line.index('*')])
                else:
                    out_line = float(in_line[in_line.index('(')+1:in_line.index('*')])
            else:    
                out_line = float(in_line[in_line.index('(')+1:in_line.index(')')])

        except Exception as e:
            print(e)

        return out_line

    def main_loop(self):

        time_in_between = 3600
        last_date_time = datetime.utcnow()
        init_run = True

        #load system and modbus variables from the environment
        self.load_env_var_sys()
        self.load_env_var_modbus()

        #the variables that are loaded
        global is_local_test, do_trace, is_var_run
        global device, baud, parity, variables

        #parse the list of variables as defined in the environment
        list_of_var = self.parse_variables(variables)

        # safety check: did we detect variables
        if (not (list_of_var is None)) and len(list_of_var) > 0:

            # load environment variables regarding influx
            if self.load_env_var_influx():

                #the variables that where loaded
                global influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host

                # init the influx connection
                #Influx.init_influx(influx_url, Influx_org, Influx_bucket, is_local_test, Influx_token, do_trace)
                influx.init_influx(influx_user, influx_password, influx_url, influx_port, influx_database, is_local_test, do_trace)

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


                e_previous_value = 0.0
                e_previous_value_2 = 0.0

                first_run = True
                second_run = True

                e_consumption_low_hours = 0.0
                e_consumption_high_hours = 0.0
                e_production_high_hours = 0.0
                e_production_low_hours = 0.0
                e_current_consumption_cummulative = 0.0
                e_current_production_cummulative = 0.0
                e_low_or_high_hour = 0
                e_current_consumption = 0.0
                e_current_production = 0.0
                                
                received_e_current_consumption = 0
                received_e_current_production = 0

                ### code smells checked up to here

                e_volt_level_p1 = None
                e_watt_production_p1 = None
                e_watt_consumption_p1 = None
                e_volt_level_p2 = None
                e_watt_production_p2 = None
                e_watt_production_p2 = None
                e_volt_level_p3 = None
                e_watt_production_p3 = None
                e_watt_consumption_p3 = None

                received_counter = 0
                old_time = datetime.utcnow()

                do_raw_log = True
                completed_a_full_raw = False

                # run our program cotiniously
                while True:

                    # update the influx database on the version we are running
                    if (((datetime.utcnow() - last_date_time).total_seconds()) > time_in_between) or init_run:
                        
                        #update time
                        last_date_time = datetime.utcnow()
                        
                        #send version number to influx
                        self.update_version(influx_measurement, influx_host)

                        try:
                            counter = 0
                            found_first = False
                            finished_raw = False

                            while((not(finished_raw)) and counter < 1000):

                                counter += 1

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

                                    if (not(found_first)):
                                        if "1-0:1.7.0" in p1_line:
                                            found_first = True
                                            self.create_raw_point_locally(influx_measurement, influx_host, counter, p1_line)
                                    else:
                                        if "1-0:1.7.0" in p1_line:
                                            finished_raw = True 
                                        else:
                                            self.create_raw_point_locally(influx_measurement, influx_host, counter, p1_line)
                                            counter += 1                                       

                            try:
                                influx.write_data()
                            except Exception as e:
                                print(e)
                                print("write raw data to influx error")

                        except Exception as e:
                            print(e)
                            print("init eror")


                        #was this the first run
                        if init_run:
                            #not anymore now
                            init_run = False 



                    #Open COM port
                    #while True:

                
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

                        if "1-3:0.2.8" in p1_line:
                            self.create_data_point_locally(influx_measurement, influx_host, "dsmr", self.parse_line(p1_line))

                            if received_counter > 1:

                                difference = datetime.utcnow() - old_time
                                difference_in_seconds = difference.total_seconds()

                                if difference_in_seconds > 60:
                                    
                                    e_current_consumption = ( e_current_consumption_cummulative / received_e_current_consumption)
                                    # print (str(e_current_consumption_cummulative) + "/" + str(received_e_current_consumption) + "=" + str($
                                    e_current_production = ( e_current_production_cummulative / received_e_current_production )
                                    # print (str(e_current_production_cummulative) + "/" + str(received_e_current_production) + "=" + str(e_current$
                                    e_current = (e_current_consumption - e_current_production)*1000

                                    #also send 0's to know difference between null and 0
                                    self.create_data_point_locally(influx_measurement, influx_host, "e_current_consumption", (e_current_consumption*1000))                                
                                    self.create_data_point_locally(influx_measurement, influx_host, "e_current_production", (e_current_production*1000))

                                    self.create_data_point_locally(influx_measurement, influx_host, "e_current", e_current)                


                                    if not(e_volt_level_p1 is None) and ( not(e_watt_production_p1) or not(e_watt_consumption_p1) ):
                                        if e_watt_consumption_p1 is None:
                                            e_watt_consumption_p1 = 0
                                        if e_watt_production_p1 is None:
                                            e_watt_production_p1 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp_calc", ((e_watt_consumption_p1 - e_watt_production_p1) / e_volt_level_p1), "l1")


                                    if not(e_volt_level_p2 is None) and ( not(e_watt_production_p2) or not(e_watt_production_p2) ):
                                        if e_watt_production_p2 is None:
                                            e_watt_production_p2 = 0
                                        if e_watt_production_p2 is None:
                                            e_watt_production_p2 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp_calc", ((e_watt_production_p2 - e_watt_production_p2) / e_volt_level_p2), "l2")


                                    if not(e_volt_level_p3 is None) and ( not(e_watt_production_p3) or not(e_watt_consumption_p3) ):
                                        if e_watt_consumption_p3 is None:
                                            e_watt_consumption_p3 = 0
                                        if e_watt_production_p3 is None:
                                            e_watt_production_p3 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp_calc", ((e_watt_consumption_p3 - e_watt_production_p3) / e_volt_level_p3), "l3")


                                    if first_run:
                                        e_previous_value = e_current
                                        first_run = False
                                    elif second_run:
                                        e_previous_value = e_current
                                        e_previous_value_2 = e_previous_value
                                        second_run = False
                                    else: 
                                        current_delta = e_current - e_previous_value
                                        current_delta_2 = e_current - e_previous_value_2
                                        self.create_data_point_locally(influx_measurement, influx_host, "current_delta", current_delta)
                                        self.create_data_point_locally(influx_measurement, influx_host, "current_delta_2", current_delta_2)
                                        e_previous_value_2 = e_previous_value
                                        e_previous_value = e_current


                                    e_current_consumption_cummulative = 0.0
                                    received_e_current_consumption = 0
                                    e_current_production_cummulative = 0.0
                                    received_e_current_production = 0
                                    e_current_consumption = 0.0
                                    e_current_production = 0.0


                                    e_volt_level_p1 = None
                                    e_watt_production_p1 = None
                                    e_watt_consumption_p1 = None
                                    e_volt_level_p2 = None
                                    e_watt_production_p2 = None
                                    e_watt_production_p2 = None
                                    e_volt_level_p3 = None
                                    e_watt_production_p3 = None
                                    e_watt_consumption_p3 = None


                                    old_time = datetime.utcnow()

                                    do_raw_log = True
                                    completed_a_full_raw = False

                            else:
                                
                                received_counter+= 1

                            time.sleep(10)
                        else:

                            # als je alles wil zien moet je de volgende line uncommenten print (p1_li$
                            if "1-0:1.7.0" in p1_line:
                                verbruik_waarde = self.parse_line(p1_line)
                                if not(verbruik_waarde is None):
                                    e_current_consumption_cummulative += verbruik_waarde
                                    received_e_current_consumption += 1

                            if "1-0:2.7.0" in p1_line:
                                terug_waarde = self.parse_line(p1_line)
                                if not(terug_waarde is None):
                                    e_current_production_cummulative += terug_waarde
                                    received_e_current_production += 1

                            if do_raw_log:

                                if "0-0:96.14.0" in p1_line:
                                    e_low_or_high_hour = self.parse_line(p1_line)
                                    if not (e_low_or_high_hour is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_low_or_high_hour_fl", e_low_or_high_hour)

                                if "1-0:1.8.1" in p1_line:
                                    e_consumption_low_hours = self.parse_line(p1_line)

                                    if not (e_consumption_low_hours is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_consumption_low_hours", e_consumption_low_hours)

                                        #check for 24h change in this value
                                        daily_change = transform.manage_daily_usage("e_consumption_low_hours", e_consumption_low_hours)
                                        if not daily_change is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "e_consumption_low_hours_change", daily_change)


                                if "1-0:1.8.2" in p1_line:
                                    e_consumption_high_hours = self.parse_line(p1_line)

                                    if not (e_consumption_high_hours is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_consumption_high_hours", e_consumption_high_hours)

                                        #check for 24h change in this value
                                        daily_change = transform.manage_daily_usage("e_consumption_high_hours", e_consumption_high_hours)
                                        if not daily_change is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "e_consumption_high_hours_change", daily_change)


                                if "1-0:2.8.1" in p1_line:
                                    e_production_low_hours = self.parse_line(p1_line)

                                    if not (e_production_low_hours is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_production_low_hours", e_production_low_hours)

                                        #check for 24h change in this value
                                        daily_change = transform.manage_daily_usage("e_production_low_hours", e_production_low_hours)
                                        if not daily_change is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "e_production_low_hours_change", daily_change)



                                if "1-0:2.8.2" in p1_line:
                                    e_production_high_hours = self.parse_line(p1_line)

                                    if not (e_production_high_hours is None) :
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_production_high_hours", e_production_high_hours)

                                        #check for 24h change in this value
                                        daily_change = transform.manage_daily_usage("e_production_high_hours", e_production_high_hours)
                                        if not daily_change is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "e_production_high_hours", daily_change)




                                if "1-0:32.7.0" in p1_line:
                                    e_volt_level_p1 = self.parse_line(p1_line)

                                    if not (e_volt_level_p1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_volt", e_volt_level_p1, "l1")

                                        if completed_a_full_raw:
                                            do_raw_log = False
                                        else:
                                            completed_a_full_raw = True

                                if "1-0:31.7.0" in p1_line:
                                    e_amp_1 = self.parse_line(p1_line)

                                    if not (e_amp_1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp", e_amp_1, "l1")

                                if "1-0:21.7.0" in p1_line:
                                    e_watt_consumption_p1 = self.parse_line(p1_line)

                                    if not (e_watt_consumption_p1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_consumption", e_watt_consumption_p1, "l1")

                                if "1-0:22.7.0" in p1_line:
                                    e_watt_production_p1 = self.parse_line(p1_line)

                                    if not (e_watt_production_p1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_production", e_watt_production_p1, "l1")

                                if "1-0:52.7.0" in p1_line:
                                    e_volt_level_p2 = self.parse_line(p1_line)

                                    if not (e_volt_level_p2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_volt", e_volt_level_p2, "l2")

                                if "1-0:51.7.0" in p1_line:
                                    e_amp_2 = self.parse_line(p1_line)

                                    if not (e_amp_2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp", e_amp_2, "l2")

                                if "1-0:41.7.0" in p1_line:
                                    e_watt_production_p2 = self.parse_line(p1_line)

                                    if not (e_watt_production_p2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_consumption", e_watt_production_p2, "l2")

                                if "1-0:42.7.0" in p1_line:
                                    e_watt_production_p2 = self.parse_line(p1_line)

                                    if not (e_watt_production_p2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_production", e_watt_production_p2, "l2")

                                if "1-0:72.7.0" in p1_line:
                                    e_volt_level_p3 = self.parse_line(p1_line)

                                    if not (e_volt_level_p3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_volt", e_volt_level_p3, "l3")

                                if "1-0:71.7.0" in p1_line:
                                    e_amp_3 = self.parse_line(p1_line)

                                    if not (e_amp_3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_amp", e_amp_3, "l3")

                                if "1-0:61.7.0" in p1_line:
                                    e_watt_consumption_p3 = self.parse_line(p1_line)

                                    if not (e_watt_consumption_p3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_consumption", e_watt_consumption_p3, "l3")

                                if "1-0:62.7.0" in p1_line:
                                    e_watt_production_p3 = self.parse_line(p1_line)

                                    if not (e_watt_production_p3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "e_watt_production", e_watt_production_p3, "l3")

                                if "0-1:24.2.1" in p1_line:
                                    g_volume = self.parse_line(p1_line)

                                    if not (g_volume is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "g_volume", g_volume)

                                        #check for 24h change in this value
                                        daily_change = transform.manage_daily_usage("g_volume", g_volume)
                                        if not daily_change is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "g_volume_change", daily_change)

                                        g_flow = transform.gas_flow("g_flow",g_volume)

                                        if not (g_flow is None):
                                            self.create_data_point_locally(influx_measurement, influx_host, "g_flow", g_flow)


                    try:
                        influx.write_data()
                    except Exception as e:
                        print(e)
                        print("write error")


if __name__ == '__main__':
    Meterclass = meter()
    Meterclass.main_loop()
