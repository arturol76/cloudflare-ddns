FROM phusion/baseimage:0.10.2
LABEL maintainer="arturol76"

RUN	apt-get update \
	&& apt-get -y upgrade -o Dpkg::Options::="--force-confold" \
	&& apt-get -y dist-upgrade -o Dpkg::Options::="--force-confold"

RUN apt-get upgrade -y \
    && apt-get install -y python3 python3-pip \
    && pip3 install CloudFlare \
    && pip3 install requests paho-mqtt
    
#debug only
#RUN apt-get install -y nano curl wget dnsutils 

RUN mkdir /app
COPY ./scripts/* /app/
RUN chmod 544 /app/*.py

RUN	apt-get -y remove make && \
	apt-get -y clean && \
	apt-get -y autoremove && \
	rm -rf /tmp/* /var/tmp/*

#python3 /app/main.py -v
CMD ["python3","/app/main.py","-v", "-c", "./conf/config.json"]
