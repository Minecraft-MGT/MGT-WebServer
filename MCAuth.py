import string, random

def random_string(size=6, chars=string.ascii_uppercase+string.digits+string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(int(size)))

tokens = {"LeeDo": "meemesheesh"}
providers = []

def token_by_name(name):
    if name in tokens:
        return tokens[name]
    return None

def create_token_for(name):
    tokens[name] = random_string(5)


def provider_register(address):
    providers.append(address)

def provider_deregister(address):
    providers.remove(address)
