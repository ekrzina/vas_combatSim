from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import asyncio
from spade import wait_until_finished
import spade

class DM(Agent):
    self.var = "help"
    async def setup(self):
        print("The DM Enters the Game!")
        await asyncio.sleep(1)
        ponasanje = self.DMBehaviour()
        self.add_behaviour(ponasanje)

    class DMBehaviour(CyclicBehaviour):
        # gives first player initiative
        async def on_start(self):
            print("Startam")   
            self.npc_turn = 0
            await asyncio.sleep(1)
        async def run(self):
            print(self.agent.jid)
            self.npc_turn += 1
            await asyncio.sleep(1)
            if self.npc_turn > 3:
                # stops behaviour
                self.kill()
        async def on_end(self):
            # stops agent
            await self.agent.stop()
            print("Ending myself...")

async def going():
    dm = DM("dungeonmaster@localhost", "tajna")
    await dm.start()

    await wait_until_finished(dm)
    
if __name__ == "__main__":
    spade.run(going())

