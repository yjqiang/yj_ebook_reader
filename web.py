import requests


session = requests.Session()
caches = {}


def get(url, headers=None, allow_cache=True):
    url = url.strip()
    if url in caches:
        # print('cached', url)
        return caches[url]
    while True:
        try:
            with session.get(url, headers=headers, timeout=4) as rsp:
                if rsp.status_code != 200 and rsp.status_code != 500:
                    pass
                else:
                    if allow_cache:
                        caches[url] = rsp
                    return rsp
        except Exception as e:
            print(e)
            pass
            
            
        
