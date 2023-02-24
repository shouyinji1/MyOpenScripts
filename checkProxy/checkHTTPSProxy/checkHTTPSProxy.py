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

from checkHTTPSProxyConfig import *



# 测试是否有网
import socket
def isConnected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.bing.com", 443))
        return True
    except OSError:
        pass
    return False

# mode:
#   1: 普通测试：两次中有一次curl成功则成功
#   2: 严格测试：两次curl成功则成功，否则失败
#   3: 简单测试
#   4: 快速测试：10秒超时
# Return:   0:连接成功  1:连接失败  -1:没网
def isConnectToHTTPSProxy(proxy,mode=1):
    try:
        if mode==1:
            output=os.popen("curl --connect-timeout 30 -m 30 --proxy %s -k https://www.bing.com"%proxy,'r').read()
            if '<title>Bing</title>' in output:
                return 0
            else:
                output=os.popen("curl --connect-timeout 30 -m 30 --proxy %s -k https://www.baidu.com"%proxy,'r').read()
                if '<!DOCTYPE html>\n<!--STATUS OK-->' and '百度一下，你就知道' in output:
                    return 0
                elif isConnected():
                    return 1
                else:
                    return -1
        if mode==2:
            output=os.popen("curl --connect-timeout 30 -m 30 --proxy %s -k https://www.bing.com"%proxy,'r').read()
            if '<title>Bing</title>' in output:
                output=os.popen("curl --connect-timeout 30 -m 30 --proxy %s -k https://www.baidu.com"%proxy,'r').read()
                if '<!DOCTYPE html>\n<!--STATUS OK-->' and '百度一下，你就知道' in output:
                    return 0
                elif isConnected():
                    return 1
                else:
                    return -1
            elif isConnected():
                return 1
            else:
                return -1
        if mode==3:
            output=os.popen("curl --connect-timeout 30 -m 30 --proxy %s -k https://www.bing.com"%proxy,'r').read()
            if '<title>Bing</title>' in output:
                return 0
            elif isConnected():
                return 1
            else:
                return -1
        if mode==4:
            output=os.popen("curl --connect-timeout 20 -m 30 --proxy %s -k https://www.bing.com"%proxy,'r').read()
            if '<title>Bing</title>' in output:
                return 0
            elif isConnected():
                return 1
            else:
                return -1
    except UnicodeDecodeError:
        return 1

# IP是否属于屏蔽Tor的国家，使用whois查询
def isTorBlockedCountry(ip):
    output=os.popen("whois %s | grep -i Country"%ip,'r').read().splitlines()
    print(output)
    for i in output:
        if i.split(':')[1].strip() in ('RU','CN','IR','BY'):
            # Russia, China, Iron, Belarus
            return True
    return False


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
    serverPosition=False    # 是否在TorOverHTTPS upstream内
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=23 and subline[0] != '#' and 'upstream TorOverHTTPS {' in subline:
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

# 测试HTML中的HTTPS代理
# Free Proxy List - Just Checked Proxy List.html
# 如果没有该文件或没网，则返回None，否则return list
def testHTTPSProxyFromHTML(htmlFile,txtFile='httpsProxy.txt'):
    from bs4 import BeautifulSoup
    proxys=[]
    if os.path.exists(htmlFile):
        with open(htmlFile) as f:
            soup=BeautifulSoup(f,'html.parser')
            soup=soup.find(id="proxylisttable").tbody
            soup=soup.find_all('tr')
            with open(txtFile,'w') as proxyFile:
                for tr in soup:
                    tr=tr.find_all('td')
                    if tr[6].text == 'yes':
                        proxy=tr[0].text+':'+tr[1].text
                        connectStatus=isConnectToHTTPSProxy(proxy,4)
                        if connectStatus==0:    # 测试连接成功
                            proxys.append(proxy)
                            print(proxy+" Available!")
                            proxyFile.write(proxy+"\n")
                        elif connectStatus==-1: # 没网
                            return None
        proxys.sort()   # 如果直接return proxys.sort()会返回NoneType类型
        return proxys
    return None

# 测试HTTPSProxy.txt
# 格式: xxx.xxx.xxx.xxx:xxxx
# 如果没有该文件或没网，则返回None，否则return list
def testHTTPSProxyFromTXT(httpsProxyTXT):
    proxys=[]
    if os.path.exists(httpsProxyTXT):
        with open(httpsProxyTXT,'r+',encoding="utf-8") as f:
            for proxy in f:
                proxy=proxy.strip()
                try:
                    if proxy[0] != '#':
                        connectStatus=isConnectToHTTPSProxy(proxy,4)
                        if connectStatus==0:    # 测试连接成功
                            if isTorBlockedCountry(proxy.split(":")[0])==False: # 非屏蔽Tor的国家
                                proxys.append(proxy)
                                print(proxy+" Available!")
                        elif connectStatus==-1: # 没网
                            return None
                except Exception:
                    pass
        proxys.sort()   # 如果直接return proxys.sort()会返回NoneType类型
        return proxys
    return None

# 补代理
def seedProxyToNginx(proxys,nginxConfigFile):
    seeds=''
    for proxy in proxys:
        seeds+='\t\tserver '+proxy+';\n'
    newText=''
    serverPosition=False    # 是否在TorOverHTTPS upstream内
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=23 and subline[0] != '#' and 'upstream TorOverHTTPS {' in subline:
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
def checkHTTPSProxyFromNginx(nginxConfigFile):
    newText= '' # 用于重新写入的暂存文本
    statusNew=False # 代理状态是否有变化，标志
    serverPosition=False    # 是否在TorOverHTTPS upstream内
    serverCount=0   # 统计有效代理
    errorProxy=[]   # 存储失效代理
    with open(nginxConfigFile,'r+',encoding="utf-8") as f:
        for line in f:
            subline=line.strip()
            if len(subline)>=23 and subline[0] != '#' and 'upstream TorOverHTTPS {' in subline: # Proxy起始
                serverPosition=True
            elif len(subline)>=1 and serverPosition==True and subline[0]=='}':  # Proxy结束
                serverPosition=False
            elif len(subline)>=14 and serverPosition==True and subline[0:7] =='server ':    # 检查有效代理
                proxy=subline.split()[1][:-1]
                connectStatus=isConnectToHTTPSProxy(proxy,3)
                if connectStatus== 0 :   # 连接成功
                    serverCount+=1
                    print("%s TEST OK!"%proxy)
                elif connectStatus==-1: #没网
                    statusNew=False
                    break
                else:   # 连接失败
                    statusNew=True
                    line='#'+line.rstrip()+'\t#'+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()) + '_1\n'
                    errorProxy.append(proxy)
                    print("%s TEST FAULT!"%proxy)
            elif len(subline)>14 and serverPosition==True and subline[1:].strip()[0:7]=='server ':  # 检查无效代理
                proxy=subline[1:].strip().split()[1][:-1]
                connectStatus=isConnectToHTTPSProxy(proxy,3)
                if connectStatus== 0 :
                    statusNew=True
                    serverCount+=1
                    line=line[0:line.find('#')] + line[line.find('#')+1:].split('#')[0].rstrip()+'\n'   # 去除注释
                    print("%s TEST OK!"%proxy)
                elif connectStatus==-1: #没网
                    statusNew=False
                    break
                else:
                    if isExpire(line,PrivateInfo.expireTime)==1:  # 如果代理过期失效就删除
                        line=''
                    else:   # 无效次数+=1
                        line=line[:line.rfind('_')+1]+str(int(line[line.rfind('_')+1:])+1)+'\n'
                    errorProxy.append(proxy)
                    print("%s TEST FAULT!"%proxy)
            newText+=line
        if statusNew == True:   # 如果代理状态有变化，则写入；无变化或没网，不写入
            f.seek(0)
            f.truncate()
            f.write(newText)
            f.flush()
    return errorProxy,serverCount,statusNew


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
    errorProxy,serverCount,statusNew=checkHTTPSProxyFromNginx(argument[2])

    # 代理不足，下载新代理
    #if serverCount<=3 and not os.path.exists('./HTTPS-proxies.txt'):
    #    import urllib.request
    #    import urllib.error
    #    try:
    #        urllib.request.urlretrieve("https://www.proxyscan.io/download?type=https","./HTTPS-proxies.txt")
    #    except urllib.error.HTTPError:
    #        pass

    # 补代理，补完删源HTML
    proxys=testHTTPSProxyFromHTML('./Free Proxy List - Just Checked Proxy List.html')
    if proxys != None:
        seedProxyToNginx(proxys,argument[2])
        os.remove('./Free Proxy List - Just Checked Proxy List.html')
    # 从TXT补代理
    proxys=testHTTPSProxyFromTXT('./HTTPS-proxies.txt')
    if proxys != None:
        seedProxyToNginx(proxys,argument[2])
        os.remove('./HTTPS-proxies.txt')

    if statusNew==True or proxys not in ([],None):  # 如果原有代理有变化或者有补代理，则重启Nginx
        tidy(argument[2])   # 去重，排序
        os.system("systemctl restart nginx")

    # 代理不足发邮件
    mailContent=''
    if statusNew ==True and serverCount<3 and (proxys==[] or proxys ==None):
        mailContent+="Proxy count: "+str(serverCount)+"\n\n"
        mailContent+='errorProxy:\n'
        for p in errorProxy:
            mailContent+=p+'\n'
        mailContent+='\n==========\n'
        mailContent+=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n'
        sendEmail(mailContent,PrivateInfo.toEmail,PrivateInfo.subjectForCheck)


######## CLI参数控制 #########
def argument():
    argument=sys.argv
    if argument[1]=='-c':
        manageNginxProxy(argument)
    elif argument[1]=='-tH':
        testHTTPSProxyFromHTML(argument[2],argument[3])
    elif argument[1]=='-tT':
        testHTTPSProxyFromTXT(argument[2])
    elif argument[1]=='-h':
        print('argument:')
        print('\t-c <File>\tCheck Nginx\'s proxy and auto seeds')
        print('\t-tH <HTML File> <TXT File>\tTest HTML\'s proxy')
        print('\t-tT < TXT File>\tTest TXT\'s proxy')
        print('\t-h\tshow help')
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
