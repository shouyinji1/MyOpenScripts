#!/usr/bin/python3

#import os
import traceback
import time
from Email import Email

from nginx import Nginx

if __name__=='__main__':
    #email_config_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/email_config.ini')
    try:
        while(True):
            Nginx('/etc/nginx/nginx.conf').check_socks4()
            time.sleep(7200)    # 间隔2小时

    except Exception as e:
        error=traceback.format_exc()
        print(error)
        error+='\n\n==========\n'
        error+=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n'
        Email().send(content=error, subject='Nginx代理更新程序异常')
