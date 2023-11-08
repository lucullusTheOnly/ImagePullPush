FROM quay.io/podman/stable

COPY requirements.txt .

RUN dnf install -y python3-pip git && \
	pip3 install -r requirements.txt

WORKDIR /home/podman/
COPY pull.py .
COPY versions.yaml .
RUN chmod 777 ./* && chown 1000:1000 ./*
USER 1000:1000

ENTRYPOINT python3 ./pull.py
#CMD ["/usr/bin/podman", "pull", "quay.io/centos/centos:stream8"]
