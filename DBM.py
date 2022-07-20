from mongoengine import *
import hashlib, random, string, time, math, os

TEAM_MAX_PLAYERS = 3
ICON_EXTENSIONS = ["png", "jpg", "jpeg"]
TRAILER_EXTENSIONS = ["mp4"]

def load(url):
    connect(host=url)

def hash_string(input):
    return str(hashlib.sha256(input.encode('utf-8')).hexdigest())

def random_string(size=6, chars=string.ascii_uppercase+string.digits+string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(int(size)))


class Account(Document):
    username = StringField(required=True, max_length=20, min_length=1, unique=True)
    password = StringField(required=True)   #no limitations becase password is stored hashed
    team = ReferenceField("Team")

    def change_team(self, new_team):

        if new_team is not None:
            if len(new_team.members) >= TEAM_MAX_PLAYERS: 
                print("Error: Team already full!")
                return False

        old_team = self.team
        self.team = new_team


        if new_team is not None:
            new_team.members.append(self)
            new_team.save()

        if old_team is not None:
            old_team.members.remove(self)
            if len(old_team.members) <= 0: 
                old_team.delete()
            else:
                old_team.save()
        self.save()
    
    def change_pw(self, new_pw):
        self.password = hash_string(new_pw)
        self.save()

class Team(Document):
    name = StringField(required=True, unique=True, min_length=1, max_length=20)
    short_name = StringField(required=True, unique=True, max_length=3)
    members = ListField(ReferenceField(Account), max_length=3)
    invites = ListField(ReferenceField(Account), default=[])
    opened = BooleanField(default=False)

    def icon_path(self):
        base = "/static/teams/"+str(self.id)+"/"
        for cc in ICON_EXTENSIONS:
            if os.path.exists("."+base+"icon."+cc):
                return base+"icon."+cc
        return "/static/teams/default/icon.png"
    
    def trailer_path(self):
        base = "/static/teams/"+str(self.id)+"/"
        for cc in TRAILER_EXTENSIONS:
            if os.path.exists("."+base+"trailer."+cc):
                return base+"trailer."+cc
        return "/static/teams/default/trailer.mp4"

    def can_join(self, acc):
        if len(self.members) >= TEAM_MAX_PLAYERS: return False
        if self.opened: return True
        if acc in self.members: return False
        return acc in self.invites


def team_create(name):
    short_name = name[:3].upper()
    while len(Team.objects(short_name=short_name))>0:
        short_name = random_string(3).upper()
    return Team(name=name, short_name=short_name, members=[]).save()

class Session(Document):
    owner = ReferenceField(Account)

class ServerSetting(Document):
    key = StringField()
    val = StringField()

def setting_get(key):
    if not ServerSetting.objects(key=key): return None
    return ServerSetting.objects(key=key)[0].val

def setting_set(key, val):
    toEdit = ServerSetting.objects(key=key)[0] if ServerSetting.objects(key=key) else ServerSetting(key=key, val=val)
    toEdit.val = val
    toEdit.save()

def session_create(owner:Account):
    if Session.objects(owner=owner): return Session.objects(owner=owner)[0]
    return Session(owner=owner).save()

def session_read(id:str):
    if Session.objects(id=id):
        return Session.objects(id=id)[0].owner
    else:
        return None

def session_terminate(id:str):
    return Session.objects(id=id).delete()

def acc_create(username, password):
    return Account(username=username, password=hash_string(password)).save()

def acc_check_access(username, password):
    if Account.objects(username=username):
        return Account.objects.get(username=username).password == hash_string(password)
    else: 
        return False
