FROM python:3

WORKDIR /usr/src/app

ADD requirements.txt /usr/src/app

RUN pip install -r requirements.txt

ADD . /usr/src/app

# collect static files
RUN python manage.py collectstatic --noinput

# run gunicorn
#CMD gunicorn --bind 0.0.0.0:$PORT wsgi
#CMD gunicorn hello_django.wsgi:application --bind 0.0.0.0:$PORT
CMD gunicorn airline.wsgi:application --bind 0.0.0.0:$PORT
