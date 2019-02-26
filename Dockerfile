FROM ubuntu:18.04

RUN apt-get update && \
    apt-get upgrade -y && \ 	
    apt-get install -y \
	git \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
    virtualenv \
    libpcre3 \
    libpcre3-dev \
    fcgiwrap \
	nginx \
	sqlite3 && \
	pip3 install -U pip setuptools && \
    rm -rf /var/lib/apt/lists/*


COPY nginx-configuration-file /etc/nginx/sites-available/default

COPY systemctl3.py /usr/bin/systemctl
RUN ln -sf /usr/bin/systemctl /bin/systemctl

COPY ./group09.service /etc/systemd/system/group09.service
RUN systemctl enable group09
RUN systemctl enable nginx

RUN mkdir -p /home/www-data/group09
COPY requirements.txt /home/www-data/group09
COPY install_pip.sh /home/www-data/group09
RUN pip3 install -r /home/www-data/group09/requirements.txt
RUN /home/www-data/group09/install_pip.sh

COPY . /home/www-data/group09


EXPOSE 8009
EXPOSE 4009

ENTRYPOINT /home/www-data/group09/docker-entrypoint.sh

CMD ["/usr/bin/systemctl"]

