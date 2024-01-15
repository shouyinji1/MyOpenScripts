import requests
import os
#import random

class TestI2P:
    def test_proxy(self,proxies):
        try:
            response=requests.get('http://www.baidu.com', proxies=proxies)
        except requests.exceptions.ConnectionError:
            return False
        if '百度' in response.text:
            return True
        return False

    def test_socks5(self):
        proxies = {
            "http": 'socks5://127.0.0.1:4452',
            'https': 'socks5://127.0.0.1:4452'
        }
        return self.test_proxy(proxies=proxies)

    # def test_socks5_tor(self):
    #     proxies = {
    #         "http": 'socks5://127.0.0.1:9050',
    #         'https': 'socks5://127.0.0.1:9050'
    #     }
    #     return self.test_proxy(proxies=proxies)

    def test_outproxy(self):
        proxies = {
            "http": 'http://127.0.0.1:4444',
            'https': 'http://127.0.0.1:4444'
        }
        return self.test_proxy(proxies=proxies)

    def test_httpproxy(self):
        proxies = {
            "http": 'http://127.0.0.1:4451',
            'https': 'http://127.0.0.1:4451'
        }
        return self.test_proxy(proxies=proxies)
    
    def test(self):
        if self.test_socks5() == False:
            #if self.test_socks5_tor() == False:
            if self.test_outproxy() == False:
                if self.test_httpproxy() == False:
                    return False
        return True


if __name__=='__main__':
    testI2P=TestI2P()
    if testI2P.test() == False:
        if testI2P.test() == False:
            if testI2P.test() == False:
                #if random.random() < 0.5:
                os.system("systemctl restart i2p")
                print("I2P不通")


# crontab:
# */35 *  * * *   root    python3 /root/MyOpenScripts/Python/test_i2p/test_i2p.py