from app.utils.myutil.url import getResponse

url = 'http://119.28.155.88:8080/data/api/v1/dataPoint/53/list'
result=getResponse(url)
list=result.get('data')
for i in list:
    sensor=i.get('name')
    str=sensor.split('-')
    sensorid=str[0]
    print(sensorid)




