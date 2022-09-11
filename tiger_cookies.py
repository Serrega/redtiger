from getpass import getpass
import pickle
import requests


def check_cookies(level: str) -> dict:
    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if level not in cooks:
            print('use prevision level')
            exit(1)
    except (FileExistsError, FileNotFoundError):
        print('use level 1')
        exit(1)

    return cooks


def save_cookies(cooks: dict, level: str, passw: str):
    level = 'level' + str(int(level[5]) + 1) + 'login'
    if (level not in cooks) or (cooks[level] != passw):
        cooks[level] = passw

    try:
        with open('cooks.pickle', 'wb') as f:
            pickle.dump(cooks, f)
    except (FileExistsError, FileNotFoundError):
        print('can not write cookies')
        exit(1)
