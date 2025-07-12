import asyncio
from random import randint

from multiprocessing import Process
from importlib import import_module

from debugger import debugMsg
import database

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox

def SetupParsers(cfg: dict[str, any]):
    # Make sure parsers exists in config.
    if "parsers" not in cfg:
        raise Exception("Parsers not found in config.")
    
    parsers = cfg["parsers"]
    
    # Ensure we have parsers.
    if len(parsers) < 1:
        raise Exception("No parsers found.")
    
    # Loop through each parser.
    idx = 0
    
    for par in parsers:
        # Increment our index now.
        idx = idx + 1
        
        # Make sure we have a parser set.
        if "scraper" not in par:
            print(f"Parser #{idx - 1} does not have a scraper set. Skipping...")
            
            continue
        
        scrName = par["scraper"]
        
        scrPath = f"webscraper.scrapers.{scrName}"
        
        debugMsg(cfg, 4, f"[Scraper {scrName}] Importing source path '{scrPath}'.")
        
        # Try to dynamically import web scraper module.
        try:
            scrMod = import_module(scrPath)
            
            # Check for disable.
            if "disabled" in par:
                if par["disabled"]:
                    debugMsg(cfg, 1, f"Skipping parser '{scrName}'. Scraper disabled...")
                    
                    continue
            
            # Set source URL.
            url = None
            
            if "url" in par:
                url = par["url"]
            
            # Set source protocol.
            protocol = "https"
            
            if "protocol" in par:
                protocol = par["protocol"]
                
            # Set source categories.
            cats = None
            
            if "categories" in par:
                cats = par["categories"]
                
            # Set category children.
            catsChildren = None
            
            if "catsChildren" in par:
                catsChildren = par["catsChildren"]
                
            # Find functionality.
            findEnabled = None
            
            if "findEnabled" in par:
                findEnabled = bool(par["findEnabled"])
                
            findIntervalMin = None
            
            if "findIntervalMin" in par:
                findIntervalMin = int(par["findIntervalMin"])
                
            findIntervalMax = None
            
            if "findIntervalMax" in par:
                findIntervalMax = int(par["findIntervalMax"])
                
            # Parsing functionality.
            parseEnabled = None
            
            if "parseEnabled" in par:
                parseEnabled = bool(par["parseEnabled"])
                
            parseIntervalMin = None
            
            if "parseIntervalMin" in par:
                parseIntervalMin = int(par["parseIntervalMin"])
                
            parseIntervalMax = None
            
            if "parseIntervalMax" in par:
                parseIntervalMax = int(par["parseIntervalMax"])
                
            parseExisting = None
            
            if "parseExisting" in par:
                parseExisting = bool(par["parseExisting"])
                
            parseNew = None
            
            if "parseNew" in par:
                parseNew = bool(par["parseNew"])
                
            # Add functionality.
            addEnabled = None
            
            if "addEnabled" in par:
                addEnabled = bool(par["addEnabled"])
                
            addIntervalMin = None
            
            if "addIntervalMin" in par:
                addIntervalMin = int(par["addIntervalMin"])
                
            addIntervalMax = None
            
            if "addIntervalMax" in par:
                addIntervalMax = int(par["addIntervalMax"])
                
            addExisting = None
            
            if "addExisting" in par:
                addExisting = bool(par["addExisting"])
                
            addNew = None
            
            if "addNew" in par:
                addNew = bool(par["addNew"])
                
            # Test mode.
            testMode = None
            
            if "testMode" in par:
                testMode = bool(par["testMode"])
                
            # Skip null category.
            skipNullCategory = None
            
            if "skipNullCategory" in par:
                skipNullCategory = bool(par["skipNullCategory"])
                
            # Log page fail output.
            logPageFailOutput = None
            
            if "logPageFailOutput" in par:
                logPageFailOutput = bool(par["logPageFailOutput"])
            
            # Cleanup banners.
            cleanupBanners = None
            
            if "cleanupBanners" in par:
                cleanupBanners = bool(par["cleanupBanners"])
                
            # Avoid IDs.
            avoidIds = None
            
            if "avoidIds" in par:
                avoidIds = list(par["avoidIds"])
                
            # We need to create a new process for this parser to initialize our web scraper.
            p = Process(target=ScraperTarget, args=(cfg, scrMod.Webscraper,
                scrName,
                url,
                protocol,
                cats,
                catsChildren,
                findEnabled,
                findIntervalMin,
                findIntervalMax,
                parseEnabled,
                parseIntervalMin,
                parseIntervalMax,
                parseExisting,
                parseNew,
                addEnabled,
                addIntervalMin,
                addIntervalMax,
                addExisting,
                addNew,
                testMode,
                skipNullCategory,
                logPageFailOutput,
                cleanupBanners,
                avoidIds
            ))
            p.start()
        except Exception as e:
            print(f"[Scraper {scrName}] Failed to import module. Skipping...")
            print(e)
            
            continue
    
        debugMsg(cfg, 1, f"[Scraper {scrName}] Initialized!")

def ScraperTarget(cfg, cls,
    scrName: str = None,
    
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
    debugMsg(cfg, 1, f"[Scraper {scrName}] Starting web scraper...")
    
    # Connect to database.
    db = cfg["database"]
    database.init(db["host"], db["name"], db["user"], db["pass"], db["port"])
    
    try:
        # Initialize class.
        scraper = cls(cfg,
            url = url,
            protocol = protocol,
            cats = cats,
            catsChildren = catsChildren,
            
            findEnabled = findEnabled,
            findIntervalMin = findIntervalMin,
            findIntervalMax = findIntervalMax,
            
            parseEnabled = parseEnabled,
            parseIntervalMin = parseIntervalMin,
            parseIntervalMax = parseIntervalMax,
            parseExisting = parseExisting,
            parseNew = parseNew,
            
            addEnabled = addEnabled,
            addIntervalMin = addIntervalMin,
            addIntervalMax = addIntervalMax,
            addExisting = addExisting,
            addNew = addNew,
            
            testMode = testMode,
            skipNullCategory = skipNullCategory,
            logPageFailOutput = logPageFailOutput,
            cleanupBanners = cleanupBanners,
            avoidIds = avoidIds
        )
        
        # Setup web driver.
        scraper.setupDriver()
    except Exception as e:
        debugMsg(cfg, 0, f"[Scraper {scrName}] Error initializing web driver. Aborting web scraper process...")
        debugMsg(cfg, 0, e)
        
        return
    
    # Run web scraper tasks.
    asyncio.run(ScraperTasks(scraper))
    
    driver.quit()

async def ScraperTasks(scraper):
    tasks = [
        asyncio.create_task(findMods(scraper)),
        asyncio.create_task(parseMods(scraper)),
        asyncio.create_task(addMods(scraper))
    ]
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        return
    
async def findMods(scraper):
    while True:
        await scraper.FindMods()
        
        delay = randint(scraper.findIntervalMin, scraper.findIntervalMax)
        await asyncio.sleep(delay)

async def parseMods(scraper):
    while True:
        await scraper.ParseMods()
        
        delay = randint(scraper.parseIntervalMin, scraper.parseIntervalMax)
        await asyncio.sleep(delay)
        
async def addMods(scraper):
    while True:
        await scraper.AddMods()
        
        delay = randint(scraper.addIntervalMin, scraper.addIntervalMax)
        await asyncio.sleep(delay)
        