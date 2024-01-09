# simulates combat
from time import sleep
from actors.agents import DM, EnemyNPC, AllyNPC
from actors.actors import Enemy, Hero
from spade import wait_until_finished

def print_initiatives(a):
        print(f"{a.name}'s initiative:  {a.initiative}\n")

def roll_initiative(actors):
    for a in actors:
         a.add_initiative()
         print_initiatives(a)

async def create_instance(attacker, i):
    if isinstance(attacker, Enemy):
        new_player = EnemyNPC(f"player{i}@rec.foi.hr", "tajna", attacker)
    else:
        new_player = AllyNPC(f"player{i}@rec.foi.hr", "tajna", attacker)
    
    # starts the new Player
    await new_player.start()
    return new_player

# implement from agent perspective with their behaviour
async def let_agents_loose(agent_list):
    players = []
    i = 0

    # kreiraj broj agenata koji su u listi agenata
    for attacker in agent_list:
         # create agent with attacker behavior (for now)
        new_player = create_instance(attacker, i)
        i += 1
        players.append(new_player)

    # svi su agenti pripremljeni i cekaju poruke
    # kreiraj prvog agenta koji je DM
    # DM salje poruke agentu po redu, s inicijativom
    # ujedno salje listu igraca kako bi znali target
    dm = DM("dm@rec.foi.hr", "tajna", players)
    await dm.start()

    # zavrsi igru
    await wait_until_finished(dm)
    # dm kills all agents on end

# combat goes through three main phases: initiantive roll, attacks and go to next battle if game isn't over
def startCombat(actors):
    global turns, game_over

    game_over = False
    turns = 0

    roll_initiative(actors)
    # sort list based on initiative
    agent_list = sorted(actors, key=lambda x: x.initiative, reverse=True)
    
    let_agents_loose(agent_list)
