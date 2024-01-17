#!/usr/bin/python3

#import os

import sys
sys.path.append('./src/')
# 参考：https://blog.csdn.net/qq_39691492/article/details/120438627

from src.nginx import Nginx

if __name__=='__main__':
    #email_config_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/email_config.ini')
    Nginx('/etc/nginx/nginx.conf').check_socks4()