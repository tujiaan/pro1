from flask_restplus.reqparse import RequestParser

knowledge_parser=RequestParser()
knowledge_parser.add_argument('type',type=str,help='知识类型',required=True,location='form')
knowledge_parser.add_argument('content',type=str,help='指示类容',required=True,location='form')
knowledge_parser.add_argument('title',type=str,help='知识标题',required=True,location='form')
knowledge_parser1=RequestParser()
knowledge_parser1.add_argument('type',type=str,help='知识类型',required=False,location='form')
knowledge_parser1.add_argument('content',type=str,help='指示类容',required=False,location='form')
knowledge_parser1.add_argument('title',type=str,help='知识标题',required=False,location='form')