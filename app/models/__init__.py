import datetime

from bson import ObjectId

from app.ext import db

def objectid():
    return str(ObjectId())


t_user_role = db.Table(
    'user_role',
    db.Column('user_id', db.String(24), db.ForeignKey('user.id')),
    db.Column('role_id', db.String(24), db.ForeignKey('role.id')),
    db.UniqueConstraint('user_id', 'role_id', name='uix_role_user')
)

t_role_menu = db.Table(
    'role_menu',
    db.Column('role_id', db.String(24), db.ForeignKey('role.id')),
    db.Column('menu_id', db.String(24), db.ForeignKey('menu.id')),
    db.UniqueConstraint('menu_id', 'role_id', name='uix_role_menu')

)

t_facility_knowledge = db.Table(
    'facility_knowledge',
    db.Column('knowledge_id', db.String(24), db.ForeignKey('knowledge.id')),
    db.Column('facility_id', db.String(24), db.ForeignKey('facility.id')),
    db.UniqueConstraint('knowledge_id', 'facility_id', name='uix_facility_knowledge')
)

t_user_home = db.Table(
    'user_home',
    db.Column('user_id', db.String(24), db.ForeignKey('user.id')),
    db.Column('home_id', db.String(24), db.ForeignKey('home.id')),
    db.UniqueConstraint('user_id', 'home_id', name='uix_home_user')
)
t_user_ins = db.Table(
    'user_ins',
    db.Column('user_id', db.String(24), db.ForeignKey('user.id')),
    db.Column('ins_id', db.String(24), db.ForeignKey('ins.id')),
    db.UniqueConstraint('user_id', 'ins_id', name='uix_ins_user')
)



class Ins(db.Model):
    __tablename__ = 'ins'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.String(255), comment='机构类型')
    name = db.Column(db.String(50), comment='机构名称')
    ins_picture = db.Column(db.LargeBinary, comment='机构图片')
    ins_address = db.Column(db.String(255), comment='机构地址')
    note = db.Column(db.Text, comment='备注')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    # administrator_Id = db.Column(db.String(50),comment='管理员?????也用下面的方式吧')
    admin_user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='管理员id')
    community=db.relationship('Community')
    user = db.relationship('User', secondary=t_user_ins,
                          backref=db.backref('f_user', lazy='dynamic') , lazy='dynamic' )




class Community(db.Model):
    __tablename__ = 'community'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(255), comment='社区名')
    community_picture = db.Column(db.LargeBinary, comment='社区图片')
    detail_address = db.Column(db.String(255), comment='详细地址')
    save_distance = db.Column(db.Integer, comment='求救距离')
    eva_distance = db.Column(db.Integer, comment='疏散距离')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    ins_id = db.Column(db.String(24), db.ForeignKey('ins.id'), comment='机构id')
    ins = db.relationship('Ins')
    homes = db.relationship('Home', lazy='dynamic')


class Facility(db.Model):
    __tablename__ = 'facility'
    id = db.Column(db.String(24), default=objectid, primary_key=True)
    facility_id = db.Column(db.String(24), db.ForeignKey('facility_data.id'), comment='设施id')
    facility = db.relationship('FacilityData')
    ins_id = db.Column(db.String(24), db.ForeignKey('ins.id'), comment='机构id')
    ins = db.relationship('Ins')
    count = db.Column(db.Integer, comment='设施数量')
    expire_time = db.Column(db.DateTime, comment='过期时间')
    knowledges = db.relationship('Knowledge', secondary=t_facility_knowledge,
                            backref=db.backref('f_knowledges', lazy='dynamic') , lazy='dynamic')


class FacilityData(db.Model):
    __tablename__ = 'facility_data'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    facility_name = db.Column(db.String(50), comment='设施名')
    facility_picture = db.Column(db.LargeBinary, comment='设施图片')





class Gateway(db.Model):
    __tablename__ = 'gateway'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    useable = db.Column(db.Boolean, default=True, comment='是否可用')
    home_id = db.Column(db.String(24), db.ForeignKey('home.id'), comment='家庭id')
    home = db.relationship('Home')
    sensors = db.relationship('Sensor', lazy='dynamic')


class Home(db.Model):
    __tablename__ = 'home'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(255), comment='家庭名称')
    community_id = db.Column(db.String(24), db.ForeignKey('community.id'), comment='社区id')
    community = db.relationship('Community')

    user = db.relationship('User', secondary=t_user_home,
                          backref=db.backref('f1_user', lazy='dynamic') , lazy='dynamic')
    admin_user_id=db.Column(db.String(24), db.ForeignKey('user.id'), comment='创建者id')
    detail_address = db.Column(db.String(255), comment='家庭地址')
    link_name = db.Column(db.String(50), comment='主人姓名')
    telephone = db.Column(db.String(50), comment='电话号码')
    longitude = db.Column(db.Float(asdecimal=True), comment='经度')
    latitude = db.Column(db.Float(asdecimal=True), comment='纬度')
    alternate_phone = db.Column(db.String(50), comment='备用电话')
    gateways = db.relationship('Gateway', lazy='dynamic')
    sensor=db.relationship('Sensor',lazy='dynamic')


class Knowledge(db.Model):
    __tablename__ = 'knowledge'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.String(50), comment='知识类型   (0.自救 1.逃生 2.灭火 3.新闻 4.其他)')
    content = db.Column(db.Text, comment='知识正文')
    title = db.Column(db.String(50), comment='知识标题')
    facility=db.relationship('Facility',secondary=t_facility_knowledge,
                       backref=db.backref('f_facility',lazy='dynamic') , lazy='dynamic')


class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    p_id = db.Column(db.String(24), db.ForeignKey('menu.id'), comment='父id')
    children = db.relationship("Menu")
    parent = db.relationship("Menu", remote_side=[id])
    label = db.Column(db.String(20), nullable=False, comment='标签')
    level = db.Column(db.SmallInteger, comment='层级')
    type = db.Column(db.SmallInteger,  comment='类型')
    style = db.Column(db.String(50), comment='样式')
    disabled = db.Column(db.Boolean, default=False, comment='是否可用')
    roles = db.relationship('Role', secondary=t_role_menu,
                            backref=db.backref('menu_roles', lazy='dynamic') , lazy='dynamic')
    path = db.Column(db.String(200), comment='和url什么区别???')
    order = db.Column(db.SmallInteger, comment='?????')
    url = db.Column(db.String(200), comment='和path什么区别???')


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    disabled = db.Column(db.Boolean, default=True, comment='是否可用')
    description = db.Column(db.String(60), comment='权限描述')
    users = db.relationship('User', secondary=t_user_role,
                            backref=db.backref('user_roles', lazy='dynamic') , lazy='dynamic')
    menus = db.relationship('Menu', secondary=t_role_menu,
                            backref=db.backref('role_menus', lazy='dynamic') , lazy='dynamic')


class Sensor(db.Model):
    __tablename__ = 'sensor'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    gateway_id = db.Column(db.String(24), db.ForeignKey('gateway.id'), comment='网关id')
    gateway = db.relationship('Gateway')
    sensor_place = db.Column(db.String(255), comment='位置')
    sensor_type = db.Column(db.Integer, comment='传感器类型   (0.烟雾 1.温度 2.燃气 3.电流)')
    start_time=db.Column(db.DateTime,comment='开始时间')
    end_time=db.Column(db.DateTime,comment='结束时间')
    max_value=db.Column(db.Float,comment='阈值')
    alarms_history = db.relationship('SensorAlarm', lazy='dynamic')
    home_id=db.Column(db.String(24),db.ForeignKey('home.id'),comment='家庭id')


class SensorAlarm(db.Model):
    __tablename__ = 'sensor_alarm'

    id = db.Column(db.String(24), default=objectid, primary_key=True, comment='')
    sensor_id = db.Column(db.String(24), db.ForeignKey('sensor.id'), comment='网关id')
    sensor = db.relationship('Sensor')
    alarm_object = db.Column(db.String(50), comment='报警项目')
    alarm_value = db.Column(db.Float, comment='报警数值')
    alarm_time = db.Column(db.DateTime, comment='报警时间')
    confirm_time = db.Column(db.DateTime, comment='确认时间')
    is_timeout = db.Column(db.Boolean, default=False, comment='是否超时')
    user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='确认人id')
    user = db.relationship('User')
    is_confirm = db.Column(db.Boolean, default=False, comment='是否确认')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    disabled = db.Column(db.Boolean, default=False, comment='是否停用   (1、禁用 0、正常)')
    contract_tel = db.Column(db.String(20), comment='用户电话')
    username = db.Column(db.String(20), index=True, comment='用户名)')
    password = db.Column(db.String(32), comment='密码')
    email = db.Column(db.String(60), comment='email')
    salt = db.Column(db.String(50), comment='加密盐')
    createTime = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    lastTime = db.Column(db.DateTime, comment='最后登陆时间')
    registion_id = db.Column(db.String(50), comment='?????')
    real_name = db.Column(db.String(50), comment='姓名')
    roles = db.relationship('Role', secondary=t_user_role,
                            backref=db.backref('user_roles',
                             lazy='dynamic'),lazy='dynamic')
    #home = db.relationship('Home', lazy='dynamic')
    home = db.relationship('Home', secondary=t_user_home,
                         backref=db.backref('f_home', lazy='dynamic') , lazy='dynamic')


    ins = db.relationship('Ins',  secondary=t_user_ins,
                        backref=db.backref('f_ins', lazy='dynamic') , lazy='dynamic')



class UserAlarmRecord(db.Model):
    __tablename__ = 'user_alarm_record'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.Integer, default=0, comment='信息类型,0:消防,1,吧啦吧啦,2吧啦吧啦')
    content = db.Column(db.String(50), comment='')
    community_id = db.Column(db.String(24), db.ForeignKey('community.id'))
    community = db.relationship('Community')
    user_id = db.Column(db.String(24), db.ForeignKey('user.id'), comment='发布人id')
    user = db.relationship('User')
