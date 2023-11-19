import subprocess
import yaml
import os
import time
import datetime

if 'CHECK_INTERVAL' in os.environ.keys():
    interval = os.environ['CHECK_INTERVAL']
else:
    interval = 10

# Load version file from either of the following sources:
#   Git Repo
#   Locally mounted file
#   Default version file of the image
if 'GIT_REPO' in os.environ.keys():
    if 'GIT_PATH' not in os.environ.keys():
        print("ERROR: No path in Git repo provided")
    result = subprocess.run(["git", "clone", "-c /home/podman/", os.environ['GIT_REPO'], "sourerepo"])
    with open("/home/podman/sourcerepo/"+os.environ['GIT_PATH'], "r") as f:
        versions = yaml.safe_load(f)
elif 'LOCAL_VERION_FILEPATH' in os.environ.keys():
    with open(os.environ['LOCAL_VERSION_FILEPATH'], "r") as f:
        versions = yaml.safe_load(f)
else:
    with open('versions.yaml', 'r') as f:
        versions = yaml.safe_load(f)

while True:
    print(str(datetime.datetime.now())+": Checking images")
    for key, data in versions.items():
        # Pull
        result = subprocess.run(["skopeo", "copy", data["image"]+":"+data["tag"], os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
        # Tag
        #result = subprocess.run(["podman", "tag", data["image"]+":"+data["tag"], os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
        # Push
        #result = subprocess.run(["podman", "push", os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
    # Wait
    print("")
    print("")
    time.sleep(interval)
