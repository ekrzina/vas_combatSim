from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from actors.actors import Enemy, Hero

class DM(Agent):
    # na pocetku DM salje poruku s flagom iducem agentu u listi
    def __init__(self, jid, password, agent_list):
        super().__init__(jid, password)
        self.agent_list = agent_list
    
    async def setup(self):
        print("The DM Enters the Game!")
        await asyncio.sleep(1)

    async def on_start(self):
        print("Bleh")


class EnemyNPC(Agent, Enemy):

    def __init__(self, jid, password, enemy):
        super().__init__(jid, password)
        self.name = enemy.name
        self.hp = enemy.hp
        self.atk = enemy.atk
        self.pdef = enemy.pdef
        self.spatk = enemy.spatk
        self.spdef = enemy.spdef
        self.attack_list = enemy.attack_list
        self.weakness = enemy.weakness
        self.pct = enemy.pct
        self.initiative = enemy.initiantive

    async def setup(self):
        print(f"Enemy {self.name} enters the battlefield!")
        await asyncio.sleep(1)
    
    def change_initiative(self, ini):
        self.initiantive = ini
    
    class DMBehaviour(CyclicBehaviour):
        # sends messages to stop players one by one
        async def on_end(self) -> None:
            return await super().on_end()
        
        async def on_start(self) -> None:
            return await super().on_start()


class AllyNPC(Agent, Hero):

    def __init__(self, jid, password, ally):
        super().__init__(jid, password)
        self.name = ally.name
        self.hp = ally.hp
        self.atk = ally.atk
        self.pdef = ally.pdef
        self.spatk = ally.spatk
        self.spdef = ally.spdef
        self.attack_list = ally.attack_list
        self.weakness = ally.weakness
        self.pct = ally.pct
        self.initiative = ally.initiantive

    async def setup(self):
        print(f"Ally {self.name} enters the battlefield!")
        await asyncio.sleep(1)
    
    def change_initiative(self, ini):
        self.initiantive = ini

# import agent behaviour, based on class they act differently, attack from there
     #   target = choose_target(attacker, agent_list)
     #   selected_attack = choose_attack(attacker)
     #   attacker.perform_attack(target, selected_attack)
