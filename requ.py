import json
import random
import re
import threading
import time
from io import BytesIO

import matplotlib.pyplot as plt
import requests as rq
from PIL import Image
from pyecharts import options as opts
from pyecharts.charts import Pie

import rbot

Interface_url = str()  # 微信主界面网址

skey, wxsid, wxuin, pass_ticket, \
webwx_data_ticket, webwx_auth_ticket = 0, 0, 0, 0, 0, 0

SyncKey = None
synckey = str()
synckey_val = False  # 初始化完成判断

User_name = str()  # 自己的用户名e
Other_user_name = str()  # 对方的用户名

MemberList, List_public_accounts, Group_list = {}, {}, {}

s = rq.Session()


# 获取UUID
def GET_UUID():
    ulr = '%s/jslogin' % ('https://login.weixin.qq.com')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头
    payload = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new', }

    r = s.post(ulr, headers=headers, params=payload)  # 请求网页
    if not r.status_code == rq.codes.ok:  # 获取响应状态码与内部正确码进行对比
        t = '获取网页错误'
        return 0
    else:
        r.encoding = 'utf-8'
        t = r.text  # 解析网页内容
        UUID = t[50:-2]
        return UUID


# 获取QRCODE
def GET_QRCODE(UUID):
    ulr = 'https://login.wx.qq.com/qrcode/' + UUID

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/80.0.3987.106 Safari/537.36'
    }

    r = s.get(ulr, headers=headers)

    bytes_file = BytesIO()  # 开辟一个二进制模式的buffer，可以像文件对象一样操作它
    bytes_file.write(r.content)  # 将二进制流写入内存
    image = Image.open(bytes_file)  # PIL打开这个内存
    try:
        plt.figure("Image")
        plt.axis('on')  # 关掉坐标轴为 off
        plt.title('QR')  # 图像题目
        plt.imshow(image, animated=True)
        plt.show()
    except RuntimeError:
        pass

    # bytes_file.close()  # 当close方法被调用的时候，这个buffer会被释放


# 扫描监控
def GET_SCAN(UUID):
    global ULR
    print('请扫码')
    while True:
        time.sleep(1)
        ulr = '%s/cgi-bin/mmwebwx-bin/login' % ('https://login.weixin.qq.com')
        headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
        }  # 伪造请求头

        payload = 'loginicon=true&uuid=%s&tip=1&r=%s&_=%s' % (
            UUID, int(-int(time.time()) / 1579), int(time.time()))

        r = s.get(ulr, headers=headers, params=payload)
        t = r.text
        txt = t.split(';')[0]

        if txt == 'window.code=408':
            if U := GET_UUID():
                UUID = U
                GET_QRCODE(UUID)  # 显示二维码
                print('tupian')


        elif txt == 'window.code=201':
            print('请确认登录')

        elif txt == 'window.code=200':
            global Interface_url

            Interface_url = re.findall('window.redirect_uri="(.*?)"', r.text)[0]
            print('已登录')
            regx = r'window.redirect_uri="(\S+)";'
            U = re.search(regx, t).group(1)
            ULR = U[:U.rfind('/')]
            login()
            Init()
            MemberList()
            print(ULR)
            t2 = threading.Thread(target=circulation, args=())
            t2.start()
            plt.close()
            break
        else:
            pass


def circulation():
    while True:
        time.sleep(1)
        if (t := New_message())[0] == '2':
            GET_message()
        else:
            retcode = re.findall('retcode:"(.+)(",)', t[1])[0][0]
            print(retcode)
            if retcode != '0':
                print('意外的值', retcode)
                return 0


# 获取参数
def login():
    global skey, wxsid, wxuin, pass_ticket, webwx_data_ticket, webwx_auth_ticket
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    r = s.get(Interface_url, headers=headers, allow_redirects=False)  # 禁用重定向
    txt = r.text
    try:
        skey = re.findall('<skey>(.+)(</skey>)', txt)[0][0]
        wxsid = re.findall('<wxsid>(.+)(</wxsid>)', txt)[0][0]
        wxuin = re.findall('<wxuin>(.+)(</wxuin>)', txt)[0][0]
        pass_ticket = re.findall('<pass_ticket>(.+)(</pass_ticket>)', txt)[0][0]
        webwx_data_ticket = r.cookies['webwx_data_ticket']
        webwx_auth_ticket = r.cookies['webwx_auth_ticket']
    except IndexError:
        print(txt)


# 初始化,初始化微信首页栏的联系人、公众号等（不是通讯录里的联系人），初始化登录者自己的信息（包括昵称等），初始化同步消息所用的SycnKey
def Init():
    global synckey, SyncKey, User_name
    url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket

    headers = {
        'ContentType': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    payload = {
        'r': int(-time.time() / 1579),
        'pass_ticket': pass_ticket, }

    data = {
        "BaseRequest": {
            "Skey": skey,
            "Sid": wxsid,
            "Uin": wxuin,
            "DeviceID": 'e' + repr(random.random())[2:17],
        },
    }

    r = s.post(url, headers=headers, params=payload, data=json.dumps(data))
    r.encoding = 'utf-8'
    txt = r.json()
    SyncKey = txt['SyncKey']
    Val_list = SyncKey['List']
    synckey = ''
    for i in Val_list:
        synckey += str(i['Key']) + "_" + str(i['Val']) + "|"
    synckey = synckey[:-1]

    User_name = txt['User']['UserName']


# 所有联系人
def test():
    global synckey_val, cook
    url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket

    headers = {
        'Referer': 'https://wx.qq.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    payload = {
        'lang': 'zh_CN',
        'pass_ticket': pass_ticket
    }  # 参数构建

    data = {
        "BaseRequest": {
            "Skey": skey,
            "Sid": wxsid,
            "Uin": wxuin,
            "DeviceID": 'e' + repr(random.random())[2:17],
        },
        'ClientMsgId': int(time.time()),
        'Code': 3,
        'FromUserName': User_name,
        'ToUserName': User_name

    }

    cookies = dict(mm_lang='zh_CN', MM_WX_NOTIFY_STATE='1', MM_WX_SOUND_STATE='1', wxuin=wxuin,
                   webwxuvid='25330f6fcc86a6e48a134af662e2ea818387f7a548414b939fe4bc767cc92321', last_wxuin=wxuin,
                   wxpluginkey='%s' % int(time.time()), refreshTimes='5', wxsid=wxsid,
                   webwx_data_ticket=webwx_data_ticket,
                   webwx_auth_ticket=webwx_auth_ticket, login_frequency='2', wxloadtime='%s_expired' % int(time.time()))

    r = s.post(url, cookies=cookies, headers=headers, params=payload, data=json.dumps(data))

    r.encoding = 'utf-8'
    txt = r.text

    print(txt)


def MemberList():
    global MemberList, List_public_accounts, Group_list
    url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket

    headers = {
        'Referer': 'https://wx.qq.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    payload = {
        'r': ~int(time.time()),  # 时间戳并取反
        'pass_ticket': pass_ticket
    }  # 参数构建

    data = {
        "BaseRequest": {
            "Skey": skey,
            "Sid": wxsid,
            "Uin": wxuin,
            "DeviceID": 'e' + repr(random.random())[2:17],
        }
    }
    r = s.post(url, headers=headers, params=payload, data=json.dumps(data))
    r.encoding = 'utf-8'
    txt = r.json()
    List = txt['MemberList']
    MemberList = {}  # 联系人
    List_public_accounts = {}  # 公众号
    Group_list = {}  # 群

    for i in List:
        # print(i)
        if i['VerifyFlag'] == 0:  # 0是联系人
            if '@@' in (val := i['UserName']):
                tp = (val, i['NickName'], i['Province'], i['City'])
                Group_list[val] = tp
            else:
                tp = (val, i['NickName'], i["RemarkName"], i['Province'], i['City'], i['Sex'], i["Signature"])
                MemberList[val] = tp
        elif i['VerifyFlag'] != 0:  # 非0就是公众号
            tp = (val := i['UserName'], i['NickName'], i['Province'], i['City'])
            List_public_accounts[val] = tp

    print('联系人', len(MemberList))
    print('公众号', len(List_public_accounts))
    print('群', len(Group_list))
    plts()


def New_message():
    url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket
    # url = '%s/synccheck' % 'webpush.wx2.qq.com'
    #    #d = 'https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck' \
    #    #    '?r=1582105914446' \
    #     #   '&skey=%40crypt_6f9668cd_bb5394f389cdbc3c82ec2a6b4f6eaab5' \
    #     #   '&sid=5mn3QVpxQjBhYIdW
    #     #   &uin=2415416838' \
    #     ##   '&deviceid=e129512488592073' \
    #     #   '&synckey=1_717346130%7C2_717346319%7C3_717346073%7C11_717345856%7C19_194%7C201_1582105880%7C206_3%7C1000_1582099585%7C1001_1582099588' \
    #     #   '&_=1582104962583'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头
    payload = {
        'r': int(time.time() * 1000),
        'skey': skey,
        'sid': wxsid,
        'uin': wxuin,
        'deviceid': 'e' + repr(random.random())[2:17],
        'synckey': synckey,
        '_': int(time.time() * 1000)
        # 'pass_ticket': pass_ticket
    }  # 参数构建

    try:
        txt = ' '
        r = s.get(url, headers=headers, params=payload)
        r.encoding = 'utf-8'
        txt = r.text
        selector = re.findall('selector:"(.+)(")', txt)[0][0]
        # print(txt)
        return selector, txt
    except:
        print("链接错误,重新连接")
        return '2', txt


def GET_message():
    global Other_user_name, SyncKey, synckey, synckey_val
    url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket

    headers = {
        'ContentType': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    payload = {
        'sid': wxsid,
        'sky': skey,
        'pass_ticket': pass_ticket
    }  # 参数构建

    data = {
        "BaseRequest": {
            "Skey": skey,
            "Sid": wxsid,
            "Uin": wxuin,
            "DeviceID": 'e' + repr(random.random())[2:17],
        },
        'SyncKey': SyncKey,
        'rr': ~(int(time.time()))
    }

    r = s.post(url, headers=headers, params=payload, data=json.dumps(data))
    r.encoding = 'utf-8'
    txt = r.json()
    # print(txt)
    if txt['BaseResponse']['Ret'] != 0:
        pass
    else:
        Val_list = txt['SyncCheckKey']['List']
        synckey = str()
        for i in Val_list:
            synckey += str(i['Key']) + "_" + str(i['Val']) + "|"
        synckey = synckey[:-1]
        SyncKey = txt['SyncCheckKey']
        if txt['AddMsgCount'] == 0:
            pass
        else:
            Other_user_name = txt['AddMsgList'][0]['FromUserName']
            line = txt['AddMsgList'][0]['Content']
            if line == '启动':
                print('机器人已启动')
                synckey_val = True
            elif line == '停止':
                synckey_val = False
            if synckey_val:
                # MemberList, List_public_accounts, Group_list
                # #(val, i['NickName'], i["RemarkName"], i['Province'], i['City'], i['Sex'], i["Signature"])
                if len(line) < 1:
                    # print('没有问句')
                    return 0
                elif Other_user_name == User_name:
                    # print('是你自己发的')
                    return 0
                elif '@@' in Other_user_name:
                    try:
                        name = Group_list[Other_user_name][1]
                        print('%s：%s' % (name, line))
                        return 0
                    except KeyError:
                        print(Group_list, Other_user_name)
                elif txt['AddMsgList'][0]['MsgType'] != 1:
                    print('不是文字信息')
                    return 0
                else:
                    Name = MemberList[Other_user_name][1]
                    RemarkName = MemberList[Other_user_name][2]
                    print('%s(%s)：%s' % (Name, RemarkName, line))
                    answer = rbot.main(line)
                    Reply_message(answer)


def Reply_message(answer):
    url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg"  # r={}".format(~int(time.time())) + "&lang=zh_CN&pass_ticket=" + pass_ticket

    headers = {
        'ContentType': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }  # 伪造请求头

    timeStamp = int(time.time() * 1e4)
    data = {
        "BaseRequest": {
            "Skey": skey,
            "Sid": wxsid,
            "Uin": wxuin,
            "DeviceID": 'e' + repr(random.random())[2:17],
        },
        "Msg": {
            "Type": 1,
            "Content": '来自百度AI应答：%s' % answer,
            "FromUserName": User_name,
            "ToUserName": Other_user_name,
            "LocalID": timeStamp,
            "ClientMsgId": timeStamp
        },
        'Scene': 0,
    }

    r = s.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf8'))
    r.encoding = 'utf-8'
    txt = r.json()
    # print('Reply_message',txt)


def plts():
    man = list()
    woman = list()
    [man.append(i[1]) for i in MemberList.items() if i[1][5] == 1]
    [woman.append(i[1]) for i in MemberList.items() if i[1][5] == 2]

    p = Pie()
    p.width = '1600px'
    p.add("",
          [['男', len(man)], ['女', len(woman)]],
          radius=["55%", "75%"],
          center=["25%", "50%"],
          label_opts=opts.LabelOpts(
              position="outside",
              formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
              background_color="#eee",
              border_color="#aaa",
              border_width=1,
              border_radius=1,
              rich={
                  "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                  "abg": {
                      "backgroundColor": "#e3e3e3",
                      "width": "100%",
                      "align": "right",
                      "height": 22,
                      "borderRadius": [4, 4, 0, 0],

                  },
                  "hr": {
                      "borderColor": "#aaa",
                      "width": "100%",
                      "borderWidth": 0.5,
                      "height": 0,
                  },
                  "b": {"fontSize": 16, "lineHeight": 33},
                  "per": {
                      "color": "#eee",
                      "backgroundColor": "#334455",
                      "padding": [2, 4],
                      "borderRadius": 2,
                  },
              },
          )
          )
    # p.set_global_opts(title_opts=opts.TitleOpts(title="微信好友结构"))
    # p.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))  # 图中显示数据量

    p.add("",
          [['联系人', len(MemberList)], ['群', len(Group_list)], ['公众号', len(List_public_accounts)]],
          radius=["55%", "75%"],
          center=["75%", "50%"],
          label_opts=opts.LabelOpts(
              position="outside",
              formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
              background_color="#eee",
              border_color="#aaa",
              border_width=1,
              border_radius=1,
              rich={
                  "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                  "abg": {
                      "backgroundColor": "#e3e3e3",
                      "width": "100%",
                      "align": "right",
                      "height": 22,
                      "borderRadius": [4, 4, 0, 0],
                  },
                  "hr": {
                      "borderColor": "#aaa",
                      "width": "100%",
                      "borderWidth": 0.5,
                      "height": 0,
                  },
                  "b": {"fontSize": 16, "lineHeight": 33},
                  "per": {
                      "color": "#eee",
                      "backgroundColor": "#334455",
                      "padding": [2, 4],
                      "borderRadius": 2,
                  },
              },
          ))
    p.set_global_opts(
        title_opts=opts.TitleOpts(title="微信成员结构图"),
        legend_opts=opts.LegendOpts(
            type_="scroll", pos_top="0%", pos_left="10%", orient="horizontal"
        ))

    # 生成到本地网页形式打开，也可自己设置保存成png图片，因为网页的使用更方便，自己按情况使用

    p.render()


if __name__ == "__main__":
    # '''
    if U := GET_UUID():
        UUID = U
        t1 = threading.Thread(target=GET_SCAN, args=(UUID,))
        t1.start()
        GET_QRCODE(UUID)  # 显示二维码

    else:
        print('错误的UUID')
# '''
