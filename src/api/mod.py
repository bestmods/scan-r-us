from requests import get, delete, request, Response
from urllib.parse import urlencode

from debugger import debugMsg

import json

class ModApi():
    cfg: dict[str, any] = None
    
    host = "http://localhost"
    endPoint = "/api/content/mod"
    token: str = None
    
    headers: dict[str, str] = {
        "Content-Type": "application/json"
    }
    
    def __init__(self, cfg: dict[str, any]):
        self.cfg = cfg
        
        apiInfo = self.cfg["api"]
        
        if "host" in apiInfo:
            self.host = apiInfo["host"]
            
        if "token" in apiInfo:
            self.token = apiInfo["token"]
            
        if self.token is not None:
            self.headers["Authorization"] = self.token
    
    def GetMod(self, id: int = None, srcUrl: str = None, srcQuery: str = None) -> Response:
        if id is None and srcUrl is None and srcQuery is None:
            print("Error retrieving mod (ID and source URL/query are all None).")
            
            return None
        
        # Build params.
        params = {
            "id": id,
            "srcUrl": srcUrl,
            "srcQuery": srcQuery
        }
        
        params = { key: value for key, value in params.items() if value is not None}
        
        reqUrl = f"{self.host}{self.endPoint}?{urlencode(params)}"
        
        debugMsg(self.cfg, 7, f"[API] GetMod() :: Sending request to => '{reqUrl}' with params => '{params}' and headers => '{self.headers}'.")
        
        resp = get(reqUrl,
            headers = self.headers                
        )
        
        return resp
    
    def UpdateOrAddMod(self, id: int = None, url: str = None, banner: str = None, categoryId: int = None, name: str = None, ownerName: str = None, description: str = None, descriptionShort: str = None, install: str = None, nsfw: bool = None, autoUpdate: bool = None, sources: list[dict[str, str]] = None, downloads: list[dict[str, str]] = None, screenshots: list[dict[str, str]] = None, installers: list[dict[str, str]] = None) -> Response:
        # Start building request URL.
        reqUrl = f"{self.host}{self.endPoint}"
        
        # Figure out what method we'll use.
        method = "POST"
        
        if id is not None:
            method = "PUT"
            
            # Add ID to parameters.
            params = {
                "id": id
            }
            
            reqUrl += f"?{urlencode(params)}"
        else:
            # Make sure we have required fields.
            if not name or not url or not description:
                raise Exception("Failed to add mod. Name, URL, or description not set.")
            
        # Set data/body.
        data: dict[str, any] = {}
        
        if url is not None:
            data["url"] = url
            
        if banner is not None:
            data["banner"] = banner
            
        if categoryId is not None:
            data["categoryId"] = categoryId
            
        if name is not None:
            data["name"] = name
            
        if ownerName is not None:
            data["ownerName"] = ownerName
            
        if description is not None:
            data["description"] = description
            
        if descriptionShort is not None:
            data["descriptionShort"] = descriptionShort
            
        if install is not None:
            data["install"] = install
            
        if nsfw is not None:
            data["nsfw"] = nsfw
            
        if autoUpdate is not None:
            data["autoUpdate"] = autoUpdate
            
        if sources is not None:
            data["sources"] = sources
            
        if downloads is not None:
            data["downloads"] = downloads
            
        if screenshots is not None:
            data["screenshots"] = screenshots
            
        if installers is not None:
            data["installers"] = installers
            
        debugMsg(self.cfg, 8, f"[API] UpdateOrAddMod() :: Sending request to => '{reqUrl}' with data => '{data}' and headers => '{self.headers}'.")
        
        # We need to convert data object to JSON.
        dataJson = json.dumps(data)
            
        resp = request(method, reqUrl,
            headers = self.headers,
            data = dataJson
        )
            
        return resp
    
    def DeleteMod(self, id: int) -> Response:
        if id is None:
            print("Unable to delete mod (ID is null).")
            
            return
        
        reqUrl = f"{self.host}{self.endPoint}?id={id}"
        
        debugMsg(self.cfg, 7, f"[API] DeleteMod() :: Sending request to => '{reqUrl}' with  headers => '{self.headers}'.")
        
        resp = delete(reqUrl,
            headers = self.headers
        )
        
        return resp