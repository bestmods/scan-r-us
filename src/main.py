import argparse
import sys
import time

from debugger import debugMsg
from parsers import SetupParsers

from config import loadCfg, printCfg, getCfg

def main():
    # Parse and add command-line arguments.
    parser = argparse.ArgumentParser(
        prog = "Scan R Us",
        description="Best Mods' web scraper.",
        epilog="Visit bestmods.io!"
    )
    
    parser.add_argument("-c", "--cfg",
        help="Location to config file.",
        default="settings.json"
    )
    
    parser.add_argument("-l", "--list",
        help = "Whether to list config rules or not.",
        default=False,
        action="store_true"
    )

    args = parser.parse_args()
    
    # Load config file.
    loadCfg(args.cfg)
    
    if args.list is True:
        printCfg()
        
        return
    
    # Retrieve config.
    cfg = getCfg()
    
    debugMsg(cfg, 2, f"Config JSON => {cfg}")
        
    # Check if we have a binary path for Selenium.
    if cfg["binaryPath"] is None:
        debugMsg(cfg, 0, "No binary path for Selenium. Exiting...")
        
        sys.exit(1)
    
    # Attempt to setup parsers.
    try:
        SetupParsers(cfg)
    except Exception as e:
        debugMsg(cfg, 0, "Error setting up parsers.")
        debugMsg(cfg, 0, e)
        
        sys.exit(1)
    
    try:
        while True:
            time.sleep(1)
    except:
        sys.exit(0)

if __name__ == "__main__":
    main()