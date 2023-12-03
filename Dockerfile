#FROM quay.io/podman/stable
FROM redhat/ubi8:8.6

COPY requirements.txt .

RUN dnf install -y skopeo python3-pip git && \
  useradd --uid 1000 --gid 0 --home-dir /home/skopeo skopeo && \
  pip3 install --upgrade pip && \
	pip3 install -r requirements.txt && \
  chmod -R g=u /run && \
# Creating ssh directory for using ssh public key authentication for git
  mkdir -p /.ssh/ && \
  chgrp 0 /.ssh/ && \
  chmod -R g=u /.ssh

ENV PYTHONUNBUFFERED=1
ENV GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
WORKDIR /home/skopeo
COPY pull.py .
COPY versions.yaml .
RUN chmod -R 770 /home/skopeo && chown -R 1000:0 /home/skopeo
USER 1000:0

ENTRYPOINT python3 ./pull.py
#CMD ["/usr/bin/podman", "pull", "quay.io/centos/centos:stream8"]
