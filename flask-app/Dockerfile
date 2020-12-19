FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN pip3 install --upgrade pip
RUN apt-get install gunicorn3 -y

COPY requirements.txt requirements.txt
COPY newsletter /opt/
COPY models_download.py models_download.py


RUN pip3 install -r requirements.txt
RUN python3 models_download.py

WORKDIR /opt/

# TODO Workers should be equal to the number of cores
CMD ["gunicorn3", "-b", "0.0.0.0:8000", "app:app", "--workers=32", "--timeout=3000", "--max-requests=3"]