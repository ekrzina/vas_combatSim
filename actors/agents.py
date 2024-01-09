from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from actors.actors import Enemy, Hero
from spade import wait_until_finished
import random

global agent_list

class DM(Agent):
    # na pocetku DM salje poruku s flagom iducem agentu u listi
    def __init__(self, jid, password, agents):
        super().__init__(jid, password)
        global agent_list
        agent_list = agents
    
    async def setup(self):
        print("The DM Enters the Game!")
        await asyncio.sleep(1)
        ponasanje = self.DMBehaviour()
        self.add_behaviour(ponasanje)

    class DMBehaviour(CyclicBehaviour):
        global agent_list
        # gives first player initiative
        async def on_start(self):
            self.battle_duration = 1
            self.npc_turn = 0

            to_whom_it_may_concern = agent_list[self.npc_turn].jid
            starting_turn_msg = Message(
                to=to_whom_it_may_concern,
                body="go",
                metadata={
                    "ontology": "initiative",
                    "performative": "inform"
                }
            )
            await self.send(starting_turn_msg)

        # checks whether both enemies and allies are in the game
        def check_participants(self):
            has_enemy = False
            has_ally = False

            for agent in agent_list:
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
            print("-----------------------")
            print(f"-------TURN-{self.battle_duration}-------")
            print("-----------------------")
            msg = await self.receive(timeout=15)
            if msg:
                both = self.check_participants()
                # if there are more players than 1
                # and there are both enemies and allies
                if both == True:
                    self.npc_turn += 1
                    # check if len - 1 later
                    if self.npc_turn > len(agent_list) - 1:
                        self.npc_turn = 0
                        self.battle_duration += 1
                    
                    # send message to start to next player
                    next_player = agent_list[self.npc_turn].jid
                    agent_data = self.setup_agent_data()
                    starting_turn_msg = Message(
                        to=next_player,
                        body="go",
                        metadata={
                            "ontology": "initiative",
                            "performative": "inform",
                            "agent_data": agent_data
                        }
                    )
                    await self.send(starting_turn_msg)

                else:
                    print(f"The Game has Been Decided! It lasted {self.battle_duration} turns. The victors are: \n")
                    for agent in agent_list:
                        print(agent.name)
                        agent.show_picture()
                    
                    self.kill()

            else:
                print(f"Player {agent_list[self.npc_turn].name} is not responding.")
        
        # sends messages to stop players one by one
        async def on_end(self):
            print(f"Cleaning up Game...\n")
            for a in agent_list:
                end_msg = Message(
                    to=a.jid,
                    body="bye",
                    metadata={
                        "ontology": "gameover",
                        "performative": "inform"
                    } 
                )
                await self.send(end_msg)
                # wait until the player is finished
                await wait_until_finished(a)
            # at the end, end self
            await self.agent.stop()
            
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
        print(f"Enemy {self.agent.name} enters the battlefield!")
        await asyncio.sleep(1)
        ponasanje = self.EnemyBehaviour()
        self.add_behaviour(ponasanje)
    
    class EnemyBehaviour(CyclicBehaviour):
        global agent_list
        
        def pick_target(self):
            target_candidates = [ag for ag in agent_list if isinstance(ag, AllyNPC)]
            return random.choice(target_candidates) if target_candidates else None

        def pick_attack(self):
            return random.choice(self.agent.attack_list)

        def calculate_damage(self, attack, target):
            dmge = int(attack.data.get("dmg", 0))

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dgme -= target.pdef
            
            if(dgme >= 0):
                my_type = attack.get("element")

                if my_type == self.agent.strength:
                    dmge *= 1.5

                if target.get("weakness") == my_type:
                    dmge *= 2
            else:
                dmge = 0

            return round(dmge)

        async def run(self):
            msg = await self.receive(timeout = 60)
            if msg:
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack()
                    dmg = self.calculate_damage(attack, target)
                    # send message to give damage to target
                    damage_message = Message(
                        to=target.jid,
                        body=str(dmg),
                        metadata={
                            "ontology": "damage",
                            "performative": "inform"
                        }
                    )
                    await self.send(damage_message)
                    print(f"{self.agent.name} used {attack} on {target.name}!")
                    await asyncio.sleep(1) 

                    # now reply to message
                    reply_msg = msg.make_reply()
                    reply_msg.body = ""
                    await self.send(msg)

                # takes damage
                elif ontology == "damage":
                    current_hp = int(self.agent.hp)
                    current_hp = current_hp - int(msg.body)
                    if current_hp <= 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.name} was defeated!")
                        await asyncio.sleep(1)
                        self.kill()

                elif ontology == "gameover":
                    self.kill()

        async def on_end(self):
            await self.agent.stop()

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
        ponasanje = self.AllyBehaviour()
        self.add_behaviour(ponasanje)
    
    class AllyBehaviour(CyclicBehaviour):
        global agent_list
        
        def pick_target(self):
            target_candidates = [ag for ag in agent_list if isinstance(ag, EnemyNPC)]
            return random.choice(target_candidates) if target_candidates else None

        def pick_attack(self):
            return random.choice(self.agent.attack_list)

        def calculate_damage(self, attack, target):
            dmge = int(attack.data.get("dmg", 0))

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dgme -= target.pdef
            
            if(dgme >= 0):
                my_type = attack.get("element")

                if target.get("weakness") == my_type:
                    dmge *= 2
                elif target.get("strength") == my_type:
                    dmge *= 0.5
                elif target.get("immunity") == my_type:
                    dmge *= 0

            else:
                dmge = 0

            return round(dmge)

        async def run(self):
            msg = await self.receive(timeout = 60)
            if msg:
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack()
                    dmg = self.calculate_damage(attack, target)
                    # send message to give damage to target
                    damage_message = Message(
                        to=target.jid,
                        body=str(dmg),
                        metadata={
                            "ontology": "damage",
                            "performative": "inform"
                        }
                    )
                    await self.send(damage_message)
                    print(f"{self.agent.name} used {attack} on {target.name}!")
                    await asyncio.sleep(1)  

                    # now reply to message
                    reply_msg = msg.make_reply()
                    reply_msg.body = ""
                    await self.send(msg)

                # takes damage
                elif ontology == "damage":
                    current_hp = int(self.agent.hp)
                    current_hp = current_hp - int(msg.body)
                    if current_hp <= 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.name} was defeated!")
                        await asyncio.sleep(1)
                        self.kill()

                elif ontology == "gameover":
                    self.kill()

        async def on_end(self):
            await self.agent.stop()