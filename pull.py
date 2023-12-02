import subprocess
import yaml
import os
import sys
import time
import datetime
import re

if 'CHECK_INTERVAL' in os.environ.keys():
    interval = os.environ['CHECK_INTERVAL']
else:
    interval = 10

if 'SKOPEO_OPTIONS' in os.environ.keys():
    skopeo_options = os.environ['SKOPEO_OPTIONS']
else:
    skopeo_options = ""

if 'OCP_USERNAME' in os.environ.keys():
    result = subprocess.run(["skopeo", "login", "--tls-verify=false", "--username="+os.environ['OCP_USERNAME'], "--password="+os.environ['OCP_TOKEN'], os.environ['OCP_REGISTRY_URL']])

# Load version file from either of the following sources:
#   Git Repo
#   Locally mounted file
#   Default version file of the image
if 'GIT_REPO' in os.environ.keys():
    if 'GIT_PATH' not in os.environ.keys():
        print("ERROR: No path in Git repo provided", file=sys.stderr)
        exit(1)
    repo = os.environ['GIT_REPO']
    match = re.match('^[a-z]+://', repo)
    if not match:
        repo = "https://" + repo
        match = re.match('^[a-z]+://', repo)
    if 'GIT_username' in os.environ.keys():
        repo = repo[:match.span()[1]]+os.environ['GIT_username']+":"+os.environ['GIT_password']+"@"+repo[match.span()[1]:]
    print("Pulling repo "+repo)
    result = subprocess.run(["git", "-C", "/home/skopeo/", "clone", repo, "sourcerepo"])
    if result.returncode != 0:
        print("ERROR: git returned code "+str(result.returncode))
        exit(1)
    try:
        with open("/home/skopeo/sourcerepo/"+os.environ['GIT_PATH'], "r") as f:
            versions = yaml.safe_load(f)
    except FileNotFound as e:
        print("ERROR: versions file not found under path \""+os.environ['GIT_PATH']+"\" in git repo!")
        exit(1)
elif 'LOCAL_VERSION_FILEPATH' in os.environ.keys():
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
        if skopeo_options != "":
            command = ["skopeo", "copy", skopeo_options, "docker://"+data["image"]+":"+data["tag"], "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"]]
        else:
            command = ["skopeo", "copy", "docker://"+data["image"]+":"+data["tag"], "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"]]
        print(" ".join(command), file=sys.stdout)
        result = subprocess.run(command)
        # Tag
        #result = subprocess.run(["podman", "tag", data["image"]+":"+data["tag"], os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
        # Push
        #result = subprocess.run(["podman", "push", os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+os.environ['OCP_IMAGESTREAM']+":"+os.environ['OCP_IMAGE_TAG']])
    # Wait
    print("", file=sys.stdout)
    print("", file=sys.stdout)
    time.sleep(int(interval))
