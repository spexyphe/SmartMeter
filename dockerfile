#Marcel Koolen

#raspberry pi's use an armv7 architecture, choosing the right image is important here
#FROM arm32v7/ubuntu:latest
FROM arm32v5/debian:latest

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN apt-get install -y apt-utils

RUN apt-get update

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

ADD . .

CMD [ "python3", "./Project/main_smart_meter.py"]
#CMD [ "python3", "./Project/test_main_smart_meter.py"]
