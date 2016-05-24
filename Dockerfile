FROM daocloud.io/library/ubuntu:trusty

MAINTAINER ax003d <ax003d@gmail.com>

RUN cp /etc/apt/sources.list /etc/apt/sources.list_backup
COPY sources.list /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y python \
                       python-dev \
                       python-pip
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

ENTRYPOINT ["cron"]
CMD ["-f"]