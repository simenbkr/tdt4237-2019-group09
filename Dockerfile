FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y && \ 	
    apt-get install -y \
	git \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	nginx \
	supervisor \
	sqlite3 && \
	pip3 install -U pip setuptools && \
   rm -rf /var/lib/apt/lists/*

RUN pip3 install uwsgi

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-configuration-file /etc/nginx/sites-available/default
#COPY supervisor-app.conf /etc/supervisor/conf.d/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.

RUN mkdir code
COPY requirements.txt /code/
RUN pip3 install -r /code/requirements.txt

# add (the rest of) our code
COPY . /code/

# install django, normally you would remove this step because your project would already
# be installed in the code/app/ directory

EXPOSE 8009

ENTRYPOINT /code/docker-entrypoint.sh
