import sys
import logging

import json
from datetime import datetime

try:
    import pytz
except Exception as e:
    logging.error("failed to load custom pytz module: " + str(e))


def NewLog(StrMessage):
    global LogTransform

    if("ERROR" in StrMessage):
        logging.error( "Mod_Transform.py, " + StrMessage)
    elif("WARNING" in StrMessage):
        logging.warning( "Mod_Transform.py, " + StrMessage)
    else:
        if LogTransform:
            logging.info( "Mod_Transform.py, " + StrMessage)

def ManageDailyUsage(VarName, VarValue):
    global T_state

    tz = pytz.timezone('Europe/Amsterdam')
    Amsterdam_now = datetime.now(tz)

    #can we access the memory
    if not T_state is None:

        #is this a known var
        if VarName in T_state:
            # do we have day and daystartvalue in our memory
            if "VarValue_DayStart" in T_state[VarName] and "daynr" in T_state[VarName]:

                #is there a difference in day in our memory and the current day
                if Amsterdam_now.day() != T_state[VarName]["daynr"]:
                    #te change is the value at the end of the day minus the start of the day
                    DailyChange = VarValue - T_state[VarName]["VarValue_DayStart"]
                    
                    #remember this as the first value of the day
                    T_state[VarName]["VarValue_DayStart"] = VarValue
                    T_state[VarName]["daynr"] = Amsterdam_now.day()

                    #return the dayly change
                    return  DailyChange    
                
            else:
                #this should not happen
                #repopulate memory for this var
                T_state[VarName]["VarValue_DayStart"] = VarValue
                T_state[VarName]["daynr"] = Amsterdam_now.day()
        else:
            #create new memory for this var
            T_state[VarName] = {}
            T_state[VarName]["VarValue_DayStart"] = VarValue
            T_state[VarName]["daynr"] = Amsterdam_now.day()
    else:
        T_state = json.loads('' or '{}')

    #there was no change in day so there is no daily change known
    return None

def Init_Transform():
    global LogTransform
    LogTransform = False

    global T_state 
    T_state = json.loads('' or '{}')
