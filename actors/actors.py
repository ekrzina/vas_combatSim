from abc import ABC, abstractmethod
from PIL import Image
import pygame
import os

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
    def show_picture(self):
        if self.pct:
            try:
                img_path = os.path.join(os.path.dirname(__file__), self.pct)
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
                text_name = font.render(f"Name: {self.name}", True, (0, 0, 0))                
                text_name_rect = text_name.get_rect(center=(target_size[0] // 2, target_size[1] - 20))  # Adjust Y-coordinate

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

    @abstractmethod
    def get_stats_string(self):
        stats_lines = [
            f"HP: {self.hp}",
            f"ATK: {self.atk}",
            f"DEF: {self.pdef}",
            f"SPATK: {self.spatk}",
            f"SPDEF: {self.spdef}",
            f"Weakness: {self.weakness}"
        ]

        # Check if strengths and immunity exist
        if self.strength is not None:
            stats_lines.append(f"Strength: {self.strength}")

        if self.immune is not None:
            stats_lines.append(f"Immune: {self.immune}")

        # Add attacks to the stats_lines
        if self.attack_list:
            stats_lines.append("Attacks:")
            for attack in self.attack_list:
                stats_lines.append(f"  {attack['name']}")

        return stats_lines

    @abstractmethod
    def show_description(self):
        pygame.init()

        window_size = (300, 300)
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Enemy Stats")

        font = pygame.font.Font(None, 24)
        text_lines = [font.render(line, True, (255, 255, 255)) for line in self.get_stats_string()]

        line_height = text_lines[0].get_height()

        total_height = len(text_lines) * line_height
        y_position = (window_size[1] - total_height) // 2

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))

            for text_line in text_lines:
                x_position = 10
                screen.blit(text_line, (x_position, y_position))
                y_position += line_height

            pygame.display.flip()
            clock.tick(60)
            y_position = (window_size[1] - total_height) // 2

        pygame.quit()


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

    def show_picture(self):
        return super().show_picture()
    
    def printStats(self):
        return super().printStats()

    def get_stats_string(self):
        return super().get_stats_string()

    def show_description(self):
        return super().show_description()
        

class Hero(AbstractActor):
    def __init__(self,name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct):
        super().__init__(name, hp, atk, pdef, spatk, spdef, attack_list, weakness, pct)
        # add behaviour

    def perform_attack(self, target):
        pass

    def take_damage(self, damage):
        pass
    
    def get_stats_string(self):
        return super().get_stats_string()

    def show_picture(self):
        if self.pct:
            try:
                img_path = os.path.join(os.path.dirname(__file__), self.pct)
                img = Image.open(img_path)
                img = img.convert("RGBA")

                target_size = (400, 450)
                img = img.resize(target_size)

                img_data = img.tobytes()

                pygame.init()
                screen = pygame.display.set_mode(target_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
                pygame.display.set_caption("Agent Picture")

                img_surface = pygame.image.fromstring(img_data, target_size, "RGBA")
                
                font = pygame.font.Font(None, 24)
                text_name = font.render(f"Name: {self.name}", True, (0, 0, 0))                
                text_name_rect = text_name.get_rect(center=(target_size[0] // 2, target_size[1] - 20))  # Adjust Y-coordinate

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

    def printStats(self):
        return super().printStats()
    
    def get_stats_string(self):
        stats_lines = [
            f"HP: {self.hp}",
            f"ATK: {self.atk}",
            f"DEF: {self.pdef}",
            f"SPATK: {self.spatk}",
            f"SPDEF: {self.spdef}",
            f"Weakness: {self.weakness}"
        ]

        if self.attack_list:
            stats_lines.append("Attacks:")
            for attack in self.attack_list:
                stats_lines.append(f"  {attack['name']}")

        return stats_lines

    def show_description(self):
        return super().show_description()