sudo apt-get update

sudo apt-get install docker-compose -y

git clone https://github.com/jweissenberger/outpost-api.git

cd outpost-api

sudo docker-compose build

sudo docker-compose up