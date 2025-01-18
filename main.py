import random

import pygame
import sys

selected_unit = None


class Game:
    def __init__(self, teams_amount, teams, player_team, map_size, screen):
        self.teams_amount = teams_amount
        self.teams = teams
        self.player_team = player_team
        self.map_size = map_size
        self.map = [[] for i in range(map_size[1])]
        self.screen = screen

    def start_game(self):
        self.generate_map()
        # self.player_team = random.choice(self.teams)

    def generate_map(self):
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                self.map[i].append(Tile((j*60, i*60), random.choice(Biomes), "src/test_unit.png", random.choice(resource_types), False))


class Biome:
    def __init__(self, name, walk_difficulty, harshness, t_color):
        self.name = name
        self.walk_difficulty = walk_difficulty
        self.harshness = harshness
        self.t_color = t_color


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, biome, image_path, resource, occupied):
        super().__init__()
        self.pos = pos
        self.biome = biome
        image_or = pygame.image.load(image_path).convert_alpha()
        image_or = pygame.transform.scale(image_or, (180, 180))
        self.image = image_or.subsurface(image_or.get_bounding_rect())
        self.resource = resource
        self.occupied = occupied
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        pass


class Unit(pygame.sprite.Sprite):
    def __init__(self, name, team, image_path, pos):
        super().__init__()
        self.name = name
        self.team = team
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (180, 180))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, events, game: Game):
        global selected_unit
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    if self.team == game.player_team:
                        if selected_unit == self:
                            selected_unit = None
                            self.deselect()
                        else:
                            selected_unit = self
                            self.select()
                elif selected_unit == self:
                    selected_unit = None
                    self.move_to(event.pos)
                    self.deselect()

    def select(self):
        self.image = self.image_original.copy()
        dark_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 100))
        self.image.blit(dark_overlay, (0, 0))

    def deselect(self):
        self.image = self.image_original.copy()

    def move_to(self, pos):
        self.rect.center = pos


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

resource_types = ("Strategic", "Valuable", "Bonus")
teams = ("Rome", "France", "Russia", "England", "Egypt")
Biomes = (Biome("Tundra", 3, 4, (255, 0, 0)), Biome("Desert", 2, 4, (255, 255, 0)),
          Biome("Swamp", 4, 5, (255, 255, 255)), Biome("Mountains", 3, 3, (0, 255, 0)),
          Biome("Plains", 1, 1, (0, 255, 255)), Biome("RollingPlains", 2, 1, (0, 0, 255)),
          Biome("Jungle", 3, 2, (125, 125, 125)), Biome("Woods", 1, 1, (255, 100, 1)),
          Biome("Sea", 5, 5, (255, 0, 125)))

game = Game(1, teams, teams[2], (10, 10), screen)
game.start_game()
test_unit = Unit("testPidor", teams[2], "src/test_unit.png",  (100, 0))
units = pygame.sprite.Group(test_unit)
tiles = pygame.sprite.Group(game.map)
# main loop
while True:
    events = pygame.event.get()
    screen.fill((0, 0, 0))
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()

    units.update(events, game)
    units.draw(screen)
    tiles.draw(screen)
    if selected_unit is not None:
        tiles.update()
    pygame.display.flip()
    clock.tick(fps)
