from datetime import datetime

def debugMsg(cfg: dict[str, any], reqLevel: int, msg: str):
    curDate = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    
    if cfg["debug"] >= reqLevel:
        fMsg = f"[D{reqLevel}][{curDate}] {msg}"
         
        print(fMsg)
        
        if cfg["logFile"] is not None:
            with open(cfg["logFile"], "a+") as f:
                f.write(fMsg + "\n")