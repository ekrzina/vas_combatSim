from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from spade import wait_until_finished
import random
import json
import pygame
from PIL import Image
import os

global agent_list

def show_picture(ago):
        if ago.pct:
            try:
                img_path = os.path.join(os.path.dirname(__file__), ago.pct)
                img = Image.open(img_path)
                img = img.convert("RGBA")

                target_size = (450, 420)
                img = img.resize(target_size)

                img_data = img.tobytes()

                pygame.init()
                screen = pygame.display.set_mode(target_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
                pygame.display.set_caption("Agent Picture")

                img_surface = pygame.image.fromstring(img_data, target_size, "RGBA")
               
                font = pygame.font.Font(None, 24)
                text_name = font.render(f"HP left: {ago.hp}", True, (0, 0, 0))                
                text_name_rect = text_name.get_rect(center=(target_size[0] // 2, target_size[1] - 20))

                clock = pygame.time.Clock()

                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

                    screen.fill((255, 255, 255))
                    screen.blit(img_surface, (0, 0))
                    screen.blit(text_name, text_name_rect)

                    pygame.display.flip()
                    clock.tick(0)

                pygame.quit()

            except Exception as e:
                print(f"Error displaying picture: {e}")    
    
class DM(Agent):
    # na pocetku DM salje poruku s flagom iducem agentu u listi
    def __init__(self, jid, password, agents):
        super().__init__(jid, password)
        global agent_list
        agent_list = agents
        self.npc_turn = 0
        self.battle_duration = 1
    
    async def setup(self):
        print("The DM Enters the Game!")
        await asyncio.sleep(2)
        ponasanje = self.DMBehaviour()
        self.add_behaviour(ponasanje)

    class DMBehaviour(CyclicBehaviour):
        global agent_list
        # gives first player initiative
        async def on_start(self):

            to_whom_it_may_concern = agent_list[self.agent.npc_turn].jid
            starting_turn_msg = Message(
                to=str(to_whom_it_may_concern),
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
            print(f"---------TURN-{self.agent.battle_duration}---------")
            print("-----------------------")
            msg = await self.receive(timeout=15)
            if msg:
                both = self.check_participants()
                    # if there are more players than 1
                    # and there are both enemies and allies
                if both == True:
                    self.agent.npc_turn += 1
                        # check if len - 1 later
                    if self.agent.npc_turn > len(agent_list) - 1:
                        self.agent.npc_turn = 0
                        self.agent.battle_duration += 1
                        
                        # send message to start to next player
                    next_player = agent_list[self.agent.npc_turn].jid
                    turn_msg = Message(
                        to=str(next_player),
                        body="go",
                        metadata={
                            "ontology": "initiative",
                            "performative": "inform"
                        }
                    )
                    await self.send(turn_msg)

                else:
                    print(f"The Game has Been Decided! It lasted {self.agent.battle_duration} turns. The victors are:")
                    for agent in agent_list:
                            print(f"{agent.nname} with {agent.hp} left!")
                            show_picture(agent)
                            
                    self.kill()
            else:
                print(f"Player {agent_list[self.agent.npc_turn].name} is not responding.")
        
        # sends messages to stop players one by one
        async def on_end(self):
            print(f"Cleaning up Game...\n")
            await asyncio.sleep(2)
            for a in agent_list:
                end_msg = Message(
                    to=str(a.jid),
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
            
class EnemyNPC(Agent):

    def __init__(self, jid, password, enemy):
        super().__init__(jid, password)
        self.nname = enemy.name
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
        self.initiative = enemy.initiative

    async def setup(self):
        print(f"Enemy {self.nname} enters the battlefield!")
        await asyncio.sleep(2)
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
            dmge = int(attack.get("dmg"))
            notes = ""

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dmge -= target.pdef
            
            if(dmge >= 0):
                my_type = attack.get("element")

                if target.get("weakness") == my_type:
                    dmge *= 2
                    notes += "W"

            else:
                dmge = 0

            return round(dmge), notes

        async def run(self):
            msg = await self.receive(timeout = 60)
            if msg:
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack()
                    dmg, notes = self.calculate_damage(attack, target)
                        
                        # send message to give damage to target
                    damage_message = Message(
                        to=str(target.jid),
                        body=json.dumps((dmg, notes)),  # Serialize the tuple into a string
                        metadata={
                            "ontology": "damage",
                            "performative": "inform"
                        }
                    )

                    
                    await self.send(damage_message)
                    print(f"{self.agent.nname} used {attack.get('name')} on {target.nname}, dealing {dmg} HP!")
                    await asyncio.sleep(2) 

                    end_turn_msg = Message(
                            to="dungeonmaster@localhost",
                            body="done",
                            metadata={
                                "ontology": "initiative",
                                "performative": "inform"
                            }
                        )
                    await self.send(end_turn_msg)

                    try:
                        ack_msg = await self.receive(timeout=60)
                        if ack_msg and ack_msg.body == "done":
                            print(f"Received acknowledgment from DM. Ending turn.")
                        else:
                            print("DM did not acknowledge. Something went wrong!")
                    except Exception as e:
                        print(f"Error in acknowledgment handling: {e}")

                    # takes damage
                elif ontology == "damage":
                    current_hp = int(self.agent.hp)
                    damage_value, notes = json.loads(msg.body)
                    current_hp = current_hp - int(damage_value)
                    if current_hp <= 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.nname} was defeated!")
                        await asyncio.sleep(2)
                        self.kill()

                elif ontology == "gameover":
                    self.agent.stop()

        async def on_end(self):
            damage_message = Message(
                            to="dungeonmaster@localhost",
                            body="done",
                            metadata={
                                "ontology": "initiative",
                                "performative": "inform"
                            }
                        )
            await self.send(damage_message)     

class AllyNPC(Agent):

    def __init__(self, jid, password, ally):
        super().__init__(jid, password)
        self.nname = ally.name
        self.hp = ally.hp
        self.atk = ally.atk
        self.pdef = ally.pdef
        self.spatk = ally.spatk
        self.spdef = ally.spdef
        self.attack_list = ally.attack_list
        self.weakness = ally.weakness
        self.pct = ally.pct
        self.initiative = ally.initiative

    async def setup(self):
        print(f"Ally {self.nname} enters the battlefield!")
        await asyncio.sleep(2)
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
            dmge = int(attack.get("dmg"))
            notes = ""

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dmge -= target.pdef
            
            if(dmge >= 0):
                my_type = attack.get("element")

                if target.get("weakness") == my_type:
                    dmge *= 2
                    notes += "W"
                elif target.get("strength") == my_type:
                    dmge *= 0.5
                    notes += "S"
                elif target.get("immunity") == my_type:
                    dmge *= 0
                    notes += "I"

            else:
                dmge = 0

            return round(dmge), notes

        async def run(self):
            msg = await self.receive(timeout = 60)
            if msg:
                print(f"That's me, {self.agent.nname}")
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack()
                    dmg, notes = self.calculate_damage(attack, target)
                        
                        # send message to give damage to target
                    damage_message = Message(
                        to=str(target.jid),
                        body=json.dumps((dmg, notes)),  # Serialize the tuple into a string
                        metadata={
                            "ontology": "damage",
                            "performative": "inform"
                        }
                    )

                        # send the message, then stop the behaviour
                    await self.send(damage_message)
                    print(f"{self.agent.nname} used {attack.get('name')} on {target.nname}, dealing {dmg} HP!")
                    await asyncio.sleep(2) 

                    end_turn_msg = Message(
                        to="dungeonmaster@localhost",
                        body="done",
                        metadata={
                            "ontology": "initiative",
                            "performative": "inform"
                        }
                    )
                    await self.send(end_turn_msg)

                    try:
                        ack_msg = await self.receive(timeout=60)
                        if ack_msg and ack_msg.body == "done":
                            print(f"Received acknowledgment from DM. Ending turn.")
                        else:
                            print("DM did not acknowledge. Something went wrong!")
                    except Exception as e:
                        print(f"Error in acknowledgment handling: {e}")

                    # takes damage
                elif ontology == "damage":
                    current_hp = int(self.agent.hp)
                    damage_value, notes = json.loads(msg.body)
                    current_hp = current_hp - int(damage_value)
                    if current_hp <= 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.nname} was defeated!")
                        await asyncio.sleep(2)
                        self.kill()

                elif ontology == "gameover":
                    self.agent.stop()

        async def on_end(self):
            damage_message = Message(
                            to="dungeonmaster@localhost",
                            body="done",
                            metadata={
                                "ontology": "initiative",
                                "performative": "inform"
                            }
                        )
            await self.send(damage_message)

            