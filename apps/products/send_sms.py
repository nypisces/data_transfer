import json
import urllib.parse
import urllib.request

from redis import Redis


redis = Redis(host='54.223.140.206', port=6379, db=0)


def spider(url, params):
    data = urllib.parse.urlencode(params)
    # res = urllib.request.urlopen(url, data.encode('UTF-8'))
    full_url = urllib.request.Request(url, data.encode())
    response = urllib.request.urlopen(full_url)
    # print(res.status, res.reason) 
    the_page = response.read() 
    print(the_page)


def get_params(query):
    print(query)
    treatys = {
        'AL': '天通现货铝',
        'AUT+D': '黄金T+D',
        'AGT+D': '白银T+D',
        'AU9999': '黄金9999',
        'AU9995': '黄金9995',
        'AU100G': '黄金100G',
        'MAUT+D': '铂金9995',
        'XAGUSD': '天通银',
        'PD': '天通钯金',
        'PT': '天通白金',
        'NI': '天通现货溴',
        'CU': '天通现货铜'
    }
    direction = ''
    if int(query['direction']) == 1:
        direction = '大于'
    elif int(query['direction']) == 2:
        direction = '小于'
    else:
        direction = '等于'
    params = {'cdkey': '6SDK-EMY-6688-KCXTS',
              'sessionKey': '9cb79cd2ec1e30c8d47c6e3226421bf3',
              'password': '9cb79cd2ec1e30c8d47c6e3226421bf3',
              'phone': query['mobile'],
              'sendTime': '',
              'addserial': '',
              'message': '【金智融】 您好：{0} 当前价格是 {1} {2}你预定的价格{3}，\
                            请及时交易，控制风险'.format(treatys.get(query['treaty'], ''), query['sellone'], direction, query['price']),
              # 'message': '【金智容】',
              'seqid': 88998989
              }
    return params


if __name__ == '__main__':
    while True:
        query = redis.rpop('sms')
        if query is not None:
            url = 'http://sdk4report.eucp.b2m.cn:8080/sdkproxy/sendtimesms.action'
            query = json.loads(query.decode())
            params = get_params(query)
            res = spider(url, params)
            print(res)