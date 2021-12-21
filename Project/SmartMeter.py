version = "0.0.3"

import os
import logging
import sys
import time
import json

from datetime import datetime
import pytz

import serial

try:
    import Mod_Influx as Influx
except Exception as e:
    logging.error("failed to load custom influx module: " + str(e))

def NewLog(StrMessage):
    global doTRACE

    if("ERROR" in StrMessage):
        logging.error( "Eastron.py, " + StrMessage)
    elif("WARNING" in StrMessage):
        logging.warning( "Eastron.py, " + StrMessage)
    else:
        if doTRACE:
            logging.info( "Eastron.py, " + StrMessage)

def LoadEnvVar_Sys():
    global doTRACE, IslocalTest, IsVarRun
    
    #by default we are doTRACE-ing
    IslocalTest = False
    doTRACE = True 
    IsVarRun = True
    
    try: #doTRACE
        doTRACE = eval( os.environ['doTRACE'] )
        NewLog("OK: succesfully loaded environment variable for system 'doTRACE'")
    except:
        NewLog("ERROR: environment variable for system 'doTRACE' FAILED")

    try: #ISLOCALTEST
        IslocalTest = eval( os.environ['ISLOCALTEST'] )
        NewLog("OK: succesfully loaded environment variable for system 'ISLOCALTEST': " + str(IslocalTest))
    except:
        NewLog("ERROR: environment variable for system 'ISLOCALTEST' FAILED")

    try: #ISVARRUN
        IsVarRun = eval( os.environ['ISVARRUN'] )
        NewLog("OK: succesfully loaded environment variable for system 'ISVARRUN'")
    except:
        NewLog("ERROR: environment variable for system 'ISVARRUN' FAILED")

def LoadEnvVar_ModBus():

    global Device, Baud, Parity, Variables

    Device = "/dev/ttyUSB0"
    Baud = 115200
    Parity = "E" 
    Variables = ""

    try: #MODBUS_DEVICE
        Device = os.environ['MODBUS_DEVICE']
        NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_DEVICE'")
    except:
        NewLog("ERROR: environment variable for Modbus 'MODBUS_DEVICE' FAILED")

    try: #MODBUS_BAUD
        Baud = int(os.environ['MODBUS_BAUD'])
        NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_BAUD'")
    except:
        NewLog("ERROR: environment variable for Modbus 'MODBUS_BAUD' FAILED")
    
    try: #MODBUS_PARITY
        Parity = os.environ['MODBUS_PARITY']
        NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_PARITY'")
    except:
        NewLog("ERROR: environment variable for Modbus 'MODBUS_PARITY' FAILED")

    try: #MODBUS_VARIABLES
        Variables = os.environ['MODBUS_VARIABLES']
        NewLog("OK: succesfully loaded environment variable for Modbus 'MODBUS_VARIABLES'")
    except:
        NewLog("ERROR: environment variable for Modbus 'MODBUS_VARIABLES' FAILED")

def ParseVariables(IN_Variables):
    OUT_Variables = None

    try:
        OUT_Variables = IN_Variables.split(",")    
    except:
        NewLog("ERROR, ParseVariables Failed")
    
    return OUT_Variables

def LoadEnvVar_Influx():
    global Influx_url, Influx_port, Influx_user, Influx_password, Influx_database, Influx_measurement, influx_host

    EnvVarInfluxSuccess = True
    
    try: #INFLUX_URL
        Influx_url = os.environ['INFLUX_URL']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_URL'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_URL' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_PORT
        Influx_port = int(os.environ['INFLUX_PORT'])
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_PORT'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_PORT' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_USER
        Influx_user = os.environ['INFLUX_USER']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_USER'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_USER' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_PASSWORD
        Influx_password = os.environ['INFLUX_PASSWORD']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_PASSWORD'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_PASSWORD' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_DATABASE
        Influx_database = os.environ['INFLUX_DATABASE']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_DATABASE'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_DATABASE' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_MEASUREMENT
        Influx_measurement = os.environ['INFLUX_MEASUREMENT']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_MEASUREMENT'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_MEASUREMENT' FAILED")
        EnvVarInfluxSuccess = False

    try: #INFLUX_HOST
        influx_host = os.environ['INFLUX_HOST']
        NewLog("OK: succesfully loaded environment variable for influx 'INFLUX_HOST'")
    except:
        NewLog("ERROR: environment variable for influx 'INFLUX_HOST' FAILED")
        EnvVarInfluxSuccess = False

    return EnvVarInfluxSuccess

#dashboards don't always like boolean values, convert to int
def BoolToInflux(Input):

    if type(Input)==bool:
        if Input == True:
            return "true"
        else:
            return "false"
    else:
        return None

def UpdateVersion(Measurement, Host):

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

def CreateDataPointLocally(Measurement, Host, ValueName, Value):

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

        Influx.AddDataPoint(Measurement, Host, CurrentYear, CurrentMonthNr, CurrentWeekNr, CurrentDayNr, ValueName, Value, PointTime)

#trims starting zeros
def Trim0(MyInput):
    running = True

    while running and len(MyInput) > 0:
        if MyInput[0] == '0':
            MyInput = MyInput[1:]
        else:
            running = False

    if len(MyInput) > 0:
        if MyInput[0] == '.':
            MyInput = "0" + MyInput

    return MyInput


if __name__ == '__main__':

    timeinbetween = 3600
    lastDateTime = datetime.utcnow()
    firstrun = True

    #load system and modbus variables from the environment
    LoadEnvVar_Sys()
    LoadEnvVar_ModBus()

    #the variables that are loaded
    global IslocalTest, doTRACE, IsVarRun
    global Device, Baud, Parity, Variables

    #parse the list of variables as defined in the environment
    ListOfVar = ParseVariables(Variables)

    # safety check: did we detect variables
    if (not (ListOfVar is None)) and len(ListOfVar) > 0:

        # load environment variables regarding influx
        if LoadEnvVar_Influx():

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

            # run our program cotiniously
            while True:

                # update the influx database on the version we are running
                if (((datetime.utcnow() - lastDateTime).total_seconds()) > timeinbetween) or firstrun:
                    
                    #update time
                    lastDateTime = datetime.utcnow()
                    
                    #send version number to influx
                    UpdateVersion(Influx_measurement, influx_host)

                    #was this the first run
                    if firstrun:
                        #not anymore now
                        firstrun = False 

                Vorigewaarde = 0.0
                Vorigewaarde2 = 0.0

                FirstRun = True
                SecondRun = True

                #Open COM port
                while True:

                    totaal_verbruik_dal = 0.0
                    totaal_verbruik_piek = 0.0
                    totaal_terug_piek = 0.0
                    totaal_terug_dal = 0.0
                    huidig_verbruik_cum = 0.0
                    huidig_terug_cum = 0.0
                    dal_piek = 0
                    huidig_verbruik = 0.0
                    huidig_terug = 0.0
                    receivedcounter = 0
                    received_huidig_verbruik = 0
                    received_huidig_terug = 0

                    if FirstRun:
                        try:

                            FoundFirst = False
                            FinishedRaw = False

                            while(not(FinishedRaw)):

                                p1_raw = ser.readline()

                                if(Reveived):
                                    p1_str=str(p1_raw)
                                    p1_line=p1_str.strip()

                                    if (not(FoundFirst)):
                                        if "1-0:1.7.0" in p1_line:
                                            FoundFirst = True
                                            CreateDataPointLocally(Influx_measurement, influx_host, "raw", p1_line)
                                    else:
                                        if "1-0:1.7.0" in p1_line:
                                            FinishedRaw = True 
                                        else:
                                            CreateDataPointLocally(Influx_measurement, influx_host, "raw", p1_line)                                       

                        except Exception as e:
                            print(e)
                            print("read eror")
                            #sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % s$
                            #print("receive error")
                            Reveived = False

                    for i in range (0,9):
                        try:
                            p1_teller = 0

                            while p1_teller < 20:
                                p1_line=''
                                #Read 1 line van de seriele poort

                                try:
                                    p1_raw = ser.readline()
                                    Reveived = True
                                    receivedcounter = receivedcounter + 1
                                except Exception as e:
                                    print(e)
                                    print("read eror")
                                    #sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % s$
                                    #print("receive error")
                                    Reveived = False

                                if(Reveived):
                                    p1_str=str(p1_raw)
                                    p1_line=p1_str.strip()

                                # als je alles wil zien moet je de volgende line uncommenten print (p1_li$
                                    if "1-0:1.7.0" in p1_line:
                                        p1_line_parse=p1_line[12:p1_line.index("*")]
                                        huidig_verbruik_cum += float(Trim0(p1_line_parse))
                                        received_huidig_verbruik += 1

                                    if "1-0:2.7.0" in p1_line:
                                        p1_line_parse=p1_line[12:p1_line.index("*")]
                                        huidig_terug_cum += float(Trim0(p1_line_parse))
                                        received_huidig_terug += 1

                                    if "0-0:96.14.0" in p1_line:
                                        p1_line_parse= p1_line[14:p1_line.index(")")]
                                        dal_piek = float(Trim0(p1_line_parse))

                                    if "1-0:1.8.1" in p1_line:
                                        try:
                                            #print(p1_line)
                                            p1_line_parse=p1_line[12:p1_line.index("*")]
                                            #print(p1_line_parse) 
                                            totaal_verbruik_dal = float(Trim0(p1_line_parse))
                                        except Exception as e:
                                            print (e)
                                            print ("totaal_verbruik_dal parse error") 
                    

                                    if "1-0:1.8.2" in p1_line:
                                        p1_line_parse=p1_line[12:p1_line.index("*")] 
                                        totaal_verbruik_piek = float(Trim0(p1_line_parse))

                                    if "1-0:2.8.1" in p1_line:
                                        p1_line_parse=p1_line[12:p1_line.index("*")]
                                        totaal_terug_dal = float(Trim0(p1_line_parse))

                                    if "1-0:2.8.2" in p1_line:
                                        p1_line_parse=p1_line[12:p1_line.index("*")]
                                        totaal_terug_piek = float(Trim0(p1_line_parse))

                                    p1_teller = p1_teller +1

                        except Exception as e:
                            print(e)
                            print("error in loop")

                        time.sleep(1)

                    if receivedcounter > 0:
                        huidig_verbruik = ( huidig_verbruik_cum / received_huidig_verbruik)
                        # print (str(huidig_verbruik_cum) + "/" + str(received_huidig_verbruik) + "=" + str($
                        huidig_terug = ( huidig_terug_cum / received_huidig_terug )
                        # print (str(huidig_terug_cum) + "/" + str(received_huidig_terug) + "=" + str(huidig$
                        huidig = (huidig_verbruik - huidig_terug)*1000

                    CreateDataPointLocally(Influx_measurement, influx_host, "huidig", huidig)

                    if dal_piek != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "dal_piek", dal_piek)

                    if huidig_verbruik != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "huidig_verbruik", (huidig_verbruik*1000))
                
                    if huidig_terug != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "huidig_terug", (huidig_terug*1000))

                    if totaal_verbruik_dal != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "totaal_verbruik_dal", totaal_verbruik_dal)

                    if totaal_verbruik_piek != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "totaal_verbruik_piek", totaal_verbruik_piek)

                    if totaal_terug_dal != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "totaal_terug_dal", totaal_terug_dal)

                    if totaal_terug_piek != 0:
                        CreateDataPointLocally(Influx_measurement, influx_host, "totaal_terug_piek", totaal_terug_piek)

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
                        CreateDataPointLocally(Influx_measurement, influx_host, "Current_Delta", Current_Delta)
                        CreateDataPointLocally(Influx_measurement, influx_host, "Current_Delta2", Current_Delta2)
                        Vorigewaarde2 = Vorigewaarde
                        Vorigewaarde = huidig

                    try:
                        Influx.WriteData()
                    except Exception as e:
                        print(e)
                        print("write error")

                #Close port and show status
                try:
                    print("closed unexpectedly")
                    ser.close()
                except:
                    print("error at close")
