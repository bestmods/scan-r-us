import re

def LimitText(text: str, limit = 10):
    if text is None:
        return None
    
    append = "..." if len(text) > limit else ""
    
    return text[:limit] + append

def FindShortDesc(text: str, min = 20) -> str | None:
    ret = re.sub(r"[^a-zA-Z0-9_/\-\.\s]", "", text)
    ret = re.sub(r"([^a-zA-Z0-9\s])\1+", r"\1", ret)
    ret = ret.strip()
    
    if len(ret) < min:
        return None
    
    return ret