#!/bin/bash

sudo apt-get update

sudo apt-get install docker-compose -y

export IP=`curl http://checkip.amazonaws.com`

git clone https://github.com/jweissenberger/newsletter.git

cd newsletter

sudo docker-compose up --build -d