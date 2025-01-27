import pygame
import sys

class Biome:
    def __init__(self, name, walk_difficulty, harshness):
        self.name = name
        self.walk_difficulty = walk_difficulty
        self.harshness = harshness


class Tile:
    def __init__(self, name, biome, image, resource, occupied):
        self.name = name
        self.biome = biome
        self.image = image
        self.resource = resource
        self.occupied = occupied


class Unit:
    def __init__(self, name, team, image):
        self.name = name
        self.team = team
        self.image = image


class Resource:
    def __init__(self, name, resource_type, rarity):
        self.name = name
        self.type = resource_type
        self.rarity = rarity


pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)
fps = 30
clock = pygame.time.Clock()

resource_types = ("strategic", "Valuable", "Bonus")
Biomes = (Biome("Tundra", 3, 4), Biome("Desert", 2, 4),
          Biome("Swamp", 4, 5), Biome("Mountains", 3, 3),
          Biome("Plains", 1, 1), Biome("RollingPlains", 2, 1),
          Biome("Jungle", 3, 2), Biome("Woods", 1, 1),
          Biome("Sea", 5, 5))

# main loop
while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    clock.tick(fps)

