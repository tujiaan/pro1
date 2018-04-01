import requests

#url = 'http://119.28.155.88:8080/data/api/v1/data/53/gatewaydemo/26/0/getMean/2018-01-01 00:00:00/2018-01-01 00:02:00'
url='http://119.28.155.88:8080/datapoint/53/list'
headers = {
    'FromAgent': 'third',
    'appKey': 'cfjbmqCwh50dShvDGhytug==',
    'appSecret': '9r2OQ+Z2j6QDdupm1mo8yQ=='
}
r = requests.get(url, headers=headers)

# print(r.text)
# print(r.json())
result=r.json()
#result.get('data')
print((result))
url='http://119.28.155.88:8080/control/api/v1/53/gatewaydemo/control'
headers = {
    'FromAgent': 'third',
    'appKey': 'cfjbmqCwh50dShvDGhytug==',
    'appSecret': '9r2OQ+Z2j6QDdupm1mo8yQ=='
}
data={
    'switch':[False]
}
r = requests.post(url, headers=headers,data=data)
