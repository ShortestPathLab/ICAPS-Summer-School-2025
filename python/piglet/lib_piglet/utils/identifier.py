import base64
import hashlib
from random import random
from time import time
from datetime import datetime
from yaml import dump


def encode(num: str):
    hasher = hashlib.sha1(num.encode())
    return str(base64.urlsafe_b64encode(hasher.digest()))[2:11]


def identifier(obj: object):
    return encode(f"{id(obj)}")

def get_random_id():
    return encode(f"{random()}")

def get_time_id():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}" + f"_{int(datetime.now().microsecond / 1000):03d}"
