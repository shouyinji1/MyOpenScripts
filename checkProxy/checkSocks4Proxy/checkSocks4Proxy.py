#!/usr/bin/python3

import os
import sys
import traceback
import time

class PrivateInfo:
    fromEmail=None
    fromEmailPasswd=None
    toEmail=None
    subjectForCheck=None
    subjectForException=None
    expireTime=7

try:
    from checkSocks4ProxyConfig import *
except ModuleNotFoundError:
    print('Config file not found！')

from proxyDBManage import ProxyDB


# 检查代理是否过期
# return:
#   -1: 出错
#   0:  没过期
#   1:   过期
import datetime
def isExpire(line,expireTime=7, expireTimes=5):
    try:
        # 过期时长
        day=line.split('#')[-1].split('_')[0].strip().split('-')
        day=datetime.date(int(day[0]),int(day[1]),int(day[2]))

        # 过期次数
        times=int(line.split('#')[-1].split('_')[2].strip())

        if datetime.date.today().__sub__(day).days > expireTime and times>expireTimes:
            return 1
        else:
            return 0
    except ValueError:
        return -1

# 去重，排序
def tidy(nginxConfigFile):
    seeds=[]
    newText=''
    serverPosition=False    # 是否在Socks4Tank upstream内
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=11 and subline[0] != '#' and 'upstream Socks4Tank {' in subline:
                serverPosition=True
            elif len(subline)>=14 and serverPosition==True and subline[0:7] =='server ':
                seeds.append(line)
                line=''
            elif len(subline)>=1 and serverPosition==True and subline[0]=='}':
                # 去重，这里需要先去重，再排序，否则顺序会乱掉
                seeds=set(seeds)
                # 升序排序
                seeds=sorted(seeds,key = lambda x: ( int(x.split('.')[0].split()[-1]), 
                                                    int(x.split('.')[1]), 
                                                    int(x.split('.')[2]),
                                                    int(x.split('.')[3].split(':')[0]),
                                                    int(x.split(':')[1].split(';')[0]) ))
                for seed in seeds:
                    newText+=seed
                serverPosition=False
            newText+=line
        # 写入
        f.seek(0)
        f.truncate()
        f.write(newText)
        f.flush()

# 测试SOCKS4-proxies.txt
# 格式: xxx.xxx.xxx.xxx:xxxx
# 如果没有该文件或没网，则返回None，否则return list
def testSocks4ProxyFromTXT(socks4ProxyTXT):
    proxyDB=ProxyDB()
    proxies=[]
    if os.path.exists(socks4ProxyTXT):
        with open(socks4ProxyTXT,'r+',encoding="utf-8") as f:
            for proxy in f:
                proxy=proxy.strip()
                if proxy[0] != '#':
                    connectStatus=proxyDB.isTorFriendly('socks4',proxy.split(':')[0], int(proxy.split(':')[1]), uploadDB=True)
                    if connectStatus==1 :    # 测试连接成功
                        proxies.append(proxy)
                        print(proxy+" Available!")
                    elif connectStatus==-1: # 没网
                        return None
                    else:
                        print(proxy+" Failed!")
        proxies.sort()   # 如果直接return proxies.sort()会返回NoneType类型
        return proxies
    return None

# 补代理
def seedProxyToNginx(proxys,nginxConfigFile):
    seeds=''
    for proxy in proxys:
        seeds+='\t\tserver '+proxy+';\n'
    newText=''
    serverPosition=False    # 是否在Socks4Tank upstream内
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=11 and subline[0] != '#' and 'upstream Socks4Tank {' in subline:
                serverPosition=True
            elif len(subline)>=1 and serverPosition==True and subline[0]=='}':
                line=seeds+line
                serverPosition=False
            newText+=line
        f.seek(0)
        f.truncate()
        f.write(newText)
        f.flush()

# 检查nginx.conf文件中的代理
def checkSocks4ProxyFromNginx(nginxConfigFile):
    newText= '' # 用于重新写入的暂存文本
    statusNew=False # 代理状态是否有变化，标志
    serverPosition=False    # 是否在Socks4Tank upstream内
    serverCount=0   # 统计有效代理
    pDB=ProxyDB()
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=11 and subline[0] != '#' and 'upstream Socks4Tank {' in subline: # Proxy起始
                serverPosition=True
            elif len(subline)>=1 and serverPosition==True and subline[0]=='}':  # Proxy结束
                serverPosition=False
            elif len(subline)>=14 and serverPosition==True and subline[0:7] =='server ':    # 检查有效代理
                proxy=subline.split()[1][:-1]
                if proxy.split(':')[0] in ('127.0.0.1','47.93.116.53'):
                    connectStatus=pDB.isTorFriendly('socks4',proxy.split(':')[0], int(proxy.split(':')[1]), uploadDB=False)
                else:
                    connectStatus=pDB.isTorFriendly('socks4',proxy.split(':')[0], int(proxy.split(':')[1]), uploadDB=True)
                if connectStatus==1:    # 连接成功
                    serverCount=serverCount+1
                    print("%s TEST OK!"%proxy)
                elif connectStatus==-1: #没网
                    statusNew=False
                    break
                else:   # 连接失败
                    statusNew=True  # 更新状态
                    line='#'+line.rstrip()+'\t#'+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) + '_1\n'
                    print("%s TEST FAULT!"%proxy)
            elif len(subline)>14 and serverPosition==True and subline[1:].strip()[0:7]=='server ':  # 检查无效代理
                proxy=subline[1:].strip().split()[1][:-1]
                if proxy.split(':')[0] in ('127.0.0.1','47.93.116.53'):
                    connectStatus=pDB.isTorFriendly('socks4',proxy.split(':')[0], int(proxy.split(':')[1]), uploadDB=False)
                else:
                    connectStatus=pDB.isTorFriendly('socks4',proxy.split(':')[0], int(proxy.split(':')[1]), uploadDB=True)
                if connectStatus== 1:   # 连接成功
                    statusNew=True
                    serverCount=serverCount+1
                    line=line[0:line.find('#')] + line[line.find('#')+1:].split('#')[0].rstrip()+'\n'   # 去除注释
                    print("%s TEST OK!"%proxy)
                elif connectStatus==-1: #没网
                    statusNew=False
                    break
                else:   # 连接失败
                    statusNew=True
                    if proxy.split(':')[0] in ('127.0.0.1','47.93.116.53'):
                        line=line[:line.rfind('_')+1]+str(int(line[line.rfind('_')+1:])+1)+'\n' # 计数加1
                    else:
                        expire=isExpire(line)   # 检查代理是否过期
                        if expire==1:   # 代理过期
                            line='' # 清除配置文件中的代理
                        elif expire==0: # 没过期
                            line=line[:line.rfind('_')+1]+str(int(line[line.rfind('_')+1:])+1)+'\n' # 计数加1
                    print("%s TEST FAULT!"%proxy)
            newText+=line
        if statusNew == True:   # 如果代理状态有变化，则写入；无变化或没网，不写入
            f.seek(0)
            f.truncate()
            f.write(newText)
            f.flush()
    return serverCount,statusNew


########## 发邮件 ############
# import for Email
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import encoders 
from email.utils import parseaddr 
from email.utils import formataddr 

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))
def sendEmail(content,to_email,subject='test'):
    from_email = PrivateInfo.fromEmail
    from_email_pwd = PrivateInfo.fromEmailPasswd
    smtp_server = "smtp.126.com"

    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = format_addr("%s" %(from_email))
    msg["To"] = format_addr("%s" %(to_email))
    msg["Subject"] = Header(subject, "utf-8").encode()

    try:
        server = smtplib.SMTP_SSL(smtp_server)
        server.connect(smtp_server, 465)
        #server = smtplib.SMTP(smtp_server, 25)
        #server.starttls()
        server.set_debuglevel(1)
        server.login(from_email, from_email_pwd)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")

# 管理Nginx代理
def manageNginxProxy(argument):
    # 检查Nginx代理
    serverCount,statusNew=checkSocks4ProxyFromNginx(argument[2])

    # 代理不足，下载新代理
    if serverCount<5 and not os.path.exists('./SOCKS4-proxies.txt'):
        import urllib.request
        #import urllib.error
        try:
            urllib.request.urlretrieve("https://www.proxyscan.io/download?type=socks4","./SOCKS4-proxies.txt")
        #except urllib.error.HTTPError:
        except Exception:
            pass

    # 从TXT补代理
    proxies=testSocks4ProxyFromTXT('./SOCKS4-proxies.txt')
    if proxies != None:
        seedProxyToNginx(proxies,argument[2])
        os.remove('./SOCKS4-proxies.txt')
        statusNew=True

    if serverCount <5 and proxies ==None: # 代理不足，TXT没有补代理，从数据库写入新代理
        proxies=ProxyDB().getAvailableForTor('socks4',20)
        if proxies != None:
            tempProxies=[]
            for proxy in proxies:
                tempProxies.append(proxy[1]+':'+str(proxy[2]))
                seedProxyToNginx(tempProxies,argument[2])
            statusNew=True

    if statusNew==True:  # 如果原有代理有变化或者有补代理，则重启Nginx
        tidy(argument[2])   # 去重，排序
        os.system("systemctl restart nginx")

    # 代理不足发邮件
    mailContent=''
    if statusNew ==True and serverCount<3 and (proxies==[] or proxies==None):
        mailContent+="Proxy count: "+str(serverCount)+"\n\n"
        mailContent+='\n==========\n'
        mailContent+=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n'
        sendEmail(mailContent,PrivateInfo.toEmail,PrivateInfo.subjectForCheck)

    # 随机检查数据库代理
    ProxyDB().checkTorFriendlyRandom(20)


######## CLI参数控制 #########
def argument():
    argument=sys.argv
    lenArgs=len(argument)
    if lenArgs>=3 and argument[1]=='-c':
        manageNginxProxy(argument)
    elif lenArgs>=3 and argument[1]=='-tT':
        testSocks4ProxyFromTXT(argument[2])
    elif lenArgs>=3 and argument[1]=='--loop':
        import time
        while(True):
            timeStart=time.time()
            manageNginxProxy(argument)
            timeEnd=time.time()
            interval=10800  # 3 hour
            if(timeEnd-timeStart<interval): # 一次循环时间少于interval时间，等待一下
                time.sleep(interval-(timeEnd-timeStart))
    elif lenArgs>=1 or (lenArgs==2 and argument[1]=='-h'):  # 帮助提示
        print('argument:')
        print('\t-c <File>\tCheck Nginx\'s proxy and auto seeds')
        print('\t-tT < TXT File>\tTest TXT\'s proxy and saving to database')
        print('\t-h\t\tShow help')
    else:
        print('Invalid argument')



if __name__ == '__main__':
    try:
        argument()
    except Exception as e:
        error=traceback.format_exc()
        print(error)
        error+='\n\n==========\n'
        error+=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n'
        sendEmail(error,PrivateInfo.toEmail,PrivateInfo.subjectForException)
