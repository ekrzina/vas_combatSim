import json
import random
from actors.actors import Enemy, Hero

def fetch_hero_entity(random_data):
    entity = Hero(
        name=random_data['name'],
        hp=random_data.get('attributes', {}).get('HP', 0),
        atk=random_data.get('attributes', {}).get('ATK', 0),
        pdef=random_data.get('attributes', {}).get('DEF', 0),
        spatk=random_data.get('attributes', {}).get('SPATK', 0),
        spdef=random_data.get('attributes', {}).get('SPDEF', 0),
        attack_list=random_data.get('attacks', []),
        weakness=random_data.get('weakness', []),
        pct=random_data.get('pct', None)
    )
    return entity

def fetch_random_hero():
    with open('desc/stats.json') as json_file:
        data = json.load(json_file)

    hero_names = list(data['heroes'].keys())
    random_hero_name = random.choice(hero_names)

    random_hero_data = data['heroes'][random_hero_name]

    # Extract hero-specific attributes
    hero_hp = random.choice(random_hero_data.get('hp_pool', []))
    hero_atk = random.choice(random_hero_data.get('atk_pool', []))
    hero_def = random.choice(random_hero_data.get('def_pool', []))
    hero_spatk = random.choice(random_hero_data.get('spatk_pool', []))
    hero_spdef = random.choice(random_hero_data.get('spdef_pool', []))
    hero_weakness = random.choice(random_hero_data.get('weakness', []))

    hero_attacks = random.sample(random_hero_data.get('attacks', []), 4)

    random_hero_data['attributes'] = {
        'HP': hero_hp,
        'ATK': hero_atk,
        'DEF': hero_def,
        'SPATK': hero_spatk,
        'SPDEF': hero_spdef
    }
    random_hero_data['weakness'] = hero_weakness
    random_hero_data['attacks'] = hero_attacks

    return fetch_hero_entity(random_hero_data)

# sets up game parameters

def fetch_enemy_entity(random_data):
    weakness = random_data['weakness'][0] if 'weakness' in random_data and random_data['weakness'] else None
    strength = random_data['strength'][0] if 'strength' in random_data and random_data['strength'] else None
    immune = random_data['immune'][0] if 'immune' in random_data and random_data['immune'] else None

    entity = Enemy(
        name=random_data['name'],
        hp=random_data['attributes']['HP'],
        atk=random_data['attributes']['ATK'],
        pdef=random_data['attributes']['DEF'],
        spatk=random_data['attributes']['SPATK'],
        spdef=random_data['attributes']['SPDEF'],
        attack_list=random_data['attacks'],
        weakness=weakness,
        strength=strength,
        immune=immune,
        pct=random_data['pct']
    )
    return entity

def fetch_random_enemy():
    with open('desc/stats.json') as json_file:
        data = json.load(json_file)

    enemy_names = list(data['enemies'].keys())
    random_enemy_name = random.choice(enemy_names)

    random_enemy_data = data['enemies'][random_enemy_name]

    return fetch_enemy_entity(random_enemy_data)

def setupGame():
    new_enemy = fetch_random_enemy()
    #new_enemy.show_picture()
    #new_enemy.show_description()

    new_hero = fetch_random_hero()
    #new_hero.show_picture()
    #new_hero.show_description()

    new_enemy2 = fetch_random_enemy()
    new_hero2 = fetch_random_hero()

    actors = [new_enemy, new_hero, new_hero2]

    return actors