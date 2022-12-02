import requests

def download(url):
    r = requests.get(url)
    return r.content