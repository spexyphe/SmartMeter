#Marcel Koolen

#raspberry pi's use an armv7 architecture, choosing the right image is important here
FROM arm32v7/alpine:3.14

RUN apk update

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk update

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

ADD . .

CMD [ "python3", "./Project/main_smart_meter.py"]
#CMD [ "python3", "./Project/test_main_smart_meter.py"]
