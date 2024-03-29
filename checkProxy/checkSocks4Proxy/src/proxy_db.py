#!/usr/bin/python3

import sqlite3
import os
#import pycurl
#from io import BytesIO
import socket
import requests
import time
import threading


class ProxySocks4:
    def __init__(self):
        database_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/myProxy.db')
        self.__conn=sqlite3.connect(database_path)  # 连接或创建数据库
        self.__conn.row_factory=self.dict_factory
        self.__cursor = self.__conn.cursor()  # 创建游标

        # 创建表
        sql = """CREATE TABLE IF NOT EXISTS proxy_socks4(
                    ip TEXT NOT NULL,  -- 代理的IP地址
                    port INTEGER NOT NULL,  -- 代理IP的端口
                    country TEXT,   -- 代理IP所属国家
                    uploadTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- 代理IP存入数据库的时间
                    latestAvailableTime TIMESTAMP, -- 最后可用时间
                    最近测试连续失败次数 INTEGER,
                    是否对Tor友好 TEXT CHECK("是否对Tor友好" IN ('是', '否')),
                    comment TEXT,
                    PRIMARY KEY(ip,port)
                );"""
        self.__cursor.execute(sql)
        self.__conn.commit()    # 提交事务

    def __del__(self):
        self.__cursor.close()
        self.__conn.commit()    # 提交事务
        self.__conn.close() # 关闭连接

    def dict_factory(self, cursor, row):
        # Python Sqlite3以字典形式返回查询结果的实现方法：
        # 参考：https://blog.csdn.net/bigcarp/article/details/114387469
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def is_available_foreign_proxy(self, ip, port):    # 检查代理是否是国外可用代理
        proxies = {
            "http": 'socks4://'+ip+':'+str(port),
            'https': 'socks4://'+ip+':'+str(port)
        }
        try:
            response=requests.get('https://www.bing.com', proxies=proxies, timeout=(10,20))  # 找出10s内建立连接，20s内响应请求的代理
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError):
            if self.isConnected():
                return False
            else:
                raise Exception("没网")
        # Bing国际版和国内版标题不同，国内访问国际版会被重定向
        if('<title>Bing</title>' in response.text 
                or '<title>Microsoft Bing Search</title>' in response.text 
                or '<title>Search</title>' in response.text):
            return True
        return False

    def sift_available_foreign_proxies(self, proxies, available_proxies, waiting_update_proxy):
        while(True):
            try:
                proxy=proxies.pop()
                if self.is_available_foreign_proxy(proxy['ip'], proxy['port']):
                    proxy['latestAvailableTime']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    proxy['最近测试连续失败次数']=0
                    available_proxies.append(proxy)
                else:
                    if proxy['最近测试连续失败次数'] != None:
                        proxy['最近测试连续失败次数']=proxy['最近测试连续失败次数']+1
                    else:
                        proxy['最近测试连续失败次数']=1
                waiting_update_proxy.append(proxy)
                print(proxy)
            except IndexError:
                break

    def get_available_foreign_proxies(self, quantity=30):  # 从数据库中提取可用的国外socks4代理，不少于quantity个
        available_proxies=[]
        waiting_update_proxy=[]
        offset = 0  # 数据库select偏移量
        scale=5 # 依据二八定律。用于筛选的代理样本中，往往最后只有小很一部分是真实有效的。故一次select扩大quantity的5倍
        while len(available_proxies) < quantity:
            proxy_db=self.__cursor.execute('''select * from proxy_socks4 where country !='China' or country is null order by 最近测试连续失败次数 asc limit ?,?'''
                                            ,(offset, quantity*scale)).fetchall()
            if len(proxy_db) < 1: break   # 已经没有代理了
            threads=[]
            for _ in range(10): # 创建10个线程，筛选代理
                threads.append(threading.Thread(target=self.sift_available_foreign_proxies, args=(
                    proxy_db, available_proxies, waiting_update_proxy
                )))
            for thread in threads: thread.start()
            for thread in threads: thread.join()    # 等待线程结束
            offset=offset+quantity*scale
            #scale=1 if quantity>=10 else 10 # 第二次及以后的select缩小至1倍。但是如果要求找的代理的数量太少，则扩大10倍。
        if len(waiting_update_proxy) != 0:  # 更新数据库中的代理状态
            for proxy in waiting_update_proxy:
                self.update(proxy)
        return available_proxies

    def update(self, proxy):   # 更新数据库
        self.__cursor.execute(
            '''update proxy_socks4 set latestAvailableTime=?, 最近测试连续失败次数=? where ip=? and port=?''',
            (proxy['latestAvailableTime'], proxy['最近测试连续失败次数'], proxy['ip'], proxy['port'])
        )
        self.__conn.commit()    # 提交事务

    def add_or_update(self, proxy):   # 添加或更新数据
        self.__cursor.execute('insert or ignore into proxy_socks4(ip,port) values(?,?)', (proxy['ip'],proxy['port']))
        if 'country' in proxy:
            self.__cursor.execute('update proxy_socks4 set country=? where ip=? and port=? and country is null', (proxy['country'], proxy['ip'],proxy['port']))
        if 'latestAvailableTime' in proxy:
            self.__cursor.execute('update proxy_socks4 set latestAvailableTime=? where ip=? and port=?', (proxy['latestAvailableTime'], proxy['ip'],proxy['port']))
        if '最近测试连续失败次数' in proxy:
            self.__cursor.execute('update proxy_socks4 set 最近测试连续失败次数=? where ip=? and port=?', (proxy['最近测试连续失败次数'], proxy['ip'],proxy['port']))
        if 'comment' in proxy:
            self.__cursor.execute('update proxy_socks4 set comment=? where ip=? and port=? and comment is null', (proxy['comment'], proxy['ip'],proxy['port']))
        self.__conn.commit()    # 提交事务
    
    def isConnected(self):  # 测试是否有网
        try:
            # connect to the host -- tells us if the host is actually reachable
            socket.create_connection(("www.bing.com", 443))
            return True
        except OSError:
            pass
        return False

    # IP是否属于屏蔽Tor的国家，使用whois查询
    # Return: True: 是，False:否，或未知
    def isTorBlockedCountry(self,ip):
        output=os.popen("whois %s | grep -i Country"%ip,'r').read().splitlines()
        #print(output)
        for i in output:
            if i.split(':')[1].strip() in ('RU','CN','IR','BY'):
                # Russia, China, Iron, Belarus
                return True
        return False

    # def combine(self, proxyDB1):    # 将proxyDB1合并到proxyDB
    #     conn1=sqlite3.connect(proxyDB1)  # 连接或创建数据库
    #     cursor1 = conn1.cursor()  # 创建游标
    #     proxies=cursor1.execute('select type,ip,port,country,uploadTime,lastAvailableTime,lastStatus,torFriendly,failedCount from proxy').fetchall()
    #     if proxies != None:
    #         for proxy in proxies:
    #             self.__cursor.execute('insert or ignore into proxy(type,ip,port,country,uploadTime,lastAvailableTime,lastStatus,torFriendly,failedCount) values(?,?,?,?,?,?,?,?,?)',
    #                     (proxy))
    #     cursor1.close()
    #     conn1.commit()    # 提交事务
    #     conn1.close() # 关闭连接

    # # uploadDB: 上传数据库，没网或无效新代理不上传
    # # Return: -1: 没网,或异常，1: 可以用于访问Tor网络，0:不可以用于访问Tor网络
    # def isTorFriendly(self, type, ip, port, uploadDB=False):   # 检查代理是否可以用于访问Tor网络
    #     lastStatus,torFriendly=0,0

    #     if self.isTorBlockedCountry(ip):    # IP属于屏蔽Tor网络的国家
    #         torFriendly=0    # 不可访问Tor网络
    #     else:
    #         try:
    #             buffer = BytesIO()
    #             c = pycurl.Curl()
    #             c.setopt(c.URL, 'https://www.bing.com')
    #             #c.setopt(c.URL, 'ipinfo.io')
    #             c.setopt(c.USERAGENT, 'curl/7.74.0')
    #             c.setopt(c.TIMEOUT, 30)
    #             c.setopt(c.WRITEDATA, buffer)
    #             c.setopt(c.CAINFO, certifi.where())
    #             c.setopt(c.PROXY, ip)
    #             c.setopt(c.PROXYPORT, port)
    #             if type=='http':
    #                 c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
    #             elif type=='https':
    #                 c.setopt(c.PROXYTYPE, 2)
    #             elif type=='socks4':
    #                 c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
    #             elif type=='socks5':
    #                 c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
    #             else:
    #                 c.close()
    #                 return -1   # 输入异常

    #             c.perform()
    #             c.close()
    #             body = buffer.getvalue().decode('utf-8')

    #             # Bing国际版和国内版标题不同，国内访问国际版会被重定向
    #             if ('<title>Bing</title>' in body 
    #                     or '<title>Microsoft Bing Search</title>' in body
    #                     or '<title>Search</title>' in body):
    #                 lastStatus,torFriendly=1,1    # 代理可用，可以用于访问Tor网络
    #             elif '<title>Object moved</title>' in body:
    #                 lastStatus,torFriendly=1,0    # 代理可用，但不可以用于访问Tor网络
    #             else:
    #                 lastStatus,torFriendly=0,0  # 代理不可用
    #         except pycurl.error as ex:
    #             #traceback.print_exc()
    #             if self.isConnected():   # 检查是否有网
    #                 lastStatus,torFriendly=0,0    # 无效代理，不可以访问Tor网络
    #             else:
    #                 return -1   # 没网
    #     if uploadDB==True:
    #         if(lastStatus==0):   # 无效代理
    #             # 对于无效代理，检查是不是新添加的代理，如果是则丢弃，如果不是则更新
    #             if self.__cursor.execute('select 1 from proxy where ip=? and port=?',(ip,port)).fetchone() ==None:
    #                 return torFriendly
    #             else:   # 有时代理不可用只是暂时现象，该代理可能可用于访问Tor网络
    #                 self.upload(type,ip,port,country=None,lastAvailableTime=None,lastStatus=lastStatus)
    #         else:
    #             self.upload(type,ip,port,country=None,lastAvailableTime=None,lastStatus=lastStatus,torFriendly=torFriendly)
    #     return torFriendly


class ProxyHTTP:
    def __init__(self):
        database_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/myProxy.db')
        self.__conn=sqlite3.connect(database_path)  # 连接或创建数据库
        self.__conn.row_factory=self.dict_factory
        self.__cursor = self.__conn.cursor()  # 创建游标

        # 创建表
        sql = """CREATE TABLE IF NOT EXISTS proxy_http(
                    ip TEXT NOT NULL,  -- 代理的IP地址
                    port INTEGER NOT NULL,  -- 代理IP的端口
                    country TEXT,   -- 代理IP所属国家
                    uploadTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- 代理IP存入数据库的时间
                    latestAvailableTime TIMESTAMP, -- 最后可用时间
                    最近测试连续失败次数 INTEGER,
                    是否对Tor友好 TEXT CHECK("是否对Tor友好" IN ('是', '否')),
                    comment TEXT,
                    PRIMARY KEY(ip,port)
                );"""
        self.__cursor.execute(sql)
        self.__conn.commit()    # 提交事务

    def __del__(self):
        self.__cursor.close()
        self.__conn.commit()    # 提交事务
        self.__conn.close() # 关闭连接

    def dict_factory(self, cursor, row):
        # Python Sqlite3以字典形式返回查询结果的实现方法：
        # 参考：https://blog.csdn.net/bigcarp/article/details/114387469
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def add_or_update(self, proxy):   # 添加数据
        self.__cursor.execute('insert or ignore into proxy_http(ip,port) values(?,?)', (proxy['ip'],proxy['port']))
        if 'country' in proxy:
            self.__cursor.execute('update proxy_http set country=? where ip=? and port=? and country is null', (proxy['country'], proxy['ip'],proxy['port']))
        if 'latestAvailableTime' in proxy:
            self.__cursor.execute('update proxy_http set latestAvailableTime=? where ip=? and port=?', (proxy['latestAvailableTime'], proxy['ip'],proxy['port']))
        if '最近测试连续失败次数' in proxy:
            self.__cursor.execute('update proxy_http set 最近测试连续失败次数=? where ip=? and port=?', (proxy['最近测试连续失败次数'], proxy['ip'],proxy['port']))
        if 'comment' in proxy:
            self.__cursor.execute('update proxy_http set comment=? where ip=? and port=? and comment is null', (proxy['comment'], proxy['ip'],proxy['port']))
        self.__conn.commit()    # 提交事务


if __name__=="__main__":
    proxy_socks4=ProxySocks4()
    proxy_socks4.get_available_foreign_proxies()
    print(proxy_socks4.available_proxies)
