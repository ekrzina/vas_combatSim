# simulates combat
from time import sleep
from actors.agents import DM, EnemyNPC, AllyNPC
from actors.actors import Enemy, Hero
from spade import wait_until_finished
import spade

def print_initiatives(a):
        print(f"{a.name}'s initiative:  {a.initiative}\n")

def roll_initiative(actors):
    for a in actors:
         a.add_initiative()
         print_initiatives(a)

# pukne na kreiranju nove instance; nesto s 
async def create_instance(attacker, i):
    if isinstance(attacker, Enemy):
        new_player = EnemyNPC(f"player{i}@localhost", "tajna", attacker)
    elif isinstance(attacker, Hero):
        new_player = AllyNPC(f"player{i}@localhost", "tajna", attacker)
        print(new_player.hp)
    # starts the new Player
    await new_player.start()
    return new_player

# implement from agent perspective with their behaviour
async def let_agents_loose(agent_list):
    players = []
    i = 1

    # kreiraj broj agenata koji su u listi agenata
    for attacker in agent_list:
        # create agent with attacker behavior (for now)
        new_player = await create_instance(attacker, i)
        i += 1
        players.append(new_player)

    # svi su agenti pripremljeni i cekaju poruke
    # kreiraj prvog agenta koji je DM
    # DM salje poruke agentu po redu, s inicijativom
    # ujedno salje listu igraca kako bi znali target
    dm = DM("dungeonmaster@localhost", "tajna", players)
    await dm.start()

    # zavrsi igru
    await wait_until_finished(dm)

# combat goes through three main phases: initiantive roll, attacks and go to next battle if game isn't over
def startCombat(actors):

    roll_initiative(actors)
    # sort list based on initiative
    agent_list = sorted(actors, key=lambda x: x.initiative, reverse=True)
    
    spade.run(let_agents_loose(agent_list))
