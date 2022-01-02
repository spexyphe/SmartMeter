import sys
import logging

import json
from datetime import datetime, timedelta

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

    fmt = '%Y%m%d%H%M%S' # ex. 20110104172008 -> Jan. 04, 2011 5:20:08pm 

    tz = pytz.timezone('Europe/Amsterdam')
    Amsterdam_now = datetime.now(tz)

    #can we access the memory
    if not T_state is None:

        #is this a known var
        if VarName in T_state:
            # do we have day and daystartvalue in our memory
            if "VarValue_DayStart" in T_state[VarName] and "oldday" in T_state[VarName] and "oldhour" in T_state[VarName]:
                             
                old_day = T_state[VarName]["oldday"]
                old_hour = T_state[VarName]["oldhour"]

                #is there a difference in day in our memory and the current day
                if old_day != Amsterdam_now.day :

                    #was the previous daystart recorded around hour 0
                    #else we are recording false values (say, when the program restarts around hour 22)
                    if old_hour == 0:
                        #te change is the value at the end of the day minus the start of the day
                        DailyChange = VarValue - T_state[VarName]["VarValue_DayStart"]
                        
                        #remember this as the first value of the day
                        T_state[VarName]["VarValue_DayStart"] = VarValue
                        T_state[VarName]["oldday"] = Amsterdam_now.day
                        T_state[VarName]["oldhour"] = Amsterdam_now.hour

                        return  DailyChange
                    else:
                        #remember this as the first value of the day
                        T_state[VarName]["VarValue_DayStart"] = VarValue
                        T_state[VarName]["oldday"] = Amsterdam_now.day
                        T_state[VarName]["oldhour"] = Amsterdam_now.hour

            else:
                #this should not happen
                #repopulate memory for this var
                T_state[VarName]["VarValue_DayStart"] = VarValue
                T_state[VarName]["oldday"] = Amsterdam_now.day
                T_state[VarName]["oldhour"] = Amsterdam_now.hour
        else:
            #create new memory for this var
            T_state[VarName] = {}
            T_state[VarName]["VarValue_DayStart"] = VarValue
            T_state[VarName]["oldday"] = Amsterdam_now.day
            T_state[VarName]["oldhour"] = Amsterdam_now.hour
    else:
        T_state = json.loads('' or '{}')

    #there was no change in day so there is no daily change known
    return None

def Init_Transform():
    global LogTransform
    LogTransform = False

    global T_state 
    T_state = json.loads('' or '{}')
