import json
import os
import statistics
import time

import numpy as np
import requests


def method_name():
    global datas, stock, values, drop, extracted_value

    # 雪球估值
    url = "https://fund.xueqiu.com/index_eva/pe_history/SH000688?day=all&_s=43d632"

    payload = {}
    headers = {
        'dj-version': '7.18',
        'dj-signature': '3f9eb0c71d613eaefd1aa65772d7f664372d457e',
        'dj-device-id': '1',
        'dj-timestamp': '1692164285222',
        'dj-client': 'iOS',
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    EastmoneyFundHeaders = {
        'Cookie': 's=ab1byus95u; cookiesu=701689840624936; device_id=5d59b3de390853c8527c504b48b53e59; xq_a_token=370309a4cfdfe4bc2704623d41715a1159be59eb; xqat=370309a4cfdfe4bc2704623d41715a1159be59eb; xq_r_token=39f1ce2c9cbdf041c8e7e72471a441c2aa4879b2; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY5NDIxOTc3NywiY3RtIjoxNjkxODg4Mjk3MzI5LCJjaWQiOiJkOWQwbjRBWnVwIn0.VJWrwjUhY6Y6kmB0OI-9A4S_iwnElh82nt7Biwht1amhllvkKamnaPxDRdn80oPspUUiMbeeu5e-8IzJYzYKthrb64k7MnCvX53ScuLPBjrXN-xlDdfHK3I4j3AYHIOBt-FQTKkXA-sg6x8VaX-Fw1r3kLwVY2erzRZsFJfHZynT9wW0UjhZncDwgRfeoJKRZZg4HaxPPLMKHJ8gPp2QfACPpJ634prO8z5Apif9hCN4wCE-bCkc-yA15lAbFVzn6aQc-NbdeKfgaBnk-J_DL1frMM61dc7UnmX43TzWtOF-3ArRyaYf2mCDFboU8Tn2E9xlOHwmliu-iaPMfcHV8Q; u=471691888334808; is_overseas=0',
        'User-Agent': 'EMProjJijin/6.2.8 (iPhone; iOS 13.6; Scale/2.00)'
    }
    # 请求参数
    data = {}
    url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={secid}&begin=1692249846430&period=day&type=before&count=-3600&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'
    nmae_url='https://xueqiu.com/query/v1/suggest_stock.json?q={secid}'
    secid_value = 'SH000688'
    url = url.replace('{secid}', secid_value)
    nmae_url = nmae_url.replace('{secid}', secid_value)
    json_response = requests.get(
        url, headers=EastmoneyFundHeaders, data=data).json()
    name = requests.get(
        nmae_url, headers=EastmoneyFundHeaders, data=data).json()['data'][0]['query']
    rows = []
    columns = ['日期', '今开', '当前', '最高', '最高', '最低', '成交量', '成交额', '振幅', '涨跌', '涨跌值', '无']
    if json_response is None:
        print(1)
    datas = json_response['data']['item']
    if len(datas) == 0:
        print(2)
    print(name)
    # 计算中位数
    zhong = []
    for stock in reversed(datas):
        zhong.append(float(stock[5]))  # 获取索引为2的值，并将其转换为浮点数
    zhong.sort()
    median = statistics.median(zhong)
    print('70分位数：' + np.percentile(zhong, 70).__str__())
    print('50分位数：' + np.percentile(zhong, 50).__str__())
    print('30分位数：' + np.percentile(zhong, 30).__str__())
    print('标准差：' + np.std(zhong).__str__())
    print('平均数：' + (sum(zhong) / len(zhong)).__str__())
    # 计算中位数
    price_list = []
    for stock in datas:
        price_list.append(float(stock[5]))  # 获取索引为2的值，并将其转换为浮点数
    # 基金数据
    fund_data = {}
    # 获取当前价格
    fund_data['price'] = price_list[-1]
    price_list.sort()
    chance = np.percentile(price_list, 30)
    danger = np.percentile(price_list, 50)
    # 30分位数
    fund_data['chance'] = chance
    fund_data['danger'] = danger
    # 涨跌幅
    drop = 0
    for stock in reversed(datas):
        extracted_value = float(stock[7])  # 获取索引为8的值，并将其转换为浮点数
        if extracted_value > 0:
            if drop == 0:
                drop = extracted_value
            break
        drop += extracted_value
    rows.append({
        '日期': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        '基金名称': name,
        '涨连续跌幅': round(drop, 2)  # 保存两位小数
    })
    fund_data['data'] = rows
    data_dict = []
    data_dict.append(fund_data)
    check_trading_decision(data_dict)

    drop = 0
    for stock in reversed(datas):
        extracted_value = float(stock[7])  # 获取索引为8的值，并将其转换为浮点数
        if extracted_value > 0:
            break
        drop += extracted_value
        print(extracted_value)


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
                # 买入分界线
                buy_threshold = data_dict['chance']
                # 卖出分界线
                sell_threshold = data_dict['danger']
                standard = buy_threshold

                name = data_dict['data'][0]['基金名称']
                if name in set_data:
                    standard = set_data[name]['基准价']

                if current_price <= buy_threshold:
                    target_price = standard - (standard * buy_percentage)
                    if current_price <= target_price:
                        qmsg_data['买入'].append(name)
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}
                        break
                    target_price = standard + (standard * buy_percentage)
                    if current_price >= target_price:
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}
                elif current_price >= sell_threshold:
                    if sell_threshold > standard:
                        standard = sell_threshold
                    target_price = standard + (standard * sell_percentage)
                    if current_price >= target_price:
                        qmsg_data['卖出'].append(name)
                        set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}
        os.remove('data.json')
    else:
        for data_dict in list_dict:
            # 当前价格
            current_price = data_dict['price']
            # 买入分界线
            buy_threshold = data_dict['chance']
            # 卖出分界线
            sell_threshold = data_dict['danger']

            name = data_dict['data'][0]['基金名称']
            if current_price <= buy_threshold:
                target_price = buy_threshold - (buy_threshold * buy_percentage)
                if current_price <= target_price:
                    qmsg_data['买入'].append(name)
                    set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}
                    break
                target_price = buy_threshold + (buy_threshold * buy_percentage)
                if current_price >= target_price:
                    set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}
            elif current_price >= sell_threshold:
                target_price = sell_threshold + (sell_threshold * sell_percentage)
                if current_price >= target_price:
                    qmsg_data['卖出'].append(name)
                    set_data[name] = {'危险分位': sell_threshold, '机会分位': buy_threshold, '基准价': target_price}

    with open(filename, 'w', encoding='utf-8') as file_obj:
        json.dump(set_data, file_obj, ensure_ascii=False)
    # 方糖推送需要购买的
    req_data1 = {
        'text': '今天需要操作的基金',
        'desp': str(qmsg_data)
    }
    if qmsg_data:
        print(req_data1)


method_name()
