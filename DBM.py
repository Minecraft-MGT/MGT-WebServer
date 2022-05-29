from mongoengine import *
import hashlib, random, string, time, math


def load(url):
    connect(host=url)

def hash_string(input):
    return str(hashlib.sha256(input.encode('utf-8')).hexdigest())

def random_string(size=6, chars=string.ascii_uppercase+string.digits+string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(int(size)))


class Account(Document):
    username = StringField(required=True, max_length=20, min_length=1, unique=True)
    password = StringField(required=True)   #no limitations becase password is stored hashed

class Team(Document):
    name = StringField(required=True, unique=True, min_length=1, max_length=20)
    players = ListField(ReferenceField(Account), max_length=3)

    def change_team(self, team):
        pass

    def get_team(self):
        pass

class Session(Document):
    owner = ReferenceField(Account)

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
