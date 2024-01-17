#!/usr/bin/python3

import configparser
import os

########## 发邮件 ############
# import for Email
import smtplib
from email.mime.text import MIMEText
from email.header import Header
#from email import encoders 
from email.utils import parseaddr 
from email.utils import formataddr 

class Email:
    def __init__(self):
        self.conf = configparser.ConfigParser()
        email_config_path=os.path.join(os.path.split(os.path.realpath(__file__))[0], '../config/email_config.ini')
        self.conf.read(email_config_path, encoding='UTF-8')

    def format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, "utf-8").encode(), addr))
    def send(self, content, subject='test'):
        from_email=self.conf['Email_Configuration']["from_email"],
        from_email=''.join(from_email)
        from_email_password=self.conf['Email_Configuration']["from_email_password"],
        from_email_password=''.join(from_email_password)
        to_email=self.conf['Email_Configuration']["to_email"],
        to_email=''.join(to_email)

        smtp_server = "smtp.126.com"

        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = self.format_addr("%s" %(from_email))
        msg["To"] = self.format_addr("%s" %(to_email))
        msg["Subject"] = Header(subject, "utf-8").encode()

        try:
            server = smtplib.SMTP_SSL(smtp_server)
            server.connect(smtp_server, 465)
            #server = smtplib.SMTP(smtp_server, 25)
            #server.starttls()
            server.set_debuglevel(1)
            server.login(from_email, from_email_password)
            server.sendmail(from_email, [to_email], msg.as_string())
            server.quit()
        except smtplib.SMTPException:
            print ("Error: 无法发送邮件")


if __name__=='__main__':
    Email().send('test')