from flask_restplus.reqparse import RequestParser

useralarmrecord_parser=RequestParser()
useralarmrecord_parser.add_argument('type',type=int,help='报警信息类型',required=True,location='form')
useralarmrecord_parser.add_argument('content',type=str,help='报警内容',required=True,location='form')
useralarmrecord_parser.add_argument('user_id',type=str,help='用户id',required=True,location='form')
useralarmrecord_parser.add_argument('community_id',type=str,help='社区id',required=True,location='form')

useralarmrecord1_parser=RequestParser()
useralarmrecord1_parser.add_argument('type',type=int,help='报警信息类型',required=False,location='form')
useralarmrecord1_parser.add_argument('content',type=str,help='报警内容',required=False,location='form')
useralarmrecord1_parser.add_argument('user_id',type=str,help='用户id',required=False,location='form')
useralarmrecord1_parser.add_argument('community_id',type=str,help='社区id',required=False,location='form')
