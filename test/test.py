import asyncio
from time import time

import aiohttp as aiohttp

d = {'title': 'aaa', 'symptom': 'asdasd', 'remark': 'ssss', 'images': ['image1', 'image2', 'image3']}
url = 'http://127.0.0.1:5002/userapi/v1/user/case/'
h = {
    'jwt': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJkb2N0b3JfaWQiOm51bGwsImV4cCI6MTUyMTQ1MTU0NiwibmJmIjoxNTE4ODU5NDg2LCJpYXQiOjE1MTg4NTk1NDZ9.CBiTfuXDbML77uaTzQZx9QCqC3NiB9dFwHSfKsMi8zT0rPoFP7xsF3LsWm_hg8o3QOdfjX_AEvHYvGJtDJ0iFAbn4NpxCON-11s7_pQKSUuTF7FFWPPDeTH2CzHO7Py7V2QN_xfmhn1bSnputs-pjq0SRTY0NQdVd7JYkg8bvCqQ_2_tWxZnUKfbrzMW2eDo9g_Bt271K5FMbBHHsQ1qCPcGDlrH_vlBphsASnxvL8bz2vC5GiDxOz4DN3YZ2766MDoCDWx7BD_SrFBzgTnNMpKar8YAYYQVF-f1uMfkzHFkSzCzufFPE0Vv4oEWmZcmAQJntk-2e1xJrXBarnLVqg'}


async def get_cbxx():
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=d, headers=h) as _:
            print(await _.text())


print(time())
task = [get_cbxx() for i in range(0, 1000)]
print(time())
loop = asyncio.get_event_loop()
print(time())
loop.run_until_complete(asyncio.wait(task))
print(time())
