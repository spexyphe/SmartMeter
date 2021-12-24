import sys
import logging

import json

try:
    from influxdb import InfluxDBClient
except Exception as e:
    logging.error("failed to load influx modules: " + str(e))


def NewLog(StrMessage):
    global LogInflux

    if("ERROR" in StrMessage):
        logging.error( "Mod_Influx.py, " + StrMessage)
    elif("WARNING" in StrMessage):
        logging.warning( "Mod_Influx.py, " + StrMessage)
    else:
        if LogInflux:
            logging.info( "Mod_Influx.py, " + StrMessage)

def CheckTags(DataYear, DataMonth, DataWeek, DataDay):

    answer = True

    try:

        if not(int(DataYear) > 2000 and int(DataYear) < 10000):
            answer = False
        
        if not(int(DataMonth) > 0 and int(DataMonth) < 13):
            answer = False

        if not(int(DataWeek) > -1 and int(DataWeek) < 54):
            answer = False

        if not(int(DataDay) > -1 and int(DataDay) < 8):
            answer = False

    except Exception as e:
        answer = False
        NewLog("ERROR: CheckTags: " + str(e))

    return answer

def AddRawPoint(Measurement, DataHost, LineNr, ValueName, Value, PointTime):
    global DataPoints

    RawDataJsonPoint = json.loads('' or '{}')
    RawDataJsonPoint["measurement"] = Measurement

    if not ("tags" in RawDataJsonPoint):
        RawDataJsonPoint["tags"] = {}
            
    if not ("host" in RawDataJsonPoint["tags"]):
        RawDataJsonPoint["tags"]["host"] = DataHost

    if not ("year" in RawDataJsonPoint["tags"]):
        RawDataJsonPoint["tags"]["LineNr"] = LineNr

    if not ("fields" in RawDataJsonPoint):
        RawDataJsonPoint["fields"] = {}

    if not (ValueName in RawDataJsonPoint["fields"]):
        RawDataJsonPoint["fields"][ValueName] = Value

    RawDataJsonPoint["time"] = PointTime

    NewLog("OK: " + DataHost + "-" + ValueName + "(" + str(Value) + ")"  + ": " + PointTime)

    DataPoints.append(RawDataJsonPoint)



def AddDataPoint(Measurement, DataHost, DataYear, DataMonth, DataWeek, DataDay, ValueName, Value, PointTime, Phase=None):
    global DataPoints

    RawDataJsonPoint = json.loads('' or '{}')
    RawDataJsonPoint["measurement"] = Measurement

    if CheckTags(DataYear,DataMonth, DataWeek,DataDay):

        if not ("tags" in RawDataJsonPoint):
            RawDataJsonPoint["tags"] = {}
                
        if not ("host" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["host"] = DataHost

        if not ("year" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["year"] = DataYear

        if not ("month" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["month"] = DataMonth

        if not ("week" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["week"] = DataWeek

        if not ("day" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["day"] = DataDay

        if not (Phase is None):
            if not ("phase" in RawDataJsonPoint["tags"]):
                RawDataJsonPoint["tags"]["phase"] = Phase

        if not ("fields" in RawDataJsonPoint):
            RawDataJsonPoint["fields"] = {}

        if not (ValueName in RawDataJsonPoint["fields"]):
            RawDataJsonPoint["fields"][ValueName] = Value

        RawDataJsonPoint["time"] = PointTime

        NewLog("OK: " + DataHost + "-" + ValueName + "(" + str(Value) + ")"  + ": " + PointTime)

        DataPoints.append(RawDataJsonPoint)

    else:
        NewLog("ERROR: AddDataPointStatus, date tag issue")

def WriteData():
    global DataPoints
    global function_influx_client
    global IslocalTest

    if not IslocalTest:

        #is there something to add
        if len(DataPoints) > 0:

            try:

                #write point to influx 
                function_influx_client.write_points(DataPoints)

                NewLog("OK, WriteData, writing data points: " + str(len(DataPoints)))
            
                DataPoints = []

            except Exception as e:

                if "dropped" in str(e):
                    parse_error = str(e)

                    try:
                        linedropped = int(parse_error[parse_error.index('=')+1:parse_error.index('}')-1])

                        if len(DataPoints) > linedropped:
                            #remove the identified line
                            DataPoints.pop(linedropped)

                            #retry
                            WriteData()
                        
                    except Exception as e2:
                        NewLog("WARNING, could not find index in error " + str(e) + ", with error: " + str(e2))
                        DataPoints = []

                else:
                    NewLog("WARNING, could not find index in error " + str(e))
                    DataPoints = []
    else:
        NewLog("WARNING, WriteData, local test is true")

def Init_Influx(IN_username, IN_password, IN_host, IN_port=8086, IN_database='home', IN_LocalTest=False, IN_DEBUG= False):
    #IN_username = string
    #IN_password = string
    #IN_host = ip - string
    #IN_port = port - int (8086)

    global LogInflux
    LogInflux = IN_DEBUG

    global function_influx_client, IslocalTest, DataPoints
    IslocalTest = IN_LocalTest
    DataPoints = []

    try:
        function_influx_client = InfluxDBClient(host=IN_host, port=IN_port, username=IN_username, password=IN_password, database=IN_database)

    except Exception as e:
        NewLog("ERROR: failed to init influx client: " + str(e))


