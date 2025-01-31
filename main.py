import random
from collections import deque

import pygame
import sys

selected_unit = None

r = 0


def update_window():
    if science_window_open:
        screen.fill((255, 255, 255))
        pygame.display.flip()
    if culture_window_open:
        screen.fill((255, 255, 255))
        pygame.display.flip()
    if city_screen_open and selected_city:
        selected_city.open_city_screen()
        pygame.display.flip()
    if unit_screen_open:
        Unit.open_unit_screen()
        pygame.display.flip()


def close_window():
    global science_window_open
    science_window_open = False
    pygame.display.set_mode(size)
    global culture_window_open
    culture_window_open = False
    pygame.display.set_mode(size)
    global open_city_screen
    open_city_screen = False
    pygame.display.set_mode(size)
    global unit_screen_open
    open_city_screen = False
    pygame.display.set_mode(size)


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
        self.resources = []  # Список для хранения всех ресурсов
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
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), biome, biome.image_path, None, False)
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
                    if random.random() <= 0.3:
                        resource_type = random.choice(["Меха", "Олени"])
                        if resource_type == "Меха":
                            self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path,
                                                  "Меха",
                                                  False)
                            self.resources.append(
                                Resource(resource_type, resourse[2].image_path, "Valuable", 0.05, Biomes[0], 1,
                                         1, 3, (x, y)))
                        else:
                            self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path,
                                                  "Олени",
                                                  False)
                            self.resources.append(
                                Resource(resource_type, resourse[8].image_path, "Bonus", 0.05, Biomes[0], 1, 1,
                                         0, (x, y)))
                    else:
                        self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path,
                                              None,
                                              False)
                elif j < sea_left or j > self.map_size[1] - sea_right - 1:
                    biome = Biomes[8]
                    if random.random() <= 0.3:
                        resource_type = "Рыба"
                        self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path,
                                              resource_types,
                                              False)
                        self.resources.append(
                            Resource(resource_type, resourse[7].image_path, "Valuable", 0.05, Biomes[4], 1, 3,
                                     1,
                                     (x, y)))
                    else:
                        self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path,
                                              None,
                                              False)

        for biome, size_range in biome_distribution.items():
            for _ in range(random.randint(3, 6)):  # Несколько областей каждого биома
                start_x = random.randint(sea_left, self.map_size[0] - 1 - sea_right)
                start_y = random.randint(tundra_up, self.map_size[1] - 1 - tundra_down)
                if random.random() <= 0.3:
                    self.map[i][j] = Tile((start_x, start_y), biome, biome.image_path,
                                          "Рыба",
                                          False)
                    self.resources.append(
                        Resource("Рыба", resourse[7].image_path, "Bonus", 0.05, Biomes[8], 1, 3,
                                 1,
                                 (x, y)))
                generate_biome_chunk((start_x, start_y), biome, size_range)

        # Шаг 2: Добавление специальных биомов (Mountains, Hills, Swamp)
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                if self.map[y][x] is None:
                    # Добавляем случайный биом
                    zvg = random.choice([Biomes[4], Biomes[7]])
                    if zvg == Biomes[4]:
                        if random.random() <= 0.3:
                            resource_type = random.choice(["Лошади", "Пшеница", "Слоновая кость"])
                            if resource_type == "Лошади":
                                self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                      resource_type, False)
                                self.resources.append(
                                    Resource(resource_type, resourse[0].image_path, "Strategic", 0.05, Biomes[4], 1, 3,
                                             1,
                                             (x, y)))

                            elif resource_type == "Пшеница":
                                self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                      resource_type, False)
                                self.resources.append(
                                    Resource(resource_type, resourse[9].image_path, "Bonus", 0.05, Biomes[4], 1, 3,
                                             1,
                                             (x, y)))
                            else:
                                self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                      resource_type, False)
                                self.resources.append(
                                    Resource(resource_type, resourse[4].image_path, "Valuable", 0.05, Biomes[4], 1, 3,
                                             1,
                                             (x, y)))
                    else:
                        if random.random() <= 0.3:
                            resource_type = random.choice(["Специи"])
                            self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                  resource_type, False)
                            self.resources.append(
                                Resource(resource_type, resourse[5].image_path, "Valuable", 0.05, Biomes[7], 1, 3,
                                         1,
                                         (x, y)))
                        else:
                            self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                  None, False)

                # Генерация гор (mountains) с шансом
                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.05:
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), Biomes[3], Biomes[3].image_path, None, False)

                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.5:
                    if random.random() <= 0.3:
                        resource_type = random.choice(["Железо", "Алмазы"])
                        if resource_type == "Железо":
                            self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                  resource_type, False)
                            self.resources.append(
                                Resource(resource_type, resourse[1].image_path, "Strategic", 0.05, Biomes[5], 1, 3,
                                         1,
                                         (x, y)))
                        else:
                            self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path,
                                                  resource_type, False)
                            self.resources.append(
                                Resource(resource_type, resourse[3].image_path, "Valuable", 0.05, Biomes[5], 1, 3,
                                         1,
                                         (x, y)))
                    else:
                        self.map[y][x] = Tile((x * tile_size, y * tile_size), Biomes[5], Biomes[5].image_path, None,
                                              False)

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
    def __init__(self, name, walk_difficulty, harshness, image_path, production, food, gold):
        self.name = name
        self.walk_difficulty = walk_difficulty
        self.harshness = harshness
        self.image_path = image_path
        self.production = production
        self.food = food
        self.gold = gold


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
            pathuwu = find_shortest_path(game.map, selected_unit.pos,
                                         (self.pos[0] / tile_size, self.pos[1] / tile_size))
            print(pathuwu, selected_unit.walk_points)
            if pathuwu <= selected_unit.walk_points:
                selected_unit.rect.center = self.rect.center
                selected_unit.pos = (int(self.pos[0] / tile_size), int(self.pos[1] / tile_size))
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

        self.font = pygame.font.SysFont("Arial", 20)
        self.unit_screen = pygame.Surface((600, 250))
        self.name_of_units = self.font.render(f"{self.name}", True, (0, 0, 0))
        self.walk = self.font.render(f"Перемещение:{self.walk_points}", True, (0, 0, 0))
        self.hp = 100

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

    def open_unit_screen(self):
        if selected_unit == self:
            # Создаем окно внизу экрана
            unit_screen = pygame.Surface((screen.get_width(), 200))
            unit_screen.fill((200, 200, 200))

            # Отображаем информацию о юните
            name_text = self.font.render(f"Юнит: {self.name}", True, (0, 0, 0))
            walk_text = self.font.render(f"Перемещение: {self.walk_points}", True, (0, 0, 0))
            hp_points = self.font.render(f"Здоровье:{self.hp}", True, (0, 0, 0))

            # Размещение текста
            unit_screen.blit(name_text, (10, 10))
            unit_screen.blit(walk_text, (10, 40))
            unit_screen.blit(hp_points, (300, 30))

            # Отображаем окно на экране
            screen.blit(unit_screen, (0, screen.get_height() - 200))


tile_size = 90


class Resource:
    def __init__(self, name, image_path, resource_type, rarity, biome, production, food, gold, pos):
        self.name = name
        self.type = resource_type
        self.rarity = rarity
        self.pos = pos
        self.production = production
        self.food = food
        self.gold = gold
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (90, 90))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.rect.center = pos

    def render(self, screen):
        screen.blit(self.image, self.pos)


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
        image = pygame.transform.scale(image, (tile_size, tile_size))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.center = game.map[pos[1]][pos[0]].rect.center
        self.pos = pos

        self.font = pygame.font.SysFont("Arial", 20)
        self.city_screen = pygame.Surface((250, 600))
        self.gold_income = self.font.render(f"Золото за ход:", True, (0, 0, 0))
        self.production_per_turn = self.font.render(f"Производство:", True, (0, 0, 0))
        self.turn_to_grow = self.font.render(f"Ходов до роста:", True, (0, 0, 0))
        self.building = self.font.render(f"Построенные здания:", True, (0, 0, 0))
        self.to_build = self.font.render(f"Здания", True, (0, 0, 0))
        self.Units = self.font.render(f"Юниты", True, (0, 0, 0))

        self.population_text = self.font.render(f"Население: {self.population}", True, (0, 0, 0))
        self.religion_text = self.font.render(f"Религия: {self.religion if self.religion else 'Нет'}", True, (0, 0, 0))
        self.queue_text = self.font.render(f"Очередь:", True, (0, 0, 0))
        self.name_text = self.font.render(f"Город: {self.name}", True, (0, 0, 0))

    def open_city_screen(self):
        self.city_screen.fill((200, 200, 200))  # Цвет фона для экрана города

        # Отображаем информацию о городе
        self.city_screen.blit(self.name_text, (10, 10))
        self.city_screen.blit(self.population_text, (10, 40))
        self.city_screen.blit(self.religion_text, (10, 70))
        self.city_screen.blit(self.gold_income, (10, 100))
        self.city_screen.blit(self.production_per_turn, (10, 130))
        self.city_screen.blit(self.turn_to_grow, (10, 160))
        self.city_screen.blit(self.to_build, (10, 190))
        self.city_screen.blit(self.Units, (10, 230))
        self.city_screen.blit(self.queue_text, (10, 260))
        self.city_screen.blit(self.building, (10, 290))
        # Отображаем экран города справа от экрана игры
        screen.blit(self.city_screen, (screen.get_width() - self.city_screen.get_width(), 0))


class Archer(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/archer.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Catapult(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/catapult.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Chariot(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/chariot.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Galley(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/galley.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Horseman(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/horseman.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Scout(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/scout.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Settler(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/settler.png", name=name, pos=pos, team=team, walk_points=walk_points)

    def update(self, event, game):
        super().update(event, game)
        global selected_unit
        if type(event) == str and event == "settle" and selected_unit == self:
            new_city = City(self.team.city_image_path, self.pos, f'{random.randint(1, 10)}_{random.randint(1, 10)}',
                            self.team, 1, None)
            self.team.cities.append(new_city)
            print(self.team.cities)
            global units, units_to_draw
            global cities_to_draw, cities
            units_to_draw.remove(self)
            units = pygame.sprite.Group(units_to_draw)
            cities_to_draw.append(new_city)
            cities = pygame.sprite.Group(cities_to_draw)
            selected_unit = None


class Spearman(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/spearman.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Swordsman(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/swordsman.png.png", name=name, pos=pos, team=team,
                         walk_points=walk_points)


class Trireme(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/trireme.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Warrior(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/warrior.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Worker(Unit):
    def __init__(self, name, pos, team, walk_points):
        super().__init__(image_path="src/units/worker.png", name=name, pos=pos, team=team, walk_points=walk_points)


class Image:
    def __init__(self, path_to_image, size):
        self.image = pygame.image.load(path_to_image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        image_original = self.image.subsurface(self.image.get_bounding_rect())
        self.image = image_original.copy()
        self.rect = self.image.get_rect()

    def change_size(self, new_size):
        self.image = pygame.transform.scale(self.image, new_size)
        image_original = self.image.subsurface(self.image.get_bounding_rect())
        self.image = image_original.copy()


class TechMenu:
    def __init__(self, techs):
        self.techs = techs


pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)

fps = 60
clock = pygame.time.Clock()

resource_types = ("Strategic", "Valuable", "Bonus")
teams = (Team("Danish", [], "src/icons/danish.png"), Team("Dutch", [], "src/icons/dutch.png"),
         Team("English", [], "src/icons/english.png"),
         Team("Indian", [], "src/icons/indian.png"), Team("Japanese", [], "src/icons/japanese.png"),
         Team("Russian", [], "src/icons/russian.png"),
         Team("Spanish", [], "src/icons/spanish.png"), Team("Swedish", [], "src/icons/swedish.png"))
Biomes = (
    Biome("Tundra", 2, 4, "src/biomes/tundra.png", 0, 1, 0), Biome("Desert", 2, 4, "src/biomes/desert.png", 0, 0, 0),
    Biome("Swamp", 3, 5, "src/biomes/swamp.png", 0, 3, 0),
    Biome("Mountains", 3, 3, "src/biomes/mountains.png", 3, 0, 0),
    Biome("Plains", 1, 1, "src/biomes/plains.png", 1, 1, 0),
    Biome("RollingPlains", 2, 1, "src/biomes/hills.png", 2, 1, 0),
    Biome("Jungle", 3, 2, "src/biomes/jungle.png", 1, 2, 0), Biome("Woods", 1, 1, "src/biomes/woods.png", 2, 1, 0),
    Biome("Sea", 3, 5, "src/biomes/sea.png", 0, 1, 1))
resourse = (Resource("Лошади", "src/resource/Horses.png", "Стратигический", 0.05, Biomes[4], 1, 2, 0, (1, 1)),
            Resource("Железо", "src/resource/Iron.png", "Стратигический", 0.05, Biomes[5], 2, 0, 0, (1, 1)),
            Resource("Меха", "src/resource/Furs.png", "Редкий", 0.05, Biomes[0], 1, 1, 3, (1, 1)),
            Resource("Алмазы", "src/resource/Gems.png", "Редкий", 0.05, Biomes[5], 2, 0, 3, (1, 1)),
            Resource("Слоновая кость", "src/resource/Ivory.png", "Редкий", 0.05, Biomes[4], 1, 1, 3, (1, 1)),
            Resource("Специи", "src/resource/Spice.png", "Редкий", 0.05, Biomes[7], 2, 0, 3, (1, 1)),
            Resource("Оазис", "src/resource/Oasis.png", "Бонусный", 0.05, Biomes[1], 0, 3, 1, (1, 1)),
            Resource("Рыба", "src/resource/fish.png", "Бонусный", 0.05, Biomes[8], 1, 3, 1, (1, 1)),
            Resource("Олени", "src/resource/Game.png ", "Бонысный", 0.05, Biomes[0], 1, 1, 0, (1, 1)),
            Resource("Пшеница", "src/resource/Wheat.png", "Бонусный", 0.05, Biomes[4], 0, 1, 0, (1, 1)),
            Resource("Сахар", "src/resource/Sugar.png", "Бонусный", 0.05, Biomes[6], 0, 1, 2, (1, 1)))
game = Game(1, teams, teams[2], (30, 30), screen)
tile_size = 90
game.start_game()
settlertest = Settler("settler1", (2, 0), teams[2], 5)
units_to_draw = [settlertest]
cities_to_draw = []
units = pygame.sprite.Group(units_to_draw)
tiles = pygame.sprite.Group(game.map)
cities = pygame.sprite.Group(cities_to_draw)

camera = Camera()

science_icon = pygame.image.load("src/icons/science_icon.png").convert_alpha()
science_icon = pygame.transform.scale(science_icon, (30, 30))
science_icon_original = science_icon.subsurface(science_icon.get_bounding_rect())
science_icon = science_icon_original.copy()

culture_icon = pygame.image.load("src/icons/culture.png").convert_alpha()
culture_icon = pygame.transform.scale(culture_icon, (30, 30))
culture_icon_original = culture_icon.subsurface(culture_icon.get_bounding_rect())
culture_icon = culture_icon_original.copy()

science_window_open = False
culture_window_open = False

unit_screen_open = False
city_screen_open = False
selected_city = None
# Позиция значка в левом верхнем углу
icon_pos = (10, 10)
icon_pos_culture = (40, 10)
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
                update_window()
            for city in cities:
                if city.rect.collidepoint(event.pos):
                    selected_city = city
                    city_screen_open = not city_screen_open
                    update_window()
                    break
            units.update(event, game)
            if pygame.Rect(icon_pos, science_icon.get_size()).collidepoint(event.pos):
                science_window_open = not science_window_open
            if pygame.Rect(icon_pos_culture, culture_icon.get_size()).collidepoint(event.pos):
                culture_window_open = not culture_window_open
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
        units.update("settle", game)
    if keys[pygame.K_ESCAPE] and (science_window_open or culture_window_open or open_city_screen or unit_screen_open):
        close_window()

    camera.update(units)
    camera.update(tiles)
    camera.update(cities)
    camera.update(game.resources)
    tiles.draw(screen)
    units.draw(screen)
    cities.draw(screen)
    game.render_resources()
    print(game.resources)
    screen.blit(science_icon, (icon_pos[0], icon_pos[1]))
    screen.blit(culture_icon, (icon_pos_culture[0], icon_pos_culture[1]))
    update_window()
    if selected_unit is not None:
        selected_unit.open_unit_screen()

    camera.reset_offset()
    pygame.display.flip()
    clock.tick(fps)
