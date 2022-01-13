import py_mcws
from MinecraftWS import MinecraftWebSocket, Event
import json
import queue
from os import path
import glob
import copy
import numpy as np

from PIL import Image
itemQue=queue.Queue

class MyWsClient(py_mcws.WsClient):
    def event_ready(self):
        print(f"Ready {self.host}:{self.port}")

        self.events = ["ItemAcquired"]
    
    async def event_connect(self):
        print("Connected!")
        await self.command("w @s Connected to Challenges")
    async def event_PlayerMessage(self, event):
        event
        global ch
        msg=event[0]['body']["properties"]["Message"]
        print(msg)
        if "!list" in msg:
            msg=msg.split(" ")
            print(msg)
            filt=" ".join(msg[1:])
            items = copy.copy(ch.remainingItems)
            if len(msg)>1:
                items = [string for string in items if filt in string]
            retString=", ".join(items)
            print(retString)
            await self.command("w {} {}".format(event[0]['body']["properties"]["Sender"],retString))
    async def event_disconnect(self):
        print("disconnect!")
    async def event_PlayerDied(self, event):
        event
    async def event_ItemAcquired(self, event):
        global ch
        print(type(ch))
    
        for ev in event:
            item=ev["body"]["properties"]["Type"]
            index=ev["body"]["properties"]["AuxType"]
            print("here")
            ret=ch.foundItem(item, index)
            
            await self.command("say "+ret)
class challenge:
    def __init__(self,folder):
        self.folder=folder
        self.prgs_overlay=Image.open("progress_overlay.png")
        self.prgs_overlay.convert("RGBA")
        self.color=np.array((0,255,0,255),dtype=np.uint8)
        self.save={}
        self.loadItems()
        self.updateProgress()
        self.loadSave()
    def setColor(self,color):
        self.color=color
    def loadItems(self):
        items=glob.glob(path.join(self.folder,"items","*.json"))
        self.items={}
        self.remainingItems=[]
        for item in items:
            name= path.basename(item).replace(".json","")
            with open(item) as file:
                data=json.load(file)
            if data["item"] not in self.items.keys():
                self.items[data["item"]]={}
            self.items[data["item"]][data["index"]]=name
            self.remainingItems.append(name)
        self.totalItems=len(self.remainingItems)
    def updateProgress(self):
        percentage=(self.totalItems-len(self.remainingItems))/self.totalItems
        width,height=self.prgs_overlay.size
        bg=np.zeros((height,width,4),dtype=np.uint8)
        progress=int(width*percentage)
        bg[4:-4,1:progress]=self.color
        img = Image.fromarray(bg, 'RGBA')
        img.paste(self.prgs_overlay,(0,0),self.prgs_overlay)
        img.save('progress.png')
        with open("progress.txt","w+") as file:
            file.write("{}/{}".format(self.totalItems-len(self.remainingItems),self.totalItems))
    def loadSave(self):
        if path.exists(path.join(self.folder,"save.json")):
            print("loading save")
            with open(path.join(self.folder,"save.json")) as file:
                self.loaded=json.load(file)
        else:
            self.loaded={}
            print("new game, ")
        prevFoundItems=list(self.save.keys())
        for item in self.loaded.keys():
            for index in self.loaded[item].keys():
                self.foundItem(int(item), int(index))
        print("{} items left to find out of {}".format(len(self.remainingItems),self.totalItems))
    def foundItem(self,item, index,save=False):
        print("here")
        if item in self.items.keys():
            if index in self.items[item].keys():
                name=self.items[item][index]
                if name in self.remainingItems:
                    self.remainingItems.remove(name)
                    if item not in self.save.keys():
                        self.save[item]={}
                    self.save[item][index]=name
                    with open(path.join(self.folder,"save.json"),"w+") as file:
                        json.dump(self.save,file,indent=2)
                    if len(self.remainingItems)==0:
                        self.winner()
                    text=("found item {}, {}/{}".format(name,self.totalItems-len(self.remainingItems),self.totalItems))
                    print(text)
                    with open("last found.txt","w+") as file:
                       file.write(name)
                    self.updateProgress()
        return text
    def winner(self):
        pass
            



if __name__ == "__main__":
    ch=challenge("All Items")
    MyWsClient().start(host="localhost", port=1234)
    
    
