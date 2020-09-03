#!/bin/bash

sudo apt-get update

sudo apt-get install docker-compose -y

export IP=`curl http://checkip.amazonaws.com`

git clone https://github.com/jweissenberger/outpost-api.git

cd outpost-api

sudo docker-compose up --build -d