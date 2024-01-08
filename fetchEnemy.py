import json
import random
from actors.actors import Enemy

def fetch_random_enemy():
    with open('desc/stats.json') as json_file:
        data = json.load(json_file)

    enemy_names = list(data['enemies'].keys())
    random_enemy_name = random.choice(enemy_names)

    random_enemy_data = data['enemies'][random_enemy_name]
    random_enemy = Enemy(
        name=random_enemy_data['name'],
        hp=random_enemy_data['attributes']['HP'],
        atk=random_enemy_data['attributes']['ATK'],
        pdef=random_enemy_data['attributes']['DEF'],
        spatk=random_enemy_data['attributes']['SPATK'],
        spdef=random_enemy_data['attributes']['SPDEF'],
        attack_list=random_enemy_data['attacks'],
        weakness=random_enemy_data['weakness'],
        strength=random_enemy_data['strength'] if 'strength' in random_enemy_data else None,
        immune=random_enemy_data['immune'] if 'immune' in random_enemy_data else None,
        pct=random_enemy_data.get('pct', None)
    )
    return random_enemy

if __name__ == "__main__":

    new_enemy = fetch_random_enemy()
    new_enemy.printStats()
