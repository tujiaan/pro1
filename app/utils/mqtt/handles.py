import json
from flask import json
from app.ext import mqtt,db
from app.models import Gateway,Sensor
def gateway_info(client, userdata, message):
    p=json.loads(message.payload)
    gateway_id=p.get('gateway_id')
    sensors=p.get('sensors')
    with client.app.app_context():
        g=Gateway.query.get(gateway_id)
        if g is None:
            g=Gateway(id=gateway_id)
            db.session.add(g)
        for sensor in sensors:
                sid=sensor.get('id',None)
                if sid is None:
                    continue
                s=Sensor.query.get(sid)
                if s is None:
                    s=Sensor(id=sid)
                    db.session.add(s)
                    s.online=sensors.get('online',False)
                    if s not in g.sensors:
                        pass
                    g.sensors.append(s)
                    db.session.commit()
    mqtt.subscribe(f'{gateway_id}/data')
    mqtt.client.message_callback_add(p['sensors'][0]['id'],gateway_data)
def gateway_data(client, userdata, message):
    p = json.loads(message.payload)
    gateway_id = p.get('gateway_id')
    sensors = p.get('sensors')
    with client.app.app_context():
        Sensor.query.all()
        pass