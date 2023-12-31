import subprocess
import yaml
import os
import sys
import time
import datetime
import re
import urllib.parse

if 'CHECK_INTERVAL' in os.environ.keys():
    interval = int(os.environ['CHECK_INTERVAL'])
else:
    interval = 10

if 'SKOPEO_OPTIONS' in os.environ.keys():
    skopeo_options = os.environ['SKOPEO_OPTIONS']
else:
    skopeo_options = ""

if 'SOURCE_REGISTRY_URL' in os.environ.keys():
    source_registry = os.environ['SOURCE_REGISTRY_URL']
    if not source_registry.endswitch('/'):
        source_registry = source_registry + '/'
else:
    source_registry = ""

if 'OCP_USERNAME' in os.environ.keys():
    result = subprocess.run(["skopeo", "login", "--tls-verify=false", "--username="+os.environ['OCP_USERNAME'], "--password="+os.environ['OCP_TOKEN'], os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']])

# Load version file from either of the following sources:
#   Git Repo
#   Locally mounted file
#   Default version file of the image
if 'GIT_REPO' in os.environ.keys():
    if 'GIT_PATH' not in os.environ.keys():
        print("ERROR: No path in Git repo provided", file=sys.stderr)
        exit(1)
    if 'GIT_SSHKEY' in os.environ.keys():
        with open('/.ssh/id_rsa','w') as f:
            f.write(os.environ['GIT_SSHKEY'])
        os.chmod('/.ssh/id_rsa', 0o600)
    
    repo = os.environ['GIT_REPO']
    match = re.match('^[a-z]+://', repo)
    if not match:
        repo = "https://" + repo
        match = re.match('^[a-z]+://', repo)
    if 'GIT_username' in os.environ.keys():
        repo = repo[:match.span()[1]]+urllib.parse.quote(os.environ['GIT_username'])+":"+urllib.parse.quote(os.environ['GIT_password'])+"@"+repo[match.span()[1]:]
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

while interval > 0:
    print(str(datetime.datetime.now())+": Checking images", file=sys.stdout)
    for key, data in versions.items():
        # Pull
        name = data["image"][data['image'].rfind("/")+1:]
        if skopeo_options != "":
            command = ["skopeo", "copy", skopeo_options, "docker://"+source_registry+data["image"]+":"+data["tag"], "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"]]
        else:
            command = ["skopeo", "copy", "docker://"+source_registry+data["image"]+":"+data["tag"], "docker://"+os.environ['OCP_REGISTRY_URL']+"/"+os.environ['OCP_PROJECT']+"/"+name+":"+data["tag"]]
        print(" ".join(command), file=sys.stdout)
        result = subprocess.run(command)
    # Wait
    print("", file=sys.stdout)
    print("", file=sys.stdout)
    time.sleep(interval)
