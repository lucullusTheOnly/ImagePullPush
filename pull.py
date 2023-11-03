import subprocess
import yaml
import os

with open('versions.yaml', 'r') as f:
    versions = yaml.safe_load(f)

for key, data in versions.items():
    result = subprocess.run(["podman", "pull", data["image"]+":"+data["tag"]])
    result = subprocess.run(["podman", "push" os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']
