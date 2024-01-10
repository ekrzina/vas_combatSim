from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import asyncio
from spade.message import Message

class DM(Agent):

    async def setup(self):
        print("The DM Enters the Game!")
        behaviour = self.DMBehaviour()
        self.add_behaviour(behaviour)

    class DMBehaviour(CyclicBehaviour):
        
        async def on_start(self):
            self.loop = 0
            self.mah = True
            print("Startam")
            msg = Message(
                to="player1@localhost",
                body="DM: Go",
                metadata={
                    "ontology": "initiative",
                    "performative": "inform"
                }
            )
            await self.send(msg)

        async def run(self):
            while self.mah==True:
                self.loop += 1
                if self.loop > 3:
                    self.mah = False
                msg = await self.receive(timeout=60)
                if msg:
                    
                    print(msg.sender)
                    if(msg.sender.localpart == "player1"):
                        to_who = "player2@localhost"
                    else:
                        to_who = "player1@localhost"

                    print(msg.body)
                    msg = Message(
                    to=to_who,
                    body="DM: Go",
                    metadata={
                        "ontology": "initiative",
                        "performative": "inform"
                    }
                    )
                    await self.send(msg)


        async def on_end(self):
            # await self.agent.stop()
            print("Ending myself...")


class Player(Agent):

    async def setup(self):
        print(f"{self.name} Enters the Game!")
        behaviour = self.PlayerBehaviour()
        self.add_behaviour(behaviour)

    class PlayerBehaviour(CyclicBehaviour):

        async def run(self):
            while 1:
                msg = await self.receive(timeout=60)
                if msg:
                    print(msg.body)
                    reply_msg = msg.make_reply()
                    reply_msg.body = f"{self.agent.name}: Hello from {self.agent.name}"
                    await self.send(reply_msg)

        async def on_end(self):
            await self.agent.stop()

async def going():
    player1 = Player("player1@localhost", "tajna")
    await player1.start()

    player2 = Player("player2@localhost", "tajna")
    await player2.start()

    dm = DM("dungeonmaster@localhost", "tajna")
    await dm.start()

    await asyncio.gather(player1.stop(), player2.stop(), dm.stop())

if __name__ == "__main__":
    asyncio.run(going())
