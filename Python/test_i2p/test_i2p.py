import requests
import os

def test_i2p():
    proxies = {
        "http": 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        requests.get('http://www.baidu.com', proxies=proxies)
    except requests.exceptions.ConnectionError:
        return False
    return True


if __name__=='__main__':
    if test_i2p() == False:
        if test_i2p() == False:
            if test_i2p() == False:
                os.system("systemctl restart i2p")