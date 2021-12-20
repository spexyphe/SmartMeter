# SmartMeter
This application will read a dutch smart meter and send the data to influx

**project setup CI/CD**\
Visual Studio Code (The IDE - where we wrote the code with)\
Python (the code language)\
Github (code version management) \
Github Actions (the pipeline that tests - builds - packages and publishes the code)\
Docker (the packaging method)\
Docker Hub (the publishing method)\
Watchtower (this is a docker package that can manage other docker packages e.g. check dockerhub for updates)\
\
**Install**\
--- text should be added on using dockerhub\
\
**Examples**\

sudo docker run -v /dev:/dev --privileged --name smartmeter -e doTRACE= "False" -e ISLOCALTEST= "False" -e ISVARRUN= "False" -e MODBUS_DEVICE = "/dev/ttyUSB0" -e MODBUS_BAUD= 115200 -e MODBUS_PARITY= "E" -e MODBUS_VARIABLES = "" -e INFLUX_URL = "<server ip>" -e INFLUX_PORT = 8086 -e INFLUX_USER = "grafana" -e INFLUX_PASSWORD = "<influx password>" -e INFLUX_DATABASE = "home" -e INFLUX_MEASUREMENT = "Slimme_meter" -e INFLUX_HOST = "<fill in random device identifier>" xyphedocker/xyphe_private_docker:smartmeter_influx_v0001
\
## Environment variables
These are the variables that can be set through the environment\
\
*Note: Variables that do not have a default (for example the influx variables) , need to be set!* \
*Note: By default ISVARRUN is set to true, in this environment variables regarding influx are not loaded and therefore do not need to be defined* \
\
**General**\
doTRACE\
Description: By default our logging level is at logging.info, set this to false and info messages will be filtered out\
Defailt: True \
\
ISLOCALTEST\
Description: When we are running as a local test data will not be send to influx\
Default: False\
\
ISVARRUN\
Description: When this is set to true this script will only print the variables as received by the modbus device to the screen, this is so we can pick variables that we want to log to influx\
Default: True\
\
**Modbus**\
MODBUS_DEVICE\
Description: The port the modbus device is connected to\
Default: "/dev/ttyUSB0"\
\
MODBUS_BAUD \ 
Default: 115200\
\
MODBUS_PARITY\
Default: "E" \
\
MODBUS_VARIABLES\
Description: The variables that we want to read from the modbus device, ',' seperated. e.g. "Variable A,Another Var Called B,..."  \
Default: ""\
\
**Influx**\

Influx_url, Influx_port, Influx_user, Influx_password, Influx_database, Influx_measurement, influx_host

INFLUX_URL\
Description: the influx database url, for example "http://127.0.0.1:8086"\

INFLUX_PORT\
Description: the port on which influx in running  
\
INFLUX_USER\
Description: The influx user that is used as authentification\
\
INFLUX_PASSWORD\
Description: The influx password that is used as authentification\
\
INFLUX_DATABASE\
Description: The database to which we want to write the data\
\
INFLUX_MEASUREMENT\
Description: \
\
INFLUX_HOST\
Description: \
\
**uses**\
https://github.com/influxdata/influxdb-client-python  \
\