FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn3 -y

COPY requirements.txt requirements.txt
COPY outpost /opt/
COPY models_download.py models_download.py


RUN pip3 install -r requirements.txt
RUN python3 models_download.py

WORKDIR /opt/

# TODO Workers should be equal to the number of cores
CMD ["gunicorn3", "-b", "0.0.0.0:8000", "app:app", "--workers=4", "--timeout=10000"]