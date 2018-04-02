from app.utils.myutil.url import getResponse


def test(self):
        url = '119.28.155.88:8080/data/api/v1/dataPoint/53/list'
        result=getResponse(url)
        print (result)
        return None



