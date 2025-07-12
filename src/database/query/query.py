from ..connection import Query

from datetime import datetime, timedelta

from peewee import fn

def AddQuery(url: str, query: str) -> Query:
    query = Query.create(url = url, query = query)
    
    query.save()
    
    return query

def GetQuery(url: str, query: str) -> Query:
    query = Query.get(Query.url == url, Query.query == query)
    
    return query
    
def GetQueries(
    limit: int = 10,
    url: str = None,
    query: str = None,
    needsUpdating: bool = None,
    preTime: timedelta = None,
    allow: bool = None,
    random: bool = None,
    orderByLastParsed: bool = True,
    nameNotNull: bool = None,
    descNotNull: bool = None,
    viewUrlNotNull: bool = None,
    lastParsedNull: bool = None,
    exists: bool = None,
    cats: list[int] = None
) -> list:
    queries = Query.select()
    
    if url is not None:
        queries = queries.where(Query.url == url)
        
    if query is not None:
        queries = queries.where(Query.query == query)
        
    if needsUpdating is not None:
        queries = queries.where(Query.needsUpdating == needsUpdating)
        
    if nameNotNull:
        queries = queries.where((Query.name.is_null(False)) & (Query.name != ""))
        
    if descNotNull:
        queries = queries.where((Query.description.is_null(False) ) & (Query.description != ""))
        
    if viewUrlNotNull:
        queries = queries.where((Query.viewUrl.is_null(False) & (Query.viewUrl != "")))
        
    if lastParsedNull is not None:
        queries = queries.where(Query.lastParsed.is_null(lastParsedNull))
        
    if exists is not None:
        if exists:
            queries = queries.where((Query.modId.is_null(False)) & (Query.modId != 0) )
        else:
            queries = queries.where((Query.modId.is_null(True)) | (Query.modId == 0))
        
    if preTime is not None:
        timeLimit = datetime.now() - preTime
        queries = queries.where(Query.lastParsed < timeLimit)
        
    if allow is not None:
        queries = queries.where(Query.allow == allow)
        
    if cats is not None:
        queries = queries.where(Query.categoryId << cats)
    
    orders = []
    
    # Order by last parsed (nulls first).
    if orderByLastParsed:
        orders.append(Query.lastParsed.asc(nulls = "FIRST"))
    
    # Randomize order by.
    if random:
        orders.append(fn.Random())
    
    queries = queries.order_by(*orders).limit(limit)
    
    return list(queries)
    
def UpdateQuery(url: str, query: str, modId: int = None, lastParsed: datetime = None, allow: bool = None) -> Query:
    query = Query.get(Query.url == url, Query.query == query)
    
    if modId is not None:
        query.modId = modId
        
    if lastParsed is not None:
        query.lastParsed = lastParsed
        
    if allow is not None:
        query.allow = allow
        
    query.save()
        
    return query
    
def UpdateQueryQuery(url: str, oldQuery: str, newQuery: str) -> Query:
    query = Query.get(Query.url == url, Query.query == oldQuery)
    
    query.query = newQuery
    query.save()
    
    return query
    
def DeleteQuery(url: str, query: str):
    query = Query.get(Query.url == url, Query.query == query)
    
    query.delete_instance()