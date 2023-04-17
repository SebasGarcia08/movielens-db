import requests

def download(url: str) -> None:
    requests.get(url)