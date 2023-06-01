FROM debian:stable-slim
LABEL maintainer="@fqlenos"
LABEL stage=zerotempbuilder

RUN mkdir -p /zerotemp /var/log/zerotemp /var/uploads
WORKDIR /zerotemp

RUN apt update
RUN apt install -y python3 python3-pip build-essential curl net-tools dos2unix
RUN apt install -y python3-dev default-libmysqlclient-dev && pip3 install mysqlclient

COPY ./ /zerotemp
RUN pip3 install --no-cache-dir -r requirements.txt
RUN dos2unix /zerotemp/entrypoint.sh && chmod +x /zerotemp/entrypoint.sh

EXPOSE 5000
CMD [ "/bin/bash", "/zerotemp/entrypoint.sh" ]