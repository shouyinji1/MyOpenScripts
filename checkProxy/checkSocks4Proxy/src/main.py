#!/usr/bin/python3

#import os

from nginx import Nginx

if __name__=='__main__':
    #email_config_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/email_config.ini')
    Nginx('/etc/nginx/nginx.conf').check_socks4()
