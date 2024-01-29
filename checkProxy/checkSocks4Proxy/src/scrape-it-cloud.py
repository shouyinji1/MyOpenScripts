#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import socket
import time
import traceback
import threading

from proxy_db import ProxySocks4
from proxy_db import ProxyHTTP
from Email import Email

class ScrapeItCloud:
    def get_proxies(self):
        response=requests.get('https://scrape-it.cloud/free-proxy-list')
        soup_table = BeautifulSoup(response.text, 'html.parser').find('tbody').find_all('tr')
        if soup_table != None and len(soup_table) !=0:
            proxies=[]
            for line in soup_table:
                data=line.find_all('td')
                proxies.append({'ip':data[0].text, 'port':data[1].text, 'protocol':data[2].text, 'country':data[3].text,
                               'comment': '来源:https://scrap-it.cloud, Protocol:'+data[2].text+', Anonymity:'+data[4].text})
        return proxies
    
    def get_available_proxy(self):
        available_proxies=[]
        proxies=self.get_proxies()
        threads=[]  # 初始化线程池
        for _ in range(10): # 创建10个线程
            threads.append(threading.Thread(target=self.test_proxies, args=(proxies,available_proxies)))
        for thread in threads: thread.start()
        for thread in threads: thread.join()    # 等待线程结束
        return available_proxies

    def test_socks_proxy(self, proxy):
        proxies = {
            "http": 'socks4://'+proxy['ip']+':'+proxy['port'],
            'https': 'socks4://'+proxy['ip']+':'+proxy['port']
        }
        try:
            response=requests.get('https://www.bing.com', proxies=proxies, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            if self.isConnected():
                return False
            else:
                raise Exception("没网")
        if ' Bing ' in response.text:
            return True
        return False

    def test_http_proxy(self, proxy):
        proxies = {
            "http": 'http://'+proxy['ip']+':'+proxy['port'],
            'https': 'http://'+proxy['ip']+':'+proxy['port']
        }
        try:
            response=requests.get('http://139.196.22.2:40758/proxy.pac', proxies=proxies, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            if self.isConnected():
                return False
            else:
                raise Exception("没网")
        if ' FindProxyForURL' in response.text:
            return True
        return False

    def test_proxy(self, proxy):
        if proxy['protocol'] in ('HTTP','HTTPS'):
            return self.test_http_proxy(proxy)
        elif proxy['protocol'] in ('SOCKS','SOCKS4','SOCKS5'):
            return self.test_socks_proxy(proxy)
        return False

    def test_proxies(self, proxies, available_proxies):
        while(True):
            try:
                proxy=proxies.pop()
                if self.test_proxy(proxy):
                    proxy['latestAvailableTime']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    proxy['最近测试连续失败次数']=0
                    if proxy['country']=='Unknown': del proxy['country']
                    available_proxies.append(proxy)
                print(proxy)
            except IndexError:
                break

    def isConnected(self):  # 测试是否有网
        try:
            # connect to the host -- tells us if the host is actually reachable
            socket.create_connection(("www.bing.com", 443))
            return True
        except OSError:
            pass
        return False
    
    def save_to_database(self):
        proxySocks4=ProxySocks4()
        proxyHTTP=ProxyHTTP()
        available_proxies=self.get_available_proxy()
        for proxy in available_proxies:
            if proxy['protocol'] in ('HTTP','HTTPS'):
                proxyHTTP.add_or_update(proxy)
            elif proxy['protocol'] in ('SOCKS','SOCKS4','SOCKS5'):
                proxySocks4.add_or_update(proxy)
        print("共"+str(len(available_proxies))+"个有效代理")



if __name__=='__main__':
    try:
        print(ScrapeItCloud().save_to_database())
    except Exception as e:
        error=traceback.format_exc()
        print(error)
        error+='\n\n==========\n'
        error+=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n'
        Email().send(content=error, subject='scrape-it.cloud代理爬取程序异常')