from app.ext import scheduler
from .test import BuiltSensorSendMessage, BuiltUserSendMessage, SendMessage, OpenSensor, builtusersendmessage


def scheduler_init_job(app):
     scheduler.add_job('test_scheduler1', BuiltSensorSendMessage, trigger='interval', seconds=10, args=[app])
     scheduler.add_job('test_scheduler2', builtusersendmessage, trigger='interval', seconds=10, args=[app])
     #scheduler.add_job('test_scheduler2', BuiltUserSendMessage, trigger='interval', seconds=10, args=[app])
     #scheduler.add_job('test_scheduler3', SendMessage, trigger='interval', seconds=10, args=[app])
     #scheduler.add_job('test_schedule4', OpenSensor, trigger='interval', minutes=10, args=[app])
    # scheduler.start()