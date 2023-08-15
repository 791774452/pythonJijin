import json
import os
import statistics
import time

import numpy as np
import requests


def method_name():
    global datas, stock, values, drop, extracted_value
    EastmoneyFundHeaders = {
        'User-Agent': 'EMProjJijin/6.2.8 (iPhone; iOS 13.6; Scale/2.00)'
    }
    # 请求参数
    data = {}
    url = 'http://26.push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=3600&_=1691851583454'
    secid_value = '1.000688'
    url = url.replace('{secid}', secid_value)
    json_response = requests.get(
        url, headers=EastmoneyFundHeaders, data=data).json()
    rows = []
    columns = ['日期', '今开', '当前', '最高', '最高', '最低', '成交量', '成交额', '振幅', '涨跌', '涨跌值', '无']
    if json_response is None:
        print(1)
    datas = json_response['data']['klines']
    if len(datas) == 0:
        print(2)
    print(json_response['data']['name'])
    # 计算中位数
    zhong = []
    for stock in reversed(datas):
        values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中

        zhong.append(float(values[2]))  # 获取索引为2的值，并将其转换为浮点数
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
        values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中

        price_list.append(float(values[2]))  # 获取索引为2的值，并将其转换为浮点数

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
    data_dict = []
    data_dict.append(fund_data)
    check_trading_decision(data_dict)

    drop = 0
    for stock in reversed(datas):
        values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中
        extracted_value = float(values[8])  # 获取索引为8的值，并将其转换为浮点数
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
