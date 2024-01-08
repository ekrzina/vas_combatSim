# simulates combat
from time import sleep

global game_over, turns

def print_initiatives(enemy, hero):
        print(f"{enemy.name}'s initiative:  {enemy.initiative}\n")
        print(f"{hero.name}'s initiative:   {hero.initiative}\n")

def roll_initiative(enemy, hero):
    enemy.add_initiative()
    hero.add_initiative()
    print_initiatives(enemy, hero)

def choose_target(attacker, list):
     # check if agent is enemyor ally
     pass

def choose_attack(attacker):
     # randomly pick attack
     pass

def attack(agent_list):
    global game_over, turns
    for attacker in agent_list:
        # import agent behaviour, based on class they act differently, attack from there
        target = choose_target(attacker, agent_list)
        selected_attack = choose_attack(attacker)
        attacker.perform_attack(target, selected_attack)

        sleep(0.5)

        if target.hp <= 0:
            print(f"{target.name} has been defeated!")
            game_over = True
            print(f"Enemies defeated in {turns} turns!")

        sleep(2)

# combat goes through three main phases: initiantive roll, attacks and go to next battle if game isn't over
def startCombat(enemy, hero):
    global turns, game_over
    game_over = False
    turns = 0

    roll_initiative(enemy, hero)
    agent_list = [enemy, hero]
    # sort list based on initiative
    agent_list = sorted(agent_list, key=lambda x: x.initiative, reverse=True)
    
    while(game_over==False):
        # start of turn
        turns += 1
        # all attack
        attack(agent_list)
