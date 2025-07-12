import config
import database

cfg = config.loadCfg("/etc/scanrus/settings.json")
dbInfo = cfg["database"]

database.init(dbInfo["host"], dbInfo["name"], dbInfo["user"], dbInfo["pass"], dbInfo["port"])

src, err = database.AddSource("gamecom.io", "Gamecom")

if err is not None:
    print("Error creating source gamecom!")
    print(err)
else:
    print("Created source gamecom!")
    print(src)
    
src, err = database.AddSource("bestmods.io", "Best Mods")

if err is not None:
    print("Error creating source bestmods!")
    print(err)
else:
    print("Created source bestmods!")
    print(src)
    
src, err = database.GetSource("bestmods.io")

if err is not None:
    print("Error retrieving source bestmods")
    print(err)
else:
    print("Got source bestmods")
    print(src)
    
src, err = database.GetSource("moddingcommunity.com")

if err is not None:
    print("Error retrieving source moddingcommunity")
    print(err)
else:
    print("Got source moddingcommunity!")
    print(src)
    
srcs, err = database.GetSources()

if err is not None:
    print("Error receiving 10 sources!")
    print(err)
else:
    print("Retrieved 10 sources!")
    print(srcs)
    print(srcs[0].name)
    
err = database.DeleteSource("bestmods.io")

if err is not None:
    print("Error deleting bestmods")
    print(err)
else:
    print("Deleted bestmods!")

err = database.DeleteSource("gamecom.io")

if err is not None:
    print("Error deleting gamecom")
    print(err)
else:
    print("Deleted gamecom!")
    