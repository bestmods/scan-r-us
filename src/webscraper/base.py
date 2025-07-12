import json
from datetime import datetime, timedelta

from utils import LimitText
from debugger import debugMsg

import database
from peewee import DoesNotExist

from api import ModApi

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox

from selenium.webdriver.remote.command import Command

from random import choice

from enum import Enum

class Status(Enum):
    RUN = 1
    EXCEED_MAX_SPACE = 3
    DISABLED = 2
    
class Webscraper():
    status: Status = Status.RUN
    
    name: str = None
    url: str = None
    tag: str = None
    protocol: str = "https"
    
    driver: Firefox = None
    autoRestartDriver: bool = True
    
    cfg: dict[str, any] = None
    
    api: ModApi = None
    
    cats: dict[str, int] = {}
    catsChildren: dict[str, dict[str, int]] = {}
    
    findEnabled: bool = True
    findIntervalMin: int = 300
    findIntervalMax: int = 600
    
    parseEnabled: bool = True
    parseIntervalMin: int = 150
    parseIntervalMax: int = 300
    parseExisting: bool = False
    parseNew: bool = True
    
    addEnabled: bool = True
    addIntervalMin: int = 30
    addIntervalMax: int = 60
    addExisting: bool = False
    addNew: bool = True
    
    testMode: bool = False
    skipNullCategory: bool = True
    logPageFailOutput: bool = True
    cleanupBanners: bool = True
    
    limit: int = 1
    
    avoidIds: list[str] = []
    
    def __init__(self,
        cfg: dict[str, any],
        
        url: str = None,
        protocol: str = None,
        
        cats: dict[str, int] = None,
        catsChildren: dict[str, dict[str, int]] = None,
        
        findEnabled: bool = None,
        findIntervalMin: int = None,
        findIntervalMax: int = None,
        
        parseEnabled: bool = None,
        parseIntervalMin: int = None,
        parseIntervalMax: int = None,
        parseExisting: bool = None,
        parseNew: bool = None,
        
        addEnabled: bool = None,
        addIntervalMin: int = None,
        addIntervalMax: int = None,
        addExisting: bool = None,
        addNew: bool = None,
        
        testMode: bool = None,
        skipNullCategory: bool = None,
        logPageFailOutput: bool = None,
        cleanupBanners: bool = None,
        avoidIds: list[str] = None
    ):
        super().__init__()
        
        self.cfg = cfg
        self.api = ModApi(self.cfg)
        
        # Override URL, protocol, and categories for parser if necessary.
        if url is not None:
            self.url = url
            
        if protocol is not None:
            self.protocol = protocol
            
        if cats is not None:
            self.cats = cats
            
        if catsChildren is not None:
            self.catsChildren = catsChildren
        
        # Find functionality.
        if findEnabled is not None:
            self.findEnabled = findEnabled
            
        if findIntervalMin is not None:
            self.findIntervalMin = findIntervalMin
            
        if findIntervalMax is not None:
            self.findIntervalMax = findIntervalMax
            
        # Parsing functionality.
        if parseEnabled is not None:
            self.parseEnabled = parseEnabled
            
        if parseIntervalMin is not None:
            self.parseIntervalMin = parseIntervalMin
            
        if parseIntervalMax is not None:
            self.parseIntervalMax = parseIntervalMax
        
        if parseExisting is not None:
            self.parseExisting = parseExisting
            
        if parseNew is not None:
            self.parseNew = parseNew
            
        # Add functionality.
        if addEnabled is not None:
            self.addEnabled = addEnabled
            
        if addIntervalMin is not None:
            self.addIntervalMin = addIntervalMin
            
        if addIntervalMax is not None:
            self.addIntervalMax = addIntervalMax
            
        if addExisting is not None:
            self.addExisting = addExisting
            
        if addNew is not None:
            self.addNew = addNew
            
        # Test mode.
        if testMode is not None:
            self.testMode = testMode
            
        # Skip null category.
        if skipNullCategory is not None:
            self.skipNullCategory = skipNullCategory
        
        # Log page fail output.
        if logPageFailOutput is not None:
            self.logPageFailOutput = logPageFailOutput
            
        # Cleanup Banners
        if cleanupBanners is not None:
            self.cleanupBanners = cleanupBanners
            
        # Avoid IDs
        if avoidIds is not None:
            self.avoidIds = avoidIds
        
        # Compile tag.
        if self.tag is None:
            self.tag = f"{self.name}::{self.url}"
            
        # Attempt to setup database.
        try:
            database.setup()
            
            debugMsg(self.cfg, 1, f"[{self.tag}] Setup database tables.")
        except:
            pass
        
        # Check if source exist. If not, insert into database.
        try:
            database.GetSource(self.url)
        except DoesNotExist:
            debugMsg(self.cfg, 2, f"[{self.tag} MF] Source does not exist in database! Inserting into database!")
            
            # Try to insert into database. Print exception otherwise.
            try:
                src = database.AddSource(self.url, self.url)
                
                debugMsg(self.cfg, 2, f"[{self.tag} MF] Inserted source into database! Source => {src}")
            except Exception as e:
                debugMsg(self.cfg, 0, f"[{self.tag} MF] Error inserting source into database!")
                debugMsg(self.cfg, 0, e)
                
    def setupDriver(self):
        # Setup options.
        opts = Options()
        
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        
        # Pick random user agent if any.
        if len(self.cfg["userAgents"]) > 0:
            # Get random user agent.
            ua = choice(self.cfg["userAgents"])
            
            opts.set_preference("general.useragent.override", ua)
        
        service = Service(executable_path=self.cfg["binaryPath"])
        
        self.driver = Firefox(options = opts, service = service)
        
    def checkDriver(self) -> bool:
        try:
            self.driver.title
            return True
        except Exception as e:
            return False
                
    def shouldRun(self) -> bool:
        return self.status == Status.RUN
                
    def checkQuerySize(self):
        try:
            curSize = database.getTableSize("query")
            maxSize = int(self.cfg["database"]["sizeLimit"])
            
            debugMsg(self.cfg, 4, f"[{self.tag} C] Checking query table size {curSize}/{maxSize} MBs.")
            
            exceeds = int(curSize) > int(maxSize)
            
            if exceeds and self.status == Status.RUN:
                debugMsg(self.cfg, 0, f"[{self.tag} C] Query table reached maximum size! Disabling web scraper for the moment. {curSize}/{maxSize} MBs")
                
                self.status = Status.EXCEED_MAX_SPACE
            elif not exceeds and self.status == Status.EXCEED_MAX_SPACE:
                debugMsg(self.cfg, 0, f"[{self.tag} C] Scraper was disabled due to exceeding maximum size. However, now it doesn't exceed. Enabling! {curSize}/{maxSize} MBs")
                
                self.status = Status.RUN
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} C] Failed to check 'query' table size due to exception.")
            debugMsg(self.cfg, 0, e)
                
    def BaseWait(self):
        pass
                
    async def GatherQueries(self) -> list[str]:
        queries = []
        
        debugMsg(self.cfg, 2, f"[{self.tag} F] Gathering mods.")
        
        return queries
    
    async def FindMods(self):
        # Check disk space.
        self.checkQuerySize()
        
        # Make sure we should run.
        if not self.shouldRun():
            debugMsg(self.cfg, 5, f"[{self.tag} F] Aborting due to scraper status ({self.status}).")
            
            return
        
        # Check if finding is enabled.
        if not self.findEnabled:
            debugMsg(self.cfg, 5, f"[{self.tag} F] Finding disabled. Aborting...")
            
            return
        
        # Retrieve queries.
        queries = await self.GatherQueries()
        
        debugMsg(self.cfg, 3, f"[{self.tag} F] Found {len(queries)} queries to add to queue.")
        
        for query in queries:
            debugMsg(self.cfg, 3, f"[{self.tag} F] Found query '{query}'.")
            
            try:
                # Attempt to find query.
                try:
                    database.GetQuery(self.url, query)
                except DoesNotExist:
                    debugMsg(self.cfg, 3, f"[{self.tag} F] Query '{query}' doesn't exist. Attempting to add.")
                    
                    # Add query to database.
                    query = database.AddQuery(self.url, query)
                    
                    debugMsg(self.cfg, 2, f"[{self.tag} F] Added query '{query}' to database!")                        
            except Exception as e:
                debugMsg(self.cfg, 0, f"[{self.tag} F] Failed to add query '{query}'.")
                debugMsg(self.cfg, 0, e)

    async def ParseMods(self):
        # Check disk space.
        self.checkQuerySize()
        
        # Make sure we should run.
        if not self.shouldRun():
            debugMsg(self.cfg, 5, f"[{self.tag} P] Aborting due to scraper status ({self.status}).")
            
            return
        
        # Check if parsing is enabled.
        if not self.parseEnabled:
            debugMsg(self.cfg, 5, f"[{self.tag} P] Parsing disabled. Aborting...")
            
            return
        
        debugMsg(self.cfg, 2, f"[{self.tag} P] Parsing Mods!")
        
        # Check if we should only search for existing entries.
        exists = None
        
        if self.parseNew and not self.parseExisting:
            exists = False
        elif not self.parseNew and self.parseExisting:
            exists = True
        
        # Retrieve list of current category IDs.
        catIds: list[int] | None = None
        
        if exists:
            catIds = self.getCategoryIds()
        
        try:            
            mods = database.GetQueries(
                limit = self.limit,
                url = self.url,
                allow = True,
                random = True,
                exists = exists,
                cats = catIds
            )
            
            debugMsg(self.cfg, 3, f"[{self.tag} P] Found {len(mods)} mods to parse.")
            debugMsg(self.cfg, 4, f"[{self.tag} P] Mods => {mods}")
            
            for mod in mods:
                url = f"{self.protocol}://{self.url}{mod.query}"
                
                debugMsg(self.cfg, 3, f"[{self.tag} P] Sending request to URL '{url}' for parsing.")
                
                try:
                    self.driver.get(url)
                    
                    # Wait if we need to based off of web scraper.
                    try:
                        self.BaseWait()
                    except Exception as e:
                        debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse query '{mod.query}' due to base wait exception.")
                        debugMsg(self.cfg, 0, e)
                        
                        # Log page output if enabled.
                        if self.logPageFailOutput:
                            self.LogPageFail()
                            
                        # If exists is on, we should update the last parsed time to avoid getting stuck.
                        if exists:
                            now = datetime.now()
                            
                            mod.lastParsed = now
                            mod.save()
                            
                        continue
                    
                    self.ParseMod(url, mod.query, self.driver.page_source)
                except Exception as e:
                    debugMsg(self.cfg, 2, f"[{self.tag} P] Error parsing query with full URL '{url}' due to exception.")
                    debugMsg(self.cfg, 2, e)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Error retrieving and parsing mods from database.")
            debugMsg(self.cfg, 0, e)
        
    async def AddMods(self):
        # Check disk space.
        self.checkQuerySize()
        
        # Make sure we should run.
        if not self.shouldRun():
            debugMsg(self.cfg, 5, f"[{self.tag} A] Aborting due to scraper status ({self.status}).")
            
            return
        
        # Check if adding is enabled.
        if not self.addEnabled:
            debugMsg(self.cfg, 5, f"[{self.tag} A] Adding disabled. Aborting...")
            
            return
        
        debugMsg(self.cfg, 2, f"[{self.tag} A] Attempting to add mods...")
        
        apiInfo = self.cfg["api"]
        
        try:            
            # Check if we should only search for existing entries.
            exists = None
            
            if self.addNew and not self.addExisting:
                exists = False
            elif not self.addNew and self.addExisting:
                exists = True
            
            queries = database.GetQueries(
                url = self.url,
                limit = apiInfo["limit"],
                needsUpdating = True,
                allow = True,
                orderByLastParsed = False,
                random = True,
                nameNotNull = True,
                descNotNull = True,
                viewUrlNotNull = True,
                exists = exists
            )
            
            debugMsg(self.cfg, 3, f"[{self.tag} A] Found {len(queries)} queries to add through API.")
            
            for query in queries:
                debugMsg(self.cfg, 4, f"[{self.tag} A] Retrieved query => '{query.query}'.")
                
                resp = self.api.GetMod(None, self.url, query.query)
                
                errGeneral = f"Failed to retrieve query => '{query.query}' from API"
                
                if resp is None:
                    debugMsg(self.cfg, 0, f"[{self.tag} A] {errGeneral}. Response is none.")
                    
                    continue
                
                if resp.status_code != 200:
                    debugMsg(self.cfg, 0, f"[{self.tag} A] {errGeneral}. Status code => {resp.status_code}.")
                    
                    continue
                
                try:
                    jsonObj = json.loads(resp.text)
                except Exception as e:
                    debugMsg(self.cfg, 0, f"[{self.tag} A] {errGeneral}. Failed to load JSON due to following exception.")
                    debugMsg(self.cfg, 0, e)
                    
                    continue
                
                debugMsg(self.cfg, 3, f"[{self.tag} A] Found JSON response for query => '{query.query}'. Response => '{jsonObj}'.")
                
                if "data" not in jsonObj:
                    debugMsg(self.cfg, 0, f"[{self.tag} A] {errGeneral}. No 'data' object found in JSON response.")
                    
                    continue
                
                data = jsonObj["data"]
                
                # Retrieve mod ID.
                id = None
                
                if data and len(data) > 0:
                    obj = data[0]
                    
                    # Retrieve ID.
                    if "id" in obj:
                        id = int(obj["id"])
                        
                    # Retrieve and check for auto update.
                    autoUpdate = False
                    
                    if "autoUpdate" in obj:
                        autoUpdate = bool(obj["autoUpdate"])
                        
                    if not autoUpdate:
                        debugMsg(self.cfg, 4, f"[{self.tag} A] Skipping query '{query.query}' due to auto updating being disabled. ID => '{id}'.")
                        
                        # Set needs updating to false and save.
                        try:
                            query.needsUpdating = False
                            
                            query.save()
                        except Exception as e:
                            debugMsg(self.cfg, 0, f"[{self.tag} A] Failed to set existing query '{query.query}' to needsUpdating = False due to exception.")
                            debugMsg(self.cfg, 0, e)
                        
                        continue
                        
                    # If add existing is off, skip this query.
                    if not self.addExisting:
                        debugMsg(self.cfg, 4, f"[{self.tag} A] Skipping query '{query.query}' due to already existing and update existing set to False. ID => '{id}'.")
                        
                        # Set mod ID to ensure we don't pick it again and save.
                        try:
                            query.modId = id
                            
                            query.save()
                        except Exception as e:
                            debugMsg(self.cfg, 0, f"[{self.tag} A] Failed to set existing query '{query.query}' mod ID due to exception.")
                            debugMsg(self.cfg, 0, e)
                        
                        continue
                else:
                    # Check if add new is enabled.
                    if not self.addNew:
                        debugMsg(self.cfg, 4, f"[{self.tag} A] Skipping query '{query.query}' due to being new.")
                        
                        # Make sure mod ID is null.
                        try:
                            query.modId = None
                            
                            query.save()
                        except Exception as e:
                            debugMsg(self.cfg, 0, f"[{self.tag} A] Failed to set new query '{query.query}' to mod ID = NULL. Didn't find match and addNew is set to false.")
                            debugMsg(self.cfg, 0, e)
                        
                        continue
                
                debugMsg(self.cfg, 3, f"[{self.tag} A] Preparing to add or update mod with ID '{id}'.")
                
                # Attempt to update mod through our API.
                try:
                    # We need to build our sources manually.
                    sources = [{
                        "sourceUrl": str(query.url),
                        "query": query.query
                    }]
                    
                    # We need to convert our relations to JSON objects.
                    downloads: list[dict[str, str]] = None
                    screenshots: list[dict[str, str]] = None
                    installers: list[dict[str, str]] = None
                    
                    if query.downloads is not None and len(query.downloads) > 0:
                        downloads = json.loads(query.downloads)
                        
                    if query.screenshots is not None and len(query.screenshots) > 0:
                        screenshots = json.loads(query.screenshots)
                        
                    if query.installers is not None and len(query.installers) > 0:
                        installers = json.loads(query.installers)
                        
                    # Extract query data into their own variables.
                    viewUrl = query.viewUrl
                    banner = query.banner
                    
                    categoryId = query.categoryId
                    
                    # Check category ID if skip null category is set to true.
                    if self.skipNullCategory and (categoryId is None or categoryId < 1):
                        debugMsg(self.cfg, 2, f"[{self.tag} A] Query '{query.query}' doesn't have a valid category ID. Skipping...")
                        
                        continue
                    
                    name = query.name
                    ownerName = query.ownerName
                    description = query.description
                    descriptionShort = query.descriptionShort
                    install = query.install
                    
                    nsfw = query.nsfw
                    autoUpdate = query.autoUpdate
                        
                    debugMsg(self.cfg, 4, f"[{self.tag} A] Adding or updating mod with query '{query.query}'. ID => '{id}'. View URL => '{viewUrl}'. Category ID => '{categoryId}'. Banner => '{LimitText(banner)}'. Name => '{name}'. Owner Name => '{ownerName}'. Description => '{LimitText(description)}'. Description short => '{descriptionShort}'. Install => '{LimitText(install)}'. NSFW => '{nsfw}'. Auto Update => '{autoUpdate}'. Sources => '{sources}'. Downloads => '{downloads}'. Screenshots => '{screenshots}'. Installers => '{installers}'.")
                    
                    # Abort actual update if we're in test mode.
                    if self.testMode:
                        continue
                    
                    resp = self.api.UpdateOrAddMod(
                        id = id,
                        url = viewUrl,
                        banner = banner,
                        categoryId = categoryId,
                        name = name,
                        ownerName = ownerName,
                        description = description,
                        descriptionShort = descriptionShort,
                        install = install,
                        
                        nsfw = nsfw,
                        autoUpdate = autoUpdate,
                        
                        sources = sources,
                        downloads = downloads,
                        screenshots = screenshots,
                        installers = installers
                    )
                    
                    # Check response code.
                    if resp.status_code != 200:
                        debugMsg(self.cfg, 0, f"[{self.tag} A] Query '{query.query}' failed to update. Status code => {resp.status_code}. Response => '{resp.text}'.")
                        
                        continue
                    
                    # Load JSON object from response contents.
                    jsonObj = json.loads(resp.text)
                    
                    if "data" not in jsonObj:
                        debugMsg(self.cfg, 0, f"[{self.tag} A] Query '{query.query}' failed to update. No JSON key 'data' found in response.")
                        
                        continue
                    
                    # Retrieve data object.
                    data = jsonObj["data"]
                    
                    # Attempt to retrieve ID and check.
                    if "id" in data:
                        id = int(data["id"])
                    
                    if id is None:
                        debugMsg(self.cfg, 0, f"[{self.tag} A] Query '{query.query}' failed to update. Mod ID is None after add/update process.")
                        
                        continue
                    
                    # Set mod ID.
                    query.modId = id
                    
                    # Set needs updating to false.
                    query.needsUpdating = False
                    
                    # Check if we need to cleanup banners.
                    if self.cleanupBanners:
                        debugMsg(self.cfg, 5, f"[{self.tag} A] Cleaning up banner to save disk space.")
                        
                        query.banner = None
                    
                    # Save query.
                    query.save()
                    
                    debugMsg(self.cfg, 2, f"[{self.tag} A] Successfully inserted mod/query '{query.query}' (ID => {id})! Query also saved in database.")
                except Exception as e:
                    debugMsg(self.cfg, 0, f"[{self.tag} A] Query '{query.query}' failed to insert/update.")
                    debugMsg(self.cfg, 0, e)
                    
                    continue
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} A] Error retrieving queries to add via API.")
            debugMsg(self.cfg, 0, e)
    
    def ParseMod(self, url: str, queryStr: str, resp: str):        
        debugMsg(self.cfg, 3, f"[{self.tag} P] Parsing query '{queryStr}'. Full URL => '{url}'")
        debugMsg(self.cfg, 6, f"[{self.tag} P] Base Parsed Resp => '{resp}'")
        
        # Retrieve mod information.
        ownerId, setOwnerId = self.ParseOwnerId(url, resp)
                
        viewUrl, setViewUrl = self.ParseViewUrl(url, resp)
        
        categoryId, setCategoryId = self.ParseCategoryId(url, resp)
        
        if not categoryId:
            debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse query '{queryStr}'. Category ID is Falsey.")
            
            return
        
        name, setName = self.ParseName(url, resp)
        ownerName, setOwnerName = self.ParseOwnerName(url, resp)
        
        description, setDescription = self.ParseDescription(url, resp)
        descriptionShort, setDescriptionShort = self.ParseDescriptionShort(url, resp)
        install, setInstall = self.ParseInstall(url, resp)
        
        nsfw, setNsfw = self.ParseNsfw(url, resp)
        autoUpdate, setAutoUpdate = self.ParseAutoUpdate(url, resp)
        
        downloads, setDownloads = self.ParseDownloads(url, resp)
        screenshots, setScreenshots = self.ParseScreenshots(url, resp)
        installers, setInstallers = self.ParseInstallers(url, resp)
        
        banner, setBanner = self.ParseBanner(url, resp)
        
        # Print results of content.
        debugMsg(self.cfg, 4, f"[{self.tag} P] View URL => {viewUrl} (set => {setViewUrl})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Category ID => {categoryId} (set => {setCategoryId})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Banner => {LimitText(banner)} (set => {setBanner})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Name => {name} (set => {setName})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Owner Name => {ownerName} (set => {setOwnerName})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Owner ID => {ownerId} (set => {setOwnerId})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Description => {LimitText(description)} (set => {setDescription})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Description Short => {descriptionShort} (set => {setDescriptionShort})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Install => {LimitText(install)} (set => {setInstall})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] NSFW => {nsfw} (set => {setNsfw})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Auto Update => {autoUpdate} (set => {autoUpdate})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Downloads => {downloads} (set => {setDownloads})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Screenshots => {screenshots} (set => {setScreenshots})")
        debugMsg(self.cfg, 4, f"[{self.tag} P] Installers => {installers} (set => {setInstallers})")
        
        # Lookup or create query.
        try:
            query = database.GetQuery(self.url, queryStr)
        except DoesNotExist:
            # Attempt to create query.
            try:
                query = database.AddQuery(self.url, queryStr)
            except Exception as e:
                debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse query '{queryStr}' due to exception when adding query.")
                debugMsg(self.cfg, 0, e)
                
                return
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse query '{queryStr}' due to unknown exception when retrieving from database.")
            debugMsg(self.cfg, 0, e)
            
            return
            
        if query is None:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse query '{queryStr}'. 'query' is None.")
            
            return
        
        # Retrieve current time.
        now = datetime.now()
        
        # Check if we need to avoid this user.
        if setOwnerId and len(self.avoidIds) > 0:
            if ownerId in self.avoidIds:
                debugMsg(self.cfg, 1, f"[{self.tag} P] Found owner ID on avoid list for query '{queryStr}'. Aborting and setting allow to false!")
                
                try:
                    # Set allowed to false and update.
                    query.allow = False
                    query.lastParsed = now
                    
                    query.save()
                except Exception as e:
                    debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to save mod that is on avoid list due to exception.")
                    debugMsg(self.cfg, 0, e)
                
                return
        
        # Assign values.
        if setViewUrl:
            query.viewUrl = viewUrl
            
        if setCategoryId:
            query.categoryId = categoryId
        
        if setBanner:
            query.banner = banner
        
        if setName:
            query.name = name
        
        if setOwnerName:
            query.ownerName = ownerName
        
        if setDescription:
            query.description = description

        if setDescriptionShort:
            query.descriptionShort = descriptionShort
        
        if setInstall:
            query.install = install
            
        if setNsfw:
            query.nsfw = nsfw
            
        if setAutoUpdate:
            query.autoUpdate = autoUpdate
        
        if setDownloads:
            query.downloads = json.dumps(downloads)
        
        if setScreenshots:
            query.screenshots = json.dumps(screenshots)
        
        if setInstallers:
            query.installers = json.dumps(installers)
            
        # Make sure we have required fields set.
        if not name or not description or not viewUrl:
            debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse query '{queryStr}'. Aborting due to no name, description, or view URL set.")
            
            return
                        
        # Update last parsed.
        query.lastParsed = now
        
        # Set needs updating to true.
        query.needsUpdating = True
        
        debugMsg(self.cfg, 4, f"[{self.tag} P] Saving query '{queryStr}' to database! Last parsed => '{now}'.")
        
        # Save mod.
        query.save()
        
    def ParseViewUrl(self, url: str, resp: str) -> (str, bool):
        return None, False
        
    def ParseCategoryId(self, url: str, resp: str) -> (int, bool):
        return None, False
    
    def ParseBanner(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseName(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseOwnerName(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseDescription(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseDescriptionShort(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseInstall(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def ParseNsfw(self, url: str, resp: str) -> (bool, bool):
        return None, False
    
    def ParseAutoUpdate(self, url: str, resp: str) -> (bool, bool):
        return True, True
    
    def ParseDownloads(self, url: str, resp: str) -> (list[dict[str, str]], bool):
        return None, False
        
    def ParseScreenshots(self, url: str, resp: str) -> (list[dict[str, str]], bool):
        return None, False
    
    def ParseInstallers(self, url: str, resp: str) -> (list[dict[str, str]], bool):
        return None, False
    
    def ParseOwnerId(self, url: str, resp: str) -> (str, bool):
        return None, False
    
    def LogPageFail(self, source: str = None):
        if source is None:
            source = self.driver.page_source
            
        try:
            curDate = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
            
            fileName = f"{self.url}-{curDate}.html"
            
            path = f"log/pages/{fileName}"
            
            with open(path, "w") as f:
                f.write(source)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag}] Failed to log page fail due to exception.")
            debugMsg(self.cfg, 0, e)
            
    def getCategoryIds(self) -> list[int]:
        cats: list[int] = []
        
        for cat, id in self.cats.items():
            cats.append(id)
            
        return cats