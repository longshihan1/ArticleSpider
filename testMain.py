#coding:utf-8
import sys
import smtplib
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header
#构造纯文本邮件内容
msg = MIMEText('hello,测试学习','plain','utf-8')
#发送者邮箱
sender = 'longshihan@163.com'
#发送者的登陆用户名和密码
user = 'longshihan@163.com'
password = '577093937'
#发送者邮箱的SMTP服务器地址
smtpserver = 'smtp.163.com'
#接收者的邮箱地址
receiver = ['577093937@qq.com'] #receiver 可以是一个list

smtp = smtplib.SMTP() #实例化SMTP对象
smtp.connect(smtpserver,25) #（缺省）默认端口是25 也可以根据服务器进行设定
smtp.login(user,password) #登陆smtp服务器
smtp.sendmail(sender,receiver,msg.as_string()) #发送邮件 ，这里有三个参数
'''
login()方法用来登录SMTP服务器，sendmail()方法就是发邮件，由于可以一次发给多个人，所以传入一个list，邮件正文
是一个str，as_string()把MIMEText对象变成str。
'''
smtp.quit()