FROM debian:latest

WORKDIR /qb

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3

RUN pip install Flask Flask-SQLAlchemy Flask-Bcrypt Flask-Login PyMySQL email-validator flask-wtf flask_limiter gunicorn Flask-Migrate flask-socketio flask-cors gevent gevent-websocket --break-system-packages

COPY app /qb/app

COPY run.py /qb/run.py

COPY gunicorn_config.py /qb/gunicorn_config.py

ENTRYPOINT ["gunicorn", "-c", "gunicorn_config.py", "run:app"]