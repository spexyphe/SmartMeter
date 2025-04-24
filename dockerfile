#Marcel Koolen

#raspberry pi's use an armv7 architecture, choosing the right image is important here

FROM arm64v7/debian:latest

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN apt-get install -y apt-utils

RUN apt-get update
