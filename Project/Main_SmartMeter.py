version = "0.1.3"

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
    import Mod_Influx as Influx
except Exception as e:
    logging.error("failed to load custom influx module: " + str(e))

try:
    import Mod_Transform as Transform
    Transform.init_transform()
except Exception as e:
    logging.error("failed to load custom Transform module: " + str(e))


class Meter():

    time_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self):
        print("init smartmeter")

    def new_log(self, str_Message, an_exception = None):
        global do_trace

        Module_Name = "Mod_SmartMeter.py, "

        if("ERROR" in str_Message):
            logging.error( Module_Name + str_Message)
            
            if not (an_exception is None):
                logging.error(str(an_exception))    
        elif("WARNING" in str_Message):
            logging.warning( Module_Name + str_Message)

            if not (an_exception is None):
                logging.warning(str(an_exception))   
        else:
            if do_trace:
                logging.info( Module_Name + str_Message)

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

        EnvVarInfluxSuccess = True
        
        try: #influx_url
            influx_url = os.environ['influx_url']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_url'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_url' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #influx_port
            influx_port = int(os.environ['influx_port'])
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_port'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_port' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #influx_user
            influx_user = os.environ['influx_user']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_user'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_user' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #influx_password
            influx_password = os.environ['influx_password']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_password'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_password' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #influx_database
            influx_database = os.environ['influx_database']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_database'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_database' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #influx_measurement
            influx_measurement = os.environ['influx_measurement']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_measurement'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_measurement' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_host
            influx_host = os.environ['influx_host']
            self.new_log("OK: succesfully loaded environment variable for influx 'influx_host'")
        except Exception as e:
            self.new_log("ERROR: environment variable for influx 'influx_host' FAILED", e)
            EnvVarInfluxSuccess = False

        return EnvVarInfluxSuccess

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

            Influx.AddDataPoint(measurement, host , current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, "Version", version, point_time )

    def create_raw_point_locally(self, measurement, host, line_nr, Value):

            #using point time to log things will ensure that everything uses the same time
            point_time = datetime.utcnow().strftime(self.time_format)

            Influx.AddRawPoint(measurement, host, line_nr, "Raw", Value, point_time)


    def create_data_point_locally(self, measurement, host, ValueName, Value, Phase=None):
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

            Influx.AddDataPoint(measurement, host, current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, ValueName, Value, point_time, Phase)

    def ParseLine(self, in_line):
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
                #Influx.Init_Influx(influx_url, Influx_org, Influx_bucket, is_local_test, Influx_token, do_trace)
                Influx.Init_Influx(influx_user, influx_password, influx_url, influx_port, influx_database, is_local_test, do_trace)

                #Set COM port config
                ser = serial.Serial()
                
                ser.baudrate = baud
                ser.port= device

                if parity == "E":
                    ser.parity=serial.parity_EVEN
                else:
                    ser.parity=serial.parity_ODD

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
                    sys.exit ("Fout bij het openen van %s. Aaaaarch."  % ser.name)


                vorige_waarde = 0.0
                vorige_waarde_2 = 0.0

                first_run = True
                second_run = True

                totaal_verbruik_dal = 0.0
                totaal_verbruik_piek = 0.0
                totaal_terug_piek = 0.0
                totaal_terug_dal = 0.0
                huidig_verbruik_cum = 0.0
                huidig_terug_cum = 0.0
                dal_piek = 0
                huidig_verbruik = 0.0
                huidig_terug = 0.0
                                
                received_huidig_verbruik = 0
                received_huidig_terug = 0

                ### code smells checked up to here

                Volt1 = None
                Watt_terug1 = None
                Watt_ver1 = None
                Volt2 = None
                Watt_terug2 = None
                Watt_ver2 = None
                Volt3 = None
                Watt_terug3 = None
                Watt_ver3 = None

                receivedcounter = 0
                OldTime = datetime.utcnow()

                DoRawLog = True
                DidAFullRaw = False

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
                            linefound = 0
                            FoundFirst = False
                            FinishedRaw = False

                            while((not(FinishedRaw)) and counter < 1000):

                                counter += 1

                                try:
                                    p1_raw = ser.readline()
                                    Reveived = True
                                except Exception as e:
                                    print(e)
                                    print("init read eror")
                                    Reveived = False

                                if(Reveived):
                                    p1_str=str(p1_raw)
                                    p1_line=p1_str.strip()

                                    if (not(FoundFirst)):
                                        if "1-0:1.7.0" in p1_line:
                                            FoundFirst = True
                                            self.create_raw_point_locally(influx_measurement, influx_host, counter, p1_line)
                                    else:
                                        if "1-0:1.7.0" in p1_line:
                                            FinishedRaw = True 
                                        else:
                                            self.create_raw_point_locally(influx_measurement, influx_host, counter, p1_line)
                                            linefound += 1                                       

                            try:
                                Influx.WriteData()
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
                        Reveived = True
                    except Exception as e:
                        print(e)
                        print("read eror")
                        #sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % s$
                        #print("receive error")
                        Reveived = False

                    if Reveived:
                        p1_str=str(p1_raw)
                        p1_line=p1_str.strip()

                        if "1-3:0.2.8" in p1_line:
                            self.create_data_point_locally(influx_measurement, influx_host, "dsmr", self.ParseLine(p1_line))

                            if receivedcounter > 1:

                                difference = datetime.utcnow() - OldTime
                                difference_in_seconds = difference.total_seconds()

                                if difference_in_seconds > 60:
                                    
                                    huidig_verbruik = ( huidig_verbruik_cum / received_huidig_verbruik)
                                    # print (str(huidig_verbruik_cum) + "/" + str(received_huidig_verbruik) + "=" + str($
                                    huidig_terug = ( huidig_terug_cum / received_huidig_terug )
                                    # print (str(huidig_terug_cum) + "/" + str(received_huidig_terug) + "=" + str(huidig$
                                    huidig = (huidig_verbruik - huidig_terug)*1000

                                    #also send 0's to know difference between null and 0
                                    self.create_data_point_locally(influx_measurement, influx_host, "huidig_verbruik", (huidig_verbruik*1000))                                
                                    self.create_data_point_locally(influx_measurement, influx_host, "huidig_terug", (huidig_terug*1000))

                                    self.create_data_point_locally(influx_measurement, influx_host, "huidig", huidig)                



                                    if not(Volt1 is None) and ( not(Watt_terug1) or not(Watt_ver1) ):
                                        if Watt_ver1 is None:
                                            Watt_ver1 = 0
                                        if Watt_terug1 is None:
                                            Watt_terug1 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp1_calc", ((Watt_ver1 - Watt_terug1) / Volt1))




                                    if not(Volt2 is None) and ( not(Watt_terug2) or not(Watt_ver2) ):
                                        if Watt_ver2 is None:
                                            Watt_ver2 = 0
                                        if Watt_terug2 is None:
                                            Watt_terug2 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp2_calc", ((Watt_ver2 - Watt_terug2) / Volt2))




                                    if not(Volt3 is None) and ( not(Watt_terug3) or not(Watt_ver3) ):
                                        if Watt_ver3 is None:
                                            Watt_ver3 = 0
                                        if Watt_terug3 is None:
                                            Watt_terug3 = 0

                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp3_calc", ((Watt_ver3 - Watt_terug3) / Volt3))





                                    if first_run:
                                        vorige_waarde = huidig
                                        first_run = False
                                    elif second_run:
                                        vorige_waarde = huidig
                                        vorige_waarde_2 = vorige_waarde
                                        second_run = False
                                    else: 
                                        Current_delta = huidig - vorige_waarde
                                        Current_delta2 = huidig - vorige_waarde_2
                                        self.create_data_point_locally(influx_measurement, influx_host, "Current_delta", Current_delta)
                                        self.create_data_point_locally(influx_measurement, influx_host, "Current_delta2", Current_delta2)
                                        vorige_waarde_2 = vorige_waarde
                                        vorige_waarde = huidig


                                    huidig_verbruik_cum = 0.0
                                    received_huidig_verbruik = 0
                                    huidig_terug_cum = 0.0
                                    received_huidig_terug = 0
                                    huidig_verbruik = 0.0
                                    huidig_terug = 0.0


                                    Volt1 = None
                                    Watt_terug1 = None
                                    Watt_ver1 = None
                                    Volt2 = None
                                    Watt_terug2 = None
                                    Watt_ver2 = None
                                    Volt3 = None
                                    Watt_terug3 = None
                                    Watt_ver3 = None


                                    OldTime = datetime.utcnow()

                                    DoRawLog = True
                                    DidAFullRaw = False

                            else:
                                
                                receivedcounter+= 1

                            time.sleep(10)
                        else:

                            # als je alles wil zien moet je de volgende line uncommenten print (p1_li$
                            if "1-0:1.7.0" in p1_line:
                                verbruik_waarde = self.ParseLine(p1_line)
                                if not(verbruik_waarde is None):
                                    huidig_verbruik_cum += verbruik_waarde
                                    received_huidig_verbruik += 1

                            if "1-0:2.7.0" in p1_line:
                                terug_waarde = self.ParseLine(p1_line)
                                if not(terug_waarde is None):
                                    huidig_terug_cum += terug_waarde
                                    received_huidig_terug += 1

                            if DoRawLog:

                                if "0-0:96.14.0" in p1_line:
                                    dal_piek = self.ParseLine(p1_line)
                                    if not (dal_piek is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "dal_piek_fl", dal_piek)

                                if "1-0:1.8.1" in p1_line:
                                    totaal_verbruik_dal = self.ParseLine(p1_line)

                                    if not (totaal_verbruik_dal is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "totaal_verbruik_dal_fl", totaal_verbruik_dal)

                                        #check for 24h change in this value
                                        DailyChange = Transform.manage_daily_usage("totaal_verbruik_dal_fl", totaal_verbruik_dal)
                                        if not DailyChange is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "totaal_verbruik_dal_fl_change", DailyChange)


                                if "1-0:1.8.2" in p1_line:
                                    totaal_verbruik_piek = self.ParseLine(p1_line)

                                    if not (totaal_verbruik_piek is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "totaal_verbruik_piek_fl", totaal_verbruik_piek)

                                        #check for 24h change in this value
                                        DailyChange = Transform.manage_daily_usage("totaal_verbruik_piek_fl", totaal_verbruik_piek)
                                        if not DailyChange is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "totaal_verbruik_piek_fl_change", DailyChange)


                                if "1-0:2.8.1" in p1_line:
                                    totaal_terug_dal = self.ParseLine(p1_line)

                                    if not (totaal_terug_dal is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "totaal_terug_dal_fl", totaal_terug_dal)

                                        #check for 24h change in this value
                                        DailyChange = Transform.manage_daily_usage("totaal_terug_dal_fl", totaal_terug_dal)
                                        if not DailyChange is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "totaal_terug_dal_fl_change", DailyChange)



                                if "1-0:2.8.2" in p1_line:
                                    totaal_terug_piek = self.ParseLine(p1_line)

                                    if not (totaal_terug_piek is None) :
                                        self.create_data_point_locally(influx_measurement, influx_host, "totaal_terug_piek_fl", totaal_terug_piek)

                                        #check for 24h change in this value
                                        DailyChange = Transform.manage_daily_usage("totaal_terug_piek_fl", totaal_terug_piek)
                                        if not DailyChange is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "totaal_terug_piek_fl_change", DailyChange)




                                if "1-0:32.7.0" in p1_line:
                                    Volt1 = self.ParseLine(p1_line)

                                    if not (Volt1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "volt", Volt1, "L1")

                                        if DidAFullRaw:
                                            DoRawLog = False
                                        else:
                                            DidAFullRaw = True

                                if "1-0:31.7.0" in p1_line:
                                    Amp1 = self.ParseLine(p1_line)

                                    if not (Amp1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp", Amp1, "L1")

                                if "1-0:21.7.0" in p1_line:
                                    Watt_ver1 = self.ParseLine(p1_line)

                                    if not (Watt_ver1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_verbruik", Watt_ver1, "L1")

                                if "1-0:22.7.0" in p1_line:
                                    Watt_terug1 = self.ParseLine(p1_line)

                                    if not (Watt_terug1 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_terug", Watt_terug1, "L1")

                                if "1-0:52.7.0" in p1_line:
                                    Volt2 = self.ParseLine(p1_line)

                                    if not (Volt2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "volt", Volt2, "L2")

                                if "1-0:51.7.0" in p1_line:
                                    Amp2 = self.ParseLine(p1_line)

                                    if not (Amp2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp", Amp2, "L2")

                                if "1-0:41.7.0" in p1_line:
                                    Watt_ver2 = self.ParseLine(p1_line)

                                    if not (Watt_ver2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_verbruik", Watt_ver2, "L2")

                                if "1-0:42.7.0" in p1_line:
                                    Watt_terug2 = self.ParseLine(p1_line)

                                    if not (Watt_terug2 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_terug", Watt_terug2, "L2")

                                if "1-0:72.7.0" in p1_line:
                                    Volt3 = self.ParseLine(p1_line)

                                    if not (Volt3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "volt", Volt3, "L3")

                                if "1-0:71.7.0" in p1_line:
                                    Amp3 = self.ParseLine(p1_line)

                                    if not (Amp3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Amp", Amp3, "L3")

                                if "1-0:61.7.0" in p1_line:
                                    Watt_ver3 = self.ParseLine(p1_line)

                                    if not (Watt_ver3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_verbruik", Watt_ver3, "L3")

                                if "1-0:62.7.0" in p1_line:
                                    Watt_terug3 = self.ParseLine(p1_line)

                                    if not (Watt_terug3 is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Watt_terug", Watt_terug3, "L3")

                                if "0-1:24.2.1" in p1_line:
                                    Gas_Volume = self.ParseLine(p1_line)

                                    if not (Gas_Volume is None):
                                        self.create_data_point_locally(influx_measurement, influx_host, "Gas_Volume", Gas_Volume)

                                        #check for 24h change in this value
                                        DailyChange = Transform.manage_daily_usage("Gas_Volume", Gas_Volume)
                                        if not DailyChange is None: # if there was a daily value to store
                                            self.create_data_point_locally(influx_measurement, influx_host, "Gas_Volume_change", DailyChange)

                                        Gas_Flow = Transform.gas_flow("Gas_Flow",Gas_Volume)

                                        if not (Gas_Flow is None):
                                            self.create_data_point_locally(influx_measurement, influx_host, "Gas_Flow", Gas_Flow)


                    try:
                        Influx.WriteData()
                    except Exception as e:
                        print(e)
                        print("write error")



                    # #Close port and show status
                    # try:
                    #     print("closed unexpectedly")
                    #     ser.close()
                    # except:
                    #     print("error at close")




if __name__ == '__main__':
    Meterclass = Meter()
    Meterclass.main_loop()
