# import datetime
#
# from app.ext import db
# from app.models import AskOrder
#
#
# def delete_order(app):
#     with app.app_context():
#         now = datetime.datetime.now()
#         yestoday = now - datetime.timedelta(days=1)
#         o = AskOrder.query.filter(AskOrder.state.in_([0, 1])).filter(AskOrder.create_time < yestoday).all()
#         for i in o:
#             if i.pay:
#                 db.session.delete(i.pay)
#             db.session.delete(i)
#             db.session.commit()

def test(app):
    print('aa')
