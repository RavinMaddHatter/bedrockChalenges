import gameManager
from tkinter import *
import glob

import threading
import asyncio


def startWebServer(host,port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    gameManager.MyWsClient().start(host=host, port=port)

def startWebServerThread():
    host="localhost"
    port=portvar.get()
    t1=threading.Thread(target=startWebServer,args=(host, port,))
    t1.start()

def startChallenge():
    gameManager.ch=gameManager.challenge(challengeSelected.get())
    startWebServerThread()
def getDirectories():
    directories = glob.glob("*/")
    directories=[ x for x in directories if "__pycache__" not in x ]
    retDirs=[]
    for directory in directories:
        retDirs.append(directory.replace("\\",""))
    return retDirs

root = Tk()
challengeSelected = StringVar(root)
portvar=IntVar(root)
w = OptionMenu(root, challengeSelected, *getDirectories())

button = Button(root, text="start", command=startChallenge)
portent=Entry(root,textvariable=portvar)
portent.pack()
w.pack()
button.pack()



