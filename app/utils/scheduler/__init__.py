from app.ext import scheduler
from .test import BuiltSensorSendMessage, BuiltUserSendMessage, SendMessage


def scheduler_init_job(app):
    scheduler.add_job('test_scheduler1', BuiltSensorSendMessage, trigger='interval', minutes=10, args=[app])
    scheduler.add_job('test_scheduler2', BuiltUserSendMessage, trigger='interval', minutes=10, args=[app])
    scheduler.add_job('test_scheduler3', SendMessage, trigger='interval', minutes=10, args=[app])
    ######有多个待写入###################
    # scheduler.add_job('online', online, trigger='cron', minute='*/30', args=[app])
