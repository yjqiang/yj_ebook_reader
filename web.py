import requests
from diskcache import Cache


session = requests.Session()
cache = Cache('cache_rsp')
cache.expire()


def get(url, headers=None, allow_cache=True):
    url = url.strip()
    if url in cache:
        # print('cached', url)
        return cache.get(url)
    while True:
        try:
            with session.get(url, headers=headers, timeout=4) as rsp:
                if rsp.status_code == 200 or rsp.status_code == 500:
                    if allow_cache or True:
                        cache.set(url, rsp)
                    return rsp
        except Exception as e:
            print(e)
            pass
                    
