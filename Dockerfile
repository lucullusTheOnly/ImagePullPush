FROM quay.io/podman/stable

COPY requirements.txt .

RUN dnf install -y python3-pip && \
	pip3 install -r requirements.txt

COPY pull.py .
COPY versions.yaml .
USER 1000:1000

CMD ["/usr/bin/podman", "pull", "quay.io/centos/centos:stream8"]
