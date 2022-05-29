import string, random

def random_string(size=6, chars=string.ascii_uppercase+string.digits+string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(int(size)))

tokens = {}
providers = []

def token_by_name(name):
    if name in tokens:
        return tokens[name]
    return None

def create_token_for(name):
    tokens[name] = random_string(5)

def remove_token_for(name):
    del tokens[name]


def provider_register(address):
    providers.append(address)
    build_authserver_string()

def provider_deregister(address):
    while address in providers:
        providers.remove(address)
    build_authserver_string()

authserver_string = ""

def build_authserver_string():
    global authserver_string
    authserver_string = ""
    authserver_string = (", ".join(providers))
    authserver_string = " oder".join(authserver_string.rsplit(",", 1))
    if authserver_string == "":
        authserver_string = "<Kein Server verfügbar>"

def get_authserver_string():
    return authserver_string

build_authserver_string()

