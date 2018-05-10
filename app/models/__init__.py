import datetime

from bson import ObjectId

from app.ext import db


def objectid():
    return str(ObjectId())


t_org_equ = db.Table(
    'org_equ',
    db.Column('org_id', db.ForeignKey('organization.id'), index=True),
    db.Column('equ_id', db.ForeignKey('equipment.id'), index=True),
    db.UniqueConstraint('org_id', 'equ_id', name='unix_org_equ')
)
t_user_org = db.Table(
    'user_org',
    db.Column('user_id', db.ForeignKey('user.id'), index=True),
    db.Column('org_id', db.ForeignKey('organization.id'), index=True),
    db.UniqueConstraint('user_id', 'org_id', name='unix_user_org')
)
t_user_work = db.Table(
    'user_work',
    db.Column('user_id', db.ForeignKey('user.id'), index=True),
    db.Column('workorder_id', db.ForeignKey('workorder.id'), index=True),
    db.UniqueConstraint('user_id', 'workorder_id', name='unix_user_work')
)


class Alarm(db.Model):
    __tablename__ = 'alarm'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    type = db.Column(db.Integer)
    value = db.Column(db.Float)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    if_confirm = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.Text)
    node_id = db.Column(db.String(24), db.ForeignKey('node.id'))
    node = db.relationship('Node', backref=db.backref('f1_node', lazy='dynamic'), lazy='joined')


class Consume(db.Model):
    __tablename__ = 'consume'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    reporter_id = db.Column(db.String(24))
    report_time = db.Column(db.DateTime)
    consume_name = db.Column(db.String(32))
    count = db.Column(db.Integer)
    work_id = db.Column(db.String(24), db.ForeignKey('workorder.id'))
    work = db.relationship('Workorder', backref=db.backref('f_worker', lazy='dynamic'), lazy='joined')


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.Integer)
    picture = db.Column(db.String(200))
    note = db.Column(db.Text)
    status = db.Column(db.Integer)
    orgs = db.relationship('Organization', secondary='org_equ', backref=db.backref('f_equi_orgs', lazy='dynamic'), lazy='dynamic')


class Node(db.Model):
    __tablename__ = 'node'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.Integer)
    status = db.Column(db.Integer)
    value = db.Column(db.Float)
    note = db.Column(db.Text)
    equ_id = db.Column(db.String(24), db.ForeignKey('equipment.id'), index=True)
    equ = db.relationship('Equipment', backref=db.backref('f_node_equ', lazy='dynamic'), lazy='joined')


class Organization(db.Model):
    __tablename__ = 'organization'

    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    name = db.Column(db.String(50))
    address = db.Column(db.String(255))
    picture = db.Column(db.String(200))
    telephone = db.Column(db.String(20))
    admin_user_id = db.Column(db.String(24), db.ForeignKey('user.id'))
    longitude = db.Column(db.Numeric(10, 7))
    latitude = db.Column(db.Numeric(10, 7))
    note = db.Column(db.Text)

    users = db.relationship('User', secondary='user_org', backref=db.backref('f_org_user', lazy='dynamic'), lazy='dynamic')


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    name = db.Column(db.String(32))
    disabled = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(60))


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    username = db.Column(db.String(24))
    real_name = db.Column(db.String(50))
    password = db.Column(db.String(32))
    email = db.Column(db.String(60))
    user_tel = db.Column(db.String(20))
    salt = db.Column(db.String(50))
    disabled = db.Column(db.Boolean, nullable=False, default=False)
    createtime = db.Column(db.DateTime, default=datetime.datetime.now)
    lastTime = db.Column(db.DateTime)
    works = db.relationship('Workorder', secondary='user_work', backref=db.backref('f_user_work', lazy='dynamic'), lazy='joined')


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    user_id = db.Column(db.String(24), db.ForeignKey('user.id'), index=True)
    role_id = db.Column(db.String(24), db.ForeignKey('role.id'), index=True)
    disable = db.Column(db.Boolean, nullable=False, default=False)
    role = db.relationship('Role', backref=db.backref('f1_role', lazy='dynamic'), lazy='joined')
    user = db.relationship('User', backref=db.backref('f1_user', lazy='dynamic'), lazy='joined')


class Workorder(db.Model):
    __tablename__ = 'workorder'

    id = db.Column(db.String(24), default=objectid,  primary_key=True)
    createperson_id = db.Column(db.String(24), db.ForeignKey('user.id'))
    equ_id = db.Column(db.String(24), db.ForeignKey('equipment.id'))
    alarm_type = db.Column(db.Integer)
    passperson_id = db.Column(db.String(255), db.ForeignKey('user.id'))
    notiperson_id = db.Column(db.String(255), db.ForeignKey('user.id'))
    mailtopass = db.Column(db.Boolean, nullable=False, default=False)
    mailtonoti = db.Column(db.Boolean, nullable=False, default=False)
    smstopass = db.Column(db.Boolean, nullable=False, default=False)
    smstonoti = db.Column(db.Boolean, nullable=False, default=False)
    problem = db.Column(db.Text)
    picture = db.Column(db.String(200))


class Currentrecord(db.Model):
    __tablename__ = 'currentrecord'

    id = db.Column(db.String(24), default=objectid, primary_key=True)
    currentperson_id = db.Column(db.String(24), db.ForeignKey('user.id'))
    currenttime = db.Column(db.DateTime, default=datetime.datetime.now)
    currentcontent = db.Column(db.Text)
    attachment = db.Column(db.String(200))
    work_id = db.Column(db.String(24), db.ForeignKey('workorder.id'))
    work = db.relationship('Workorder', backref=db.backref('f1_worker', lazy='dynamic'), lazy='joined')











