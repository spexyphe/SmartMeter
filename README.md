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
**Install docker**\
sudo apt-get update && sudo apt-get upgrade\
curl -fsSL https://get.docker.com -o get-docker.sh\
sudo sh get-docker.sh\
sudo usermod -aG docker pi\
docker version\

**Download docker images**
sudo docker pull xyphedocker/home_power:smartmeter_influx_v0001\
sudo docker pull containrrr/watchtower\
\
**Run Examples**\

sudo docker run -v /dev:/dev --privileged --name smartmeter -e do_trace= "False" -e is_local_test= "False" -e is_var_run= "False" -e modbus_device = "/dev/ttyUSB0" -e modbus_baud= 115200 -e modbus_parity= "E" -e modbus_variables = "" -e influx_url = "<server ip>" -e influx_port = 8086 -e influx_user = "grafana" -e influx_password = "<influx password>" -e influx_database = "home" -e influx_measurement = "Slimme_meter" -e INFLUX_host = "<fill in random device identifier>" xyphedocker/xyphe_private_docker:smartmeter_influx_v0001

docker run -d --name watchtower -v /var/run/docker.sock:/var/run/docker.sock containrrr/watchtower smartmeter --debug --interval=300
\
## Environment variables
These are the variables that can be set through the environment\
\
*Note: variables that do not have a default (for example the influx variables) , need to be set!* \
*Note: By default is_var_run is set to true, in this environment variables regarding influx are not loaded and therefore do not need to be defined* \
\
**General**\
do_trace\
Description: By default our logging level is at logging.info, set this to false and info messages will be filtered out\
Defailt: True \
\
is_local_test\
Description: When we are running as a local test data will not be send to influx\
Default: False\
\
is_var_run\
Description: When this is set to true this script will only print the variables as received by the modbus device to the screen, this is so we can pick variables that we want to log to influx\
Default: True\
\
**modbus**\
modbus_device\
Description: The port the modbus device is connected to\
Default: "/dev/ttyUSB0"\
\
modbus_baud \ 
Default: 115200\
\
modbus_parity\
Default: "E" \
\
modbus_variables\
Description: The variables that we want to read from the modbus device, ',' seperated. e.g. "Variable A,Another Var Called B,..."  \
Default: ""\
\
**Influx**\

influx_url, influx_port, influx_user, influx_password, influx_database, influx_measurement, influx_host

influx_url\
Description: the influx database url, for example "http://127.0.0.1:8086"\

influx_port\
Description: the port on which influx in running  
\
influx_user\
Description: The influx user that is used as authentification\
\
influx_password\
Description: The influx password that is used as authentification\
\
influx_database\
Description: The database to which we want to write the data\
\
influx_measurement\
Description: \
\
INFLUX_host\
Description: \
\
**uses**\
https://github.com/influxdata/influxdb-client-python  \
\