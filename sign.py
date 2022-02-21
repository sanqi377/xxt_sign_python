import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time
import os

user_info = {
    'name': '*****', # 学习通账号
    'pwd': '****', # 学习通密码
    'schoolId': '***', # 学校 Id
    'UA': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}
}

# 所有的课程列表
course_list = [
    "fid="+user_info['schoolId']+"&courseId=222822293&classId=51036384", # 系统分析
]

# 所有课程对应课程名称
course_title = ['系统分析']

# 邮件提醒
def sendMail2(recv_mail, title, content):
    msg_from = '****@qq.com'  # 发送方邮箱
    passwd = '****'  # 填入发送方邮箱的授权码(填入自己的授权码，相当于邮箱密码)
    msg_to = [recv_mail]  # 收件人邮箱
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = title
    msg['From'] = formataddr(["签到提醒助手", msg_from])
    msg['To'] = recv_mail
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print('邮件发送成功')
    except s.SMTPException as e:
        print(e)
    finally:
        s.quit()

# 写入 log
def setlog(msg):
    with open("./log.txt", "a") as f:
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(time_str+" "+str(msg)+"\n")

# 获取网页独立开来方便做异常处理
def getHtml(url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r
    except Exception as e:
        setlog(e)

# 登录
def login():
    global cookie
    setlog("登录成功")
    url = "https://passport2-api.chaoxing.com/v11/loginregister?uname=" + \
        user_info['name']+"&code=" + user_info['pwd']
    r = getHtml(url, headers=user_info['UA'])
    cookie = r.headers["Set-Cookie"]


# 获取活动id
def getActionID(html,title):
    if len(html) == 0:
        return
    res = json.loads(html)["data"]["activeList"]
    if len(res) == 0:  # 没有ID的时候 表示可能是cookie过期了
        login()  # 重新登录
    for a in res:
        if(a["type"] == 2 and a["type"] == 1):
            signIn(a["id"],title)

# 签到
def signIn(activeId,title):
    print(activeId)
    if os.path.exists("id.txt"):
        with open("./id.txt", 'r') as f:
            ids = f.readlines()
        if str(activeId)+"\n" in ids:
            return
    url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId=" + \
        str(activeId)
    headers = {}
    headers.update(user_info['UA'])
    headers.update({"cookie": cookie})
    res = getHtml(url, headers=headers)
    res = res.text
    with open("id.txt", 'a') as f:
        sendMail2("sanqi377@outlook.com", "学习通签到提醒", title+"："+res)
        setlog(str(activeId)+"-"+title+"："+res)
        f.write(str(activeId)+"\n")
    time.sleep(1)

# 获取所有课程的任务界面
def openTask():
    global cookie
    headers = {}
    headers.update(user_info['UA'])
    headers.update({"cookie": cookie})
    for course in course_list:
        for title in course_title:
            r = getHtml(
                "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist?"+course, headers=headers)
            if r == None:
                return
            getActionID(r.text,title)

count = 0
while True:
    openTask()
    count += 1
    setlog("----------"+str(count)+"-----------")
    time.sleep(60)
