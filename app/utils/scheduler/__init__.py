from app.ext import scheduler
from .test import test


def scheduler_init_job(app):
    scheduler.add_job('test_scheduler', test, trigger='interval', seconds=10, args=[app])
    # scheduler.add_job('online', online, trigger='cron', minute='*/30', args=[app])
