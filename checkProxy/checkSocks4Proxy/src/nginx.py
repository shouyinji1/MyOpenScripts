#!/usr/bin/python3

import os
from proxy_db import ProxySocks4
from Email import Email

class Nginx:
    def __init__(self, config_path):
        self.config_path=config_path

    def check_socks4(self):
        newText= '' # 用于重新写入的暂存文本
        serverPosition=False    # 是否在Socks4Tank upstream内
        with open(self.config_path,'r+',encoding="utf-8") as f:
            for line in f:  # 清空代理
                subline=line.strip()
                if len(subline)>=11 and subline[0] != '#' and 'upstream Socks4Tank {' in subline: # Proxy起始
                    serverPosition=True
                elif len(subline)>=1 and serverPosition==True and subline[0]=='}':  # Proxy结束
                    line=self.seed_to_line()+line
                    serverPosition=False
                elif len(subline)>=14 and serverPosition==True and subline[0:7] =='server ' and '#' not in subline:    # 是没有注释的代理
                    line='' # 清空代理所在的行
                newText+=line
            # 写入文件
            f.seek(0)
            f.truncate()
            f.write(newText)
            f.flush()
        os.system("systemctl restart nginx")

    def seed_to_line(self):
        line=''
        quantity = 30    # 获取的代理条数大于等于30
        proxies=ProxySocks4().get_available_foreign_proxies(quantity)
        if proxies != None and proxies !=[]:
            #if len(proxies) < quantity: self.sendEmail('代理不足')
            if len(proxies) < 10: 
                Email().send(subject='代理不足',content=str(proxies))
            for proxy in proxies:
                line+='\t\tserver '+proxy['ip']+':'+str(proxy['port'])+';\n'
        else:
            Email().send(subject='没有代理了',content='没有代理了，没有代理了，没有代理了，没有代理了，没有代理了')
        return line



if __name__=='__main__':
    pass
