import random
from collections import deque

import pygame
import sys

selected_unit = None


class Image:
    def __init__(self, path_to_image, size, pos=(0, 0)):
        self.image = pygame.image.load(path_to_image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        image_original = self.image.subsurface(self.image.get_bounding_rect())
        self.image = image_original.copy()
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = pos

    def change_size(self, new_size):
        self.image = pygame.transform.scale(self.image, new_size)
        image_original = self.image.subsurface(self.image.get_bounding_rect())
        self.image = image_original.copy()
        self.rect = self.image.get_rect()

    def change_pos(self, new_pos):
        self.rect.topleft = new_pos


def update_window():
    if science_window_open:
        screen.blit(scroll.image, (0, 0))
    if culture_window_open:
        screen.blit(scroll.image, (0, 0))


def close_window():
    global science_window_open
    science_window_open = False
    global culture_window_open
    culture_window_open = False
    global city_screen_open, selected_city
    city_screen_open = False
    selected_city = None
    global unit_screen_open, selected_unit
    if unit_screen_open:
        selected_unit.deselect()
        selected_unit = None
        unit_screen_open = False


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
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), biome, biome.image_path, None, False)
                    created_tiles += 1

                    # Добавляем соседей в очередь (случайный порядок для более естественной формы)
                    neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                    random.shuffle(neighbors)
                    queue.extend(neighbors)

        global resources_to_draw

        # Шаг 1: Генерация крупных биомов
        biome_distribution = {
            Biomes[4]: (10, 15),
            Biomes[7]: (8, 15),
            Biomes[1]: (5, 10),
            Biomes[8]: (10, 15),
            Biomes[6]: (5, 10),
            Biomes[3]: (5, 8),
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
                    self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path, None, False)
                elif j < sea_left or j > self.map_size[1] - sea_right - 1:
                    biome = Biomes[8]
                    self.map[i][j] = Tile((j * tile_size, i * tile_size), biome, biome.image_path, None, False)

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
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), zvg, zvg.image_path, None, False)

                # Генерация гор (mountains) с шансом
                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.05:
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), Biomes[3], Biomes[3].image_path, None, False)

                elif self.map[y][x].biome == Biomes[4] and random.random() < 0.5:
                    self.map[y][x] = Tile((x * tile_size, y * tile_size), Biomes[5], Biomes[5].image_path, None, False)
                    generate_biome_chunk((x, y), Biomes[5], (3, 6))

    def generate_resources(self):
        global resources_to_draw
        for i in self.map:
            for j in i:
                k = random.randint(0, 200)
                resource = None
                if j.biome == Biomes[0]:
                    if k <= 10:
                        resource = Resource("Furs", "src/resources/Furs.png", "Valuable", 1, 1, 3, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                    elif 10 < k <= 20:
                        resource = Resource("Game", "src/resources/Game.png", "Bonus", 1, 1, 0, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[1]:
                    if k <= 20:
                        resource = Resource("Oasis", "src/resources/Oasis.png", "Bonus", 0, 3, 1, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[4]:
                    if k <= 10:
                        resource = Resource("Horses", "src/resources/Horses.png", "Strategic", 1, 2, 0, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                    elif 10 < k <= 20:
                        resource = Resource("Ivory", "src/resources/Ivory.png", "Valuable", 1, 1, 3, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                    elif 20 < k <= 30:
                        resource = Resource("Wheat", "src/resources/Wheat.png", "Bonus", 0, 1, 0, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[5]:
                    if k <= 10:
                        resource = Resource("Iron", "src/resources/Iron.png", "Strategic", 2, 0, 0, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                    elif 10 < k <= 20:
                        resource = Resource("Gems", "src/resources/Gems.png", "Valuable", 2, 0, 3, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[6]:
                    if k <= 20:
                        resource = Resource("Sugar", "src/resources/Sugar.png", "Bonus", 0, 1, 2, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[7]:
                    if k <= 10:
                        resource = Resource("Spice", 'src/resources/Spice.png', "Valuable", 2, 0, 3, j)
                        j.resource = resource
                        resources_to_draw.append(resource)
                elif j.biome == Biomes[8]:
                    if k <= 10:
                        resource = Resource("Fish", "src/resources/fish.png", "Bonus", 1, 3, 1, j)
                        j.resource = resource
                        resources_to_draw.append(resource)


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
        self.rect = self.image.get_rect(topleft=pos)
        self.resource = resource
        self.occupied = occupied

    def update(self, event, game):
        global selected_unit
        global MOVING
        if self.rect.collidepoint(event.pos) and (selected_unit.pos[0] * 90, selected_unit.pos[1] * 90) != self.pos:
            pathuwu = find_shortest_path(game.map, selected_unit.pos,
                                         (self.pos[0] / tile_size, self.pos[1] / tile_size))
            if pathuwu <= selected_unit.walk_points:
                selected_unit.rect.center = self.rect.center
                selected_unit.pos = (int(self.pos[0] / tile_size), int(self.pos[1] / tile_size))
                selected_unit.deselect()
                selected_unit = None
                MOVING = True
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
            global selected_unit, unit_screen_open
            if self.rect.collidepoint(event.pos):
                if self.team == game.player_team:
                    if selected_unit == self:
                        selected_unit = None
                        self.deselect()
                        unit_screen_open = False
                    else:
                        selected_unit = self
                        self.select()
                        unit_screen_open = True

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


class Resource(pygame.sprite.Sprite):
    def __init__(self, name, image_path, resource_type, production, food, gold, tile):
        super().__init__()
        self.name = name
        self.type = resource_type
        self.production = production
        self.food = food
        self.gold = gold
        self.tile = tile
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (45, 45))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=tile.pos)
        self.rect.center = tile.rect.center


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

    def update(self):
        global city_screen_open, selected_city
        if selected_city == self:
            city_screen_open = False
            selected_city = None
        else:
            city_screen_open = True
            selected_city = self


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
            global units, units_to_draw, unit_screen_open
            global cities_to_draw, cities
            units_to_draw.remove(self)
            units = pygame.sprite.Group(units_to_draw)
            cities_to_draw.append(new_city)
            cities = pygame.sprite.Group(cities_to_draw)
            selected_unit = None
            unit_screen_open = False


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


class Tech(pygame.sprite.Sprite):
    def __init__(self, image: Image, requirements, unlocked=False):
        super().__init__()
        self.image_class = image
        self.image = image.image
        self.rect = image.rect
        self.requirements = requirements
        self.unlocked = unlocked

    def update(self, event):
        if type(event) == pygame.event.Event and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.unlocked:
                for i in self.requirements:
                    if not i.unlocked:
                        return
                print("UNLOCKED UWU!!!!!!!!!!!")
                self.unlocked = True


pygame.init()
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)

fps = 60
clock = pygame.time.Clock()

# main menu
start_game = Image("src/icons/start_game.png", (150, 75), (400, 200))
loading = Image("src/icons/loading.png", (150, 75), (400, 400))
game_started = False
while True:
    events = pygame.event.get()
    screen.fill((0, 0, 0))
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if start_game.rect.collidepoint(event.pos):
                game_started = True

    screen.blit(start_game.image, start_game.pos)
    if game_started:
        screen.blit(loading.image, loading.pos)
        pygame.display.flip()
        clock.tick(fps)
        break
    pygame.display.flip()
    clock.tick(fps)

# main game
resource_types = ("govno", "z")
teams = (Team("Danish", [], "src/icons/danish.png"), Team("Dutch", [], "src/icons/dutch.png"),
         Team("English", [], "src/icons/english.png"),
         Team("Indian", [], "src/icons/indian.png"), Team("Japanese", [], "src/icons/japanese.png"),
         Team("Russian", [], "src/icons/russian.png"),
         Team("Spanish", [], "src/icons/spanish.png"), Team("Swedish", [], "src/icons/swedish.png"))
Biomes = (Biome("Tundra", 2, 4, "src/biomes/tundra.png"), Biome("Desert", 2, 4, "src/biomes/desert.png"),
          Biome("Swamp", 3, 5, "src/biomes/swamp.png"), Biome("Mountains", 3, 3, "src/biomes/mountains.png"),
          Biome("Plains", 1, 1, "src/biomes/plains.png"), Biome("RollingPlains", 2, 1, "src/biomes/hills.png"),
          Biome("Jungle", 3, 2, "src/biomes/jungle.png"), Biome("Woods", 1, 1, "src/biomes/woods.png"),
          Biome("Sea", 3, 5, "src/biomes/sea.png"))
'''
Resources = (Resource("Horses", "src/resource/Horses.png", "Strategic", 0.05, 1, 2, 0, (1, 1)),
             Resource("Iron", "src/resource/Iron.png", "Strategic", 0.05, 2, 0, 0, (1, 1)),
             Resource("Flur", "src/resource/Furs.png", "Valuable", 0.05, 1, 1, 3, (1, 1)),
             Resource("Diamonds", "src/resource/Gems.png", "Valuable", 0.05, 2, 0, 3, (1, 1)),
             Resource("Ivory", "src/resource/Ivory.png", "Valuable", 0.05, 1, 1, 3, (1, 1)),
             Resource("Spices", "src/resource/Spice.png", "Valuable", 0.05, 2, 0, 3, (1, 1)),
             Resource("Oasis", "src/resource/Oasis.png", "Bonus", 0.05, 0, 3, 1, (1, 1)),
             Resource("Fish", "src/resource/fish.png", "Bonus", 0.05, 1, 3, 1, (1, 1)),
             Resource("Game", "src/resource/Game.png ", "Bonus", 0.05, 1, 1, 0, (1, 1)),
             Resource("Пшеница", "src/resource/Wheat.png", "Bonus", 0.05, 0, 1, 0, (1, 1)),
             Resource("Сахар", "src/resource/Sugar.png", "Bonus", 0.05, 0, 1, 2, (1, 1)))
'''

game = Game(1, teams, teams[2], (30, 30), screen)
tile_size = 90
resources_to_draw = []
game.start_game()
game.generate_resources()
settlertest = Settler("settler1", (2, 0), teams[2], 5)
units_to_draw = [settlertest]
cities_to_draw = []
units = pygame.sprite.Group(units_to_draw)
tiles = pygame.sprite.Group(game.map)
cities = pygame.sprite.Group(cities_to_draw)
resourcesss = pygame.sprite.Group()
resourcesss.add(resources_to_draw)

camera = Camera()

bronze_working = Tech(Image("src/icons/bronze_working.png", (50, 50), (100, 80)), [])
masonry = Tech(Image("src/icons/masonry.png", (50, 50), (100, 140)), [])
alphabet = Tech(Image("src/icons/alphabet.png", (50, 50), (100, 200)), [])
pottery = Tech(Image("src/icons/pottery.png", (50, 50), (100, 260)), [])
wheel = Tech(Image("src/icons/wheel.png", (50, 50), (100, 320)), [])
warrior_code = Tech(Image("src/icons/warrior_code.png", (50, 50), (100, 380)), [])
ceremonial_burial = Tech(Image("src/icons/ceremonial_burial.png", (50, 50), (100, 440)), [])
iron_working = Tech(Image("src/icons/iron_working.png", (50, 50), (200, 80)), [bronze_working])
mathematics = Tech(Image("src/icons/mathematics.png", (50, 50), (200, 140)), [masonry])
writing = Tech(Image("src/icons/writing.png", (50, 50), (200, 200)), [alphabet])
horseback_riding = Tech(Image("src/icons/horseback_riding.png", (50, 50), (200, 350)), [wheel, warrior_code])
mysticism = Tech(Image("src/icons/mysticism.png", (50, 50), (200, 440)), [ceremonial_burial])
construction = Tech(Image("src/icons/construction.png", (50, 50), (300, 80)), [iron_working, mathematics])
currency = Tech(Image("src/icons/currency.png", (50, 50), (300, 140)), [mathematics])
philosophy = Tech(Image("src/icons/philosophy.png", (50, 50), (300, 200)), [writing])
code_of_law = Tech(Image("src/icons/code_of_law.png", (50, 50), (300, 260)), [writing])
literature = Tech(Image("src/icons/literature.png", (50, 50), (300, 320)), [writing])
map_making = Tech(Image("src/icons/map_making.png", (50, 50), (300, 380)), [writing])
polytheism = Tech(Image("src/icons/polytheism.png", (50, 50), (300, 440)), [mysticism])
republic = Tech(Image("src/icons/republic.png", (50, 50), (400, 230)), [philosophy, code_of_law])
monarchy = Tech(Image("src/icons/monarchy.png", (50, 50), (400, 440)), [polytheism])

techs_to_draw = [bronze_working, masonry, alphabet, pottery, wheel, warrior_code, ceremonial_burial, iron_working,
                 mathematics, writing, horseback_riding, mysticism, construction, currency, philosophy, code_of_law,
                 literature, map_making, polytheism, republic, monarchy]
techs = pygame.sprite.Group(techs_to_draw)

science_icon = Image("src/icons/science_icon.png", (30, 30), (10, 10))
scroll = Image("src/icons/scroll.png", window_size)

science_window_open = False
culture_window_open = False

unit_screen_open = False
city_screen_open = False
selected_city = None
MOVING = False

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
            cities.update()
            if not MOVING:
                units.update(event, game)
            if science_window_open:
                techs.update(event)
            if science_icon.rect.collidepoint(event.pos):
                science_window_open = not science_window_open

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera.move(0, 10)
    if keys[pygame.K_s]:
        camera.move(0, -10)
    if keys[pygame.K_a]:
        camera.move(10, 0)
    if keys[pygame.K_d]:
        camera.move(-10, 0)

    if keys[pygame.K_SPACE] and selected_unit is not None:
        units.update("settle", game)
    if keys[pygame.K_ESCAPE] and (science_window_open or culture_window_open or city_screen_open or unit_screen_open):
        close_window()

    camera.update(units)
    camera.update(tiles)
    camera.update(cities)
    camera.update(resourcesss)
    update_window()
    if science_window_open:
        techs.draw(screen)
    else:
        tiles.draw(screen)
        resourcesss.draw(screen)
        units.draw(screen)
        cities.draw(screen)
    screen.blit(science_icon.image, science_icon.pos)

    if selected_unit is not None:
        selected_unit.open_unit_screen()

    if selected_city is not None:
        selected_city.open_city_screen()

    MOVING = False
    camera.reset_offset()
    pygame.display.flip()
    clock.tick(fps)
