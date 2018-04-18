import json
from datetime import datetime, timedelta

import dateutil
from flask import json
from app.ext import mqtt, db
from app.models import Gateway, Sensor, SensorHistory, SensorAlarm, AlarmHandle


def gateway_info(client, userdata, message):
    p=json.loads(message.payload)
    gateway_id = p.get('gateway_id')
    sensors = p.get('sensors')
    with client.app.app_context():
        g = Gateway.query.get(gateway_id)
        if g is None:
            g = Gateway(id=gateway_id)
            db.session.add(g)
            db.session.commit()
        for sensor in sensors:
                sid = sensor.get('id',None)
                if sid is None:
                    continue
                s = Sensor.query.get(sid)
                if s is None:
                    s = Sensor(id=sid)
                    s.online = sensor.get('online', False)
                    if sid>'S1001'and sid<'S1999':
                        s.type = 0
                    elif sid>'S2001'and sid<'S299':
                        s.type = 1
                    elif sid>'S3001'and sid<'S3999':
                        s.type = 3
                        s.max_value = 100
                        s.set_type = 0
                    else: s.type = 4
                    db.session.add(s)
                    db.session.commit()
                    if s not in g.sensors:
                        pass
                    g.sensors.append(s)
                    db.session.commit()
    mqtt.subscribe(f'{gateway_id}/data')
    mqtt.client.message_callback_add(f'{gateway_id}/data',gateway_data)


def gateway_data(client, userdata, message):
    p = json.loads(message.payload)
    list = p.get('sensors')
    time = dateutil.parser.parse(p.get('time'))
    with client.app.app_context():
        for i in list:
            sensorhistory = SensorHistory()
            if i['id']>'S0001'and i['id']<'S0999':
                 sensorhistory.sensor_id = i
                 sensorhistory.time = time
                 sensorhistory.sensor_value = i.get('value')
                 if sensorhistory.sensor_value == 1:
                    sensoralarm = SensorAlarm(sensor_id=i, sensor_type=0, alarm_time=time, gateway_id= Sensor.query.get(i['id']).gateway_id)
                    db.session.add(sensoralarm)
                    db.session.commit()
                    pass
                 else:pass
            elif i.get('id')>='S1001'and i.get('id')<'S1999':
                sensorhistory.sensor_id = i['id']
                sensorhistory.time = time
                sensorhistory.sensor_value = i.get('value')
                if int(sensorhistory.sensor_value) > 50:
                    sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=1, var_type='温度', alarm_value=i.get('value'),unit='℃',alarm_time=time,gateway_id=Sensor.query.get(i['id']).gateway_id )
                    db.session.add(sensoralarm)
                    sm = SensorHistory.query.filter(SensorHistory.sensor_id == i['id']).filter(SensorHistory.time.between(time,time-timedelta(minutes=10)))
                    count = 1
                    for i in sm:
                        if int(i.sensor_value) > 50:
                            count += 1
                    if count>9:
                        db.session.commit()
                    else:
                        pass
                else:
                    pass
            elif i['id']>'S2001'and i['id']<'S2999':
                sensorhistory.sensor_id = i
                sensorhistory.time =time
                sensorhistory.sensor_value = i.get('value')
                if sensorhistory.sensor_value == 1:
                     sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=2,  alarm_time=time, gateway_id= Sensor.query.get(i['id']).gateway_id)
                     db.session.add(sensoralarm)
                     db.session.commit()
                else:
                    pass

            elif i['id'] > 'S3001' and i['id']< 'S3999':
                sensorhistory.sensor_id = i
                sensorhistory.time = time
                sensorhistory.sensor_value = i.get('value')
                if float(sensorhistory.sensor_value)>Sensor.query.get(i).max_value:
                  sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=3, alarm_value=i.get('value'), var_type='电流', unit='A', alarm_time=time, gateway_id=Sensor.query.get(i['id']).gateway_id)
                  db.session.add(sensoralarm)
                  sm = SensorHistory.query.filter(SensorHistory.sensor_id == i['id']).filter(
                      SensorHistory.time.between(time, time - timedelta(seconds=40)))
                  count = 1
                  for i in sm:
                      if float(i.sensor_value) > Sensor.query.get(i).max_value:
                          count += 1
                  if count >= len(sm-1):
                      db.session.commit()
                  else:
                      pass

                  db.session.commit()
                else:pass

            else:
                sensorhistory.sensor_id = i
                sensorhistory.time = time
                sensorhistory.sensor_value = i.get('value')
                if sensorhistory.sensor_value == 1:
                    sensoralarm = SensorAlarm(sensor_id=i['id'], sensor_type=4, alarm_time=time, gateway_id=Sensor.query.get(i['id']).gateway_id)
                    db.session.add(sensoralarm)
                    db.session.commit()
                else:
                    pass
            db.session.add(sensorhistory)
            db.session.commit()
    alarmhandler = AlarmHandle(type='0', handle_type='100', reference_message_id=sensoralarm.id, handle_time=datetime.datetime.now())
    db.session.add(alarmhandler)
    db.session.commit()
    return None, 200



