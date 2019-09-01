#!/bin/bash

#echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
#docker push USER/REPO


docker ps
sudo docker login --username $HEROKU_DOCKER_USERNAME --password $HEROKU_AUTH_TOKEN registry.heroku.com
sudo docker tag webapp-dpdth:latest registry.heroku.com/webapp-dpdth/web
sudo docker inspect --format='{{.Id}}' registry.heroku.com/webapp-dpdth/web
if [ $TRAVIS_BRANCH == "master" ] && [ $TRAVIS_PULL_REQUEST == "false" ]; then sudo docker push registry.heroku.com/webapp-dpdth/web; fi

#    - heroku addons:create heroku-postgresql:hobby-dev -a mywebapp0

#    - heroku run container:release web -a webapp-dpdth
#    - heroku run python manage.py makemigrations -a webapp-dpdth
#    - heroku run python manage.py migrate -a webapp-dpdth
chmod +x heroku-container-release.sh

sudo chown $USER:docker ~/.docker
sudo chown $USER:docker ~/.docker/config.json
sudo chmod g+rw ~/.docker/config.json

./heroku-container-release.sh
