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
        self.npc_turn = 0
        await asyncio.sleep(1)

    class DMBehaviour(CyclicBehaviour):
        # sends messages to stop players one by one
        async def on_end(self) -> None:
            return await super().on_end()
        
        # gives first player initiative
        async def on_start(self):
            to_whom_it_may_concern = str(self.agent_list[self.npc_turn].jid)
            starting_turn_msg = Message(
                to=to_whom_it_may_concern,
                body="go",
                metadata={
                    "ontology": "initiative",
                    "performative": "inform"
                }
            )
            await self.send(starting_turn_msg)
         
        def process_the_body(self, msg):
            if msg.body == "defeated":
                defeated_player = self.agent_list[self.npc_turn]
                self.agent_list.remove(defeated_player)
                print(f"Player {defeated_player.name} has been defeated and removed from the list.")

        # checks whether both enemies and allies are in the game
        def check_participants(self):
            has_enemy = False
            has_ally = False

            for agent in self.agent_list:
                if isinstance(agent, EnemyNPC):
                    has_enemy = True
                elif isinstance(agent, AllyNPC):
                    has_ally = True

            if has_ally == True and has_enemy == True:
                return True
            else:
                return False

        async def run(self):
            # waits for player to respond
            msg = await self.receive(timeout=10)
            if msg:
                # process message body using self.process_the_body
                self.process_the_body(msg)
                both = check_participants()
                # if there are more players than 1
                # and there are both enemies and allies
                if len(self.agent_list) > 1 and both == True:
                    
                    self.npc_turn += 1
                    if self.npc_turn > len(self.agent_list):
                        self.npc_turn = 0
                    
                    # send message to start to next player
                    next_player = str(self.agent_list[self.npc_turn].jid)
                    starting_turn_msg = Message(
                        to=next_player,
                        body="go",
                        metadata={
                            "ontology": "initiative",
                            "performative": "inform"
                        }
                    )
                    await self.send(starting_turn_msg)

                else:
                    print(f"The Game has Been Decided! The victors are: \n")
                    for agent in self.agent_list:
                        print(agent.name)

                # give turn to the next player in line

            else:
                print(f"Player {self.agent_list[self.npc_turn].name} is not responding.")


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
        self.strength = enemy.strength
        self.immune = enemy.immune
        self.initiative = enemy.initiantive

    async def setup(self):
        print(f"Enemy {self.name} enters the battlefield!")
        await asyncio.sleep(1)
    
    def change_initiative(self, ini):
        self.initiantive = ini
    
    


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
