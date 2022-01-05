import sys
import logging

import json
from datetime import datetime, timedelta

try:
    import pytz
except Exception as e:
    logging.error("failed to load custom pytz module: " + str(e))


def new_log(str_Message, an_exception = None):
    global log_transform

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
        if log_transform:
            logging.info( Module_Name + str_Message)

            if not (an_exception is None):
                logging.info(str(an_exception)) 

def manage_daily_usage(var_name, var_value):
    global transform_mem_state

    fmt = '%Y%m%d%H%M%S' # ex. 20110104172008 -> Jan. 04, 2011 5:20:08pm 

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
                    if old_hour == 0:
                        #te change is the value at the end of the day minus the start of the day
                        DailyChange = var_value - transform_mem_state[var_name]["var_value_day_start"]
                        
                        #remember this as the first value of the day
                        transform_mem_state[var_name]["var_value_day_start"] = var_value
                        transform_mem_state[var_name]["old_day"] = amsterdam_now.day
                        transform_mem_state[var_name]["old_hour"] = amsterdam_now.hour

                        return  DailyChange
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

    #there was no change in day so there is no daily change known
    return None

def gas_flow(var_name, var_value):
    global transform_mem_state

    delta = None

    #validate that the unput is a float
    if type(var_value) is float:

        #can we access the memory
        if not transform_mem_state is None:

            #is this a known var
            if var_name in transform_mem_state:
                # do we have day and daystartvalue in our memory
                if "var_value_previous" in transform_mem_state[var_name]:
                    delta = round(var_value - transform_mem_state[var_name]["var_value_previous"],2)
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
        

    #there was no change in day so there is no daily change known
    return delta

def init_transform():
    global log_transform
    log_transform = False

    global transform_mem_state 
    transform_mem_state = json.loads('{}')
