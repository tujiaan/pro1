from app.ext import mqtt
from.handles import gateway_info
app=None
def mqtt_register(a):
    mqtt.client.app=a
    mqtt.subscribe('gatewayinfo')
    mqtt.client.message_callback_add('gatewayinfo', gateway_info)