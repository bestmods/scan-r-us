import re

from urllib.parse import urlparse

def ConvertToUrl(text: str) -> str:
    url = text
    
    # Make URL friendly.
    url = re.sub(r"[^a-zA-Z0-9\s]", "", url)
    url = url.replace(" ", "-").lower()
    
    return url

def PathHas(url: str, contains: str) -> bool:
    pathName = urlparse(url).path
    
    if contains in pathName:
        return True
    
    return False

def GetPath(url: str) -> str:
    return urlparse(url).path