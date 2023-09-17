FROM python:3.7.3
LABEL authors="irbystrova"

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=task_api_project.settings
RUN mkdir /project
WORKDIR /project
COPY . /project
RUN pip install pipenv && pipenv install --system
