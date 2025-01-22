import random
from collections import deque

import pygame
import sys

selected_unit = None


def find_shortest_path(grid, start, goal):
    """
    Находит кратчайший путь на двумерной карте от start до goal.

    :param grid: двумерный массив клеток класса Tile
    :param start: кортеж (x, y), начальная позиция
    :param goal: кортеж (x, y), целевая позиция
    :return: список клеток, представляющих путь, или None, если путь не найден
    """
    # Проверка на границы
    rows, cols = len(grid), len(grid[0])
    if not (0 <= start[0] < cols and 0 <= start[1] < rows):
        return 999
    if not (0 <= goal[0] < cols and 0 <= goal[1] < rows):
        return 999

    # Направления для перемещения (вверх, вправо, вниз, влево)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Очередь для BFS
    queue = deque([(start, [start])])  # Кортеж: текущая клетка, путь до неё
    visited = set()
    visited.add(start)
    length = 0

    while queue:
        current, path = queue.popleft()

        # Если дошли до цели, возвращаем путь
        if current == goal:
            for i in path[1:len(path)]:
                length += game.map[i[1]][i[0]].biome.walk_difficulty
            return length

        # Проверяем соседей
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            if (0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows  # Проверка границ
                    and neighbor not in visited):  # Клетка не посещена
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    # Если путь не найден
    return 999


class Game:
    def __init__(self, teams_amount, teams, player_team, map_size, screen):
        self.teams_amount = teams_amount
        self.teams = teams
        self.player_team = player_team
        self.map_size = map_size
        self.map = [[None for z in range(map_size[0])] for i in range(map_size[1])]
        self.screen = screen

    def start_game(self):
        self.generate_map()
        # self.player_team = random.choice(self.teams)

    def generate_map(self):
        def is_valid_pos(x, y):
            """Проверяет, находится ли позиция в пределах карты."""
            return 0 <= x < self.map_size[0] and 0 <= y < self.map_size[1]

        def generate_biome_chunk(start_pos, biome, size_range):
            """
            Генерирует область биома случайной формы.
            :param start_pos: стартовая позиция (x, y)
            :param biome: тип биома
            :param size_range: диапазон размеров области
            """
            chunk_size = random.randint(*size_range)  # Случайный размер области
            queue = [start_pos]
            created_tiles = 0

            while queue and created_tiles < chunk_size:
                x, y = queue.pop(0)
                if is_valid_pos(x, y) and self.map[y][x] is None:
                    self.map[y][x] = Tile((x * 90, y * 90), biome, biome.image_path, None, False)
                    created_tiles += 1

                    # Добавляем соседей в очередь (случайный порядок для более естественной формы)
                    neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                    random.shuffle(neighbors)
                    queue.extend(neighbors)

        # Шаг 1: Генерация крупных биомов
        biome_distribution = {
            Biomes[4]: (10, 15),
            Biomes[7]: (8, 15),
            Biomes[1]: (5, 10),
            Biomes[8]: (10, 15),
            Biomes[6]: (5, 10),
            Biomes[3]: (4, 6),
            Biomes[5]: (3, 6)
        }

        tundra_up = random.randint(2, 3)
        tundra_down = random.randint(2, 3)
        sea_left = random.randint(2, 3)
        sea_right = random.randint(2, 3)

        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                if (i < tundra_down or i > self.map_size[0] - tundra_up - 1) and not (
                        j < sea_left or j > self.map_size[0] - sea_right - 1):
                    biome = Biomes[0]
                    self.map[i][j] = Tile((j * 90, i * 90), biome, biome.image_path, random.choice(resource_types),
                                          False)
                elif j < sea_left or j > self.map_size[1] - sea_right - 1:
                    biome = Biomes[8]
                    self.map[i][j] = Tile((j * 90, i * 90), biome, biome.image_path, random.choice(resource_types),
                                          False)

        for biome, size_range in biome_distribution.items():
            for _ in range(random.randint(3, 6)):  # Несколько областей каждого биома
                start_x = random.randint(sea_left, self.map_size[0] - 1 - sea_right)
                start_y = random.randint(tundra_up, self.map_size[1] - 1 - tundra_down)
                generate_biome_chunk((start_x, start_y), biome, size_range)

        # Шаг 2: Добавление специальных биомов (Mountains, Hills, Swamp)
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                if self.map[y][x] is None:
                    # Добавляем случайный биом
                    zvg = random.choice([Biomes[4], Biomes[7]])
                    self.map[y][x] = Tile((x * 90, y * 90), zvg, zvg.image_path, None, False)

                # Генерация гор (mountains) с шансом
                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.05:
                    self.map[y][x] = Tile((x * 90, y * 90), Biomes[3], Biomes[3].image_path, None, False)

                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.5:
                    self.map[y][x] = Tile((x * 90, y * 90), Biomes[5], Biomes[5].image_path, None, False)
                    generate_biome_chunk((x, y), Biomes[5], (3, 6))

                # Генерация болот (swamp) вокруг биома "Sea"
                elif self.map[y][x].biome == Biomes[8] and random.random() < 0.1:
                    generate_biome_chunk((x, y), Biomes[2], (3, 6))  # Генерация болот вокруг моря


class Team:
    def __init__(self, name, cities, city_image_path):
        self.name = name
        self.cities = []
        self.city_image_path = city_image_path


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
        image_or = pygame.transform.scale(image_or, (180, 180))
        self.image = image_or.subsurface(image_or.get_bounding_rect())
        self.resource = resource
        self.occupied = occupied
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, event, game):
        global selected_unit
        if self.rect.collidepoint(event.pos):
            pathuwu = find_shortest_path(game.map, selected_unit.pos, (self.pos[0] / 90, self.pos[1] / 90))
            print(pathuwu, selected_unit.walk_points)
            if pathuwu <= selected_unit.walk_points:
                selected_unit.rect.center = self.rect.center
                selected_unit.pos = (int(self.pos[0] / 90), int(self.pos[1] / 90))
                selected_unit.deselect()
            else:
                print("too far")
                selected_unit.deselect()
                selected_unit = None


class Unit(pygame.sprite.Sprite):
    def __init__(self, image_path, name, team, pos, walk_points):
        super().__init__()
        self.name = name
        self.team = team
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (150, 150))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.rect.center = game.map[self.pos[1]][self.pos[0]].rect.center
        self.walk_points = walk_points

    def update(self, event, game: Game):
        if type(event) == pygame.event.Event and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
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


class City(pygame.sprite.Sprite):
    def __init__(self, image_path, pos, name, team, population, religion):
        super().__init__()
        self.name = name
        self.team = team
        self.population = population
        self.religion = religion
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (90, 90))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.center = game.map[pos[1]][pos[0]].rect.center
        self.pos = pos


class Settler(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/settler.png", name=name, pos=pos, team=team, walk_points=walk_points)

    def update(self, event, game):
        super().update(event, game)
        global selected_unit
        if type(event) == str and event == "space" and selected_unit == self:
            new_city = City(self.team.city_image_path, self.pos, f'{random.randint(1, 10)}_{random.randint(1, 10)}', self.team, 1, None)
            self.team.cities.append(new_city)
            print(self.team.cities)
            global units, units_to_draw
            global cities_to_draw, cities
            units_to_draw.remove(self)
            units = pygame.sprite.Group(units_to_draw)
            cities_to_draw.append(new_city)
            cities = pygame.sprite.Group(cities_to_draw)
            selected_unit = None


pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)
fps = 60
clock = pygame.time.Clock()

resource_types = ("Strategic", "Valuable", "Bonus")
teams = (Team("Rome", [], "src/units/trireme.png"), Team("Egypt", [], "src/units/trireme.png"), Team("Russia", [], "src/icons/russia.png"))
Biomes = (Biome("Tundra", 2, 4, "src/biomes/tundra.png"), Biome("Desert", 2, 4, "src/biomes/desert.png"),
          Biome("Swamp", 3, 5, "src/biomes/swamp.png"), Biome("Mountains", 3, 3, "src/biomes/mountains.png"),
          Biome("Plains", 1, 1, "src/biomes/plains.png"), Biome("RollingPlains", 2, 1, "src/biomes/hills.png"),
          Biome("Jungle", 3, 2, "src/biomes/jungle.png"), Biome("Woods", 1, 1, "src/biomes/woods.png"),
          Biome("Sea", 3, 5, "src/biomes/sea.png"))

game = Game(1, teams, teams[2], (30, 30), screen)
game.start_game()
settlertest = Settler("settler1", (2, 0), teams[2], 5)
units_to_draw = [settlertest]
cities_to_draw = []
units = pygame.sprite.Group(units_to_draw)
tiles = pygame.sprite.Group(game.map)
cities = pygame.sprite.Group(cities_to_draw)

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

    if keys[pygame.K_SPACE] and selected_unit is not None:
        units.update("space", game)

    camera.update(units)
    camera.update(tiles)
    tiles.draw(screen)
    units.draw(screen)
    cities.draw(screen)
    camera.reset_offset()
    pygame.display.flip()
    clock.tick(fps)
