import urllib.parse
import urllib.request
import uuid


def spider(url, params):
    data = urllib.parse.urlencode(params)
    # res = urllib.request.urlopen(url, data.encode('UTF-8'))
    full_url = urllib.request.Request(url, data.encode())
    response = urllib.request.urlopen(full_url)
    # print(res.status, res.reason) 
    the_page = response.read() 
    print(the_page)


def get_params():
    params = {'serialNumber': '6SDK-EMY-6688-KCXTS',
              'sessionKey': '9cb79cd2ec1e30c8d47c6e3226421bf3',
              'password': '675760',
              'mobiles': ('15021630677'),
              'sendTime': '',
              'addSerial': '',
              # 'smsContent': '[金智容] 您好：{0},你预定的规则已经实现，请及时交易，以免带来损失'.format(query['name']),
              'smsContent': '测试短信发送',
              'smsPriority': 1,
              'smsID': uuid.uuid4().hex
              }
    return params

url = 'http://sdk4report.eucp.b2m.cn:8080/sdk/SDKService?wsdl'
params = get_params()
res = spider(url, params)
print(res)