import subprocess
import yaml
import os
import sys
import time
import datetime

if 'CHECK_INTERVAL' in os.environ.keys():
    interval = os.environ['CHECK_INTERVAL']
else:
    interval = 10

if 'SKOPEO_OPTIONS' in os.environ.keys():
    skopeo_options = os.environ['SKOPEO_OPTIONS']
else:
    skopeo_options = ""

if 'OCP_USERNAME' in os.environ.keys():
    result = subprocess.run(["skopeo", "login", "--username="+os.environ['OCP_USERNAME'], "--password="+os.environ['OCP_TOKEN'], os.environ['OCP_REGISTRY_URL']])

# Load version file from either of the following sources:
#   Git Repo
#   Locally mounted file
#   Default version file of the image
if 'GIT_REPO' in os.environ.keys():
    if 'GIT_PATH' not in os.environ.keys():
        print("ERROR: No path in Git repo provided", file=sys.stderr)
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
    print(str(datetime.datetime.now())+": Checking images", file=sys.stdout)
    for key, data in versions.items():
        # Pull
        name = data["image"][data['image'].rfind("/")+1:]
        print("docker://"+data["image"]+":"+data["tag"]+" -> "+ "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"], file=sys.stdout)
        result = subprocess.run(["skopeo", "copy", skopeo_options, "docker://"+data["image"]+":"+data["tag"], "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"]])
        # Tag
        #result = subprocess.run(["podman", "tag", data["image"]+":"+data["tag"], os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
        # Push
        #result = subprocess.run(["podman", "push", os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
    # Wait
    print("", file=sys.stdout)
    print("", file=sys.stdout)
    time.sleep(int(interval))
