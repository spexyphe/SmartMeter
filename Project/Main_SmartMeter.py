version = "0.1.2"

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

class Meter():

    def __init__(self):
        print("init smartmeter")

    def NewLog(self, StrMessage, AnException = None):
        global doTRACE

        if("ERROR" in StrMessage):
            logging.error( "Eastron.py, " + StrMessage)
            
            if not (AnException is None):
                logging.error(str(AnException))    
        elif("WARNING" in StrMessage):
            logging.warning( "Eastron.py, " + StrMessage)

            if not (AnException is None):
                logging.warning(str(AnException))   
        else:
            if doTRACE:
                logging.info( "Eastron.py, " + StrMessage)

                if not (AnException is None):
                    logging.info(str(AnException)) 

    def LoadEnvVar_Sys(self):
        global doTRACE, IslocalTest, IsVarRun
        
        #by default we are doTRACE-ing
        IslocalTest = False
        doTRACE = True 
        IsVarRun = True
        
        try: #doTRACE
            doTRACE = eval( os.environ['doTRACE'] )
            self.NewLog("OK: succesfully loaded environment variable for system 'doTRACE'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for system 'doTRACE' FAILED", e)

        try: #ISLOCALTEST
            IslocalTest = eval( os.environ['ISLOCALTEST'] )
            self.NewLog("OK: succesfully loaded environment variable for system 'ISLOCALTEST': " + str(IslocalTest))
        except Exception as e:
            self.NewLog("ERROR: environment variable for system 'ISLOCALTEST' FAILED", e)

        try: #ISVARRUN
            IsVarRun = eval( os.environ['ISVARRUN'] )
            self.NewLog("OK: succesfully loaded environment variable for system 'ISVARRUN'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for system 'ISVARRUN' FAILED", e)

    def LoadEnvVar_ModBus(self):

        global Device, Baud, Parity, Variables

        Device = "/dev/ttyUSB0"
        Baud = 115200
        Parity = "E" 
        Variables = ""

        try: #MODBUS_DEVICE
            Device = os.environ['MODBUS_DEVICE']
            self.NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_DEVICE'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for Modbus 'MODBUS_DEVICE' FAILED", e)

        try: #MODBUS_BAUD
            Baud = int(os.environ['MODBUS_BAUD'])
            self.NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_BAUD'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for Modbus 'MODBUS_BAUD' FAILED", e)
        
        try: #MODBUS_PARITY
            Parity = os.environ['MODBUS_PARITY']
            self.NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_PARITY'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for Modbus 'MODBUS_PARITY' FAILED", e)

        try: #MODBUS_VARIABLES
            Variables = os.environ['MODBUS_VARIABLES']
            self.NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_VARIABLES'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for Modbus 'MODBUS_VARIABLES' FAILED", e)

    def ParseVariables(self, IN_Variables):
        OUT_Variables = None

        try:
            OUT_Variables = IN_Variables.split(",")    
        except Exception as e:
            self.NewLog("ERROR, ParseVariables Failed", e)
        
        return OUT_Variables

    def LoadEnvVar_Influx(self):
        global Influx_url, Influx_port, Influx_user, Influx_password, Influx_database, Influx_measurement, influx_host

        EnvVarInfluxSuccess = True
        
        try: #INFLUX_URL
            Influx_url = os.environ['INFLUX_URL']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_URL'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_URL' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_PORT
            Influx_port = int(os.environ['INFLUX_PORT'])
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_PORT'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_PORT' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_USER
            Influx_user = os.environ['INFLUX_USER']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_USER'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_USER' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_PASSWORD
            Influx_password = os.environ['INFLUX_PASSWORD']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_PASSWORD'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_PASSWORD' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_DATABASE
            Influx_database = os.environ['INFLUX_DATABASE']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_DATABASE'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_DATABASE' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_MEASUREMENT
            Influx_measurement = os.environ['INFLUX_MEASUREMENT']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_MEASUREMENT'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_MEASUREMENT' FAILED", e)
            EnvVarInfluxSuccess = False

        try: #INFLUX_HOST
            influx_host = os.environ['INFLUX_HOST']
            self.NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_HOST'")
        except Exception as e:
            self.NewLog("ERROR: environment variable for influx 'INFLUX_HOST' FAILED", e)
            EnvVarInfluxSuccess = False

        return EnvVarInfluxSuccess

    #dashboards don't always like boolean values, convert to int
    def BoolToInflux(self, Input):

        if type(Input)==bool:
            if Input == True:
                return "true"
            else:
                return "false"
        else:
            return None

    def UpdateVersion(self, Measurement, Host):

            # Tags are fixed values, that are not time zone transformed
            # Hence for tags we need the current timezone
            #Else we get a timezone difference
            tz = pytz.timezone('Europe/Amsterdam')
            Amsterdam_now = datetime.now(tz)

            # tag values that allows searching based on time tags
            CurrentYear = str(Amsterdam_now.strftime("%Y"))
            CurrentMonthNr = str(Amsterdam_now.strftime("%m"))
            CurrentWeekNr = str(Amsterdam_now.strftime("%U"))
            CurrentDayNr = str(Amsterdam_now. strftime("%w"))

            #using point time to log things will ensure that everything uses the same time
            PointTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            Influx.AddDataPoint(Measurement, Host , CurrentYear, CurrentMonthNr, CurrentWeekNr, CurrentDayNr, "Version", version, PointTime )

    def CreateRawPointLocally(self, Measurement, Host, LineNr, Value):

            #using point time to log things will ensure that everything uses the same time
            PointTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            Influx.AddRawPoint(Measurement, Host, LineNr, "Raw", Value, PointTime)


    def CreateDataPointLocally(self, Measurement, Host, ValueName, Value, Phase=None):

            # Tags are fixed values, that are not time zone transformed
            # Hence for tags we need the current timezone
            #Else we get a timezone difference
            tz = pytz.timezone('Europe/Amsterdam')
            Amsterdam_now = datetime.now(tz)

            # tag values that allows searching based on time tags
            CurrentYear = str(Amsterdam_now.strftime("%Y"))
            CurrentMonthNr = str(Amsterdam_now.strftime("%m"))
            CurrentWeekNr = str(Amsterdam_now.strftime("%U"))
            CurrentDayNr = str(Amsterdam_now. strftime("%w"))

            #using point time to log things will ensure that everything uses the same time
            PointTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            Influx.AddDataPoint(Measurement, Host, CurrentYear, CurrentMonthNr, CurrentWeekNr, CurrentDayNr, ValueName, Value, PointTime, Phase)

    def ParseLine(self, In_Line):
        Out_Line = None

        try:
            if In_Line.count('*') > 0:
                if In_Line.count(')') == 2:
                    Out_Line = float(In_Line[In_Line.index(')')+2:In_Line.index('*')])
                else:
                    Out_Line = float(In_Line[In_Line.index('(')+1:In_Line.index('*')])
            else:    
                Out_Line = float(In_Line[In_Line.index('(')+1:In_Line.index(')')])

        except Exception as e:
            print(e)

        return Out_Line

    def MainLoop(self):

        timeinbetween = 3600
        lastDateTime = datetime.utcnow()
        initrun = True

        #load system and modbus variables from the environment
        self.LoadEnvVar_Sys()
        self.LoadEnvVar_ModBus()

        #the variables that are loaded
        global IslocalTest, doTRACE, IsVarRun
        global Device, Baud, Parity, Variables

        #parse the list of variables as defined in the environment
        ListOfVar = self.ParseVariables(Variables)

        # safety check: did we detect variables
        if (not (ListOfVar is None)) and len(ListOfVar) > 0:

            # load environment variables regarding influx
            if self.LoadEnvVar_Influx():

                #the variables that where loaded
                global Influx_url, Influx_port, Influx_user, Influx_password, Influx_database, Influx_measurement, influx_host

                # init the influx connection
                #Influx.Init_Influx(Influx_url, Influx_org, Influx_bucket, IslocalTest, Influx_token, doTRACE)
                Influx.Init_Influx(Influx_user, Influx_password, Influx_url, Influx_port, Influx_database, IslocalTest, doTRACE)

                #Set COM port config
                ser = serial.Serial()
                
                ser.baudrate = Baud
                ser.port= Device

                if Parity == "E":
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
                    sys.exit ("Fout bij het openen van %s. Aaaaarch."  % ser.name)


                Vorigewaarde = 0.0
                Vorigewaarde2 = 0.0

                FirstRun = True
                SecondRun = True

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
                    if (((datetime.utcnow() - lastDateTime).total_seconds()) > timeinbetween) or initrun:
                        
                        #update time
                        lastDateTime = datetime.utcnow()
                        
                        #send version number to influx
                        self.UpdateVersion(Influx_measurement, influx_host)

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
                                            self.CreateRawPointLocally(Influx_measurement, influx_host, counter, p1_line)
                                    else:
                                        if "1-0:1.7.0" in p1_line:
                                            FinishedRaw = True 
                                        else:
                                            self.CreateRawPointLocally(Influx_measurement, influx_host, counter, p1_line)
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
                        if initrun:
                            #not anymore now
                            initrun = False 



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
                            self.CreateDataPointLocally(Influx_measurement, influx_host, "dsmr", self.ParseLine(p1_line))

                            if receivedcounter > 1:

                                difference = datetime.utcnow() - OldTime
                                difference_in_seconds = difference.total_seconds()

                                if difference_in_seconds > 60:
                                    
                                    huidig_verbruik = ( huidig_verbruik_cum / received_huidig_verbruik)
                                    # print (str(huidig_verbruik_cum) + "/" + str(received_huidig_verbruik) + "=" + str($
                                    huidig_terug = ( huidig_terug_cum / received_huidig_terug )
                                    # print (str(huidig_terug_cum) + "/" + str(received_huidig_terug) + "=" + str(huidig$
                                    huidig = (huidig_verbruik - huidig_terug)*1000

                                    if huidig_verbruik != 0:
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "huidig_verbruik", (huidig_verbruik*1000))
                                
                                    if huidig_terug != 0:
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "huidig_terug", (huidig_terug*1000))

                                    self.CreateDataPointLocally(Influx_measurement, influx_host, "huidig", huidig)                



                                    if not(Volt1 is None) and ( not(Watt_terug1) or not(Watt_ver1) ):
                                        if Watt_ver1 is None:
                                            Watt_ver1 = 0
                                        if Watt_terug1 is None:
                                            Watt_terug1 = 0

                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp1_calc", ((Watt_ver1 - Watt_terug1) / Volt1))




                                    if not(Volt2 is None) and ( not(Watt_terug2) or not(Watt_ver2) ):
                                        if Watt_ver2 is None:
                                            Watt_ver2 = 0
                                        if Watt_terug2 is None:
                                            Watt_terug2 = 0

                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp2_calc", ((Watt_ver2 - Watt_terug2) / Volt2))




                                    if not(Volt3 is None) and ( not(Watt_terug3) or not(Watt_ver3) ):
                                        if Watt_ver3 is None:
                                            Watt_ver3 = 0
                                        if Watt_terug3 is None:
                                            Watt_terug3 = 0

                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp3_calc", ((Watt_ver3 - Watt_terug3) / Volt3))





                                    if FirstRun:
                                        Vorigewaarde = huidig
                                        FirstRun = False
                                    elif SecondRun:
                                        Vorigewaarde = huidig
                                        Vorigewaarde2 = Vorigewaarde
                                        SecondRun = False
                                    else: 
                                        Current_Delta = huidig - Vorigewaarde
                                        Current_Delta2 = huidig - Vorigewaarde2
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Current_Delta", Current_Delta)
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Current_Delta2", Current_Delta2)
                                        Vorigewaarde2 = Vorigewaarde
                                        Vorigewaarde = huidig


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
                                huidig_verbruik_cum += self.ParseLine(p1_line)
                                received_huidig_verbruik += 1

                            if "1-0:2.7.0" in p1_line:
                                huidig_terug_cum += self.ParseLine(p1_line)
                                received_huidig_terug += 1

                            if DoRawLog:

                                if "0-0:96.14.0" in p1_line:
                                    dal_piek = self.ParseLine(p1_line)
                                    if not (dal_piek is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "dal_piek_fl", dal_piek)

                                if "1-0:1.8.1" in p1_line:
                                    totaal_verbruik_dal = self.ParseLine(p1_line)

                                    if not (totaal_verbruik_dal is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "totaal_verbruik_dal_fl", totaal_verbruik_dal)

                                if "1-0:1.8.2" in p1_line:
                                    totaal_verbruik_piek = self.ParseLine(p1_line)

                                    if not (totaal_verbruik_piek is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "totaal_verbruik_piek_fl", totaal_verbruik_piek)

                                if "1-0:2.8.1" in p1_line:
                                    totaal_terug_dal = self.ParseLine(p1_line)

                                    if not (totaal_terug_dal is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "totaal_terug_dal_fl", totaal_terug_dal)

                                if "1-0:2.8.2" in p1_line:
                                    totaal_terug_piek = self.ParseLine(p1_line)

                                    if not (totaal_terug_piek is None) :
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "totaal_terug_piek_fl", totaal_terug_piek)

                                if "1-0:32.7.0" in p1_line:
                                    Volt1 = self.ParseLine(p1_line)

                                    if not (Volt1 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "volt", Volt1, "L1")

                                        if DidAFullRaw:
                                            DoRawLog = False
                                        else:
                                            DidAFullRaw = True

                                if "1-0:31.7.0" in p1_line:
                                    Amp1 = self.ParseLine(p1_line)

                                    if not (Amp1 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp", Amp1, "L1")

                                if "1-0:21.7.0" in p1_line:
                                    Watt_ver1 = self.ParseLine(p1_line)

                                    if not (Watt_ver1 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_verbruik", Watt_ver1, "L1")

                                if "1-0:22.7.0" in p1_line:
                                    Watt_terug1 = self.ParseLine(p1_line)

                                    if not (Watt_terug1 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_terug", Watt_terug1, "L1")

                                if "1-0:52.7.0" in p1_line:
                                    Volt2 = self.ParseLine(p1_line)

                                    if not (Volt2 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "volt", Volt2, "L2")

                                if "1-0:51.7.0" in p1_line:
                                    Amp2 = self.ParseLine(p1_line)

                                    if not (Amp2 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp", Amp2, "L2")

                                if "1-0:41.7.0" in p1_line:
                                    Watt_ver2 = self.ParseLine(p1_line)

                                    if not (Watt_ver2 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_verbruik", Watt_ver2, "L2")

                                if "1-0:42.7.0" in p1_line:
                                    Watt_terug2 = self.ParseLine(p1_line)

                                    if not (Watt_terug2 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_terug", Watt_terug2, "L2")

                                if "1-0:72.7.0" in p1_line:
                                    Volt3 = self.ParseLine(p1_line)

                                    if not (Volt3 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "volt", Volt3, "L3")

                                if "1-0:71.7.0" in p1_line:
                                    Amp3 = self.ParseLine(p1_line)

                                    if not (Amp3 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Amp", Amp3, "L3")

                                if "1-0:61.7.0" in p1_line:
                                    Watt_ver3 = self.ParseLine(p1_line)

                                    if not (Watt_ver3 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_verbruik", Watt_ver3, "L3")

                                if "1-0:62.7.0" in p1_line:
                                    Watt_terug3 = self.ParseLine(p1_line)

                                    if not (Watt_terug3 is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Watt_terug", Watt_terug3, "L3")

                                if "0-1:24.2.1" in p1_line:
                                    Gas_Volume = self.ParseLine(p1_line)

                                    if not (Gas_Volume is None):
                                        self.CreateDataPointLocally(Influx_measurement, influx_host, "Gas_Volume", Gas_Volume)




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
    Meterclass.MainLoop()
