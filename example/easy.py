from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import asyncio
from spade import wait_until_finished
import spade

class DM(Agent):
    # na pocetku DM salje poruku s flagom iducem agentu u listi
    def __init__(self, jid, password):
        super().__init__(jid, password)
    
    async def setup(self):
        print("The DM Enters the Game!")
        self.npc_turn = 0
        await asyncio.sleep(1)

        ponasanje = self.DMBehaviour()
        self.add_behaviour(ponasanje)

    class DMBehaviour(CyclicBehaviour):
        # gives first player initiative
        async def on_start(self):
            print("Startam")
            await asyncio.sleep(1)
        async def run(self):
            print("Started moving")
            self.npc_turn += 1
            if self.npc_turn > 3:
                self.kill()
        async def on_end(self):
            print("Ending myself...")

async def going():
    dm = DM("dm@rec.foi.hr", "tajna")
    await dm.start()

    await wait_until_finished(dm)

if __name__ == "__main__":
    spade.run(going())

