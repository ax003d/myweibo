FROM daocloud.io/library/ubuntu:trusty

MAINTAINER ax003d <ax003d@gmail.com>

RUN cp /etc/apt/sources.list /etc/apt/sources.list_backup
COPY sources.list /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y python \
                       python-dev \
                       python-pip \
                       python-virtualenv \
                       supervisor
RUN apt-get clean && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt requirements.txt
COPY tagignore tagignore
COPY myweibo.py myweibo.py
RUN pip install -r requirements.txt
COPY scheduler /etc/cron.d/

COPY server server
RUN virtualenv /env-server
RUN /env-server/bin/pip3 install -r server/requirements.txt -i http://mirrors.aliyun.com/pypi/simple
EXPOSE 8080

COPY supervisord.conf supervisord.conf
VOLUME /data/supervisor
COPY entrypoint.sh entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
