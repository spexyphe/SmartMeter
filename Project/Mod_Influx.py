import sys
import logging

import json

try:
    from influxdb import InfluxDBClient
except Exception as e:
    logging.error("failed to load influx modules: " + str(e))


def new_log(str_Message):
    global LogInflux

    Module_Name = "Mod_Influx.py, "

    if("ERROR" in str_Message):
        logging.error( Module_Name + str_Message)
    elif("WARNING" in str_Message):
        logging.warning( Module_Name + str_Message)
    else:
        if LogInflux:
            logging.info( Module_Name + str_Message)

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
        new_log("ERROR: CheckTags: " + str(e))

    return answer

def AddRawPoint(measurement, Datahost, line_nr, ValueName, Value, point_time):
    global DataPoints

    RawDataJsonPoint = json.loads('' or '{}')
    RawDataJsonPoint["measurement"] = measurement

    if not ("tags" in RawDataJsonPoint):
        RawDataJsonPoint["tags"] = {}
            
    if not ("host" in RawDataJsonPoint["tags"]):
        RawDataJsonPoint["tags"]["host"] = Datahost

    if not ("year" in RawDataJsonPoint["tags"]):
        RawDataJsonPoint["tags"]["line_nr"] = line_nr

    if not ("fields" in RawDataJsonPoint):
        RawDataJsonPoint["fields"] = {}

    if not (ValueName in RawDataJsonPoint["fields"]):
        RawDataJsonPoint["fields"][ValueName] = Value

    RawDataJsonPoint["time"] = point_time

    new_log("OK: " + Datahost + "-" + ValueName + "(" + str(Value) + ")"  + ": " + point_time)

    DataPoints.append(RawDataJsonPoint)



def AddDataPoint(measurement, Datahost, DataYear, DataMonth, DataWeek, DataDay, DayOfYear, ValueName, Value, point_time, Phase=None):
    global DataPoints

    RawDataJsonPoint = json.loads('{}')
    RawDataJsonPoint["measurement"] = measurement

    if CheckTags(DataYear,DataMonth, DataWeek,DataDay):

        if not ("tags" in RawDataJsonPoint):
            RawDataJsonPoint["tags"] = {}
                
        if not ("host" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["host"] = Datahost

        if not ("year" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["year"] = DataYear

        if not ("month" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["month"] = DataMonth

        if not ("week" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["week"] = DataWeek

        if not ("day" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["day"] = DataDay

        if not ("day_of_year" in RawDataJsonPoint["tags"]):
            RawDataJsonPoint["tags"]["day_of_year"] = DayOfYear

        if not (Phase is None):
            if not ("phase" in RawDataJsonPoint["tags"]):
                RawDataJsonPoint["tags"]["phase"] = Phase

        if not ("fields" in RawDataJsonPoint):
            RawDataJsonPoint["fields"] = {}

        if not (ValueName in RawDataJsonPoint["fields"]):
            RawDataJsonPoint["fields"][ValueName] = Value

        RawDataJsonPoint["time"] = point_time

        new_log("OK: " + Datahost + "-" + ValueName + "(" + str(Value) + ")"  + ": " + point_time)

        DataPoints.append(RawDataJsonPoint)

    else:
        new_log("ERROR: AddDataPointStatus, date tag issue")

def WriteData():
    global DataPoints
    global function_influx_client
    global is_local_test

    if not is_local_test:

        #is there something to add
        if len(DataPoints) > 0:

            try:

                #write point to influx 
                function_influx_client.write_points(DataPoints)

                new_log("OK, WriteData, writing data points: " + str(len(DataPoints)))
            
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
                        new_log("WARNING, could not find index in error " + str(e) + ", with error: " + str(e2))
                        DataPoints = []

                else:
                    new_log("WARNING, could not find index in error " + str(e))
                    DataPoints = []
    else:
        new_log("WARNING, WriteData, local test is true")

def Init_Influx(IN_username, IN_password, IN_host, IN_port=8086, IN_database='home', IN_LocalTest=False, IN_DEBUG= False):
    #IN_username = string
    #IN_password = string
    #IN_host = ip - string
    #IN_port = port - int (8086)

    global LogInflux
    LogInflux = IN_DEBUG

    global function_influx_client, is_local_test, DataPoints
    is_local_test = IN_LocalTest
    DataPoints = []

    try:
        function_influx_client = InfluxDBClient(host=IN_host, port=IN_port, username=IN_username, password=IN_password, database=IN_database)

    except Exception as e:
        new_log("ERROR: failed to init influx client: " + str(e))


