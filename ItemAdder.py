import py_mcws
from MinecraftWS import MinecraftWebSocket, Event
import json
import queue
from os import path
folder="All Items\\items"
itemName=queue.Queue()

class MyWsClient(py_mcws.WsClient):
    def event_ready(self):
        print(f"Ready {self.host}:{self.port}")

        self.events = ["PlayerMessage", "PlayerDied","ItemAcquired"]
    
    async def event_connect(self):
        print("Connected!")

        await self.command("say Hello")
    
    async def event_disconnect(self):
        print("disconnect!")

    async def event_PlayerMessage(self, event):
        print( event)
        if event[0]['body']["properties"]["Message"][0]=="!":
            item=event[0]['body']["properties"]["Message"][1:]
            itemName.queue.clear()
            itemName.put(item)
            print(item)
            await self.command("w @s pick up some {}".format(item))
    async def event_ItemAcquired(self, event):
        if not(itemName.empty()):
            testName=itemName.get()
            for ev in event:
                item=ev["body"]["properties"]["Type"]
                index=ev["body"]["properties"]["AuxType"]
                values={"item":item,"index":index}            
                with open(path.join(folder,"{}.json").format(testName),"w+") as file:
                    json.dump(values,file,indent=2)
                await self.command("w @s {}  pickedup".format(testName))
        
    async def event_PlayerDied(self, event):
        print(event)
        
val=dir(Event)
for ev in val:
    print(ev)


MyWsClient().start(host="localhost", port=1234)


