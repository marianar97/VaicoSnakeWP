FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1
ENV PROJECT_ROOT /code/

COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

COPY start.sh /start.sh

COPY . /code/
WORKDIR /code/

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000


CMD ["/start.sh", "-docker"]