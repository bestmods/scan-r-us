import json

cfg: dict[str, any] = {}

def setDefaultValues():
    if "debug" not in cfg:
        cfg["debug"] = 1
        
    if "logFile" not in cfg:
        cfg["logFile"] = None
        
    if "binaryPath" not in cfg:
        cfg["binaryPath"] = "/usr/bin/geckodriver"
    
    if "database" not in cfg:
        cfg["database"] = {}
    
    if "host" not in cfg["database"]:
        cfg["database"]["host"] = "localhost"
        
    if "name" not in cfg["database"]:
        cfg["database"]["name"] = "scanrus"
        
    if "user" not in cfg["database"]:
        cfg["database"]["user"] = "root"
    
    if "pass" not in cfg["database"]:
        cfg["database"]["pass"] = ""
        
    if "port" not in cfg["database"]:
        cfg["database"]["port"] = 5432
        
    if "sizeLimit" not in cfg["database"]:
        cfg["database"]["sizeLimit"] = 25000
        
    if "userAgents" not in cfg:
        cfg["userAgents"] = [
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        
    if "parsers" not in cfg:
        cfg["parsers"] = []
        
    if "api" not in cfg:
        cfg["api"] = {}
        
    if "host" not in cfg["api"]:
        cfg["api"]["host"] = "localhost"
        
    if "token" not in cfg["api"]:
        cfg["api"]["token"] = None
        
    if "limit" not in cfg["api"]:
        cfg["api"]["limit"] = 5
        
    if "preTime" not in cfg["api"]:
        cfg["api"]["preTime"] = 5
        
    if "intervalMin" not in cfg["api"]:
        cfg["api"]["intervalMin"] = 30
        
    if "intervalMax" not in cfg["api"]:
        cfg["api"]["intervalMax"] = 60

def loadCfg(path: str):
    global cfg
    
    try:
        with open(path) as f:
            cfg = json.load(f)
    except:
        print(f"WARNING - Failed to load config. Path => {path}. Using default settings as a fallback...")
        
    # Load default config values if they don't exist.
    setDefaultValues()
    
def printCfg():
    print("Config Settings")
    print("\tGeneral")
    print(f"\t\tDebug Level => {cfg['debug']}")
    print(f"\t\tBinary Path => {cfg['binaryPath']}")
    print("\tUser Agents")
    for agent in cfg["userAgents"]:
        print(f"\t\t- {agent}")
    print("\tDatabase")
    print(f"\t\tHost => {cfg['database']['host']}")
    print(f"\t\tName => {cfg['database']['name']}")
    print(f"\t\tUser => {cfg['database']['user']}")
    print(f"\t\tPass => {cfg['database']['pass']}")
    print(f"\t\tPort => {cfg['database']['port']}")
    print(f"\t\tSize Limit => {cfg['database']['sizeLimit']} MBs")
    print("\tAPI")
    print(f"\t\tHost => {cfg['api']['host']}")
    print(f"\t\tToken => {cfg['api']['token']}")
    print(f"\t\tLimit => {cfg['api']['limit']}")
    print("\tParsers")
    idx = 0
    for par in cfg["parsers"]:
        idx = idx + 1
        
        print(f"\t\tParser #{idx - 1}")   
        
        if "scraper" in par:
            print(f"\t\t\tScraper => {par['scraper']}")
            
        if "disable" in par:
            print(f"\t\t\tDisabled => {par['disabled']}")
            
        if "url" in par:
            print(f"\t\t\tURL => {par['url']}")
            
        if "protocol" in par:
            print(f"\t\t\tProtocol => {par['protocol']}")
            
        if "findEnabled" in par:
            print(f"\t\t\tFind Enabled => {par['findEnabled']}")
            
        if "findIntervalMin" in par:
            print(f"\t\t\tFind Interval Min => {par['findIntervalMin']}")
            
        if "findIntervalMax" in par:
            print(f"\t\t\tFind Interval Max => {par['findIntervalMax']}")
            
        if "parseEnabled" in par:
            print(f"\t\t\tParse Enabled => {par['parseEnabled']}")
            
        if "parseIntervalMin" in par:
            print(f"\t\t\tParse Interval Min => {par['parseIntervalMin']}")
            
        if "parseIntervalMax" in par:
            print(f"\t\t\tParse Interval Max => {par['parseIntervalMax']}")
            
        if "parseExisting" in par:
            print(f"\t\t\tParse Existing => {par['parseExisting']}")
            
        if "parseNew" in par:
            print(f"\t\t\tParse New => {par['parseNew']}")
            
        if "addEnabled" in par:
            print(f"\t\t\tAdd Enabled => {par['addEnabled']}")
            
        if "addIntervalMin" in par:
            print(f"\t\t\tAdd Interval Min => {par['addIntervalMin']}")
            
        if "addIntervalMax" in par:
            print(f"\t\t\tAdd Interval Max => {par['addIntervalMax']}")
            
        if "addExisting" in par:
            print(f"\t\t\tAdd Existing => {par['addExisting']}")
            
        if "addNew" in par:
            print(f"\t\t\tAdd New => {par['addNew']}")
            
        if "testMode" in par:
            print(f"\t\t\tTest Mode => {par['testMode']}")
            
        if "skipNullCategory" in par:
            print(f"\t\t\tSkip Null Category => {par['skipNullCategory']}")
            
        if "logPageFailOutput" in par:
            print(f"\t\t\tLog Page Fail Output => {par['logPageFailOutput']}")
            
        if "cleanupBanners" in par:
            print(f"\t\t\tCleanup Banners => {par['cleanupBanners']}")
        
        if "categories" in par:
            print("\t\t\tCategories (Name => ID)")
            for k, v in par["categories"].items():
                print(f"\t\t\t\t{k} => {v}")
                
                # Look for category children.
                if "catsChildren" in par and k in par["catsChildren"]:
                    for k2, v2 in par["catsChildren"][k].items():
                        print(f"\t\t\t\t\t{k2} => {v2}")
                        
        if "avoidIds" in par:
            print("\t\t\tAvoid IDs")
            for id in par["avoidIds"]:
                print(f"\t\t\t\t- {id}")

def getCfg() -> list[str, any]:
    return cfg