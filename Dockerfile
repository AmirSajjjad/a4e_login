FROM python:3.11.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
# RUN pip3 install django gunicorn

COPY . /app/

CMD python3 simple_login_register/manage.py makemigrations --no-input && \
    python3 simple_login_register/manage.py migrate --no-input && \
    python3 simple_login_register/manage.py runserver 0.0.0.0:8000
