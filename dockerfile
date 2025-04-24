#Marcel Koolen

#raspberry pi's use an armv7 architecture, choosing the right image is important here
FROM arm32v7/node

RUN apt-get update
