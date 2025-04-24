from pyexpat import EXPAT_VERSION
import sys
import logging

import json
from datetime import datetime, timedelta

try:
    import pytz
except Exception as e:
    logging.error("failed to load custom pytz module: " + str(e))

time_format = '%Y-%m-%dT%H:%M:%SZ'

code_list = [ "1-0:1.7.0", "1-0:2.7.0", "1-0:32.7.0", "1-0:52.7.0", "1-0:72.7.0", "1-0:31.7.0", "1-0:51.7.0", "1-0:71.7.0", "1-0:21.7.0", "1-0:41.7.0", "1-0:61.7.0", "1-0:22.7.0", "1-0:42.7.0", "1-0:62.7.0", "0-1:24.2.1", "1-0:1.8.1", "1-0:1.8.2", "1-0:2.8.1", "1-0:2.8.2", "0-0:96.14.0"]

#name - phase - 24h
var_list = [["e_current_consumption", None, False], ["e_current_production", None, False], 
["e_volt", "l1", False], ["e_volt", "l2", False], ["e_volt", "l3", False], 
["e_amp", "l1", False], ["e_amp", "l2", False], ["e_amp", "l3", False], 
["e_watt_consumption", "l1", False], ["e_watt_consumption", "l2", False], ["e_watt_consumption", "l3", False],
["e_watt_production", "l1", False], ["e_watt_production", "l2", False], ["e_watt_production", "l3", False],
["g_volume", None, True], ["e_consumption_low_hours", None, True], ["e_consumption_high_hours", None, True], ["e_production_low_hours", None, True], ["e_production_high_hours", None, True], 
["e_low_or_high_hour_fl", None, False]]



#"1-0:1.7.0" # (verbruik_waarde) (e_current_consumption_cummulative)
#"1-0:2.7.0" # (terug_waarde) (e_current_production_cummulative)                                                                                                                                                      
#"1-0:32.7.0" # (e_volt - l1)                                                                                                                                                     
#"1-0:52.7.0" # (e_volt - l2)                                                                                                                                                      
#"1-0:72.7.0" # (e_volt - l3)                                                                                                                                                     
#"1-0:31.7.0" # (e_amp - l1)                                                                                                                                                       
#"1-0:51.7.0" # (e_amp - l2)                                                                                                                                                       
#"1-0:71.7.0" # (e_amp - l3)                                                                                                                                                        
#"1-0:21.7.0" # (e_watt_consumption - l1)                                                                                                                                                   
#"1-0:41.7.0" # (e_watt_consumption - l2)                                                                                                                                                 
#"1-0:61.7.0" # (e_watt_consumption - l3)                                                                                                                                                   
#"1-0:22.7.0" # (e_watt_production - l1)                                                                                                                                                   
#"1-0:42.7.0" # (e_watt_production - l2)                                                                                                                                                   
#"1-0:62.7.0" # (e_watt_production - l3)                                                                                                                                                                                                                                                                         
#"0-1:24.2.1" # (g_volume) (parsed: g_flow)                                                                                                                                                                                                                                                        
#"1-0:1.8.1" # (e_consumption_low_hours)                                                                                                                                           
#"1-0:1.8.2" # (e_consumption_high_hours)                                                                                                                                               
#"1-0:2.8.1" # (e_production_low_hours)                                                                                                                                               
#"1-0:2.8.2" # (e_production_high_hours)                                                                                                                                               


def new_log(str_message, an_exception = None):
    global log_transform

    global influx_measurement, influx_host, time_format
    
    module_name = "module_transform.py, "

    try:
        point_time = datetime.utcnow().strftime(time_format)
        
        if("ERROR" in str_message):
            logging.error( module_name + str_message)
            # influx.add_raw_point(influx_measurement, influx_host, 0, "Logging", "ERROR: " + str_message, point_time)
        
            if not (an_exception is None):
                logging.error(str(an_exception))    
        elif("WARNING" in str_message):
            logging.warning( module_name + str_message)
            # influx.add_raw_point(influx_measurement, influx_host, 0, "Logging", "WARNING: " + str_message, point_time)

            if not (an_exception is None):
                logging.warning(str(an_exception))   
        else:
            if log_transform:
                logging.info( module_name + str_message)

                if not (an_exception is None):
                    logging.info(str(an_exception)) 

    except Exception as logging_exception:
        print(str(logging_exception))
        
def create_data_point_locally(value_name, value, phase=None):
    global influx_measurement, influx_host
    ### mk: measurement and host should not be needed as input
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
    
    current_day_of_year = amsterdam_now.timetuple().tm_yday

    #using point time to log things will ensure that everything uses the same time
    point_time = datetime.utcnow().strftime(time_format)

    influx.add_data_point(influx_measurement, influx_host, current_year, current_month_nr, current_week_nr, current_day_nr, current_day_of_year, value_name, value, point_time, phase)


def create_raw_point_locally(line_nr, value):
    global influx_measurement, influx_host

    global time_format

    if not (influx is None):
        #using point time to log things will ensure that everything uses the same time
        point_time = datetime.utcnow().strftime(time_format)

        influx.add_raw_point(influx_measurement, influx_host, line_nr, "Raw", value, point_time)

def store_last_value(var_info, value):
    global lastvalues

    if not (var_info[0] in lastvalues):
        lastvalues[var_info[0]] = {}

    if not(var_info[1] is None):   

        if not(var_info[1] in lastvalues[var_info[0]]):
            lastvalues[var_info[0]][var_info[1]] = {}

        lastvalues[var_info[0]][var_info[1]]["value"] = value
        lastvalues[var_info[0]][var_info[1]]["time"] = datetime.utcnow()
        lastvalues[var_info[0]][var_info[1]]["updated"] = True 
    else:
        lastvalues[var_info[0]]["value"] = value
        lastvalues[var_info[0]]["time"] = datetime.utcnow()
        lastvalues[var_info[0]]["updated"] = True              

def reset_stored():
    global lastvalues

    for a_val in lastvalues:
        if "updated" in lastvalues[a_val]:
            try:
                lastvalues[a_val]["updated"] = False
            except:
                print(a_val)
                print(lastvalues)
        else:
            for ph in lastvalues[a_val]:
                try:
                    lastvalues[a_val][ph]["updated"] = False
                except:
                    print(a_val)
                    print(ph)
                    print(lastvalues)

def time_to_update(var_info, value, deltatime):
    global lastvalues

    try:      
        try:
            # to get the last known timestamp this value was updated
            if var_info[1] is None: #this var has no phase
                last_updated_time = lastvalues[var_info[0]]["time"]
            else:
                last_updated_time = lastvalues[var_info[0]][var_info[1]]["time"]
        except:
            # register this problem
            new_log("WARNING: could not find " + str(var_info) + " in lastvalues array")
            store_last_value(var_info, value) #add this entry
                
            #since we do not know when we last updated, do it now
            return True 
      
        if (datetime.utcnow() - last_updated_time).total_seconds() > deltatime:
            store_last_value(var_info, value)
            return True

    except Exception as e:    
        new_log("WARNING: time_to_update, timerissue: " + str(e))

    return False


def gas_flow(var_name, var_value):
    global transform_mem_state

    #validate that the unput is a float
    if type(var_value) is float:

        #can we access the memory
        if not transform_mem_state is None:

            #is this a known var
            if var_name in transform_mem_state:
                # do we have day and daystartvalue in our memory
                if "var_value_previous" in transform_mem_state[var_name]:
                    delta = round(var_value - transform_mem_state[var_name]["var_value_previous"],2)

                    create_data_point_locally("g_flow", delta)

                    transform_mem_state[var_name]["var_value_previous"] = var_value

                else:
                    #this should not happen
                    #repopulate memory for this var
                    transform_mem_state[var_name]["var_value_previous"] = var_value

            else:
                #create new memory for this var
                transform_mem_state[var_name] = {}
                transform_mem_state[var_name]["var_value_previous"] = var_value

        else:
            transform_mem_state = json.loads('{}')

    else:
        print(str(var_value) + " is a " + str(type(var_value)))


def calculated_values():

    global lastvalues

    if ("e_volt" in lastvalues) and ("e_watt_consumption" in lastvalues) and ("e_watt_production" in lastvalues):
        if ("l1" in lastvalues["e_volt"]) and ("l1" in lastvalues["e_watt_consumption"]) and ("l1" in lastvalues["e_watt_production"]):

            if lastvalues["e_volt"]["l1"]["updated"] and lastvalues["e_watt_consumption"]["l1"]["updated"] and lastvalues["e_watt_production"]["l1"]["updated"]:
                e_amp_calc_l1 = round((((abs(lastvalues["e_watt_consumption"]["l1"]["value"] - lastvalues["e_watt_production"]["l1"]["value"]))*1000) / lastvalues["e_volt"]["l1"]["value"]),3)
                create_data_point_locally("e_amp_calc", e_amp_calc_l1, "l1")

        if ("l2" in lastvalues["e_volt"]) and ("l2" in lastvalues["e_watt_consumption"]) and ("l2" in lastvalues["e_watt_production"]):
            if lastvalues["e_volt"]["l2"]["updated"] and lastvalues["e_watt_consumption"]["l2"]["updated"] and lastvalues["e_watt_production"]["l2"]["updated"]:
                e_amp_calc_l2 = round((((abs(lastvalues["e_watt_consumption"]["l2"]["value"] - lastvalues["e_watt_production"]["l2"]["value"]))*1000) / lastvalues["e_volt"]["l2"]["value"]),3)
                create_data_point_locally("e_amp_calc", e_amp_calc_l2, "l2")

        if ("l3" in lastvalues["e_volt"]) and ("l3" in lastvalues["e_watt_consumption"]) and ("l3" in lastvalues["e_watt_production"]):
            if lastvalues["e_volt"]["l3"]["updated"] and lastvalues["e_watt_consumption"]["l3"]["updated"] and lastvalues["e_watt_production"]["l3"]["updated"]:
                e_amp_calc_l3 = round((((abs(lastvalues["e_watt_consumption"]["l3"]["value"] - lastvalues["e_watt_production"]["l3"]["value"]))*1000) / lastvalues["e_volt"]["l3"]["value"]),3)
                create_data_point_locally("e_amp_calc", e_amp_calc_l3, "l3")


def update(code, value, deltatime):
    global code_list, var_list

    # is this code in the list of known codes
    if code_list.count(code) > 0:

        # get the variable info for this code
        var_info = var_list[code_list.index(code)] #name - phase - 24h

        # is it time to update this variable with the new info
        if time_to_update(var_info, value, deltatime):

            # update value
            create_data_point_locally(var_info[0], value, var_info[1])

            # is this a "gas" volume value?
            if var_info[0] == "g_volume":
                gas_flow("g_volume", value)

            # should we calculate 24 hour change?
            if var_info[2]:
                manage_daily_usage(var_info[0], value)

def parse_line(in_line, deltatime):
    global influx_measurement, influx_host

    line_value = None
    raw_code = None

    try:
        raw_code = in_line[:in_line.index('(') ]

        if not(raw_code in raw_variables_mem):
            x = raw_variables_mem["count"] + 1
            raw_variables_mem["count"] = x
            
            raw_variables_mem[raw_code] = "parsed"

            create_raw_point_locally(x, raw_code )

    except Exception as e:
        raw_code = None
        #new_log("WARNING: " + in_line)
        #new_log("WARNING: parse_line, raw_liner: " + str(e))

    try:
        if in_line.count('*') > 0:
            if in_line.count(')') == 2:
                line_value = float(in_line[in_line.index(')')+2:in_line.index('*')])
            else:
                line_value = float(in_line[in_line.index('(')+1:in_line.index('*')])
        else:  
            line_value = float(in_line[in_line.index('(')+1:in_line.index(')')])

    except Exception as e:
        line_value = None
        #new_log("WARNING: " + in_line)
        #new_log("WARNING: parse_line, value: " + str(e))

    if (not (raw_code is None)) and (not (line_value is None)):
        update(raw_code, line_value, deltatime)

def parse_variables(in_variables):
    out_variables = None

    try:
        out_variables = in_variables.split(",")    
    except Exception as e:
        new_log("ERROR, parse_variables Failed", e)
    
    return out_variables

def manage_daily_usage(var_name, var_value):
    global transform_mem_state

    tz = pytz.timezone('Europe/Amsterdam')
    amsterdam_now = datetime.now(tz)

    #can we access the memory
    if not transform_mem_state is None:

        #is this a known var
        if var_name in transform_mem_state:
            # do we have day and daystartvalue in our memory
            if "var_value_day_start" in transform_mem_state[var_name] and "old_day" in transform_mem_state[var_name] and "old_hour" in transform_mem_state[var_name]:
                             
                #what is the day and hour memory
                old_day = transform_mem_state[var_name]["old_day"]
                old_hour = transform_mem_state[var_name]["old_hour"]

                #is there a difference in day in our memory and the current day
                if old_day != amsterdam_now.day :

                    #was the previous daystart recorded around hour 0
                    #else we are recording false values (say, when the program restarts around hour 22)
                    if old_hour == 23:
                        #te change is the value at the end of the previous day minus the start of the day
                        daily_change = var_value - transform_mem_state[var_name]["var_value_day_start"]
                        
                        create_data_point_locally(var_name + "_change", daily_change)

                        #remember this as the first value of the day
                        transform_mem_state[var_name]["var_value_day_start"] = var_value
                        transform_mem_state[var_name]["old_day"] = amsterdam_now.day
                        transform_mem_state[var_name]["old_hour"] = amsterdam_now.hour

                        return  daily_change
                    else:
                        #remember this as the first value of the day
                        transform_mem_state[var_name]["var_value_day_start"] = var_value
                        transform_mem_state[var_name]["old_day"] = amsterdam_now.day
                        transform_mem_state[var_name]["old_hour"] = amsterdam_now.hour

            else:
                #this should not happen
                #repopulate memory for this var
                transform_mem_state[var_name]["var_value_day_start"] = var_value
                transform_mem_state[var_name]["old_day"] = amsterdam_now.day
                transform_mem_state[var_name]["old_hour"] = amsterdam_now.hour
        else:
            #create new memory for this var
            transform_mem_state[var_name] = {}
            transform_mem_state[var_name]["var_value_day_start"] = var_value
            transform_mem_state[var_name]["old_day"] = amsterdam_now.day
            transform_mem_state[var_name]["old_hour"] = amsterdam_now.hour
    else:
        transform_mem_state = json.loads('{}')

def set_influx_module(in_influx, in_influx_measurement, in_influx_host):
    global influx
    influx = in_influx

    global influx_measurement, influx_host
    influx_measurement = in_influx_measurement
    influx_host = in_influx_host

def clear_mem():
    global transform_mem_state 
    transform_mem_state = json.loads('{}')

    global raw_variables_mem 
    raw_variables_mem = json.loads('{}')
    raw_variables_mem["count"] = 0

    global lastvalues 
    lastvalues = json.loads('{}')

def init_transform():
    global log_transform
    log_transform = False

    global transform_mem_state 
    transform_mem_state = json.loads('{}')

    global raw_variables_mem 
    raw_variables_mem = json.loads('{}')
    raw_variables_mem["count"] = 0

    global lastvalues 
    lastvalues = json.loads('{}')

    global influx
    influx = None
