from flask_restplus import Model, fields

user_model = Model('UserModel', {
    'id': fields.String,
    'disabled': fields.Boolean,
    'contract_tel': fields.String,
    'username': fields.String,
    'email': fields.String,
    'createTime': fields.DateTime,
    'lastTime': fields.DateTime,
    'real_name': fields.String
})
