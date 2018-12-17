import requests


session = requests.Session()
def get(url, headers=None):
    url = url.strip()
    while True:
        try:
            rsp = session.get(url, headers=headers, timeout=4)
            if rsp.status_code != 200:
                print(rsp.status_code, url)
            else:
                return rsp
        except Exception as e:
            print(e)
            pass
            
            
        
