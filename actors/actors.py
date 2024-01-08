from abc import ABC, abstractmethod

class AbstractActor(ABC):
    def __init__(self, name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.pdef = pdef
        self.spatk = spatk
        self.spdef = spdef
        self.attack_list = attack_list
        self.weakness = weakness
        self.pct = pct
    
    @abstractmethod
    def perform_attack(self, target):
        pass

    @abstractmethod
    def take_damage(self, damage):
        pass

    @abstractmethod
    def show_picture(self, pct):
        print("Swowing picture...")
    
    @abstractmethod
    def printStats(self):
        print(f"Random Enemy: {self.name}")  # Assuming 'name' attribute exists
        print("Stats:")
        print(f"  HP: {self.hp}")
        print(f"  ATK: {self.atk}")
        print(f"  DEF: {self.pdef}")
        print(f"  SPATK: {self.spatk}")
        print(f"  SPDEF: {self.spdef}")
        print(f"  Weakness: {self.weakness}")

        # For Hero, there are no strengths and immunity
        if self.strength is not None:
            print(f"  Strength: {self.strength}")

        if self.immune is not None:
            print(f"  Immune: {self.immune}")

        print("Attacks:")
        for attack in self.attack_list:
            print(f"  {attack['name']}: {attack}")

class Enemy(AbstractActor):
    def __init__(self, name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct, strength, immune):
        super().__init__(name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct)
        self.strength = strength
        self.immune = immune
        # add behaviour

    def perform_attack(self, target):
        # Implement the logic for performing an attack on the target
        pass

    def take_damage(self, damage):
        # Implement the logic for taking damage
        pass

    def show_picture(self, pct):
        return super().show_picture(pct)
    
    def printStats(self):
        return super().printStats()

class Hero(AbstractActor):
    def __init__(self,name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct):
        super().__init__(name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct)
        # add behaviour

    def perform_attack(self, target):
        # Implement the logic for performing an attack on the target
        pass

    def take_damage(self, damage):
        # Implement the logic for taking damage
        pass
    
    def show_picture(self, pict):
        return super().show_picture(pict)

    def printStats(self):
        return super().printStats()