import os
import sys
import pygame
import random


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, app):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - app.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - app.height // 2)


class Tile(pygame.sprite.Sprite):
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
    def __init__(self, app, image, pos_x, pos_y):
        super().__init__(app.load_image(image), app, pos_x, pos_y)
        self.im = image
        self.x = pos_x
        self.y = pos_y
        # self.add(app.items)

    def update(self):
        if pygame.sprite.collide_mask(self, app.hero):
            app.hero.stop()
            if app.keys[self.im[0]]:
                pygame.mixer.Sound('data/safe.mp3').play()
                app.keys[self.im[0]] = False
                app.tutorials['keys'] = True


class Keys(pygame.sprite.Sprite):
    def __init__(self, app, im, pos_x, pos_y):
        super().__init__(app.tiles_group, app.all_sprites, app.items)
        self.add(app.items)
        self.im = im
        self.image = pygame.transform.scale(app.load_image(im), (app.tile_width, app.tile_height))
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)

    def get(self):
        app.keys[self.im[0]] = True
        print(app.keys)
        pygame.mixer.Sound('data/open.mp3').play()
        self.kill()


class Border(Wall):
    def __init__(self, app, image, pos_x, pos_y):
        super().__init__(app.load_image(image), app, pos_x, pos_y)


class Door(Wall):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.load_image('door.png'), app, pos_x, pos_y)

    def update(self):
        if pygame.sprite.collide_mask(self, app.hero):
            if all([val is False for val in app.keys.values()]):
                app.tutorials['doors'] = True
                app.loading_screen()
            else:
                app.hero.stop()
            # app.loading_screen()


class App(pygame.sprite.Sprite):
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
        self.horiz = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.tutorial_group = pygame.sprite.Group()
        self.camera = Camera(self)
        self.hero = None
        self.tutorial = None
        self.score = 0
        self.time = 0
        self.num = -1
        self.done = False
        self.bar_length = 0
        self.fon = pygame.transform.scale(self.load_image('fon.jpeg'), (self.width, self.height))
        self.tutorials = {'walking': False, 'coins': False, 'keys': False, 'doors': False}

    def terminate(self):
        pygame.quit()
        sys.exit()

    @staticmethod
    def load_image(name, colorkey=None):
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
        pygame.time.delay(1000)
        font = pygame.font.Font(None, int(0.04 * self.width))
        string_rendered = font.render(text, True, pygame.Color(col))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = int(0.22 * self.width)
        intro_rect.y = int(0.8 * self.height)
        self.screen.blit(string_rendered, intro_rect)

    def start_wind(self):
        intro_text = ['<НАЗВАНИЕ ИГРЫ>']
        self.sound = pygame.mixer.Sound('data/start.mp3')
        self.sound.play()
        self.fon = pygame.transform.scale(self.load_image('start_fon.jpg'), (self.width, self.height))
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

    def draw_bar(self, len):
        pygame.time.delay(70)
        self.screen.blit(self.fon, (0, 0))
        pygame.draw.rect(self.screen, (169, 172, 199), ((424, 577), (len, 45)))

    def loading_screen(self):
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
            self.run_game()

    def load_level(self, filename):

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
        self.fon = pygame.transform.scale(self.load_image('fon.jpeg'), (self.width, self.height))
        self.x = 0
        self.y = 0
        self.sound2 = pygame.mixer.Sound('data/Void-Walk.mp3')
        # self.sound2.play()

        run = True
        lvl = ['map1', 'map2', 'map3']

        self.generate_level(self.load_level(lvl[self.num]))
        pygame.mixer.music.play(-1)

        self.tutorial = Tutorial(self)

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.terminate()
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
            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def spaceship(self):
        sp = SpaceshipGame(self)
        sp.run()

    def get_tutorial(self):
        for key, value in self.tutorials.items():
            if not value:
                return key


class Tutorial:
    def __init__(self, app):
        self.window = app
        self.font = pygame.font.Font(None, 50)
        self.texts = {'walking': 'Чтобы перемщаться, используте стрелки',
                      'coins': 'За собранные монетки Вы получаете очки',
                      'keys': 'Чтобы открыть сейф, нужно взять соответствующий ключ и подойти к сейфу',
                      'doors': 'Чтобы перейти на следующий уровень, откройте все сейфы и пройдите через дверь'}

    def update(self):
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


class SpaceshipGame:
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
        self.time = 0
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.app.terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.app.terminate()
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
            self.time += 1
            pygame.display.update()
            pygame.display.flip()
            self.app.clock.tick(app.fps)

    def end(self):
        self.app.score = self.score
        self.app.time += self.time
        self.running = False


class AnimatedSprite(pygame.sprite.Sprite):
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
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if app.time % self.speed == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class SpaceshipTile(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.all_sprites, app.items)
        self.app = app
        self.image = pygame.transform.scale(app.load_image("spaceship.png", -1), (app.tile_width, app.tile_height))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect().move(pos_x * app.tile_width, pos_y * app.tile_height)

    def get(self):
        self.app.spaceship()


class Coin(AnimatedSprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(pygame.transform.scale(app.load_image('coin.png'), (app.tile_width * 8, app.tile_height)), 8,
                         1, app.tile_width * pos_x, app.tile_height * (pos_y + 1), 2, (app.all_sprites, app.items))

    def get(self):
        app.score += 100
        # pygame.mixer.Sound('data/coin.mp3').play()
        """вариант другой мелодии"""
        pygame.mixer.Sound('data/coin(var).mp3').play()
        self.kill()
        app.tutorials['coins'] = True


class Hero(AnimatedSprite):
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
        if self.direction == 1:
            self.rect.x -= 10
        elif self.direction == 2:
            self.rect.x += 10
        elif self.direction == 3:
            self.rect.y += 10
        else:
            self.rect.y -= 10

    def update_pos(self, direction):
        if not self.direction:
            self.direction = direction

    def get_item(self):
        item = pygame.sprite.spritecollideany(self, app.items)
        if item:
            item.get()

    def stop(self):
        direction = {1: 2, 2: 1, 3: 4, 4: 3}
        self.direction = direction[self.direction]
        for _ in range(self.count):
            self.move()
        self.count = 0
        self.direction = 0


class Spaceship(pygame.sprite.Sprite):
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
        Laser(self.app, self.rect.x + 100, self.rect.y + 45)


class Laser(pygame.sprite.Sprite):
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
        self.rect.x -= self.speed
        if pygame.sprite.collide_mask(self, self.app.hero):
            self.app.hero.hp -= 1
            self.kill()
        if self.rect.x < -80:
            self.kill()


class Star(pygame.sprite.Sprite):
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
        self.rect.x -= self.speed
        if pygame.sprite.collide_mask(self, self.app.hero):
            self.app.score += 100
            self.kill()
        if self.rect.x < -80:
            self.kill()


if __name__ == '__main__':
    app = App()
    app.start_wind()
