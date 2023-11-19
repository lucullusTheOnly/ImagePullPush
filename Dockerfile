#FROM quay.io/podman/stable
FROM redhat/ubi8:8.6

COPY requirements.txt .

RUN dnf install -y skopeo python3-pip git && \
  useradd --uid 1000 --home-dir /home/skopeo skopeo && \
  pip3 install --upgrade pip && \
	pip3 install -r requirements.txt
#&& \
	#mkdir /home/podman && \
	#chmod 777 /home/podman && \
	#chown 1000:0 /home/podman #&& \
	#mkdir -p /.local/share/containers/storage/libpod && \
	#chown -R 1000:0 /.local && \
	#chmod -R 777 /.local


WORKDIR /home/skopeo
COPY pull.py .
COPY versions.yaml .
RUN chmod -R 777 /home/skopeo && chown -R 1000:1000 /home/skopeo
USER 1000:1000

ENTRYPOINT python3 ./pull.py
#CMD ["/usr/bin/podman", "pull", "quay.io/centos/centos:stream8"]
