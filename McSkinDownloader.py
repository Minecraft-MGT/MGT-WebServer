import sys
import json
import shutil
from base64 import b64decode
import requests
from pathlib import Path

userid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
userinfo_url = "https://sessionserver.mojang.com/session/minecraft/profile/{userid}"

def fail(msg, verbose_msg):
    print(msg, file=sys.stderr)

def find_texture_info(properties):
    for prop in properties:
        if prop['name'] == 'textures':
            return json.loads(b64decode(prop['value'], validate=True).decode('utf-8'))
    return None

def get_url(url, **kwargs):
    return requests.get(url, **kwargs)

def download(username, outputpath):
    #make sure that folder exists
    Path(outputpath).mkdir(parents=True, exist_ok=True)

    r = get_url(userid_url.format(username=username))
    if r.status_code != 200:
        fail("Could not retrieve user ID for {username}".format(username=username),
             "{0} {1}".format(r.status_code, userid_url.format(username=username)))
    userid = r.json()['id']

    r = get_url(userinfo_url.format(userid=userid))
    if r.status_code != 200:
        fail("Failed to download user info for {username}".format(username=username),
             "{0} {1}".format(r.status_code, userinfo_url.format(userid=userid)))
    userinfo = r.json()
    texture_info = find_texture_info(userinfo['properties'])
    if texture_info is None:
        fail("Failed to find texture info for {username}".format(username=username),
             userinfo)

    try:
        skin_url = texture_info['textures']['SKIN']['url']
    except:
        fail("Failed to find texture info for {username}".format(username=username),
             texture_info)
    r = get_url(skin_url, stream=True)
    if r.status_code != 200:
        fail("Could not download skin for {username}".format(username=username),
             "{0} {1}".format(r.status_code, skin_url))

    with open(outputpath+username+".png", 'wb') as f:
        shutil.copyfileobj(r.raw, f)
