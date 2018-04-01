import requests
def getResponse(url):
    headers = {
        'FromAgent': 'third',
        'appKey': 'cfjbmqCwh50dShvDGhytug==',
        'appSecret': '9r2OQ+Z2j6QDdupm1mo8yQ=='
    }
    r = requests.get(url, headers=headers)
    result=r.json()
    return result
