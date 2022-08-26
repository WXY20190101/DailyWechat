from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import json

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")

app_id = os.getenv["APP_ID"]
app_secret = os.getenv["APP_SECRET"]
template_id = os.getenv["TEMPLATE_ID"]

def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日 %H时%M分 ")+ a


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_weather(city):
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['high']), math.floor(weather['low']), weather['city'],weather['airQuality'],weather['wind']


def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

f = open("./users_info.json", encoding="utf-8")
js_text = json.load(f)
f.close()
data = js_text['data']
num = 0
for user_info in data:
    born_date = user_info['born_date']
    birthday = born_date[5:]
    city = user_info['city']
    user_id = user_info['user_id']
    name=' 【'+user_info['user_name'].upper()+'】 '
    
    wea, tem_high, tem_low, tem_city, air, wind= get_weather(city)

    data = dict()
    data['time'] = {'value': get_time(), 'color':'#470024'}
    data['words'] = {'value': get_words(), 'color': get_random_color()}

    data['weather'] = {'value': wea, 'color': '#002fa4'}
    data['city'] = {'value': tem_city, 'color': get_random_color()}
    data['tem_high'] = {'value': tem_high, 'color': '#D44848'}
    data['tem_low'] = {'value': tem_low, 'color': '#01847F'}
    data['born_days'] = {'value': get_count(born_date), 'color': get_random_color()}
    data['birthday_left'] = {'value': get_birthday(birthday), 'color': get_random_color()}
    data['air'] = {'value': air, 'color': get_random_color()}
    data['wind'] = {'value': wind, 'color': get_random_color()}
    data['name'] = {'value': name, 'color': get_random_color()}
    
    res = wm.send_template(user_id, template_id, data,'https://froan.cn')
    print(res)
    num += 1
res = wm.send_text('oEqYm6sOo2VdJdl4dGh40OrYYrKM', f'共计分发{num}卡片信息')
print(res)
