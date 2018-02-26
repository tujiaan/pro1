from datetime import date

from flask_restplus.reqparse import RequestParser
facility_parser=RequestParser()
facility_parser.add_argument('facility_id' , type=str, help='设施id', required=True, location='form' )
facility_parser.add_argument('ins_id' , type=str, help='机构id', required=True, location='form' )
facility_parser.add_argument('count' , type=int,help='设施数量', required=True, location='form' )
facility_parser.add_argument('expire_time', type=date, help='过期日期', required=True, location='form' )



facility_parser1=RequestParser()
#facility_parser1.add_argument('facility_id' , type=str, help='设施id', required=True, location='form' )
facility_parser1.add_argument('ins_id' , type=str, help='机构id', required=True, location='form' )
facility_parser1.add_argument('count' , type=int,help='设施数量', required=False, location='form' )
facility_parser1.add_argument('expire_time', type=date, help='过期日期', required=False, location='form' )
