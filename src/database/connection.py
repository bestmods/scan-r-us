from peewee import *

from playhouse.migrate import *

db = PostgresqlDatabase(None)
migrator = None

import re

class BaseModel(Model):
    class Meta:
        database = db

class Source(BaseModel):
    name = CharField()
    url = CharField(primary_key=True)
    
class Query(BaseModel):
    url = ForeignKeyField(Source, backref="source")
    query = CharField()
    
    modId = IntegerField(null=True)
    
    lastParsed = DateTimeField(null=True)
    allow = BooleanField(default=True)
    needsUpdating = BooleanField(default=False)
    
    viewUrl = CharField(null=True, max_length=256)
    
    categoryId = IntegerField(null=True)
    
    banner = TextField(null=True)
    
    name = CharField(null=True, max_length=120)
    ownerName = CharField(null=True, max_length=64)
    
    description = TextField(null=True)
    descriptionShort = CharField(null=True, max_length=256)
    install = TextField(null=True)
    
    nsfw = BooleanField(null=True)
    autoUpdate = BooleanField(null=True)
    
    downloads = TextField(null=True)
    screenshots = TextField(null=True)
    installers = TextField(null=True)
    
    class Meta:
        primary_key = CompositeKey("url", "query")
        indexes = (
            (("url", "modId"), True)
        )
    
def init(host: str, name: str, user: str, password: str, port: int):
    try:
        global db
        db.init(name,
            host=host,
            user=user,
            password=password,
            port=port)
        
        global migrator
        migrator = PostgresqlMigrator(db)
        
        db.connect()
    except Exception as e:
        return e

def setup():
    try:            
        db.create_tables([Source, Query], safe=True)
    except Exception as e:
        if not "'u'" in str(e):
            print("Failed to create tables!")
            print(str(e))
        
    if migrator:
        # Add "nsfw" and "autoUpdate" fields (1-14-24).
        try:
            migrate(
                migrator.add_column("query", "nsfw", Query.nsfw),
                migrator.add_column("query", "autoUpdate", Query.autoUpdate)
            )
        except Exception as e:
            if not "already exists" in str(e):
                print("[M1] Failed to migrate database!")
                print(e)
                
def getTableSize(table: str) -> int:
    cursor = db.cursor()
    
    cursor.execute(f"SELECT pg_table_size('public.{table}') / 1024 /1024 || 'MB';")

    res = cursor.fetchone()
    
    if res is None:
        return -1
    
    cursor.close()
    
    resStr = res[0]
    
    if not resStr:
        return -1
    
    match = re.search("([0-9]+)", resStr)
    
    if not match:
        return -1
    
    group = match.group(1)
    
    if not group:
        return -1
    
    size = int(group)
    
    return size

def close():
    try:
        db.close()
    except Exception as e:
        return e