import random
from collections import deque

import pygame
import sys
import math

science_to_unlock = 50
selected_unit = None


class Checkbox:
    def __init__(self, x, y, width, height, color_active=(0, 200, 0), color_inactive=(200, 0, 0),
                 border_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.border_color = border_color
        self.checked = False

    def handle_event(self, event, team):
        global teams
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.checked:
                    teams.append(team)
                    print(teams)
                else:
                    teams.remove(team)
                    print(teams)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color_active if self.checked else self.color_inactive, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 3)

        if self.checked:
            pygame.draw.line(screen, self.border_color, (self.rect.left + 5, self.rect.centery),
                             (self.rect.centerx, self.rect.bottom - 5), 3)
            pygame.draw.line(screen, self.border_color, (self.rect.centerx, self.rect.bottom - 5),
                             (self.rect.right - 5, self.rect.top + 5), 3)


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
    global city_screen_open, selected_city, buildings_to_draw
    city_screen_open = False
    selected_city = None
    buildings_to_draw = pygame.sprite.Group()
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

    if game.map[int(goal[1])][int(goal[0])].biome.name == "Sea" and map_making.unlocked == False:
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

    def next_turn(self):
        global science_to_unlock, teams
        for i in units_to_draw:
            if i.cur_walk_points != 0:
                if i.hp + 5 < 100:
                    i.hp += 5
                else:
                    i.hp += (100 - i.hp)
            i.cur_walk_points = i.walk_points
        print(teams)
        for i in range(len(teams)):
            if self.player_team.name == teams[i].name:
                z = (i + 1) % len(teams)
                self.player_team = teams[z]
                break
        print(self.player_team.name)
        for i in cities:
            if i.in_progress is not None:
                i.in_progress = (i.in_progress[0], i.in_progress[1] - 1)
            i.left_to_grow -= 1
            science_to_unlock += i.science

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
    def __init__(self, name, walk_difficulty, harshness, image_path, production, food):
        self.name = name
        self.walk_difficulty = walk_difficulty
        self.harshness = harshness
        self.image_path = image_path
        self.production = production
        self.food = food


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
        self.unit = None
        self.city = None

    def update(self, event, game):
        global selected_unit
        global MOVING
        if self.rect.collidepoint(event.pos) and (selected_unit.pos[0] * 90, selected_unit.pos[1] * 90) != self.pos \
                and selected_unit.team == game.player_team:
            pathuwu = find_shortest_path(game.map, selected_unit.pos,
                                         (self.pos[0] / tile_size, self.pos[1] / tile_size))
            if pathuwu <= selected_unit.cur_walk_points:
                for i in range(len(units_to_draw)):
                    if units_to_draw[i].pos == (self.pos[0] / tile_size, self.pos[1] / tile_size):
                        self.unit = units_to_draw[i]
                if self.unit is None:
                    selected_unit.rect.center = self.rect.center
                    game.map[selected_unit.pos[0]][selected_unit.pos[1]].unit = None
                    selected_unit.pos = (int(self.pos[0] / tile_size), int(self.pos[1] / tile_size))
                    selected_unit.cur_walk_points -= pathuwu
                    self.unit = selected_unit
                    selected_unit.deselect()
                    selected_unit = None
                    MOVING = True
                elif self.unit.team == selected_unit.team:
                    selected_unit.deselect()
                    selected_unit = None
                elif self.unit.team != selected_unit.team:
                    selected_unit.Attack(self.unit)
            else:
                print("too far")
                selected_unit.deselect()
                selected_unit = None


class Unit(pygame.sprite.Sprite):
    def __init__(self, image_path, name, team, pos, walk_points, attack, defense):
        super().__init__()
        self.name = name
        self.team = team
        self.image_path = image_path
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (150, 150))
        self.image_original = image.subsurface(image.get_bounding_rect())
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.rect.center = game.map[self.pos[1]][self.pos[0]].rect.center
        self.walk_points = walk_points
        self.unit_walk_points = walk_points

        self.font = pygame.font.SysFont("Arial", 20)
        self.unit_screen = pygame.Surface((600, 250))
        self.name_of_units = self.font.render(f"{self.name}", True, (0, 0, 0))
        self.walk = self.font.render(f"Перемещение: {self.unit_walk_points}", True, (0, 0, 0))
        self.unit_hp = 100
        self.hp_text = self.font.render(f"Здоровье: {self.unit_hp}", True, (0, 0, 0))
        self.team_text = self.font.render(f'Команда: {self.team.name if self.team is not None else "Нет"}', True, (0, 0, 0))
        self.defense = defense
        self.attack = attack

    @property
    def cur_walk_points(self):
        return self.unit_walk_points

    @cur_walk_points.setter
    def cur_walk_points(self, new_value):
        self.unit_walk_points = new_value
        self.walk = self.font.render(f"Перемещение:{self.unit_walk_points}", True, (0, 0, 0))

    @property
    def hp(self):
        return self.unit_hp

    @hp.setter
    def hp(self, new_value):
        self.unit_hp = new_value
        self.hp_text = self.font.render(f"Здоровье: {self.unit_hp}", True, (0, 0, 0))

    def update(self, event, game: Game):
        if type(event) == pygame.event.Event and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            global selected_unit, unit_screen_open
            if self.rect.collidepoint(event.pos):
                if selected_unit is not None:
                    selected_unit.deselect()
                if selected_unit == self:
                    selected_unit = None
                    self.deselect()
                    unit_screen_open = False
                else:
                    selected_unit = self
                    self.select()
                    unit_screen_open = True

    def Attack(self, other_unit):
        if self.cur_walk_points > 0:
            if self.team == other_unit.team:
                print(f"{self.name} не может атаковать {other_unit.name}, так как они из одной команды.")
                return
            global units, units_to_draw, selected_unit, MOVING
            x_diff = abs(self.pos[0] - other_unit.pos[0])
            y_diff = abs(self.pos[1] - other_unit.pos[1])
            if x_diff > 1 or y_diff > 1:
                print(f"{self.name} не может атаковать {other_unit.name}, так как они не на соседних клетках.")
                return
            if other_unit.hp > 0:  # У противника должно быть здоровье
                # Рассчитываем урон
                damage = self.attack * (1 - (other_unit.defense / 100))
                if damage > 0:
                    other_unit.hp -= damage
                    self.hp -= (damage / 2)
                    print(f"{self.name} атакует {other_unit.name} и наносит {damage} урона.")
                else:
                    print(f"{self.name} атакует {other_unit.name}, но не наносит урона.")
                    # Проверка на смерть юнита
                selected_unit.deselect()
                if other_unit.hp <= 0:
                    other_unit.hp = 0
                    print(f"{other_unit.name} погибает.")
                    units_to_draw.remove(other_unit)  # Удаляем юнита из игры
                    units = pygame.sprite.Group(units_to_draw)
                    selected_unit = None
                    game.map[self.pos[0]][self.pos[1]].unit = None
                    game.map[other_unit.pos[0]][other_unit.pos[1]].unit = self
                    self.rect.center = game.map[other_unit.pos[1]][other_unit.pos[0]].rect.center
                    self.pos = (int(game.map[other_unit.pos[1]][other_unit.pos[0]].pos[1] / tile_size),
                                int(game.map[other_unit.pos[1]][other_unit.pos[0]].pos[0] / tile_size))
                    self.cur_walk_points = 0
                    self.deselect()
                    selected_unit = None
                    MOVING = True
                if self.hp <= 0:
                    self.hp = 0
                    print(f"{self.name} погиб в бою")
                    self.deselect()
                    if self in units_to_draw:
                        units_to_draw.remove(self)
                        units = pygame.sprite.Group(units_to_draw)
                        selected_unit = None
                        game.map[self.pos[0]][self.pos[1]].unit = None
            self.cur_walk_points = 0
        else:
            print(f"Недостаточно очков перемещения")
        selected_unit = None

    def select(self):
        self.image = self.image_original.copy()
        dark_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 100))
        self.image.blit(dark_overlay, (0, 0))

    def deselect(self):
        self.image = self.image_original.copy()

    def open_unit_screen(self):
        global selected_unit
        if selected_unit == self:
            # Создаем окно внизу экрана
            unit_screen = pygame.Surface((screen.get_width(), 200))
            unit_screen.fill((200, 200, 200))

            # Отображаем информацию о юните
            name_text = self.font.render(f"Юнит: {self.name}", True, (0, 0, 0))

            # Размещение текста
            unit_screen.blit(name_text, (10, 10))
            unit_screen.blit(self.walk, (10, 40))
            unit_screen.blit(self.hp_text, (300, 10))
            unit_screen.blit(self.team_text, (300, 40))

            # Отображаем окно на экране
            screen.blit(unit_screen, (0, screen.get_height() - 100))


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
        self.can_build = buildings.copy()
        self.can_unit = units_for_city.copy()
        self.built = []
        self.building = False
        self.uniting = False
        self.progress = None
        self.queue = []

        self.neighbours = []
        for r in range(pos[0] - 1, pos[0] + 2):
            for c in range(pos[1] - 1, pos[1] + 2):
                if r == pos[0] and c == pos[1]:
                    continue
                if 0 <= r < len(game.map) and 0 <= c < len(game.map[0]):
                    for i in cities:
                        if i.pos == (r, c):
                            break
                    else:
                        self.neighbours.append((r, c))

        self._production = 1
        self._food = 1
        self._gold_income = 1
        for i in self.neighbours:
            cur = game.map[i[1]][i[0]]
            if cur.resource is not None:
                self._production += cur.resource.production
                self._food += cur.resource.food
                self._gold_income += cur.resource.gold
            self._production += cur.biome.production
            self._food += cur.biome.food

        self.food_to_grow = self.population * 15
        self.grow = math.ceil(self.food_to_grow / self._food)
        self._left_to_grow = self.grow
        self.science = 1

        self.font = pygame.font.SysFont("Arial", 20)
        self.city_screen = pygame.Surface((250, 600))
        self.gold_income_text = self.font.render(f"Золото за ход: {self._gold_income}", True, (0, 0, 0))
        self.production_per_turn_text = self.font.render(f"Производство: {self._production}", True, (0, 0, 0))
        self.food_text = self.font.render(f"Пищи за ход: {self._food}", True, (0, 0, 0))
        self.turn_to_grow_text = self.font.render(f"Ходов до роста: {self._left_to_grow}", True, (0, 0, 0))
        self.buildings_text = self.font.render(f"Построенные здания:", True, (0, 0, 0))

        self.population_text = self.font.render(f"Население: {self.population}", True, (0, 0, 0))
        self.religion_text = self.font.render(f"Религия: {self.religion if self.religion else 'Нет'}", True, (0, 0, 0))
        self.queue_text = self.font.render(f"Очередь:", True, (0, 0, 0))
        self.name_text = self.font.render(f"Город: {self.name}", True, (0, 0, 0))

    @property
    def in_progress(self):
        return self.progress

    @in_progress.setter
    def in_progress(self, new_value):
        self.progress = new_value
        if self.progress is not None and self.progress[1] <= 0:
            if type(self.progress[0]) == Building:
                self.built.append(self.progress[0])
                self.production += self.progress[0].production_give
                self.food += self.progress[0].food_give
                self.gold_income += self.progress[0].gold_give
                self.science += self.progress[0].science_give
            else:
                global units
                for i in self.neighbours:
                    if game.map[i[1]][i[0]].unit is None and game.map[i[1]][i[0]].biome.name != "Sea":
                        z = type(self.progress[0].unit)((i[0], i[1]), self.team)
                        units_to_draw.append(z)
                        units.add(z)
                        game.map[i[1]][i[0]].unit = z
                        break
            self.progress = None

    @property
    def production(self):
        return self._production

    @production.setter
    def production(self, new_value):
        self._production = new_value
        self.production_per_turn_text = self.font.render(f"Производство: {self._production}", True, (0, 0, 0))

    @property
    def food(self):
        return self._food

    @food.setter
    def food(self, new_value):
        self._food = new_value
        self.food_text = self.font.render(f"Пищи за ход: {self._food}", True, (0, 0, 0))

    @property
    def gold_income(self):
        return self._gold_income

    @gold_income.setter
    def gold_income(self, new_value):
        self._gold_income = new_value
        self.gold_income_text = self.font.render(f"Золото за ход: {self._gold_income}", True, (0, 0, 0))

    @property
    def left_to_grow(self):
        return self._left_to_grow

    @left_to_grow.setter
    def left_to_grow(self, new_value):
        self._left_to_grow = new_value
        if self._left_to_grow <= 0:
            self.population += 1
            self.population_text = self.font.render(f"Население: {self.population}", True, (0, 0, 0))
            self.food_to_grow = self.population * 15
            self.grow = math.ceil(self.food_to_grow / self._food)
            self._left_to_grow = self.grow
        self.turn_to_grow_text = self.font.render(f"Ходов до роста: {self._left_to_grow}", True, (0, 0, 0))

    def open_city_screen(self):
        global buildings_to_draw
        self.city_screen.fill((200, 200, 200))  # Цвет фона для экрана города

        # Отображаем информацию о городе
        self.city_screen.blit(build_button.image, (10, 10))
        self.city_screen.blit(unit_button.image, (60, 10))
        build_button.change_pos((screen.get_width() - self.city_screen.get_width() + 10, 10))
        unit_button.change_pos((screen.get_width() - self.city_screen.get_width() + 60, 10))
        if not self.building and not self.uniting:
            self.city_screen.blit(self.name_text, (10, 60))
            self.city_screen.blit(self.population_text, (10, 90))
            self.city_screen.blit(self.religion_text, (10, 120))
            self.city_screen.blit(self.production_per_turn_text, (10, 150))
            self.city_screen.blit(self.food_text, (10, 180))
            self.city_screen.blit(self.gold_income_text, (10, 210))
            self.city_screen.blit(self.turn_to_grow_text, (10, 240))
            self.city_screen.blit(self.queue_text, (10, 270))
            self.city_screen.blit(self.buildings_text, (10, 300))
            for i in range(len(self.built)):
                self.city_screen.blit(self.built[i].image.image, (10, 270 + (60 * (i + 1))))
                self.city_screen.blit(self.font.render(self.built[i].name, True, (0, 0, 0)), (90, 280 + (65 * (i + 1))))
        elif self.building:
            for i in range(len(self.can_build)):
                self.city_screen.blit(self.can_build[i].image.image, (10, 10 + (60 * (i + 1))))
                self.city_screen.blit(self.font.render(self.can_build[i].name, True, (0, 0, 0)),
                                      (90, 20 + (61 * (i + 1))))
                self.can_build[i].image.change_pos((screen.get_width() - self.city_screen.get_width() + 10,
                                                    screen.get_height() - self.city_screen.get_height() + 10 + (
                                                            60 * (i + 1))))
            buildings_to_draw = pygame.sprite.Group(self.can_build)
        else:
            auf = 0
            drawuwu = []
            for i in range(len(self.can_unit)):
                for z in self.can_unit[i][1]:
                    if not z.unlocked:
                        break
                else:
                    self.city_screen.blit(self.can_unit[i][0].image.image, (10, 10 + (60 * (auf + 1))))
                    self.city_screen.blit(self.font.render(self.can_unit[i][0].unit.name, True, (0, 0, 0)),
                                          (90, 20 + (61 * (auf + 1))))
                    self.can_unit[i][0].image.change_pos((screen.get_width() - self.city_screen.get_width() + 10,
                                                          screen.get_height() - self.city_screen.get_height() + 10 + (
                                                                  60 * (auf + 1))))
                    auf += 1
                    drawuwu.append(self.can_unit[i][0])
            buildings_to_draw = pygame.sprite.Group(drawuwu)

        # Отображаем экран города справа от экрана игры
        screen.blit(self.city_screen, (screen.get_width() - self.city_screen.get_width(), 0))

    def update(self, event):
        global city_screen_open, selected_city, buildings_to_draw
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            if selected_city == self:
                city_screen_open = False
                selected_city = None
                buildings_to_draw = pygame.sprite.Group()
            else:
                city_screen_open = True
                selected_city = self


class UnitToBuild(pygame.sprite.Sprite):
    def __init__(self, food_to_build, image_path, unit):
        super().__init__()
        self.image = Image(image_path, (150, 150), (10, 10))
        self.food_to_build = food_to_build
        self.unit = unit

    def update(self, event):
        global selected_city
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.image.rect.collidepoint(
                event.pos) and selected_city.uniting:
            if selected_city.in_progress is not None:
                selected_city.queue.append(selected_city.in_progress)
                selected_city.in_progress = None
            for i in selected_city.queue:
                if i[0] == self:
                    selected_city.in_progress = i
                    selected_city.queue.remove(i)
                    break
            else:
                selected_city.in_progress = (self, math.ceil(self.food_to_build / selected_city.food))


class Building(pygame.sprite.Sprite):
    def __init__(self, name, image_path, production_to_build, production_give, food_give, gold_give, science_give):
        super().__init__()
        self.name = name
        self.image = Image(image_path, (150, 150), (10, 10))
        self.production_to_build = production_to_build
        self.production_give = production_give
        self.food_give = food_give
        self.gold_give = gold_give
        self.science_give = science_give

    def update(self, event):
        global selected_city
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.image.rect.collidepoint(
                event.pos) and selected_city.building:
            selected_city.can_build.remove(self)
            if selected_city.in_progress is not None:
                selected_city.queue.append(selected_city.in_progress)
                selected_city.can_build.insert(0, selected_city.in_progress[0])
                selected_city.in_progress = None
            for i in selected_city.queue:
                if i[0] == self:
                    selected_city.in_progress = i
                    selected_city.queue.remove(i)
                    break
            else:
                selected_city.in_progress = (self, math.ceil(self.production_to_build / selected_city.production))


class Archer(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/archer.png", name="Лучник", pos=pos, team=team, walk_points=5, attack=35,
                         defense=10)


class Catapult(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/catapult.png", name="Катапульта", pos=pos, team=team, walk_points=3,
                         attack=55,
                         defense=20)


class Chariot(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/chariot.png", name="Колесница", pos=pos, team=team, walk_points=4,
                         attack=37,
                         defense=25)


class Galley(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/galley.png", name="Галера", pos=pos, team=team, walk_points=5, attack=40,
                         defense=10)


class Horseman(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/horseman.png", name="Всадник", pos=pos, team=team, walk_points=7,
                         attack=47,
                         defense=20)


class Scout(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/scout.png", name="Разведчик", pos=pos, team=team, walk_points=8,
                         attack=20,
                         defense=10)


class Settler(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/settler.png", name="Поселенец", pos=pos, team=team, walk_points=5,
                         attack=1,
                         defense=1)

    def update(self, event, game):
        super().update(event, game)
        global selected_unit
        if type(event) == str and event == "settle" and selected_unit == self and game.map[self.pos[1]][
            self.pos[0]].biome.name != "Sea":
            new_city = City(self.team.city_image_path, self.pos, f'{random.randint(1, 10)}_{random.randint(1, 10)}',
                            self.team, 1, None)
            self.team.cities.append(new_city)
            print(self.team.cities)
            global units, units_to_draw, unit_screen_open
            global cities_to_draw, cities
            units.remove(self)
            cities.add(new_city)
            selected_unit = None
            unit_screen_open = False


class Spearman(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/spearman.png", name="Копейщик", pos=pos, team=team, walk_points=6,
                         attack=30,
                         defense=20)


class Swordsman(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/swordsman.png", name="Мечник", pos=pos, team=team,
                         walk_points=5, attack=35, defense=30)


class Trireme(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/trireme.png", name="Трирема", pos=pos, team=team, walk_points=6,
                         attack=30,
                         defense=10)


class Warrior(Unit):
    def __init__(self, pos, team):
        super().__init__(image_path="src/units/warrior.png", name="Воин", pos=pos, team=team, walk_points=5, attack=27,
                         defense=17)


class Tech(pygame.sprite.Sprite):
    def __init__(self, image: Image, requirements, unlocked=False):
        super().__init__()
        self.image_class = image
        self.image = image.image
        self.rect = image.rect
        self.requirements = requirements
        self.unlocked = unlocked

    def update(self, event):
        global science_to_unlock
        if type(event) == pygame.event.Event and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.unlocked and science_to_unlock >= 50:
                for i in self.requirements:
                    if not i.unlocked:
                        return
                science_to_unlock = 0
                print("UNLOCKED UWU!!!!!!!!!!!")
                self.unlocked = True
                self.image.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)


pygame.init()
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Kirilization 3")

fps = 60
clock = pygame.time.Clock()
teams_c = (Team("Дания", [], "src/icons/danish.png"), Team("Нидерланды", [], "src/icons/dutch.png"),
           Team("Англия", [], "src/icons/english.png"),
           Team("Индия", [], "src/icons/indian.png"), Team("Япония", [], "src/icons/japanese.png"),
           Team("Россия", [], "src/icons/russian.png"),
           Team("Испания", [], "src/icons/spanish.png"), Team("Швеция", [], "src/icons/swedish.png"))

teams = []

# main menu
start_game = Image("src/icons/start_game.png", (150, 75), (325, 500))
loading = Image("src/icons/loading.png", (150, 75), (600, 500))
danish = Image("src/icons/danish_menu.png", (150, 75), (100, 25))
danish_c = Checkbox(25, 35, 50, 50)
dutch = Image("src/icons/dutch_menu.png", (150, 75), (100, 100))
dutch_c = Checkbox(25, 110, 50, 50)
english = Image("src/icons/english_menu.png", (150, 75), (100, 175))
english_c = Checkbox(25, 185, 50, 50)
indian = Image("src/icons/indian_menu.png", (150, 75), (100, 250))
indian_c = Checkbox(25, 260, 50, 50)
japanese = Image("src/icons/japanese_menu.png", (150, 75), (550, 25))
japanese_c = Checkbox(475, 35, 50, 50)
russia = Image("src/icons/russia_menu.png", (150, 75), (550, 100))
russia_c = Checkbox(475, 110, 50, 50)
spanish = Image("src/icons/spanish_menu.png", (150, 75), (550, 175))
spanish_c = Checkbox(475, 185, 50, 50)
swedish = Image("src/icons/swedish_menu.png", (150, 75), (550, 250))
swedish_c = Checkbox(475, 260, 50, 50)
background = Image("src/icons/menu_background.png", (800, 600), (0, 0))
game_started = False
while True:
    events = pygame.event.get()
    screen.fill((0, 0, 0))
    screen.blit(background.image, background.pos)
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if len(teams) > 0 and start_game.rect.collidepoint(event.pos):
                game_started = True
        danish_c.handle_event(event, teams_c[0])
        dutch_c.handle_event(event, teams_c[1])
        english_c.handle_event(event, teams_c[2])
        indian_c.handle_event(event, teams_c[3])
        japanese_c.handle_event(event, teams_c[4])
        russia_c.handle_event(event, teams_c[5])
        spanish_c.handle_event(event, teams_c[6])
        swedish_c.handle_event(event, teams_c[7])

    screen.blit(start_game.image, start_game.pos)
    screen.blit(danish.image, danish.pos)
    screen.blit(dutch.image, dutch.pos)
    screen.blit(english.image, english.pos)
    screen.blit(indian.image, indian.pos)
    screen.blit(japanese.image, japanese.pos)
    screen.blit(russia.image, russia.pos)
    screen.blit(spanish.image, spanish.pos)
    screen.blit(swedish.image, swedish.pos)
    danish_c.draw(screen)
    dutch_c.draw(screen)
    english_c.draw(screen)
    indian_c.draw(screen)
    japanese_c.draw(screen)
    russia_c.draw(screen)
    spanish_c.draw(screen)
    swedish_c.draw(screen)
    if game_started:
        screen.blit(loading.image, loading.pos)
        pygame.display.flip()
        clock.tick(fps)
        break
    pygame.display.flip()
    clock.tick(fps)

# main game
Biomes = (Biome("Tundra", 2, 4, "src/biomes/tundra.png", 1, 0), Biome("Desert", 2, 4, "src/biomes/desert.png", 0, 0),
          Biome("Swamp", 3, 5, "src/biomes/swamp.png", 1, 0),
          Biome("Mountains", 3, 3, "src/biomes/mountains.png", 2, 0),
          Biome("Plains", 1, 1, "src/biomes/plains.png", 1, 1),
          Biome("RollingPlains", 2, 1, "src/biomes/hills.png", 2, 1),
          Biome("Jungle", 3, 2, "src/biomes/jungle.png", 1, 2), Biome("Woods", 1, 1, "src/biomes/woods.png", 2, 1),
          Biome("Sea", 3, 5, "src/biomes/sea.png", 0, 1))
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

game = Game(1, teams, None, (30, 30), screen)
tile_size = 90
buildings = [Building("Акведук", "src/building/aqueduct.png", 70, 1, 3, 0, 0),
             Building("Колизей", "src/building/Colosseum.png", 70, 0, 0, 3, 1),
             Building("Здание суда", "src/building/Courthouse.png", 80, 1, 1, 1, 1),
             Building("Зернохранилище", "src/building/granary.png", 40, 0, 2, 0, 0),
             Building("Гавань", "src/building/harbor.png", 80, 1, 2, 2, 0),
             Building("Библиотека", "src/building/library.png", 58, 0, 0, 0, 3),
             Building("Рынок", "src/building/market.png", 80, 0, 1, 3, 0),
             Building("Аванпост", "src/building/library.png", 40, 1, 0, 1, 0),
             Building("Дворец", "src/building/Palace.png", 64, 1, 1, 3, 2),
             Building("Храм", "src/building/temple.png", 70, 0, 0, 2, 2),
             Building("Стены", "src/building/wall.png", 58, 2, 0, 0, 0)]

resources_to_draw = []
game.start_game()
game.generate_resources()
units_to_draw = []
cities_to_draw = []
units = pygame.sprite.Group(units_to_draw)
tiles = pygame.sprite.Group(game.map)
cities = pygame.sprite.Group(cities_to_draw)
resourcesss = pygame.sprite.Group()
resourcesss.add(resources_to_draw)
buildings_to_draw = pygame.sprite.Group()

build_button = Image("src/icons/build.png", (50, 50), (10, 10))
unit_button = Image("src/icons/unit_button.png", (50, 50), (10, 10))

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

unitsss = [Archer((0, 0), None), Catapult((0, 0), None),
           Chariot((0, 0), None), Galley((0, 0), None),
           Horseman((0, 0), None), Scout((0, 0), None),
           Settler((0, 0), None),
           Spearman((0, 0), None),
           Swordsman((0, 0), None), Trireme((0, 0), None),
           Warrior((0, 0), None)]

units_for_city = [[UnitToBuild(30, unitsss[0].image_path, unitsss[0]), [warrior_code]],
                  [UnitToBuild(30, unitsss[1].image_path, unitsss[1]), [mathematics]],
                  [UnitToBuild(30, unitsss[2].image_path, unitsss[2]), [wheel]],
                  [UnitToBuild(30, unitsss[3].image_path, unitsss[3]), [map_making]],
                  [UnitToBuild(30, unitsss[4].image_path, unitsss[4]), [horseback_riding]],
                  [UnitToBuild(30, unitsss[5].image_path, unitsss[5]), []],
                  [UnitToBuild(30, unitsss[6].image_path, unitsss[6]), []],
                  [UnitToBuild(30, unitsss[7].image_path, unitsss[7]), [bronze_working]],
                  [UnitToBuild(30, unitsss[8].image_path, unitsss[8]), [iron_working]],
                  [UnitToBuild(30, unitsss[9].image_path, unitsss[9]), [alphabet]],
                  [UnitToBuild(30, unitsss[10].image_path, unitsss[10]), []]]

science_icon = Image("src/icons/science_icon.png", (30, 30), (10, 10))
scroll = Image("src/icons/scroll.png", window_size)
next_turn_icon = Image("src/icons/next_turn.png", (200, 200), (610, 420))
open_tech_text = Image("src/icons/You can open tech.png", (200, 100), (400, 5))

science_window_open = False
culture_window_open = False

unit_screen_open = False
city_screen_open = False
selected_city = None
MOVING = False
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
game.player_team = teams[0]
for z in teams:
    i = random.randint(0, len(game.map) - 1)
    j = random.randint(0, len(game.map[i]) - 1)
    while game.map[i][j].biome.name == "Sea" or game.map[i][j].unit is not None:
        i = random.randint(0, len(game.map) - 1)
        j = random.randint(0, len(game.map[i]) - 1)
    s = Settler((j, i), z)
    units_to_draw.append(s)
    units.add(s)
    game.map[i][j].unit = units_to_draw[len(units_to_draw) - 1]


# main loop
while True:
    text_surface = my_font.render(f"{game.player_team.name}", False, (255, 255, 255))
    events = pygame.event.get()
    screen.fill((0, 0, 0))
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if selected_unit is None and selected_city is None and next_turn_icon.rect.collidepoint(event.pos):
                game.next_turn()
            if selected_unit is not None:
                tiles.update(event, game)
                update_window()
            cities.update(event)
            buildings_to_draw.update(event)
            if not MOVING:
                units.update(event, game)
            if science_window_open:
                techs.update(event)
            if science_icon.rect.collidepoint(event.pos):
                science_window_open = not science_window_open
            if selected_city is not None and build_button.rect.collidepoint(
                    event.pos) and selected_city.team == game.player_team:
                selected_city.building = not selected_city.building
                if selected_city.building:
                    selected_city.uniting = False
            if selected_city is not None and unit_button.rect.collidepoint(
                    event.pos) and selected_city.team == game.player_team:
                selected_city.uniting = not selected_city.uniting
                if selected_city.uniting:
                    selected_city.building = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera.move(0, 7)
    if keys[pygame.K_s]:
        camera.move(0, -7)
    if keys[pygame.K_a]:
        camera.move(7, 0)
    if keys[pygame.K_d]:
        camera.move(-7, 0)

    if keys[pygame.K_SPACE]:
        units.update("settle", game)
    if keys[pygame.K_ESCAPE] and (
            science_window_open or culture_window_open or city_screen_open or unit_screen_open):
        close_window()

    camera.update(units)
    camera.update(tiles)
    camera.update(cities)
    camera.update(resourcesss)
    update_window()
    if science_window_open:
        techs.draw(screen)
        if science_to_unlock >= 50:
            text_surface = my_font.render(f"Вы можете открыть новую технологию", False, (255, 255, 255))
            screen.blit(text_surface, (200, 30))
    else:
        tiles.draw(screen)
        resourcesss.draw(screen)
        units.draw(screen)
        cities.draw(screen)
    if selected_city is not None:
        selected_city.open_city_screen()
    if selected_unit is not None:
        selected_unit.open_unit_screen()

    screen.blit(science_icon.image, science_icon.pos)

    if selected_unit is None and selected_city is None and not science_window_open:
        screen.blit(next_turn_icon.image, next_turn_icon.pos)
        screen.blit(text_surface, (next_turn_icon.pos[0] + 40, next_turn_icon.pos[1]))
    MOVING = False
    camera.reset_offset()
    pygame.display.flip()
    clock.tick(fps)
