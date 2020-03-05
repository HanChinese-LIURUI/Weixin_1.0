# encoding:utf-8
import requests
import json
import random

access_token = None  # 在使用前初次声明


def getBaiDuAK():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id' \
           'client_id&client_secret=client_secret'
    r = requests.get(host)
    return r.json()['access_token']


def baiduApi(text):
    global access_token
    url = 'https://aip.baidubce.com/rpc/2.0/unit/bot/chat?access_token=' + access_token
    query = text
    # 下面的log_id在真实应用中要自己生成，可是递增的数字
    log_id = '1111111'
    # 下面的user_id在真实应用中要是自己业务中的真实用户id、设备号、ip地址等，方便在日志分析中分析定位问题
    user_id = '888888'
    # 下面要替换成自己的bot_id，是你的技能ID！！

    if '天气' in text:
        bot_id = '1017418'
    elif '疫情' in text:
        bot_id = '1017421'
    elif '翻译' in text:
        bot_id = '1017420'
    elif '笑话' in text:
        bot_id = '1017419'
    else:
        bot_id = '1017404'
    post_data = '{\"bot_session\":\"\",\"log_id\":\"' + log_id + '\",\"request\":{\"bernard_level\":1,\"client_session\":\"{\\\"client_results\\\":\\\"\\\", \\\"candidate_options\\\":[]}\",\"query\":\"' + query + '\",\"query_info\":{\"asr_candidates\":[],\"source\":\"KEYBOARD\",\"type\":\"TEXT\"},\"updates\":\"\",\"user_id\":\"' + user_id + '\"},\"bot_id\":' + bot_id + ',\"version\":\"2.0\"}'
    # print(json.loads(post_data))
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=post_data.encode('utf-8'), headers=headers)
    try:
        txt = r.json()['result']['response']['action_list'][0]['say']
    except:
        txt = r.json()['result']['response']['action_list'][1]['say']
    return txt


def main(txt):
    try:
        global access_token
        access_token = getBaiDuAK()
        answer = baiduApi(txt)
        print('AI:', answer)
        return answer
    except:
        answer = '我开小差了~~~~'
        return answer


if __name__ == '__main__':
    main()
