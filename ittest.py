import itchat


# 自动回复
@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    return "东小东回复数据:" + msg["Text"]


# 登入
itchat.auto_login()
# 保持运行
itchat.run()

