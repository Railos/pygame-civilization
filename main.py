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
        mountain = random.randint(2, 3)
        tundra = random.randint(2, 2)
        rand_desert = "random.randint(5, 10)"
        desert = eval(rand_desert)
        n_desert = random.randint(1, 3)
        ms_plants = []
        ms_desert = []
        ms_mountain = []
        banned_biomes = [Biomes[0], Biomes[3], Biomes[8], Biomes[1]]
        sea = random.randint(2, 2)
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                # Проработать алгоритм для нормальной генерации биомов. После выполнения алгоритма, записать итоговый биом для данной клетки
                # в переменную biome
                biome = random.choice(Biomes)  # ВРЕМЕННО
                if (i < tundra or i > self.map_size[0] - tundra) and not (
                        j < sea or j > self.map_size[0] - sea):
                    biome = Biomes[0]
                elif j < sea or j > self.map_size[1] - sea:
                    biome = Biomes[8]
                else:
                    biome = Biomes[4]
                    ms_plants.append((j, i))
                    ms_desert.append((j, i))

                self.map[i].append(
                    Tile((j * 60, i * 60), biome, biome.image_path, random.choice(resource_types), False))

        for _ in range(mountain):
            m = random.choice(ms_plants)
            ms_mountain.append(m)
            biome = Biomes[3]
            self.map[m[1]][m[0]] = Tile((m[0] * 60, m[1] * 60), biome, biome.image_path, random.choice(resource_types),
                                        False)

        for qq in range(n_desert):
            desert = eval(rand_desert)
            m = random.choice(ms_desert)
            biome = Biomes[1]
            self.map[m[1]][m[0]] = Tile((m[0] * 60, m[1] * 60), biome, biome.image_path, random.choice(resource_types),
                                        False)

            print(m[0], m[1])

            while desert != 1:
                r = random.randint(1, 4)
                if r == 1:
                    if self.map[m[1]-1][m[0]].biome not in banned_biomes:
                        m = (m[0], m[1] - 1)
                        desert -= 1
                elif r == 2:
                    if self.map[m[1]][m[0]+1].biome not in banned_biomes:
                        m = (m[0] + 1, m[1])
                        desert -= 1
                elif r == 3:
                    if self.map[m[1]+1][m[0]].biome not in banned_biomes:
                        m = (m[0], m[1] + 1)
                        desert -= 1
                elif r == 4:
                    if self.map[m[1]][m[0]-1].biome not in banned_biomes:
                        m = (m[0] - 1, m[1])
                        desert -= 1
                biome = Biomes[1]
                self.map[m[1]][m[0]] = Tile((m[0] * 60, m[1] * 60), biome, biome.image_path, random.choice(resource_types),
                                            False)

class Biome:
    def __init__(self, name, walk_difficulty, harshness, image_path):
        self.name = name
        self.walk_difficulty = walk_difficulty
        self.harshness = harshness
        self.image_path = image_path


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, biome, image_path, resource, occupied):
        super().__init__()
        self.pos = pos
        self.biome = biome
        image_or = pygame.image.load(image_path).convert_alpha()
        image_or = pygame.transform.scale(image_or, (120, 120))
        self.image = image_or.subsurface(image_or.get_bounding_rect())
        self.resource = resource
        self.occupied = occupied
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, event, game):
        global selected_unit
        if self.rect.collidepoint(event.pos):
            selected_unit.rect.center = self.rect.center
            selected_unit.deselect()


class Unit(pygame.sprite.Sprite):
    def __init__(self, name, team, image_path, pos):
        super().__init__()
        self.name = name
        self.team = team
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (150, 150))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, event, game: Game):
        global selected_unit
        if self.rect.collidepoint(event.pos):
            if self.team == game.player_team:
                if selected_unit == self:
                    selected_unit = None
                    self.deselect()
                else:
                    selected_unit = self
                    self.select()

    def select(self):
        self.image = self.image_original.copy()
        dark_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 100))
        self.image.blit(dark_overlay, (0, 0))

    def deselect(self):
        self.image = self.image_original.copy()


class Resource:
    def __init__(self, name, resource_type, rarity):
        self.name = name
        self.type = resource_type
        self.rarity = rarity


class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def move(self, x, y):
        self.offset_x += x
        self.offset_y += y

    def apply(self, sprite):
        sprite.rect.x += self.offset_x
        sprite.rect.y += self.offset_y

    def update(self, group):
        for sprite in group:
            sprite.rect.x += self.offset_x
            sprite.rect.y += self.offset_y

    def reset_offset(self):
        self.offset_x = 0
        self.offset_y = 0


pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)
fps = 60
clock = pygame.time.Clock()

resource_types = ("Strategic", "Valuable", "Bonus")
teams = ("Rome", "France", "Russia", "England", "Egypt")
Biomes = (Biome("Tundra", 3, 4, "src/biomes/tundra.png"), Biome("Desert", 2, 4, "src/biomes/desert.png"),
          Biome("Swamp", 4, 5, "src/biomes/jungle.png"), Biome("Mountains", 3, 3, "src/biomes/mountains.png"),
          Biome("Plains", 1, 1, "src/biomes/plains.png"), Biome("RollingPlains", 2, 1, "src/biomes/hills.png"),
          Biome("Jungle", 3, 2, "src/biomes/jungle.png"), Biome("Woods", 2, 1, "src/biomes/woods.png"),
          Biome("Sea", 5, 5, "src/biomes/sea.png"))

game = Game(1, teams, teams[2], (15, 15), screen)
game.start_game()
test_unit = Unit("testPidor", teams[2], "src/units/spearman.png",  (100, 0))
units = pygame.sprite.Group(test_unit)
tiles = pygame.sprite.Group(game.map)

camera = Camera()
# main loop
while True:
    events = pygame.event.get()
    screen.fill((0, 0, 0))
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if selected_unit is not None:
                tiles.update(event, game)
            units.update(event, game)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera.move(0, 5)
    if keys[pygame.K_s]:
        camera.move(0, -5)
    if keys[pygame.K_a]:
        camera.move(5, 0)
    if keys[pygame.K_d]:
        camera.move(-5, 0)

    camera.update(units)
    camera.update(tiles)
    tiles.draw(screen)
    units.draw(screen)
    camera.reset_offset()
    pygame.display.flip()
    clock.tick(fps)
