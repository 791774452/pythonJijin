import requests

EastmoneyFundHeaders = {
    'User-Agent': 'EMProjJijin/6.2.8 (iPhone; iOS 13.6; Scale/2.00)'
}
# 请求参数
data = {}
url = 'http://26.push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=120&_=1691851583454'
secid_value = '1.000852'
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
print(datas)
drop = 0
for stock in reversed(datas):
    values = stock.split(",")  # 使用逗号分割字符串并将结果存储在列表中
    extracted_value = float(values[8])  # 获取索引为8的值，并将其转换为浮点数
    if extracted_value > 0:
        break
    drop += extracted_value
    print(extracted_value)
