[![Build Status](https://travis-ci.com/ChuaCheowHuan/web_app_DPDTH.svg?branch=master)](https://travis-ci.com/ChuaCheowHuan/web_app_DPDTH)

**What is this repository about?**

This repository serves as a demo setup illustrating the basic workflow of
testing a dockerized Django & Postgres web app with Travis
(continuous integration) & deployment to Heroku (continuous deployment).

---

**Prerequisite:**

1) This post assumes that the reader has accounts with Github, Travis & Heroku
& already has the accounts configured. For example, linking Travis with Github,
adding a Postgres server in Heroku & setting OS environment variables in
Travis & Heroku websites.

2) Basic working knowledge of Django & Docker.

---

**Which copy of Postgres to use during the different stages in the workflow?**

During development, we won't be using a local copy of Postgres database
server. The Docker's copy of Postgres is used.

When testing in Travis, we don't have to ask Travis for a copy of Postgres, we
won't be using Travis's copy, we'll be using the Docker's copy.

During deployment, we have to use Heroku's copy.

---

**makemigrations**

Always run ```docker-compose run web python manage.py makemigrations``` before
deployment to Heroku or in our case, before pushing to Github.

The actual ```python manage.py migrate``` for the Postgres server addon from
Heroku will be run in the ```Procfile``` file.

---

**Listing files & directories in a tree:**

```
cd web_app_DPDTH

$ tree -a -I "CS50_web_dev|staticfiles|static|templates|LICENSE|README.md|__init__.py|settings_DPTH_.py|urls.py|wsgi.py|db.sqlite3|airline4_tests_.py|apps.py|migrations|views.py|models.py|flights.csv|manage.py|wait-for-it.sh|admin.py|.git|.travis_DPTH_.yml|__pycache__"

.
├── .travis.yml
├── .travis_DPDTH_.yml
├── .travis_old.yml
├── Dockerfile
├── Procfile
├── airline
│   └── settings.py
├── docker-compose.yml
├── docker_push.sh
├── flights
│   └── tests.py
├── heroku-container-release.sh
└── requirements.txt

```

As shown in the tree above, the 9 files that matter in the workflow:

1) tests.py

2) settings.py

3) requirements.txt

4) Dockerfile

5) docker-compose.yml

6) .travis.yml

7) docker_push.sh

8) heroku-container-release.sh

9) Procfile

We will look at the contents of each of the 9 files in the sections below.

---

**tests.py**

This is the test file that Travis will use for testing the app.
You write whatever test you want for Travis to run with.

```
from django.db.models import Max
from django.test import Client, TestCase

from .models import Airport, Flight, Passenger

# Create your tests here.
class FlightsTestCase(TestCase):

    def setUp(self):

        # Create airports.
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        # Create flights.
        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a1, destination=a1, duration=200)
        Flight.objects.create(origin=a2, destination=a1, duration=300)

    # 1
    def test_departures_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.departures.count(), 2)

    # 2
    def test_arrivals_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 2)

    # 3
    def test_valid_flight(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2)
        self.assertTrue(f.is_valid_flight())
```

---

**settings.py**

Under the database section, the ```DATABASES['default']``` sets the default
database so the default database is the one connected by the OS environment
variable ```DATABASE_URL```, however if this is unavailable, we'll use the one
defined with ```'HOST': 'db'```.

This setup allows us to use ```'HOST': 'db'``` which is the Docker's copy of
postgres during development phase & also during tesing phase with Travis
while using the Heroku's copy during deployment which is provided by
connecting to the ```DATABASE_URL```.

The ```DATABASE_URL```, as an OS environment variable which is generated by
Heroku after a Database is added to the web app in the Heroku website.

Add and/or edit the following to the ```settings.py``` file:

```
import django_heroku
import dj_database_url
```

```
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',  # new

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db', # Docker's copy of postgres
        'PORT': 5432,
        #'PORT': 5433,
    }
}

DATABASE_URL = os.environ.get('DATABASE_URL')
db_from_env = dj_database_url.config(default=DATABASE_URL, conn_max_age=500, ssl_require=True)
DATABASES['default'].update(db_from_env)
```

```
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

```
django_heroku.settings(locals())

```

---

**requirements.txt**

This file lets Docker & Travis know what packages are needed for the app.
This is needed in ```Dockerfile``` & ```.travis.yml``` files.

```
django>=2.0.11
psycopg2
psycopg2-binary
dj-database-url==0.5.0
gunicorn
whitenoise
django-heroku
pytz
sqlparse
```

---

**Dockerfile**

This contains the instructions for building a Docker image.

The ```CMD gunicorn airline.wsgi:application --bind 0.0.0.0:$PORT``` tells
Docker to use gunicorn as the web server.
See [here](https://devcenter.heroku.com/articles/container-registry-and-runtime#testing-an-image-locally)
for details.

```
FROM python:3

WORKDIR /usr/src/app

ADD requirements.txt /usr/src/app

RUN pip install -r requirements.txt

ADD . /usr/src/app

# collect static files
RUN python manage.py collectstatic --noinput

CMD gunicorn airline.wsgi:application --bind 0.0.0.0:$PORT
```

---

**docker-compose.yml**

This contains the instructions on how to run a Docker containers which is an
instance of a Docker image.

Notice the ```sleep``` delay introduced in the 2 ```command:``` sections.
See [here](https://chuacheowhuan.github.io/docker_travis/) for details.

EDIT: The environment variables are added under `db` as newly required when
testing on Travis.

```
version: '3'

services:
    db:
        image: postgres
        environment:
            - POSTGRES_DB=${POSTGRES_DB}
            - POSTGRES_USER=${POSTGRES_USER}
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}        
    migration:
        build: .
        command: bash -c 'while !</dev/tcp/db/5432; do sleep 1; done; python3 manage.py migrate'
        volumes:
            - .:/usr/src/app
        depends_on:
            - db
    web:
        build: .
#        container_name: webapp-dpdth
        image: webapp-dpdth
        command: bash -c 'while !</dev/tcp/db/5432; do sleep 1; done; python3 manage.py runserver 0.0.0.0:8000'
        volumes:
            - .:/usr/src/app
        ports:
            - "8000:8000"
        depends_on:
            - db
            - migration

```

---

**.travis.yml**

This file contains instructions for Travis. Notice that we're not using the
Postgres from Travis because we're using Postgres from Docker directly.
The ```postgresql``` is therefore commented out under the ```services:```
section.

Under ```script:```, we ask Travis to run the test using Docker with
the ```docker-compose``` command.

Under ```deploy:```, we execute a ```docker_push.sh``` script, more details in
the sections below.

The ```skip_cleanup: true``` tells Travis not to remove any files that it
deems unnecessary after deployment. Travis does not have permission to do that
on Heroku anyway.

```
language: python
python:
    - 3.6
services:
    - docker
#    - postgresql
install:
    - pip install -r requirements.txt
script:
    - docker-compose run web python manage.py test
deploy:
    provider: script
    script: bash docker_push.sh
    skip_cleanup: true
    on:
        branch: master
```

---

**Workflow for after testing with Travis to deployment to Heroku**

The main workflow after testing to deployment is as such:

tag image -> push image to registry -> release image

We'll see how to do that in the following script files:

1) docker_push.sh

2) heroku-container-release.sh

---

**docker_push.sh**

This file does several things listed as follows:

1) Login to the Heroku's image registry.

2) ```tag``` the source image ```webapp-dpdth:latest``` to the target
image ```registry.heroku.com/webapp-dpdth/web```.
Replace ```webapp-dpdth``` with your app name on Heroku.

3) Push the target image to Heroku's registry if the branch tested on Travis
is a master branch & that it's not a PR.

4) Change ownership & permission of files to allow Travis to execute
the ```heroku-container-release.sh``` script.

```
#!/bin/bash

sudo docker login --username $HEROKU_DOCKER_USERNAME --password $HEROKU_AUTH_TOKEN registry.heroku.com
sudo docker tag webapp-dpdth:latest registry.heroku.com/webapp-dpdth/web
if [ $TRAVIS_BRANCH == "master" ] && [ $TRAVIS_PULL_REQUEST == "false" ]; then sudo docker push registry.heroku.com/webapp-dpdth/web; fi

chmod +x heroku-container-release.sh
sudo chown $USER:docker ~/.docker
sudo chown $USER:docker ~/.docker/config.json
sudo chmod g+rw ~/.docker/config.json

./heroku-container-release.sh

```

---

**heroku-container-release.sh**

This file is for releasing a Docker image via Heroku's API.
Replace ```webapp-dpdth``` with your app name on Heroku.

```
#!/bin/bash
imageId=$(docker inspect registry.heroku.com/webapp-dpdth/web --format={{.Id}})
payload='{"updates":[{"type":"web","docker_image":"'"$imageId"'"}]}'
curl -n -X PATCH https://api.heroku.com/apps/webapp-dpdth/formation \
-d "$payload" \
-H "Content-Type: application/json" \
-H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
-H "Authorization: Bearer $HEROKU_AUTH_TOKEN"
```

See [here](https://devcenter.heroku.com/articles/container-registry-and-runtime#releasing-an-image)
for details.

---

**Procfile**

This file is for Heroku. The command in the ```release:``` section will run
after a Docker image is released. It will run the ```migrate``` command
with ```--noinput``` option. Without running ```migrate```, the database on
Heroku may not function correctly.

It also tells Heroku to deploy the web app using Gunicorn as the production
server.

Note that ```airline``` is the Django project name. It's not the web app name
in the Django project & is also not the web app name in Heroku.

```
release: python manage.py migrate --noinput
web: gunicorn airline.wsgi
```

---

**The deployed web app**

With the above files in place, push to Github & Travis will start testing.
After all tests passed, deployment starts. If there isn't any failures,
the web app will be running on:

[https://webapp-dpdth.herokuapp.com](https://webapp-dpdth.herokuapp.com)

This [link](https://webapp-dpdth.herokuapp.com/admin) brings you to the admin
page. It is using the **Heroku's copy** of Postgres.

This [link](https://travis-ci.com/ChuaCheowHuan/web_app_DPDTH/builds/125458792) brings you to my built log in Travis.com which shows how a successful
test/deploy built looks like.

---

**Web security:**

Please note that web security has not been throughly consider in this basic
workflow describe above. **Do NOT** simply use the above workflow for
production.

For example the ```SECRET_KEY``` in the ```settings.py``` isn't dealt with at all
and web security is really beyond the scope of this post.

---

<br>
