#!/usr/bin/python3

import random
import traceback

import myStockConfig    # 配置文件


import datetime
def getPreviousDate(days):     # 获取“days”天前的日期，return日期型
    today=datetime.date.today() 
    oneday=datetime.timedelta(days) 
    return today-oneday  

# 参数：股票代码列表
# return 股票代码与对应股价的字典。股票代码、股价为字符串型
import baostock as bs
def getSpecificStockLatestClosePrice(stockCodes):
    #lg=bs.login()
    bs.login()
    stockPrices={}  # 存储股票代码对应的股价
    for code in stockCodes:
        rs = bs.query_history_k_data_plus(code,"date,close",
            start_date=str(getPreviousDate(30)),    # 起始日期为30天前
            #end_date=str(getYesterday()),  # 默认最后一个交易日
            frequency="d", adjustflag="3"
        )   #frequency="d"取日k线，adjustflag="3"默认不复权
        data_list=[]    # 用于存储查出的股价数据
        while (rs.error_code == '0') & rs.next():  # 查出所有股价
            data_list.append(rs.get_row_data())
        stockPrices[code]=data_list[-1][-1] # 获取最新交易日的股价
    bs.logout()
    return stockPrices

# 参数：盈亏比例（最新价/成本价）
# return True: 可卖出，False: 暂不卖出
# 用于判断某股票的盈亏比例，是否建议卖出
def stock_hold_handle(ratio):
    if(ratio>1.5):  # 如果股价上涨超50%
        if(random.random()<0.5):    # 50%的概率，可卖出
            return True
    elif(ratio>1.4):    # 如果股价上涨超40%
        if(random.random()<0.4):    # 40%的概率，可卖出
            return True
    elif(ratio>1.3):    # 如果股价上涨超30%
        if(random.random()<0.3):    # 30%的概率，可卖出
            return True
    elif(ratio>1.2):    # 如果股价上涨超20%
        if(random.random()<0.2):    # 20%的概率，可卖出
            return True
    elif(ratio>1.1):    # 如果股价上涨超10%
        if(random.random()<0.1):    # 10%的概率，可卖出
            return True
    else:
        return False

# 作用：检查已买入的股票有哪些可卖出，观望的股票哪些可买入
# 参数：
#   stocks_hold: 已买入股票字典
#   stocks_wait: 观望股票字典
# return: 
#   result_string: 文本形式存储检查结果，用于邮件发送正文
#   result_status: 是否有可卖出、可买入的股票，默认没有
def check_stock(stocks_hold, stocks_wait):
    result_string=""    # 文本形式存储检查结果，用于邮件发送正文
    result_status=False # 是否有可卖出、可买入的股票，默认没有
    stocks=list(stocks_hold.keys())+list(stocks_wait.keys())    # 存储所有待查询的股票
    stock_prices_latest=getSpecificStockLatestClosePrice(stocks)   # 获取最新股票价格

    if stock_prices_latest: # 如果获取的值不为空、{}
        result_string+="可卖出的股票：\n"
        for stock in stocks_hold.keys():    # 检查我持有的股票哪些可卖出
            ratio=float(stock_prices_latest[stock]) / float(stocks_hold[stock])   # 计算盈亏比例（最新价/成本价）
            if(stock_hold_handle(ratio)):   # 如果股票可卖出
                result_status=True
                result_string+=stock+"盈亏比例："+str(ratio)+"\n"

        result_string+="可买入的股票：\n"
        for stock in stocks_wait.keys():    # 检查我观望的股票，有哪些可买入
            if(float(stock_prices_latest[stock]) <= float(stocks_wait[stock])):
                if(random.random()<0.5):    # 有50%的概率，建议买入
                    result_status=True
                    result_string+=stock+"\n"
    return result_string,result_status


########## 发邮件 ############
# import for Email
import smtplib
from email.mime.text import MIMEText
from email.header import Header
#from email import encoders 
from email.utils import parseaddr 
from email.utils import formataddr 

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))
def sendEmail(from_email, from_email_password, to_email, content, subject='test'):
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
        server.login(from_email, from_email_password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")



if __name__ == "__main__": 
    try:
        if(random.random()*30 < 1.0):   # 1/30概率，相当于一个月检查一次左右
        #if(True):
            result_string,result_status=check_stock(myStockConfig.stocks_hold, myStockConfig.stocks_wait)
            if(result_status):
                sendEmail(
                    from_email=myStockConfig.email_config["from_email"],
                    from_email_password=myStockConfig.email_config["from_email_password"],
                    to_email=myStockConfig.email_config["to_email"],
                    subject="我的股票检查",
                    content=result_string
                )
    except Exception as e:
        sendEmail(
            from_email=myStockConfig.email_config["from_email"],
            from_email_password=myStockConfig.email_config["from_email_password"],
            to_email=myStockConfig.email_config["to_email"],
            subject="myStock.py异常",
            content=traceback.format_exc()
        )
