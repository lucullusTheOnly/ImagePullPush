FROM quay.io/podman/stable

COPY requirements.txt .

RUN dnf install -y python3-pip git && \
	pip3 install -r requirements.txt #&& \
	#mkdir /opt/podman && \
	#chmod 777 /home/podman && \
	#chown 1000:0 /home/podman && \
	#mkdir -p /.local/share/containers/storage/libpod && \
	#chown -R 1000:0 /.local && \
	#chmod -R 777 /.local

WORKDIR /home/podman
COPY pull.py .
COPY versions.yaml .
RUN chmod 777 /home/podman/* && chown 1000:0 /home/podman/*
USER 1000:0

ENTRYPOINT python3 ./pull.py
#CMD ["/usr/bin/podman", "pull", "quay.io/centos/centos:stream8"]
