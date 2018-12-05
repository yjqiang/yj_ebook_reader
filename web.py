import requests
import sys


def get(url, headers=None):
    url = url.strip()
    while True:
        try:
            rsp = requests.get(url, headers=headers, timeout=2)
            if rsp.status_code != 200:
                print(rsp.status_code, url)
            else:
                print(rsp)
                return rsp
        except:
            pass
            
            
        
