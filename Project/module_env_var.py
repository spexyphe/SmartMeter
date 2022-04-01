import logging
import os

def new_log(str_message, an_exception = None):

    module_name = "module_env_var.py, "

    if("ERROR" in str_message):
        logging.error( module_name + str_message)
        
        if not (an_exception is None):
            logging.error(str(an_exception))    
    elif("WARNING" in str_message):
        logging.warning( module_name + str_message)

        if not (an_exception is None):
            logging.warning(str(an_exception))   
    else:
        logging.info( module_name + str_message)

        if not (an_exception is None):
            logging.info(str(an_exception))     

def load_env_var_sys():
  
    #by default we are do_trace-ing
    succes = True
    is_local_test = False
    do_trace = True 
    is_var_run = True
    
    try: #do_trace
        do_trace_str = os.environ['do_trace']

        if do_trace_str == "True":
            do_trace = True
        else:
            do_trace = False

        new_log("OK: succesfully loaded environment variable for system 'do_trace'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for system 'do_trace' FAILED", e)

    try: #is_local_test
        is_local_test_str = os.environ['is_local_test']

        if is_local_test_str == "True":
            is_local_test = True
        else:
            is_local_test = False

        new_log("OK: succesfully loaded environment variable for system 'is_local_test': " + str(is_local_test))
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for system 'is_local_test' FAILED", e)

    try: #is_var_run
        is_var_run_str = os.environ['is_var_run']

        if is_var_run_str == "True":
            is_var_run = True
        else:
            is_var_run = False

        new_log("OK: succesfully loaded environment variable for system 'is_var_run'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for system 'is_var_run' FAILED", e)

        #by default we are do_trace-ing
    return (succes, is_local_test, do_trace, is_var_run)

def load_env_var_modbus():
    succes = True
    device = "/dev/ttyUSB0"
    baud = 115200
    parity = "E" 
    variables = ""
    auto_detect = False

    # modbus_auto_detect is a method where we detect the usb device
    # when having 2 different modbus devices connected to USB the device nr can change after a restart, and break our service code

    try: #modbus_auto_detect
        in_auto_detect = os.environ['modbus_auto_detect']

        if in_auto_detect == "True":
            auto_detect = True
        else:
            auto_detect = False

        new_log("OK: succesfully loaded environment variable for modbus 'modbus_auto_detect'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for modbus 'modbus_auto_detect' FAILED", e)


    try: #modbus_device
        device = os.environ['modbus_device']
        new_log("OK: succesfully loaded environment variable for modbus 'modbus_device'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for modbus 'modbus_device' FAILED", e)

    try: #modbus_baud
        baud = int(os.environ['modbus_baud'])
        new_log("OK: succesfully loaded environment variable for modbus 'modbus_baud'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for modbus 'modbus_baud' FAILED", e)
    
    try: #modbus_parity
        parity = os.environ['modbus_parity']
        new_log("OK: succesfully loaded environment variable for modbus 'modbus_parity'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for modbus 'modbus_parity' FAILED", e)

    try: #modbus_variables
        variables = os.environ['modbus_variables']
        new_log("OK: succesfully loaded environment variable for modbus 'modbus_variables'")
    except Exception as e:
        succes = False
        new_log("ERROR: environment variable for modbus 'modbus_variables' FAILED", e)



    return (succes, auto_detect, device, baud, parity, variables)

def load_env_var_influx():
    succes = True

    influx_url = ""
    influx_port = 8086
    influx_user = "default_user" 
    influx_password = "default_password"
    influx_database = "default_home"
    influx_measurement = "default_measurement"
    influx_host = "default_host"
    
    try: #influx_url
        influx_url = os.environ['influx_url']
        new_log("OK: succesfully loaded environment variable for influx 'influx_url'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_url' FAILED", e)
        succes = False

    try: #influx_port
        influx_port = int(os.environ['influx_port'])
        new_log("OK: succesfully loaded environment variable for influx 'influx_port'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_port' FAILED", e)
        succes = False

    try: #influx_user
        influx_user = os.environ['influx_user']
        new_log("OK: succesfully loaded environment variable for influx 'influx_user'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_user' FAILED", e)
        succes = False

    try: #influx_password
        influx_password = os.environ['influx_password']
        new_log("OK: succesfully loaded environment variable for influx 'influx_password'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_password' FAILED", e)
        succes = False

    try: #influx_database
        influx_database = os.environ['influx_database']
        new_log("OK: succesfully loaded environment variable for influx 'influx_database'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_database' FAILED", e)
        succes = False

    try: #influx_measurement
        influx_measurement = os.environ['influx_measurement']
        new_log("OK: succesfully loaded environment variable for influx 'influx_measurement'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_measurement' FAILED", e)
        succes = False

    try: #INFLUX_host
        influx_host = os.environ['influx_host']
        new_log("OK: succesfully loaded environment variable for influx 'influx_host'")
    except Exception as e:
        new_log("ERROR: environment variable for influx 'influx_host' FAILED", e)
        succes = False

    return (succes, influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host)
