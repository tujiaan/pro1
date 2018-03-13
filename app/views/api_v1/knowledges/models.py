from flask_restplus import fields

from . import api

knowledges_model=api.model('KnowledgesModel',{
    'id':fields.String,
    'type':fields.String,
    'content':fields.String,
    'title':fields.String
})