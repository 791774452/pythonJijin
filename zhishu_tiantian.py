import json
import logging
import os
import random
import re
import time
import urllib
import urllib.request
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from aip import AipOcr  # baiduapi
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from interval import Interval

# 将表格直接生成图片

# 定义常量(百度云ORC）
APP_ID = '25110951'
API_KEY = '3DlI5k8XHuZ5B5XgdB7aa8dY'
SECRET_KEY = 'KSgGh6kwk0LNVB7ZG7IeVQW795V4HjiE '

# 初始化AipFace对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


# 获取微信公众号文章中的股债利差值
def get_wechat_pe(sky):
    # 获取韭菜投资学公众号最新文章
    # 目标url
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    # yourcookie=''
    with open("token.txt", "r") as f:  # 打开文件
        token_data = f.readlines()  # 读取文件
    # 使用Cookie，跳过登陆操作
    headers = {
        "Cookie": token_data[1],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        'Content-Type': 'application/json'
    }

    """
    需要提交的data
    以下个别字段是否一定需要还未验证。
    注意修改yourtoken,number
    number表示从第number页开始爬取，为5的倍数，从0开始。如0、5、10……
    token可以使用Chrome自带的工具进行获取
    fakeid是公众号独一无二的一个id，等同于后面的__biz
    """
    data = {
        "token": int(token_data[0]),
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "action": "list_ex",
        "begin": 0,
        "count": "5",
        "query": "",
        "fakeid": 'MzkyODMxMzgwOA==',
        "type": "9",
    }

    # 使用get方法进行提交
    content_json = requests.get(url, headers=headers, params=data).json()
    essay_url = content_json["app_msg_list"][sky]['link']

    imglist = []  # 存放图片链接
    title = ''
    resp = requests.get(essay_url)  # 建立链接
    content = resp.text
    bs = BeautifulSoup(content, 'html.parser')
    title = bs.select('h1')[0].text  # 获取文章标题，每个文章标题基本上放在h2标签中
    title = re.findall('[\u4e00-\u9fa5a-zA-Z0-9]+', title, re.S)  # 只要字符串中的中文，字母，数字，防止出现文件命名不允许的符号
    title = "".join(title)
    for im in bs.select('img'):  # 每张图片都是放在img整个标签里面
        if 'data-src' in im.attrs:  # 我们想要文章里的照片，通过data-src这一个属性来进行进一步筛选
            imglist.append(im['data-src'])
    for img in imglist:
        # urllib.request.urlretrieve(img, '{0}{1}.jpg'.format('./', 1))  # 打开imglist中保存的图片网址，并下载图片保存在本地，format格式化字符串
        urllib.request.urlretrieve(img, '1.jpg')
        with open('1.jpg', 'rb') as fp:
            jpg = fp.read()
            wechat_data = client.general(jpg)
            if wechat_data['words_result'][0]['words'] == "A股整体估值":
                return jpg
    return jpg


def sendMail(message, Subject, sender_show, recipient_show, to_addrs, cc_show=''):
    '''
    :param message: str 邮件内容
    :param Subject: str 邮件主题描述
    :param sender_show: str 发件人显示，不起实际作用如："xxx"
    :param recipient_show: str 收件人显示，不起实际作用 多个收件人用','隔开如："xxx,xxxx"
    :param to_addrs: str 实际收件人
    :param cc_show: str 抄送人显示，不起实际作用，多个抄送人用','隔开如："xxx,xxxx"
    '''
    # 填写真实的发邮件服务器用户名、密码
    user = '1784306049@qq.com'
    password = 'xfwyotvnwohlciif'
    # 邮件内容
    msg = MIMEMultipart()
    msg.attach(MIMEText(message, 'html', _charset="utf-8"))
    # 邮件主题描述
    msg["Subject"] = Subject
    # 发件人显示，不起实际作用
    msg["from"] = sender_show
    # 收件人显示，不起实际作用
    msg["to"] = recipient_show
    # 抄送人显示，不起实际作用
    msg["Cc"] = cc_show
    # 指定图片为当前目录
    fp = open('test.jpg', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    # 定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', '<image>')
    msg.attach(msgImage)
    with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
        # 登录发送邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=to_addrs.split(','), msg=msg.as_string())


def get_fund_k_history(fund_code: str, pz: int = 30) -> pd.DataFrame:
    # 请求头
    EastmoneyFundHeaders = {
        'User-Agent': 'EMProjJijin/6.2.8 (iPhone; iOS 13.6; Scale/2.00)'
    }
    # 请求参数
    data = {}
    url = 'http://26.push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=3600&_=1691851583454'
    guzhi_url='https://fundcomapi.tiantianfunds.com/mm/FundIndex/indexValueTrend?indexCode={secid}&range=10n'
    secid_value = f'{fund_code}'
    url = url.replace('{secid}', secid_value)
    guzhi_url = guzhi_url.replace('{secid}', secid_value.split(".")[1])
    # print('fund_code'+fund_code)
    json_response = requests.get(
        url, headers=EastmoneyFundHeaders, data=data).json()
    guzhi_data = requests.get(guzhi_url).json()['data']
    # 基金数据
    fund_data = {}
    rows = []
    datas = json_response['data']['klines']
    # 计算中位数
    price_list = []
    for stock in datas:
        values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中
        price_list.append(float(values[2]))  # 获取索引为2的值，并将其转换为浮点数
    # 获取当前价格
    fund_data['price'] = price_list[-1]
    # 计算pe分位数
    pe_lsit=[]
    for stock in guzhi_data:
        pe_lsit.append(float(stock['PETTM']))
    current_pe=pe_lsit[-1]
    pe_lsit.sort()
    price_list.sort()
    chance = np.percentile(pe_lsit, 30)
    danger = np.percentile(pe_lsit, 50)
    # pe30分位数
    fund_data['standard'] = np.percentile(price_list, 30) #指数30分位
    fund_data['chance'] = chance
    fund_data['current_pe'] = current_pe
    fund_data['danger'] = danger
    # 涨跌幅
    drop = 0
    for stock in reversed(datas):
        values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中
        extracted_value = float(values[8])  # 获取索引为8的值，并将其转换为浮点数
        if extracted_value > 0:
            if drop == 0:
                drop = extracted_value
            break
        drop += extracted_value
    rows.append({
        '日期': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        '基金名称': json_response['data']['name'],
        '涨连续跌幅': round(drop, 2)  # 保存两位小数
    })
    fund_data['data'] = rows
    return fund_data


def TTMrequests():
    r = requests.get('https://legulegu.com/stockdata/a-ttm-lyr')
    # logging.info(len(r.json()))
    # logging.info(r.text)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')

    # price_box = soup.find("div", "col-md-2 market-title-data-for-index-time")
    # price_box2=soup.find("div", "col-md-4 market-title-data-for-index")
    price_box2 = soup.find("div", attrs={'style': 'color: #25ac22'})
    # price = price_box.text.strip()
    price2 = price_box2.text.strip()
    # desp = price + price2
    # 沪深三百TTM
    r = requests.get('https://legulegu.com/stockdata/a-ttm-lyr')
    # logging.info(len(r.json()))
    # logging.info(r.text)
    # html = r.text
    # soup = BeautifulSoup(html, 'lxml')

    # data = {
    #     'TTM(滚动市盈率)等权平均': desp,
    #     '沪深300滚动市盈率(TTM)等权平均': desp
    # }
    return price2
    # logging.info(desp)


def pe():
    my_headers = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
    ]

    url = "https://danjuanapp.com/djapi/fundx/activity/user/vip_valuation/show/detail?source=jiucai"

    randdom_header = random.choice(my_headers)

    req = urllib.request.Request(url)

    req.add_header("User-Agent", randdom_header)
    req.add_header("GET", url)

    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    data = json.loads(html)['data']
    comment = data['comment']

    # 公众号获取到的数据
    sky = 0

    try:
        while True:
            wechat_data = client.general(get_wechat_pe(sky))
            if wechat_data['words_result'][0]['words'] == "A股整体估值" or sky > 5:
                break
            sky += 1

        # 股债利差估值百分位
        ashares_data = float(wechat_data['words_result'][3]['words'].strip('%'))
    except:
        # requests.post('https://sc.ftqq.com/SCT91472TNR7Z25Qoey6Qq1cfGlm92Rs4.send', data={'text': "我猜你的小饼干过期了！"})
        ashares_data = round(data['ashares_total_percent'] * 100, 2)
    ashares = ""
    zoom_0_10 = Interval(0, 10)
    zoom_10_20 = Interval(10, 20)
    zoom_20_60 = Interval(20, 60)
    zoom_60_70 = Interval(60, 70)
    zoom_70_80 = Interval(70, 80)
    zoom_80_90 = Interval(80, 90)
    zoom_90_100 = Interval(90, 100)
    if ashares_data in zoom_0_10:
        ashares = str(ashares_data) + "%(买入比例:300%)"
    if ashares_data in zoom_10_20:
        ashares = str(ashares_data) + "%(买入比例:200%)"
    if ashares_data in zoom_20_60:
        ashares = str(ashares_data) + "%(买入比例:100%)"
    if ashares_data in zoom_60_70:
        ashares = str(ashares_data) + "%(买入比例:50%)"
    if ashares_data in zoom_70_80:
        ashares = str(ashares_data) + "%(买入比例:0%)"
    if ashares_data in zoom_80_90:
        ashares = str(ashares_data) + "%(买入比例:-300%)"
    if ashares_data in zoom_90_100:
        ashares = str(ashares_data) + "%(全部赎回)"
    try:
        spread = float(wechat_data['words_result'][4]['words'].strip('%'))
    except:
        spread = round(data['spread_td'] * 100, 2)
    xy = ""
    if (spread < 2.72):
        if (spread > 1.65):
            xy = str(spread) + "(偏高)"
        else:
            xy = str(spread) + "(危险)"
    else:
        if (spread < 3.86):
            xy = str(spread) + "(偏低)"
        else:
            xy = str(spread) + "(机会)"
    ttm = float(re.findall(r"\d+\.?\d*", TTMrequests())[0])
    TTM = ""
    if ttm < 45:
        if ttm > 40:
            TTM = str(ttm) + "(可以建仓)"
        else:
            TTM = str(ttm) + "(马上建仓)"
    elif ttm > 45:
        if ttm < 60:
            TTM = str(ttm) + "(观望看看)"
        else:
            TTM = str(ttm) + "(分批卖出)"

    # 获取沪深300前一天PE
    req_pe = urllib.request.Request('https://danjuanapp.com/djapi/index_eva/detail/SH000300')

    req_pe.add_header("User-Agent", randdom_header)
    req_pe.add_header("GET", 'https://danjuanapp.com/djapi/index_eva/detail/SH000300')

    response_pe = urllib.request.urlopen(req_pe)
    html = response_pe.read().decode('utf-8')
    data_pe = json.loads(html)['data']
    if data_pe['pe_percentile'] < 0.3 or data_pe['pb_percentile'] < 0.3 and data_pe['pe'] < 20:
        pe = str(round(data_pe['pe'], 2)) + "(买买买)"
    elif data_pe['pe_percentile'] > 0.7 or data_pe['pb_percentile'] > 0.7 and data_pe['pe'] > 20:
        pe = str(round(data_pe['pe'], 2)) + "(快跑啊)"
    else:
        pe = str(round(data_pe['pe'], 2)) + "(适中)"

    # 当日成交量
    snapshot = requests.get('https://wx.wind.com.cn/indexofficialwebsite/snapshot?indexId=881001.WI&lan=cn')
    volume = str(round(snapshot.json()['Result']['amount'] / 100000000, 2))
    req_data = data[
                   'time'] + "更新    " + comment + "\nA股整体估值分位:" + ashares + " \n" + "股债利差:" + xy + "  TTM:" + TTM + "\n沪深300PE：" + pe + "  成交额:" + volume + "亿"
    return req_data


def get_data():
    # <p>基金累计涨跌幅...</p>
    message = '''
    <p><img src="cid:image"></p>
    <p>股债利差：危险值<1.65 中位值=2.72 机会值>3.86</p>
    <p>沪深300估值：危险值>14.03 中位值=12.33 机会值<10.42</p>
    '''

    Subject = '基金当前涨跌幅'
    # 显示发送人
    sender_show = '1784306049@qq.com'
    # 显示收件人
    recipient_show = '791774452@qq.com'
    # 实际发给的收件人
    to_addrs = '791774452@qq.com'
    # to_addrs = 'Saladbob@outlook.com'

    # 6 位基金代码
    # fund_codes=['000991']
    df = pd.read_excel('指数代码.xlsx', converters={'指数代码': str})
    fund_codes = df.loc[:, ['基金代码']].values.flatten().tolist()  # 读所有行的title以及data列的值，这里需要嵌套列表
    # 调用函数获取基金历史净值数据
    data = []
    data_dict = []
    columns = ['日期', '基金名称', '涨连续跌幅']
    for fund_code in list(set(fund_codes)):
        fund_data = get_fund_k_history(fund_code)
        data.extend(fund_data['data'])
        data_dict.append(fund_data)
    # logging.info(data)

    ttm = pe()
    # 4% 提醒
    check_trading_decision(data_dict)

    # 画图
    df = pd.DataFrame(data)
    df['涨连续跌幅'] = pd.to_numeric(df['涨连续跌幅'], errors='coerce')
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.sort_values(by='涨连续跌幅')

    # plt.rcParams['font.sans-serif']=['SimHei']  # 显示中文字体
    # fig = plt.figure(figsize=(4,3), dpi=400)  # dpi表示清晰度
    # ax = fig.add_subplot(111, frame_on=False)
    # ax.xaxis.set_visible(False)  # hide the x axis
    # ax.yaxis.set_visible(False)  # hide the y axis
    # table(ax, df, loc='center')  # 将df换成需要保存的dataframe即可
    # plt.title(ttm)
    # plt.show()
    # plt.savefig('test.jpg')

    plt.rcParams['font.family'] = 'simhei'
    plt.figure(figsize=(4, 6), dpi=300)
    plt.table(cellText=df.values, rowLabels=None, colLabels=df.columns,
              loc='upper center',
              cellLoc='center',
              rowLoc='center')
    plt.xticks([])
    plt.title(ttm, fontsize=10)
    plt.axis('off')
    # plt.show()
    plt.savefig('test.jpg')
    logging.info(ttm)
    logging.info(df)
    logging.info("=====================================================")
    sendMail(message, Subject, sender_show, recipient_show, to_addrs)


def check_trading_decision(list_dict):
    # 读取data.json 文件
    set_data = {}
    qmsg_data = {'买入': [], '卖出': []}
    filename = 'data.json'
    # 买入提醒百分比
    buy_percentage = 0.04
    # 卖出提醒百分比
    sell_percentage = 0.06
    # 保存需要购买的为json文件,
    if os.path.exists(filename):
        with open(filename) as file_obj:
            set_data = json.load(file_obj)
        if not set_data:
            print()
        else:
            for data_dict in list_dict:
                # 当前价格
                current_price = data_dict['price']
                # 当前pe
                current_pe = data_dict['current_pe']
                # 买入分界线
                buy_threshold = data_dict['chance']
                # 卖出分界线
                sell_threshold = data_dict['danger']
                standard = current_price

                name = data_dict['data'][0]['基金名称']
                if name in set_data:
                    standard = set_data[name]['基准价']

                if current_pe <= buy_threshold:
                    target_price = standard - (standard * buy_percentage)
                    if current_price <= target_price:
                        qmsg_data['买入'].append(name)
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold,
                                          '基准价': current_price - (current_price * buy_percentage)}
                        continue
                    target_price = standard + (standard * buy_percentage)
                    if current_price >= target_price:
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold,
                                          '基准价': current_price + (current_price * buy_percentage)}
                        continue
                    # 基准价不变
                    set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': standard}
                elif current_pe >= sell_threshold:

                    target_price = standard + (standard * sell_percentage)
                    if current_price >= target_price:
                        qmsg_data['卖出'].append(name)
                        # 卖出这基准价位30分位值
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold,
                                          '基准价': current_price + (current_price * buy_percentage)}
                        continue
                    # 基准价不变
                    set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': standard}
    else:
        for data_dict in list_dict:
            # 基准价格30分位
            standard_price = data_dict['standard']
            # 当前pe
            current_pe = data_dict['current_pe']
            # 买入分界线
            buy_threshold = data_dict['chance']
            # 卖出分界线
            sell_threshold = data_dict['danger']

            name = data_dict['data'][0]['基金名称']
            set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': standard_price}

    with open(filename, 'w', encoding='utf-8') as file_obj:
        json.dump(set_data, file_obj, ensure_ascii=False)
    # 方糖推送需要购买的
    req_data1 = {
        'text': '今天需要操作的基金',
        'desp': str(qmsg_data)
    }
    if len(qmsg_data['买入']) + len(qmsg_data['卖出']) > 0:
        logging.info(req_data1)
        requests.post('https://sc.ftqq.com/SCT91472TNR7Z25Qoey6Qq1cfGlm92Rs4.send', data=req_data1)


def getWorkday():
    date = time.strftime('%Y-%m-%d', time.localtime())
    url = "http://timor.tech/api/holiday/info/" + date
    payload = {}
    headers = {
        'Cookie': '',
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)'
    }
    data = requests.request("GET", url, headers=headers, data=payload)
    x = data.json()["type"]["type"]
    if x == 0:
        get_data()
    else:
        logging.info("今天不是工作日")


def getWorkday2():
    date = time.strftime('%Y-%m-%d', time.localtime())
    data = requests.get("http://timor.tech/api/holiday/info/" + date)
    # logging.info(date.json())
    x = data.json()["type"]["type"]
    if x == 0:
        get_data()
    else:
        logging.info("今天不是工作日")
        logging.info("今天不是工作日")


# nohup python3 fund.py >fund.out 2>&1 &
# ps -ef | grep fund
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # get_data()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    try:
        scheduler.add_job(getWorkday, 'cron', day_of_week='0-6', hour=14, minute=50)
        # scheduler.add_job(getWorkday, 'interval', seconds=5)
        # scheduler.add_job(getWorkday, 'interval', seconds=30)
        scheduler.start()
    except Exception:
        inputStr = input("发生异常")
