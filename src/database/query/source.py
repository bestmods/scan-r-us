from ..connection import Source

def AddSource(url: str, name: str) -> Source:
    src = Source.create(url = url, name = name)
    
    src.save()
    
    return src

def GetSource(url: str) -> (Source):
    src = Source.get_by_id(url)
    
    return src

def GetSources(limit: int = 10) -> list:
    srcs = Source.select().limit(limit)
    
    return list(srcs), None

def UpdateSource(name: str, url: str) -> Source:
    src = Source.get_by_id(url)
    
    src.name = name
    src.save()
    
    return src, None

def DeleteSource(url: str):
    src = Source.get_by_id(url)
    
    src.delete_instance()
    