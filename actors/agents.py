from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from spade import wait_until_finished
import random
import pygame
from PIL import Image
import os
from pyswip import Prolog

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
                text_name = font.render(f"HP left: {ago.combat_hp}", True, (0, 0, 0))                
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
                    clock.tick(30)

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

        async def on_start(self):
            await self.start_turn()

        async def start_turn(self):
            
            if self.agent.npc_turn < len(agent_list):
                # first print banner
                await asyncio.sleep(2) 
                print("-----------------------")
                print(f"---------TURN-{self.agent.battle_duration}---------")
                print("-----------------------")
                await asyncio.sleep(2) 
                
                # now send msg
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

        async def run(self):
            msg = await self.receive(timeout=60)
            if msg:
                both = self.check_participants()
                if both:
                    self.agent.npc_turn += 1
                    if self.agent.npc_turn > len(agent_list) - 1:
                        self.agent.npc_turn = 0
                        self.agent.battle_duration += 1
                    await self.start_turn()
                else:
                    print(f"The Game has Been Decided! It lasted {self.agent.battle_duration} turns. The victors are:")
                    for agent in agent_list:
                        print(f"{agent.nname} with {agent.combat_hp} HP left!")
                        show_picture(agent)
                    self.kill()
            else:
                print(f"Player {agent_list[self.agent.npc_turn].name} is not responding.")

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
                await wait_until_finished(a)
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

        # setting up knowledge base
        self.prolog = Prolog()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "enemy_knowledge_base.pl"
        self.file_path = os.path.join(script_dir, file_name).replace('\\', '/')

        ponasanje = self.EnemyBehaviour()
        self.add_behaviour(ponasanje)
        self.combat_hp = self.hp
    
    class EnemyBehaviour(CyclicBehaviour):
        global agent_list

        def write_to_file(self, statement):
            with open(self.agent.file_path, 'a') as file:
                file.write(statement + "\n")

        def pick_target(self):
            target_candidates = [ag for ag in agent_list if isinstance(ag, AllyNPC)]
            return random.choice(target_candidates) if target_candidates else None

        def pick_attack(self, target):
            try:
                self.agent.prolog.consult(self.agent.file_path)
                weakness_result = list(self.agent.prolog.query(f'is_weak_to({target.nname}, Weakness).'))

                if weakness_result:
                    print(f"The enemy knows {target.nname}'s weakness!")
                    target_weakness = weakness_result[0]["Weakness"]
                    matching_weakness_attacks = [attack for attack in self.agent.attack_list if attack.get("element") == target_weakness]

                    if matching_weakness_attacks:
                        chosen_attack = random.choice(matching_weakness_attacks)
                        print(f"...And it attacks {target.nname}'s weakness: {chosen_attack['element']}!")
                        return chosen_attack
                    else:
                        print("But it doesn't seem to act on the weakness.")
                # return something, always    
                return random.choice(self.agent.attack_list)
            
            except Exception as e:
                print(f"Error in pick_attack: {e}")

        def calculate_damage(self, attack, target):
            dmge = int(attack.get("dmg"))

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dmge -= target.pdef

            if(dmge >= 0):
                my_type = attack.get("element")
                weaknesses = target.weakness
                # consult the knowledge base to see whether it has the same weakness for the ally
                # if not, assert into it
                if weaknesses == my_type:
                    dmge *= 2
                    self.agent.prolog.consult(self.agent.file_path)
                    if not list(self.agent.prolog.query(f"is_weak_to({target.nname}, {my_type}).")):
                        print(f"The enemy found {target.nname}'s weakness: {my_type}!")
                        self.write_to_file(f"is_weak_to({target.nname}, {my_type}).")
            else:
                dmge = 0

            return round(dmge)

        async def send_status(self, attack, target):
            status = attack.get("dmg")
            status_message = Message(
                        to=str(target.jid),
                        body=str(status),
                        metadata={
                            "ontology": "status",
                            "performative": "inform"
                        }
                    )
            await self.send(status_message)
            print(f"{self.agent.nname} used {attack.get('name')} on {target.nname} (EFFECT: {status})!")
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

        async def run(self):            
            msg = await self.receive(timeout = 60)
            if msg:
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack(target)

                    # for status moves
                    if attack['type'] == "status":
                        await self.send_status(attack, target)
                    else:
                        dmg = self.calculate_damage(attack, target)
                            
                            # send message to give damage to target
                        damage_message = Message(
                            to=str(target.jid),
                            body=str(dmg),
                            metadata={
                                "ontology": "damage",
                                "performative": "inform"
                            }
                        )

                        await self.send(damage_message)
                        print(f"{self.agent.nname} used {attack.get('name')} on {target.nname}, dealing {dmg} HP!")
                        await asyncio.sleep(3) 

                        end_turn_msg = Message(
                                to="dungeonmaster@localhost",
                                body="done",
                                metadata={
                                    "ontology": "initiative",
                                    "performative": "inform"
                                }
                            )
                        await self.send(end_turn_msg)
                        self.combat_hp = self.agent.combat_hp

                # takes damage
                elif ontology == "damage":
                    current_hp = self.agent.combat_hp
                    damage_value = msg.body
                    current_hp = current_hp - int(damage_value) 
                    if current_hp < 0:
                        current_hp = 0
                    self.agent.combat_hp = current_hp
                    if current_hp == 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.nname} was defeated!")
                        await asyncio.sleep(2)
                        self.kill()

                elif ontology == "gameover":
                    self.kill()

        async def on_end(self):
            await self.agent.stop()    

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
        
        self.prolog = Prolog()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "ally_knowledge_base.pl"
        self.file_path = os.path.join(script_dir, file_name).replace('\\', '/')

        ponasanje = self.AllyBehaviour()
        self.add_behaviour(ponasanje)
        self.combat_hp = self.hp
    
    class AllyBehaviour(CyclicBehaviour):
        global agent_list

        def write_to_file(self, statement):
            with open(self.agent.file_path, 'a') as file:
                file.write(statement + "\n")

        def pick_target(self):
            target_candidates = [ag for ag in agent_list if isinstance(ag, EnemyNPC)]
            return random.choice(target_candidates) if target_candidates else None

        def pick_attack(self, target):
            try:
                self.agent.prolog.consult(self.agent.file_path)
                
                weakness_result = list(self.agent.prolog.query(f'has_weakness({target.nname}, Weakness).'))
                strength_result = list(self.agent.prolog.query(f'has_strength({target.nname}, Strength).'))
                immune_result = list(self.agent.prolog.query(f'is_immune({target.nname}, Immunity).'))

                if weakness_result:
                    print(f"We know the weakness of {target.nname}!")
                    target_weakness = weakness_result[0]["Weakness"]
                    matching_weakness_attacks = [attack for attack in self.agent.attack_list if attack.get("element") == target_weakness]

                    if matching_weakness_attacks:
                        chosen_attack = random.choice(matching_weakness_attacks)
                        print(f"...And I have an attack of the same element as {target.nname}'s weakness: {chosen_attack['name']}!")
                        return chosen_attack
                    else:
                        print("But I don't have an attack that could be used for this weakness.")
                
                elif immune_result:
                    target_im = immune_result[0]["Immunity"]
                    print(f"We know the immunity of {target.nname} ({target_im})!")
                    different_type_attacks = [attack for attack in self.agent.attack_list if attack.get("element") != target_im]

                    if different_type_attacks:
                        chosen_attack = random.choice(different_type_attacks)
                        print(f"...So we will instead use {chosen_attack['name']}!")
                        return chosen_attack
                
                elif strength_result:
                    target_str = strength_result[0]["Strength"]
                    print(f"We know the strength of {target.nname} ({target_str})!")
                    different_type_attacks = [attack for attack in self.agent.attack_list if attack.get("element") != target_str]

                    if different_type_attacks:
                        chosen_attack = random.choice(different_type_attacks)
                        print(f"...So we will instead use {chosen_attack['name']}!")
                        return chosen_attack
                # if nothing is found, return a random attack
                return random.choice(self.agent.attack_list)
            
            except Exception as e:
                print(f"Error in pick_attack: {e}")

        def calculate_damage(self, attack, target):
            dmge = int(attack.get("dmg"))

            if attack.get("type") == "spatk":
                dmge += self.agent.spatk
                dmge -= target.spdef

            elif attack.get("type") == "atk":
                dmge += self.agent.atk
                dmge -= target.pdef
            
            if(dmge >= 0):
                my_type = attack.get("element")
                self.agent.prolog.consult(self.agent.file_path)

                damage_multiplier = 1.0
                weaknesses = target.weakness
                strengths = target.strength
                immunes = target.immune
                
                if my_type == weaknesses:
                    damage_multiplier = 2.0
                    if not list(self.agent.prolog.query(f"has_weakness({target.nname}, {my_type}).")):
                        print(f"We found {target.nname}'s weakness: {my_type}!")
                        self.write_to_file(f"has_weakness({target.nname}, {my_type}).")

                elif my_type == strengths:
                    damage_multiplier = 0.5
                    if not list(self.agent.prolog.query(f"has_strength({target.nname}, {my_type}).")):
                        print(f"We found {target.nname}'s strength: {my_type}!")
                        self.write_to_file(f"has_strength({target.nname}, {my_type}).")

                elif my_type == immunes:
                    damage_multiplier = 0.0
                    if not list(self.agent.prolog.query(f"is_immune({target.nname}, {my_type}).")):
                        print(f"We found {target.nname}'s immunity: {my_type}!")
                        self.write_to_file(f"is_immune({target.nname}, {my_type}).")

                dmge = round(dmge * damage_multiplier)

            else:
                dmge = 0

            return round(dmge)

        async def rather_heal(self, attack):
            # mustn't be themselves!
            target_candidates = [ag for ag in agent_list if isinstance(ag, AllyNPC) and ag != self.agent]            
            sorted_targets = sorted(target_candidates, key=lambda ally: ally.hp)
            if sorted_targets:
                # gets the target that has the least HP
                target_for_healing = sorted_targets[0]
                dmg = attack.get("dmg")
                damage_message = Message(
                            to=str(target_for_healing.jid),
                            body=str(dmg),
                            metadata={
                                "ontology": "heal",
                                "performative": "inform"
                            }
                        )
                # send the message, then stop the behaviour
                await self.send(damage_message)
                print(f"{self.agent.nname} used {attack.get('name')} on {target_for_healing.nname}, healing {dmg} HP!")
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
                self.combat_hp = self.agent.combat_hp

            else:
                print(f"No AllyNPCs found for healing. {self.agent.nname} waits this turn out.")
                end_turn_msg = Message(
                    to="dungeonmaster@localhost",
                    body="done",
                    metadata={
                        "ontology": "initiative",
                        "performative": "inform"
                    }
                )
                await self.send(end_turn_msg)
                self.combat_hp = self.agent.combat_hp

        async def send_status(self, attack, target):
            status = attack.get("dmg")
            status_message = Message(
                        to=str(target.jid),
                        body=str(status),
                        metadata={
                            "ontology": "status",
                            "performative": "inform"
                        }
                    )
            await self.send(status_message)
            print(f"{self.agent.nname} used {attack.get('name')} on {target.nname} (EFFECT: {status})!")
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

        async def run(self):

            msg = await self.receive(timeout = 60)
            if msg:
                ontology = msg.metadata.get("ontology")

                if ontology == "initiative":
                    target = self.pick_target()
                    attack = self.pick_attack(target)

                    # for healers
                    if attack['type'] == "heal":
                        await self.rather_heal(attack)
                    elif attack['type'] == "status":
                        await self.send_status(attack, target)
                    else:
                        dmg = self.calculate_damage(attack, target)
                            
                        damage_message = Message(
                            to=str(target.jid),
                            body=str(dmg),
                            metadata={
                                "ontology": "damage",
                                "performative": "inform"
                            }
                        )

                        # send the message, then stop the behaviour
                        await self.send(damage_message)
                        print(f"{self.agent.nname} used {attack.get('name')} on {target.nname}, dealing {dmg} HP!")
                        end_turn_msg = Message(
                            to="dungeonmaster@localhost",
                            body="done",
                            metadata={
                                "ontology": "initiative",
                                "performative": "inform"
                            }
                        )
                        await self.send(end_turn_msg)
                        self.combat_hp = self.agent.combat_hp
                    
                    # takes damage
                elif ontology == "damage":
                    current_hp = self.agent.combat_hp
                    damage_value= msg.body
                    current_hp = current_hp - int(damage_value)
                    if current_hp < 0:
                        current_hp = 0
                    self.agent.combat_hp = current_hp
                    if current_hp == 0:
                        agent_list.remove(self.agent)
                        print(f"{self.agent.nname} was defeated!")
                        await asyncio.sleep(2)
                        self.kill()

                elif ontology == "heal":
                    current_hp = self.agent.combat_hp
                    heal_value= int(msg.body)
                    max_hp = self.agent.hp

                    if current_hp + heal_value > max_hp:
                        current_hp = max_hp
                    else:
                        current_hp += heal_value

                    self.agent.combat_hp = current_hp

                elif ontology == "gameover":
                    self.kill()

        async def on_end(self):
            await self.agent.stop()