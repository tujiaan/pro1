from app.ext import scheduler
from .test import BuiltSensorSendMessage


def scheduler_init_job(app):
    scheduler.add_job('test_scheduler', BuiltSensorSendMessage, trigger='interval', minutes=30, args=[app])
    ######有多个待写入###################
    # scheduler.add_job('online', online, trigger='cron', minute='*/30', args=[app])
