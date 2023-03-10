import os
import sys
import pygame
import random


class Camera:
    """Класс камеры. Перемещает спрайты ртносительно героя

    Attributes
    ----------
    dx : int
        смещние объекта по оси x
    dy : int
        смещние объекта по оси y

    Methods
    -------
    apply(obj)
        сдвигает объект obj на смещение камеры
    update(target)
        изменить смещение камеры для target
    """
    # зададим начальный сдвиг камеры
    def __init__(self, app):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        """сдвинуть объект obj на смещение камеры"""
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        """позиционировать камеру на объекте target"""
        self.dx = -(target.rect.x + target.rect.w // 2 - app.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - app.height // 2)


class Tile(pygame.sprite.Sprite):
    """Класс тайла"""
    def __init__(self, app, tile_type, pos_x, pos_y, *groups):
        super().__init__(app.tiles_group, app.all_sprites)
        tile_images = {
            'box': app.load_image('box.jpg'),
            'floor': app.load_image('Floor.png'),
            'wall': app.load_image("bord_hor.png"),
            'black': app.load_image("black.png"),
            'vent': app.load_image("vent.png")
        }
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    """Класс стены

    Methods
    -------
    update()
        Проверяет столкновение с героем. В случае столкновения возвращает гроя назад
    """
    def __init__(self, image, app, pos_x, pos_y):
        super().__init__(app.tiles_group, app.all_sprites, app.boxes_group)
        self.add(app.boxes_group)
        self.image = pygame.transform.scale(image, (app.tile_width, app.tile_height))
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)

    def update(self):
        if pygame.sprite.collide_mask(self, app.hero):
            pygame.mixer.Sound('data/wall.mp3').play()
            app.hero.stop()


class Safe(Wall):
    """Класс сейфа

    Attributes
    ----------
    x : int
        позиция по оси x
    y : int
        позиция по оси y

    Methods
    -------
    update()
        Проверяет столкновение с героем и реализует открытие сейфа
    """
    def __init__(self, app, image, pos_x, pos_y):
        super().__init__(app.load_image(image), app, pos_x, pos_y)
        self.im = image
        self.x = pos_x
        self.y = pos_y
        # self.add(app.items)

    def update(self):
        """Проверяет столкновение с героем и реализует открытие сейфа, если грой имеет ключ к нему"""
        if pygame.sprite.collide_mask(self, app.hero):
            app.hero.stop()
            if app.keys[self.im[0]]:
                pygame.mixer.Sound('data/safe.mp3').play()
                app.keys[self.im[0]] = False
                app.tutorials['keys'] = True


class Keys(pygame.sprite.Sprite):
    """Класс ключа

    Attributes
    ----------
    im : str
        Название изображения

    Methods
    -------
    get()
        Реализует поднятие ключа
    """
    def __init__(self, app, im, pos_x, pos_y):
        super().__init__(app.tiles_group, app.all_sprites, app.items)
        self.add(app.items)
        self.im = im
        self.image = pygame.transform.scale(app.load_image(im), (app.tile_width, app.tile_height))
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)

    def get(self):
        """Поднятие ключа"""
        app.keys[self.im[0]] = True
        print(app.keys)
        pygame.mixer.Sound('data/open.mp3').play()
        self.kill()


class Border(Wall):
    """Класс непроходимого объекта с изображнием image"""
    def __init__(self, app, image, pos_x, pos_y):
        super().__init__(app.load_image(image), app, pos_x, pos_y)


class Door(Wall):
    """Класс двери

    Methods
    -------
    update()
        Когда сталкивается с героем осуществляет переход на следующий уровень, если открыты сейфы
    """
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.load_image('door.png'), app, pos_x, pos_y)

    def update(self):
        """Осуществляет переход на следующий уровень, если открыты сейфы"""
        if pygame.sprite.collide_mask(self, app.hero):
            if all([val is False for val in app.keys.values()]):
                app.tutorials['doors'] = True
                app.all_sprites = pygame.sprite.Group()
                app.all_sprites = pygame.sprite.Group()
                app.boxes_group = pygame.sprite.Group()
                app.items = pygame.sprite.Group()
                app.hero_gr = pygame.sprite.Group()
                app.tiles_group = pygame.sprite.Group()
                app.tutorial_group = pygame.sprite.Group()
                app.loading_screen()

            else:
                app.hero.stop()
            # app.loading_screen()


class App(pygame.sprite.Sprite):
    """Основной класс игры

    Attributes
    ----------
    all_sprites : pygame.sprite.Group
        Группа всех српайтов
    clock : pygame.time.Clock
        Отвечает за время
    screen
        Окно приложения
    width : int
        Ширина экрана
    height : int
        Высота окна
    fps : int
        Количество кадров в секунду
    keys : dict
        Состояние кючей
    tile_width : int
        Ширина тайла(клетки)
    tile_height : int
        Высота тайла(клетки)
    all_sprites : pygame.sprite.Group
        Группа всех спрайтов
    boxes_group : pygame.sprite.Group
        Группа коробок
    items : pygame.sprite.Group
        Группа вещей
    hero_gr : pygame.sprite.Group
        Группа играбельных персоанажей
    hero : Hero
        Персоанаж игрока
    tiles_group : pygame.sprite.Group
        Группа тайлов
    tutorial_group : pygame.sprite.Group
        Обучение
    buttons : pygame.sprite.Group
        Группа кнопок
    camera : Camera
        Камера
    score : int
        Количество набранных очков
    time : int
        Время игры(в фреймах)
    num : int
        Номер текущего уровня
    open_menu : bool
        Состояние меню(открыто/закрыто)
    bar_length : int
        Длина ползунка загрузки
    fon
        Фон игры
    tutorials : dict
        Словарь с состоянием обучения

    Methods
    -------
    terminate()
        Закрытие игры
    load_image(name, colorkey=None)
        Загружает изображение name из папки data
    msg(text, col):
        Выводит на экран text цвета col
    start_wind():
        Открывает стартовое окно
    final_wind():
        Открывает финальное окно
    draw_bar(len):
        Отрисовка прямой загрузки
    loading_screen():
        Открывает экран загрузки и загружает новый уровень
    load_level(filename):
        Загружает уровень из тексового файла
    generate_level(level):
        Создает уроень из строки
    run_game():
        Запускает игру
    spaceship():
        Запускает игру с космическим кораблем
    get_tutorial():
        Возвращает текущий этап обучения
    end_game():
        Открывает финальное окно, после его закрытия запускает игру заново
    menu():
        Открывает меню паузы
    """
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        super().__init__(self.all_sprites)
        pygame.init()
        pygame.mixer.music.load('data/Void-Walk.mp3')
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption('Title')
        pygame.key.set_repeat(200, 70)
        self.fps = 50
        self.keys = {'r': None,
                     'g': None,
                     'p': None}
        self.tile_width = self.tile_height = 50
        self.all_sprites = pygame.sprite.Group()
        self.boxes_group = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.hero_gr = pygame.sprite.Group()
        self.hero = Hero(self, 100, 100)
        self.tiles_group = pygame.sprite.Group()
        self.tutorial_group = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.camera = Camera(self)
        self.hero = None
        self.tutorial = None
        self.score = 0
        self.time = 0
        self.num = -1
        self.open_menu = False
        self.bar_length = 0
        self.fon = pygame.transform.scale(self.load_image('fon.jpeg'), (self.width, self.height))
        self.tutorials = {'walking': False, 'coins': False, 'keys': False, 'doors': False}

    def terminate(self):
        """Закрывает приложение"""
        pygame.quit()
        sys.exit()

    @staticmethod
    def load_image(name, colorkey=None):
        """Загружает зображение из папки data

        Parameters
        ----------
        name : str
            имя файла
        colorkey : None or int
            если -1, делает фон прозрачным
        """
        fullname = os.path.join('data', name)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def msg(self, text, col):
        """Выводит текст на экран

        Parameters
        ----------
        text : str
            текст
        col : tuple or str
            цвет текста
        """
        pygame.time.delay(1000)
        font = pygame.font.Font(None, int(0.04 * self.width))
        string_rendered = font.render(text, True, pygame.Color(col))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = int(0.22 * self.width)
        intro_rect.y = int(0.8 * self.height)
        self.screen.blit(string_rendered, intro_rect)

    def start_wind(self):
        """Открывает стартовое окно"""

        intro_text = ['<НАЗВАНИЕ ИГРЫ>']
        self.sound = pygame.mixer.Sound('data/start.mp3')
        self.sound.play()
        self.fon = pygame.transform.scale(self.load_image('start.jpg'), (self.width, self.height))
        self.screen.blit(self.fon, (0, 0))
        font = pygame.font.Font(None, int(0.06 * self.width))
        text_coord = int(0.4 * self.height)
        for line in intro_text:
            string_rendered = font.render(line, True, pygame.Color(255, 240, 240))
            intro_rect = string_rendered.get_rect()
            text_coord += 30
            intro_rect.top = text_coord
            intro_rect.x = int(0.3 * self.width)
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        count = 0
        while True:
            colors = [(0, 0, 0), "white"]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.sound.stop()
                        # self.run_game()
                        self.loading_screen()
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()

            count += 1

            self.msg('НАЖМИТЕ ПРОБЛЕЛ, ЧТОБЫ ПРОДОЛЖИТЬ', colors[count % 2])
            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def final_wind(self):
        """Открывает финальное окно"""
        intro_text = ['Игра окончена!', f'Ваш счет: {self.score}']
        # self.sound = pygame.mixer.Sound('data/start.mp3')
        self.sound.play()
        self.fon = pygame.transform.scale(self.load_image('final_'), (self.width, self.height))
        self.screen.blit(self.fon, (0, 0))
        font = pygame.font.Font(None, int(0.06 * self.width))
        text_coord = int(0.4 * self.height)
        for line in intro_text:
            string_rendered = font.render(line, True, pygame.Color(255, 240, 240))
            intro_rect = string_rendered.get_rect()
            text_coord += 30
            intro_rect.top = text_coord
            intro_rect.x = int(0.45 * self.width)
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        count = 0
        while True:
            colors = [(0, 0, 0), "white"]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    self.terminate()

            count += 1

            self.msg('НАЖМИТЕ ЛЮБУЮ КНОПКУ', colors[count % 2])
            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def draw_bar(self, len):
        """Отрисовывает прямую загрузки

        Parameters
        ----------
        len : int
            длина прямой
        """
        pygame.time.delay(70)
        self.screen.blit(self.fon, (0, 0))
        pygame.draw.rect(self.screen, (169, 172, 199), ((424, 577), (len, 45)))

    def loading_screen(self):
        """Отрисовывает экран загрузки"""
        self.num += 1

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()
            self.fon = pygame.transform.scale(self.load_image('load.jpg'), (self.width, self.height))

            for i in range(0, 1081, 90):
                self.draw_bar(i)
                pygame.display.update()
                pygame.display.flip()
                self.clock.tick(self.fps)

            # pygame.display.flip()
            #
            # pygame.display.update()
            # pygame.display.flip()
            # self.clock.tick(self.fps)
            print(self.num)
            if self.num < 2:
                self.run_game()
            else:
                self.final_wind()

    def load_level(self, filename):
        """Загружает уровень и возвращает его в виде списка

        Parameters
        ----------
        filename : str
            имя файла
        """

        fullname = os.path.join('data', filename)
        if not os.path.isfile(fullname):
            print(f"Уровень '{fullname}' не найден")
            sys.exit()
        filename = "data/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))

        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level):
        """Создает уровень

        Parameters
        ----------
        level : list
            схема уровня
        """
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    self.tile = Tile(self, 'floor', x, y)
                elif level[y][x] == '#':
                    self.tile_box = Border(self, 'box.jpg', x, y)
                elif level[y][x] == 'd':
                    self.tile_box = Door(self, x, y)
                elif level[y][x] == 'R':
                    self.tile_box = Safe(self, 'red_safe.png', x, y)
                elif level[y][x] == 'P':
                    self.tile_box = Safe(self, 'purple_safe.png', x, y)
                elif level[y][x] == 'G':
                    self.tile_box = Safe(self, 'green_safe.png', x, y)
                elif level[y][x] == 'r':
                    Tile(self, 'floor', x, y)
                    self.tile_box = Keys(self, ('red_key.png'), x, y)
                elif level[y][x] == 'p':
                    Tile(self, 'floor', x, y)
                    self.tile_box = Keys(self, ('purple_key.png'), x, y)
                elif level[y][x] == 'g':
                    Tile(self, 'floor', x, y)
                    self.tile_box = Keys(self, ('green_key.png'), x, y)
                elif level[y][x] == '|':
                    self.tile_box = Border(self, 'bord_hor.png', x, y)
                elif level[y][x] == '@':
                    self.tile_hero = Tile(self, 'floor', x, y)
                    self.hero = Hero(self, x, y)
                elif level[y][x] == 'b':
                    self.tile_hero = Tile(self, 'black', x, y)
                elif level[y][x] == 'C':
                    Tile(self, 'floor', x, y)
                    Coin(self, x, y)
                elif level[y][x] == 'v':
                    self.tile_hero = Tile(self, 'vent', x, y)
                elif level[y][x] == 'S':
                    Tile(self, 'floor', x, y)
                    SpaceshipTile(self, x, y)
        # вернем игрока, а также размер поля в клетках

    def run_game(self):
        """Запускает игру"""
        self.fon = pygame.transform.scale(self.load_image('fon.jpeg'), (self.width, self.height))
        self.x = 0
        self.y = 0
        self.sound2 = pygame.mixer.Sound('data/Void-Walk.mp3')
        self.keys = {'r': None,
                     'g': None,
                     'p': None}
        # self.sound2.play()

        run = True
        lvl = ['map1', 'map2', 'map3']

        self.generate_level(self.load_level(lvl[self.num]))
        pygame.mixer.music.play(-1)

        self.tutorial = Tutorial(self)

        self.font = pygame.font.Font(None, 50)

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.menu()
                # key = pygame.key.get_pressed()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.hero.update_pos(3)
                    if event.key == pygame.K_UP:
                        self.hero.update_pos(4)
                    if event.key == pygame.K_RIGHT:
                        self.hero.update_pos(2)
                    if event.key == pygame.K_LEFT:
                        self.hero.update_pos(1)

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)
            self.tiles_group.draw(self.screen)
            self.items.draw(self.screen)
            self.items.update()
            self.hero_gr.draw(self.screen)
            self.hero_gr.update()
            self.boxes_group.draw(self.screen)
            self.boxes_group.update()
            self.tutorial.update()
            self.time += 1

            text = self.font.render(f"Очки: {self.score}", True, (235, 255, 255))
            text_w = text.get_width()
            text_h = text.get_height()
            self.screen.blit(text,
                             (self.width // 2 - text_w // 2,
                              self.height - 200))

            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def spaceship(self):
        """Запускает игру с космичеким кораблем"""
        sp = SpaceshipGame(self)
        sp.run()

    def get_tutorial(self):
        """Возвращает текущий этап обучения"""
        for key, value in self.tutorials.items():
            if not value:
                return key

    def end_game(self):
        """Открывает финальное окно, после его закрытия запускает игру заново"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    running = False

            self.screen.blit(self.fon, (0, 0))

            font = pygame.font.Font(None, 100)
            text = font.render(f"Ваш счет: {self.score}", True, (100, 255, 100))
            text_x = self.width // 2 - text.get_width() // 2
            text_y = self.height // 2 - text.get_height() // 2
            self.screen.blit(text, (text_x, text_y))

            font = pygame.font.Font(None, 50)
            text = font.render("Нажмите любую кнопку", True, (100, 255, 100))
            text_x = self.width // 2 - text.get_width() // 2
            text_y = self.height // 2 - text.get_height() // 2 + 100
            self.screen.blit(text, (text_x, text_y))

            pygame.display.update()
            pygame.display.flip()
        global app
        app = App()
        app.start_wind()

    def menu(self):
        """Открывает меню паузы"""
        Button(self, 'continue', int(self.width * 0.3), int(self.height * 0.2))
        Button(self, 'exit', int(self.width * 0.3), int(self.height * 0.6))
        self.open_menu = True
        while self.open_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.buttons.update(*event.pos)

                self.buttons.draw(self.screen)
                pygame.display.update()
                pygame.display.flip()

        for button in self.buttons:
            button.kill()


class Tutorial:
    """Класс обуеня

    Attributes
    ----------
    window : App
        Приложение, в котором будет идти игра
    font : pygame.font.Font
        Шрифт
    texts : dict
        Текст обучения

    Methods
    -------
    update()
        Вывод текста обучения на экран
    """
    def __init__(self, app):
        self.window = app
        self.font = pygame.font.Font(None, 50)
        self.texts = {'walking': 'Чтобы перемщаться, используте стрелки',
                      'coins': 'За собранные монетки Вы получаете очки',
                      'keys': 'Чтобы открыть сейф, нужно взять соответствующий ключ и подойти к сейфу',
                      'doors': 'Чтобы перейти на следующий уровень, откройте все сейфы и пройдите через дверь'}

    def update(self):
        """Вывод текста обучения на экран"""
        try:
            line = self.texts[self.window.get_tutorial()]
        except KeyError:
            line = ''
        if line:
            text = self.font.render(line, True, (255, 255, 255))
            text_w = text.get_width()
            text_h = text.get_height()
            self.window.screen.blit(text,
                                    (self.window.width // 2 - text_w // 2,
                                     self.window.height - 100 - text_h // 2))


class Button(pygame.sprite.Sprite):
    """Класс кнопки

    Attributes
    ----------
    width : int
        ширина кнопки
    height : int
        высота кнопки
    x : int
        координата левого верхнего угла по оси x
    y : int
        координата левого верхнего угла по оси y
    text : str
        текст кнопки
    do : dict
        словарь с дейстиями

    Methods
    -------
    is_clicked(x, y)
        проверяет нажата ли кнопка, возврщает ее текст при нажатии
    continue_game()
        выход из меню
    update()
        при нажатии на кнопку выполняет соответствубщее ей действие
    """
    def __init__(self, app, name, x, y):
        super(Button, self).__init__(app.all_sprites, app.buttons)
        self.width, self.height = int(app.width * 0.4), int(app.height * 0.2)
        self.image = pygame.transform.scale(App.load_image(f'button_{name}.png', -1), (self.width, self.height))
        self.rect = self.image.get_rect().move(x, y)
        self.x, self.y = x, y
        self.text = name
        self.do = {'exit': app.terminate, 'continue': self.continue_game}

    def is_clicked(self, x, y):
        """Проверяет нажата ли кнопка, возврщает ее текст при нажатии"""
        if x in range(self.x, self.x + self.width) and y in range(self.y, self.y + self.height):
            return self.text

    def continue_game(self):
        """Выход из меню"""
        app.open_menu = False

    def update(self, x, y):
        """При нажатии на кнопку выполняет соответствубщее ей действие"""
        try:
            self.do[self.is_clicked(x, y)]()
        except KeyError:
            pass


class Heart(pygame.sprite.Sprite):
    """Класс для отбражения жизней в игре с космическим кораблем"""
    def __init__(self, app, x, y):
        super().__init__(app.all_sprites, app.hp)
        self.image = pygame.transform.scale(App.load_image('heart.jpeg', -1), (100, 100))
        self.rect = self.image.get_rect().move(x, y)


class SpaceshipGame:
    """Класс игры с космическим кораблем

    Attributes
    ----------
    app : App
        Приложение в котором будет идти игра
    screen
        Окно игры
    score : int
        Количество набранных очков
    all_sprites : pygame.sprite.Group
        Группа всех спрайтов
    hero_gr : pygame.sprite.Group
        Группа играбельных персоанажей
    stars : pygame.sprite.Group
        Группа звезд
    meteors : pygame.sprite.Group
        Группа метеоритов
    lasers : pygame.sprite.Group
        Группа лазеров
    hero : Spaceship
        Космический корабль
    width : int
        Ширина экрана
    height : int
        Высота экрана
    hp : pygame.sprite.Group
        Группа сердечек
    time : int
        Время игры(в кадрах)
    running : bool
        Флаг игры

    Methods
    -------
    run()
        Запуск игры
    end()
        Завешение игры
    """
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.score = app.score
        self.all_sprites = pygame.sprite.Group()
        self.hero_gr = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.hero = Spaceship(self, (10, app.height // 2))
        self.width, self.height = app.width, app.height
        self.hp = pygame.sprite.Group()
        for i in range(3):
            Heart(self, int(self.width * 0.8 + i * 100), 0)
        self.time = 0
        self.running = True

    def run(self):
        """Запуск игры"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.app.terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.app.menu()
                    if event.key == pygame.K_DOWN:
                        self.hero.move[1] = 5
                    if event.key == pygame.K_UP:
                        self.hero.move[1] = -5
                    if event.key == pygame.K_RIGHT:
                        self.hero.move[0] = 5
                    if event.key == pygame.K_LEFT:
                        self.hero.move[0] = -5
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.hero.move[1] = 0
                    if event.key == pygame.K_UP:
                        self.hero.move[1] = 0
                    if event.key == pygame.K_RIGHT:
                        self.hero.move[0] = 0
                    if event.key == pygame.K_LEFT:
                        self.hero.move[0] = 0

            self.screen.blit(self.app.fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.hero_gr.update()
            self.meteors.update()
            self.stars.update()
            self.lasers.update()
            if self.time % 10 == 0:
                self.hero.shoot()
                if self.time % 20 == 0:
                    Meteor(self)
                    if self.time % 100 == 0:
                        Star(self)
                        if self.time == 10000:
                            self.end()
            self.time += 1
            pygame.display.update()
            pygame.display.flip()
            self.app.clock.tick(app.fps)

    def end(self):
        """Завешение игры"""
        self.app.score = self.score
        self.app.time += self.time
        self.running = False
        self.app.end_game()


class AnimatedSprite(pygame.sprite.Sprite):
    """Класс анимированного спрайта

    Attributes
    ----------
    speed : int
        Скорость изменения анмимации
    frames : list
        Список кадров анимации

    Methods
    -------
    cut_sheet(sheet, columns, rows)
        Разрезает сет на отдельные кадры
    update()
        Меняет анимацию
    """
    def __init__(self, sheet, columns, rows, x, y, speed, groups=None):
        if groups is None:
            groups = [app.all_sprites]
        super().__init__(*groups)
        self.speed = speed
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        """Разрезает сет на отдельные кадры

        Parameters
        ----------
        sheet : image
            название файла с сетом
        columns : int
            количество столбцов
        rows : int
            количество строк
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """Меняет анимацию"""
        if app.time % self.speed == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class SpaceshipTile(pygame.sprite.Sprite):
    """Класс комического корабля(когда не летает)

    Attributes
    ----------
    app : App
        Приложение, в котором будет использоваться

    Methods
    -------
    get()
        Запускает игру с космическим кораблем
    """
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.all_sprites, app.items)
        self.app = app
        self.image = pygame.transform.scale(app.load_image("spaceship.png", -1), (app.tile_width, app.tile_height))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(pos_x * app.tile_width, pos_y * app.tile_height)

    def get(self):
        self.app.spaceship()


class Coin(AnimatedSprite):
    """Класс анимированной монетки

    Methods
    -------
    get()
        Увеличивает счет и убирает монетку
    """
    def __init__(self, app, pos_x, pos_y):
        super().__init__(pygame.transform.scale(app.load_image('coin.png'), (app.tile_width * 8, app.tile_height)), 8,
                         1, app.tile_width * pos_x, app.tile_height * (pos_y + 1), 2, (app.all_sprites, app.items))

    def get(self):
        """Увеличивает счет и убирает монетку"""
        app.score += 100
        # pygame.mixer.Sound('data/coin.mp3').play()
        """вариант другой мелодии"""
        pygame.mixer.Sound('data/coin(var).mp3').play()
        self.kill()
        app.tutorials['coins'] = True


class Hero(AnimatedSprite):
    """Класс героя

    Attributes
    ----------
    widow : App
        Приложение, в котором используется
    direction : int
        Направление двизения
    count : int
        Счетчик времени движения
    x : int
        Координата левого верхнего угла по оси x
    y : int
        Координата левого верхнего угла по оси y

    Methods
    -------
    update()
        Осуществляет движение героя
    move()
        Перемещение героя по полю
    update_pos(direction)
        Изменение направления движения героя
    get_item()
        Поднятие предмета
    stop()
        Отмена движения
    """
    def __init__(self, app, pos_x, pos_y):
        super().__init__(
            pygame.transform.scale(app.load_image('hero0.png', -1), (app.tile_width * 4, app.tile_height * 4)),
            4, 4, app.tile_width * pos_x, app.tile_height * (pos_y + 1), 5, (app.all_sprites, app.hero_gr))
        self.widow = app
        self.direction = 0
        self.count = 0
        self.x = self.rect.x
        self.y = self.rect.y

    def update(self):
        """Осуществляет движение героя"""
        if self.direction:
            if app.time % self.speed == 0:
                self.cur_frame = (self.direction - 1) * 4 + self.count
                self.image = self.frames[self.cur_frame]
                self.move()
                self.count += 1
                if self.count == 4:
                    self.move()
                    self.get_item()
                    self.direction = 0
                    self.count = 0
                    self.x = self.rect.x
                    self.y = self.rect.y
            self.widow.tutorials['walking'] = True
        else:
            self.image = self.frames[9]

    def move(self):
        """Перемещение героя по полю"""
        if self.direction == 1:
            self.rect.x -= 10
        elif self.direction == 2:
            self.rect.x += 10
        elif self.direction == 3:
            self.rect.y += 10
        else:
            self.rect.y -= 10

    def update_pos(self, direction):
        """Изменение направления движения героя

        Parameters
        ----------
        direction : int
            Новое направление движения
        """
        if not self.direction:
            self.direction = direction

    def get_item(self):
        """Поднятие предмета"""
        item = pygame.sprite.spritecollideany(self, app.items)
        if item:
            item.get()

    def stop(self):
        """Отмена движения"""
        direction = {1: 2, 2: 1, 3: 4, 4: 3}
        self.direction = direction[self.direction]
        for _ in range(self.count):
            self.move()
        self.count = 0
        self.direction = 0


class Spaceship(pygame.sprite.Sprite):
    """Класс играбельного космического корабля

    Attributes
    ----------
    app : App
        Приложение, в котором используется
    hp : int
        Очки здоровья
    move : list
        Скорость движения по осям

    Methods
    -------
    update()
        Двигает космический корабль
    shoot()
        Выстрел
    """
    def __init__(self, app, pos):
        self.app = app
        super().__init__(app.hero_gr, app.all_sprites)
        self.image = App.load_image("spaceship.png", -1)
        self.rect = self.image.get_rect()
        self.hp = 3
        # вычисляем маску для эффективного сравнения
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos)
        self.move = [0, 0]

    def update(self):
        """Двигает космический корабль"""
        if self.hp == 0:
            self.app.end()
        x, y = self.move
        self.rect.x += x
        self.rect.y += y
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > self.app.width - 100:
            self.rect.x = self.app.width - 100
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > self.app.height - 100:
            self.rect.y = self.app.height - 100

    def shoot(self):
        """Выстрел"""
        Laser(self.app, self.rect.x + 100, self.rect.y + 45)


class Laser(pygame.sprite.Sprite):
    """Класс лазера

    Attributes
    ----------
    app : SpaceshipGame
        Обьект, в котором используется
    speed : int
        Скорость полета

    Methods
    -------
    update()
        Двигает лазер и уничтожает метеор при столкновении
    """
    def __init__(self, window, x, y):
        self.app = window
        super(Laser, self).__init__(window.lasers, window.all_sprites)
        self.image = App.load_image('laserRed01.png', -1)
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(x, y)
        self.speed = 20

    def update(self):
        self.rect.x += self.speed
        if meteor := pygame.sprite.spritecollideany(self, self.app.meteors):
            meteor.kill()
            self.kill()
        if self.rect.x > self.app.width:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    """Класс метеорита

    Attributes
    ----------
    app : SpaceshipGame
        Обьект, в котором используется
    speed : int
        Скорость полета

    Methods
    -------
    update()
        Двигает метеорит и уничтожает его при столкновении с кораблем
    """
    def __init__(self, window):
        self.app = window
        super(Meteor, self).__init__(window.meteors, window.all_sprites)
        self.image = App.load_image(f'meteor{str(random.randint(0, 6))}.webp')
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(window.app.width + 80, random.randint(0, window.app.height))
        self.speed = random.randint(5, 20)

    def update(self):
        """Двигает метеорит и уничтожает его при столкновении с кораблем"""
        self.rect.x -= self.speed
        if pygame.sprite.collide_mask(self, self.app.hero):
            self.app.hero.hp -= 1
            list(self.app.hp)[0].kill()
            self.kill()
        if self.rect.x < -80:
            self.kill()


class Star(pygame.sprite.Sprite):
    """Класс метеорита

    Attributes
    ----------
    app : SpaceshipGame
        Обьект, в котором используется
    speed : int
        Скорость полета

    Methods
    -------
    update()
        Двигает звезду и уничтожает ее, увеличивая счет, при столкновении с кораблем
    """
    def __init__(self, window):
        self.app = window
        super(Star, self).__init__(window.stars, window.all_sprites)
        self.image = App.load_image('star.webp')
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(window.app.width + 80, random.randint(0, window.app.height))
        self.speed = random.randint(2, 5)

    def update(self):
        """Двигает звезду и уничтожает ее, увеличивая счет, при столкновении с кораблем"""
        self.rect.x -= self.speed
        if pygame.sprite.collide_mask(self, self.app.hero):
            self.app.score += 100
            self.kill()
        if self.rect.x < -80:
            self.kill()


if __name__ == '__main__':
    app = App()
    app.start_wind()
