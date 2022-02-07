import sys
import logging

import json

try:
    from influxdb import InfluxDBClient
except Exception as e:
    logging.error("failed to load influx modules: " + str(e))


def new_log(str_message):
    global log_influx, is_local_test

    module_name = "module_influx.py, "

    if("ERROR" in str_message):
        logging.error( module_name + str_message)
    elif("WARNING" in str_message):
        logging.warning( module_name + str_message)
    else:
        if log_influx:
            logging.info( module_name + str_message)
        if is_local_test:
            print(str_message)

def check_tags(data_year, data_month, data_week, data_day):

    answer = True

    try:

        if not(int(data_year) > 2000 and int(data_year) < 10000):
            answer = False
        
        if not(int(data_month) > 0 and int(data_month) < 13):
            answer = False

        if not(int(data_week) > -1 and int(data_week) < 54):
            answer = False

        if not(int(data_day) > -1 and int(data_day) < 8):
            answer = False

    except Exception as e:
        answer = False
        new_log("ERROR: check_tags: " + str(e))

    return answer

def add_raw_point(measurement, data_host, line_nr, value_name, value, point_time):
    global raw_data_points

    raw_data_json_point = json.loads('{}')
    raw_data_json_point["measurement"] = measurement

    if not ("tags" in raw_data_json_point):
        raw_data_json_point["tags"] = {}
            
    if not ("host" in raw_data_json_point["tags"]):
        raw_data_json_point["tags"]["host"] = data_host

    if not ("year" in raw_data_json_point["tags"]):
        raw_data_json_point["tags"]["line_nr"] = line_nr

    if not ("fields" in raw_data_json_point):
        raw_data_json_point["fields"] = {}

    if not (value_name in raw_data_json_point["fields"]):
        raw_data_json_point["fields"][value_name] = value

    raw_data_json_point["time"] = point_time

    new_log("OK: " + data_host + "-" + value_name + "(" + str(value) + ")"  + ": " + point_time)

    raw_data_points.append(raw_data_json_point)


def add_data_point(measurement, data_host, data_year, data_month, data_week, data_day, day_of_year, value_name, value, point_time, phase=None):
    global data_points

    raw_data_json_point = json.loads('{}')
    raw_data_json_point["measurement"] = measurement

    if check_tags(data_year,data_month, data_week,data_day):

        if not ("tags" in raw_data_json_point):
            raw_data_json_point["tags"] = {}
                
        if not ("host" in raw_data_json_point["tags"]):
            raw_data_json_point["tags"]["host"] = data_host

        if not ("year" in raw_data_json_point["tags"]):
            raw_data_json_point["tags"]["year"] = data_year

        if not ("month" in raw_data_json_point["tags"]):
            raw_data_json_point["tags"]["month"] = data_month

        # if not ("week" in raw_data_json_point["tags"]):
        #     raw_data_json_point["tags"]["week"] = data_week

        if not ("day" in raw_data_json_point["tags"]):
            raw_data_json_point["tags"]["day"] = data_day

        # if not ("day_of_year" in raw_data_json_point["tags"]):
        #     raw_data_json_point["tags"]["day_of_year"] = day_of_year

        if not (phase is None):
            if not ("phase" in raw_data_json_point["tags"]):
                raw_data_json_point["tags"]["phase"] = phase

        if not ("fields" in raw_data_json_point):
            raw_data_json_point["fields"] = {}

        if not (value_name in raw_data_json_point["fields"]):
            raw_data_json_point["fields"][value_name] = value

        raw_data_json_point["time"] = point_time

        new_log("OK: " + data_host + "-" + value_name + "(" + str(value) + ")"  + ": " + point_time)

        data_points.append(raw_data_json_point)

    else:
        new_log("ERROR: Add_data_point, date tag issue")

def write_data():
    global data_points
    global raw_data_points
    global function_influx_client
    global is_local_test

    try:
        logging.warning(data_points)

        if not is_local_test:

            if len(raw_data_points) > 0:
                try:

                    #write point to influx 
                    function_influx_client.write_points(raw_data_points)

                    new_log("OK, write_data, writing data points: " + str(len(raw_data_points)))
                
                    raw_data_points = []

                except Exception as e:

                    if "dropped" in str(e):
                        parse_error = str(e)

                        try:
                            linedropped = int(parse_error[parse_error.index('=')+1:parse_error.index('}')-1])

                            if len(raw_data_points) > linedropped:
                                #remove the identified line
                                raw_data_points.pop(linedropped)

                                #retry
                                write_data()
                            
                        except Exception as e2:
                            new_log("WARNING, could not find index in error " + str(e) + ", with error: " + str(e2))
                            raw_data_points = []

                    else:
                        new_log("WARNING, could not find index in error " + str(e))
                        raw_data_points = []

            #is there something to add
            if len(data_points) > 0:

                try:

                    #write point to influx 
                    function_influx_client.write_points(data_points)

                    new_log("OK, write_data, writing data points: " + str(len(data_points)))
                
                    data_points = []

                except Exception as e:

                    if "dropped" in str(e):
                        parse_error = str(e)

                        try:
                            linedropped = int(parse_error[parse_error.index('=')+1:parse_error.index('}')-1])

                            if len(data_points) > linedropped:
                                #remove the identified line
                                data_points.pop(linedropped)

                                #retry
                                write_data()
                            
                        except Exception as e2:
                            new_log("WARNING, could not find index in error " + str(e) + ", with error: " + str(e2))
                            data_points = []

                    else:
                        new_log("WARNING, could not find index in error " + str(e))
                        data_points = []
        else:
            new_log(str(data_points))
            data_points = []

    except Exception as e_main_write:
        new_log("WARNING,issue with write " + str(e_main_write))

def init_influx(in_username, in_password, in_host, in_port=8086, in_database='home', in_local_test=False, in_debug= False):

    global log_influx
    log_influx = in_debug

    global function_influx_client, is_local_test, data_points, raw_data_points
    is_local_test = in_local_test
    data_points = []
    raw_data_points = []

    try:
        function_influx_client = InfluxDBClient(host=in_host, port=in_port, username=in_username, password=in_password, database=in_database)

    except Exception as e:
        new_log("ERROR: failed to init influx client: " + str(e))


