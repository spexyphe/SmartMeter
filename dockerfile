#Marcel Koolen

#raspberry pi's use an armv7 architecture, choosing the right image is important here
FROM linux/arm/v7

RUN apt-get update
