FROM python:3.11

# set environment variables
ENV APP_HOME=/Portal_proveedores
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR $APP_HOME

# update pip, install dependencies
RUN adduser --disabled-password --no-create-home django-user
RUN pip install --upgrade pip
COPY ./requirements.txt $APP_HOME
RUN pip install -r requirements.txt

COPY . $APP_HOME

RUN chown -R 1002:1002 $APP_HOME

RUN chmod -R 755 $APP_HOME


