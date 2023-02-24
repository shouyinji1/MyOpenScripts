#!/usr/bin/python3

import sqlite3
import urllib.request
import traceback
import os
import pycurl
import certifi
from io import BytesIO
import socket


class ProxyDB:
    def __init__(self,database='./myProxy.db'):
        self.__conn=sqlite3.connect(database)  # 连接或创建数据库
        self.__cursor = self.__conn.cursor()  # 创建游标

        # 创建表
        sql = """CREATE TABLE IF NOT EXISTS proxy(
                    type TEXT NOT NULL,   -- 代理类型
                    ip TEXT,  -- 代理的IP地址
                    port INTEGER,  -- 代理IP的端口
                    country TEXT,   -- 代理IP所属国家
                    uploadTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- 代理IP存入数据库的时间
                    lastAvailableTime TIMESTAMP, -- 最后可用时间
                    lastStatus BOOLEAN,  -- 最后检查时的状态,0:不可用,1:可用
                    torFriendly BOOLEAN,    -- 是否可以用于访问Tor网络,0:不可以,1:可以
                    failedCount INTEGER DEFAULT 0,  -- 可用检测失败次数
                    PRIMARY KEY(ip,port),
                    CHECK(type IN('http','https','socks','socks4','socks4a','socks5'))
                );"""
        self.__cursor.execute(sql)
        self.__conn.commit()    # 提交事务

    def __del__(self):
        self.__cursor.close()
        self.__conn.commit()    # 提交事务
        self.__conn.close() # 关闭连接

    def isAvailable(self, type, ip, port):    # 检查代理是否可用
        pass
    
    # uploadDB: 上传数据库，没网或无效新代理不上传
    # Return: -1: 没网,或异常，1: 可以用于访问Tor网络，0:不可以用于访问Tor网络
    def isTorFriendly(self, type, ip, port, uploadDB=False):   # 检查代理是否可以用于访问Tor网络
        lastStatus,torFriendly=0,0

        if self.isTorBlockedCountry(ip):    # IP属于屏蔽Tor网络的国家
            torFriendly=0    # 不可访问Tor网络
        else:
            try:
                buffer = BytesIO()
                c = pycurl.Curl()
                c.setopt(c.URL, 'https://www.bing.com')
                #c.setopt(c.URL, 'ipinfo.io')
                c.setopt(c.USERAGENT, 'curl/7.74.0')
                c.setopt(c.TIMEOUT, 30)
                c.setopt(c.WRITEDATA, buffer)
                c.setopt(c.CAINFO, certifi.where())
                c.setopt(c.PROXY, ip)
                c.setopt(c.PROXYPORT, port)
                if type=='http':
                    c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
                elif type=='https':
                    c.setopt(c.PROXYTYPE, 2)
                elif type=='socks4':
                    c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
                elif type=='socks5':
                    c.setopt(c.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
                else:
                    c.close()
                    return -1   # 输入异常

                c.perform()
                c.close()
                body = buffer.getvalue().decode('utf-8')

                # Bing国际版和国内版标题不同，国内访问国际版会被重定向
                if ('<title>Bing</title>' in body 
                        or '<title>Microsoft Bing Search</title>' in body
                        or '<title>Search</title>' in body):
                    lastStatus,torFriendly=1,1    # 代理可用，可以用于访问Tor网络
                elif '<title>Object moved</title>' in body:
                    lastStatus,torFriendly=1,0    # 代理可用，但不可以用于访问Tor网络
                else:
                    lastStatus,torFriendly=0,0  # 代理不可用
            except pycurl.error as ex:
                #traceback.print_exc()
                if self.isConnected():   # 检查是否有网
                    lastStatus,torFriendly=0,0    # 无效代理，不可以访问Tor网络
                else:
                    return -1   # 没网
        if uploadDB==True:
            if(lastStatus==0):   # 无效代理
                # 对于无效代理，检查是不是新添加的代理，如果是则丢弃，如果不是则更新
                if self.__cursor.execute('select 1 from proxy where ip=? and port=?',(ip,port)).fetchone() ==None:
                    return torFriendly
                else:   # 有时代理不可用只是暂时现象，该代理可能可用于访问Tor网络
                    self.upload(type,ip,port,country=None,lastAvailableTime=None,lastStatus=lastStatus)
            else:
                self.upload(type,ip,port,country=None,lastAvailableTime=None,lastStatus=lastStatus,torFriendly=torFriendly)
        return torFriendly

    def checkTorFriendlyRandom(self,quantity=1):  # 随机检查代理是否可以用于访问Tor网络
        proxies=self.__cursor.execute('SELECT type,ip,port FROM proxy ORDER BY RANDOM() limit ?;',(quantity,)).fetchall()
        if proxies != None:
            for i in proxies:
                self.isTorFriendly(i[0],i[1],i[2],uploadDB=True)

    def upload(self, type, ip, port, country=None, lastAvailableTime=None, lastStatus=None, torFriendly=None):   # 上传数据库
        self.__cursor.execute('''insert or ignore into proxy(type,ip,port) values(?,?,?)''',(type,ip,port))
        if country != None:
            self.__cursor.execute('''update proxy set country=? where ip=? and port=?''',(country,ip,port))
        if lastAvailableTime !=None:
            self.__cursor.execute('update proxy set lastAvailableTime=? where ip=? and port=?',(lastAvailableTime,ip,port))
        if lastStatus != None:
            if lastStatus==1:   # 有效代理
                self.__cursor.execute('update proxy set lastAvailableTime=CURRENT_TIMESTAMP,lastStatus=1,failedCount=0 where ip=? and port=?',(ip,port))
            elif lastStatus==0: # 无效代理
                self.__cursor.execute('update proxy set lastStatus=0,failedCount=failedCount+1 where ip=? and port=?',(ip,port))
        if torFriendly != None:
            if torFriendly==1:  # 可用于Tor，肯定是有效代理
                self.__cursor.execute('update proxy set lastAvailableTime=CURRENT_TIMESTAMP,lastStatus=1,torFriendly=1,failedCount=0 where ip=? and port=?',
                        (ip,port))
            elif torFriendly==0:  # 不可用于Tor
                self.__cursor.execute('update proxy set torFriendly=0 where ip=? and port=?',(ip,port))
        self.__conn.commit()    # 提交事务

    def getAvailableForTor(self, type="socks4", quantity=10):  # 从数据库中提取最新可用于Tor的代理
        # 查找数据库中标记可用并能连上Tor的代理
        proxyDB=self.__cursor.execute('''select type,ip,port from proxy where type=? and lastStatus=1 and torFriendly=1 
                and (strftime('%s','now')-strftime('%s',lastAvailableTime))<1800 
                order by failedCount asc,lastAvailableTime asc''',(type,)).fetchall()   # 查找最近半小时可用代理
        proxies=[]
        if proxyDB != None: # 最近半小时可用代理不检查
            proxies=proxyDB
        if len(proxies) < quantity: # 查询最新可用状态距现在大于29分钟的可用代理
            proxyDB=self.__cursor.execute('''select type,ip,port from proxy where type=? and lastStatus=1 and torFriendly=1 
                    and ((strftime('%s','now')-strftime('%s',lastAvailableTime)) >1740 or lastAvailableTime is null) 
                    order by failedCount asc,lastAvailableTime asc''',(type,)).fetchall()
            for i in proxyDB:
                if self.isTorFriendly(i[0],i[1],i[2],uploadDB=True)==1:
                    proxies.append(i)
                if len(proxies)>=quantity:
                    break
        if len(proxies) < quantity:  # 如果代理不够，查找数据库中标记不可用，但能用于Tor的代理
            proxyDB=self.__cursor.execute('select type,ip,port from proxy where type=? and lastStatus=0 and torFriendly=1 order by failedCount asc,lastAvailableTime desc',
                    (type,)).fetchall()
            if proxyDB != None:
                for i in proxyDB:
                    if self.isTorFriendly(i[0],i[1],i[2],uploadDB=True)==1:
                        proxies.append(i)
                    if len(proxies)>=quantity:
                        break
        if len(proxies) < quantity:  # 如果代理不够，查找数据库中没有标记是否可用于Tor的代理
            proxyDB=self.__cursor.execute('select type,ip,port from proxy where type=? and torFriendly is null order by failedCount asc,lastAvailableTime desc',
                    (type,)).fetchall()
            if proxyDB != None:
                for i in proxyDB:
                    if self.isTorFriendly(i[0],i[1],i[2],uploadDB=True)==1:
                        proxies.append(i)
                    if len(proxies)>=quantity:
                        break
        if len(proxies) < quantity:  # 如果代理不够，查找数据库中标记不能用于Tor的代理
            proxyDB=self.__cursor.execute('select type,ip,port from proxy where type=? and torFriendly !=1 order by failedCount asc,lastAvailableTime desc',
                    (type,)).fetchall()
            if proxyDB != None:
                for i in proxyDB:
                    if self.isTorFriendly(i[0],i[1],i[2],uploadDB=True)==1:
                        proxies.append(i)
                    if len(proxies)>=quantity:
                        break
        return proxies
    
    def getLastHalfHourAvailableForTor(self, type="socks4", quantity=10):  # 从数据库中提取最近半小时可用于Tor的代理
        pass

    def delete(self, ip, port):   # 从数据库删除代理
        pass

    def combine(self, proxyDB1):    # 将proxyDB1合并到proxyDB
        conn1=sqlite3.connect(proxyDB1)  # 连接或创建数据库
        cursor1 = conn1.cursor()  # 创建游标
        proxies=cursor1.execute('select type,ip,port,country,uploadTime,lastAvailableTime,lastStatus,torFriendly,failedCount from proxy').fetchall()
        if proxies != None:
            for proxy in proxies:
                self.__cursor.execute('insert or ignore into proxy(type,ip,port,country,uploadTime,lastAvailableTime,lastStatus,torFriendly,failedCount) values(?,?,?,?,?,?,?,?,?)',
                        (proxy))
        cursor1.close()
        conn1.commit()    # 提交事务
        conn1.close() # 关闭连接

    def isConnected(self):  # 测试是否有网
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
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


if __name__=="__main__":
    p=ProxyDB()
    #print(p.isTorFriendly(type='socks5',ip='47.93.116.53',port=40755,uploadDB=True))
    #p.upload(type='socks5',ip='47.93.116.53',port=40756,country='CN',lastStatus=1,torFriendly=1)
    #p.upload(type='socks5',ip='127.0.0.1',port=9050,lastStatus=1,torFriendly=1)
    #p.upload(type='socks5',ip='127.0.0.1',port=4451,torFriendly=1)
    #print(p.getAvailableForTor('socks5'))
    #p.combine('./myProxy1.db')
    pass
