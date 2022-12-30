import os
import sys
import pygame


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


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        # super().__init__(app.all_sprites)
        super().__init__(app.player_group, app.all_sprites)
        self.image = app.load_image("mar.png")
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(app.tile_width * pos[0] + 20, app.tile_height * pos[1] + 50)

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.get_item()

    def get_item(self):
        item = pygame.sprite.spritecollideany(self, app.items)
        if item:
            item.get()


class Tile(pygame.sprite.Sprite):
    def __init__(self, app, tile_type, pos_x, pos_y):
        super().__init__(app.tiles_group, app.all_sprites)
        tile_images = {
            'wall': app.load_image('box.png'),
            'empty': app.load_image('Floor.png'),
            'vert_bord': app.load_image("bord.png")
        }
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)


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
        self.tile_width = self.tile_height = 50
        self.player_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.hero = Hero(self, (100, 100))
        self.tiles_group = pygame.sprite.Group()
        self.camera = Camera(self)
        self.hero = None
        self.score = 0
        self.time = 0

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
                print(colorkey)
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def msg(self, col):
        pygame.time.delay(1000)
        font = pygame.font.Font(None, int(0.04 * self.width))
        string_rendered = font.render('НАЖМИТЕ ПРОБЛЕЛ, ЧТОБЫ ПРОДОЛЖИТЬ', True, pygame.Color(col))
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
                        self.run_game()
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()

            count += 1

            self.msg(colors[count % 2])
            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)

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
                    self.tile = Tile(self, 'empty', x, y)
                elif level[y][x] == '#':
                    self.tile_box = Tile(self, 'wall', x, y)
                elif level[y][x] == '|':
                    self.tile_box = Tile(self, 'vert_bord', x, y)
                elif level[y][x] == '@':
                    self.tile_hero = Tile(self, 'empty', x, y)
                    self.hero = Hero(self, (x, y))
                elif level[y][x] == 'C':
                    Tile(self, 'empty', x, y)
                    Coin(self, x, y)
        # вернем игрока, а также размер поля в клетках

    def run_game(self):
        fon = pygame.transform.scale(self.load_image('fon.jpeg'), (self.width, self.height))
        run = True
        lvl = ['map1', 'map2', 'map3']
        self.generate_level(self.load_level(lvl[0]))
        pygame.mixer.music.play(-1)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.terminate()
                key = pygame.key.get_pressed()
                if key[pygame.K_DOWN]:
                    self.hero.update(self.hero.rect.x, self.hero.rect.y + 50)
                if key[pygame.K_UP]:
                    self.hero.update(self.hero.rect.x, self.hero.rect.y - 50)
                if key[pygame.K_RIGHT]:
                    self.hero.update(self.hero.rect.x + 50, self.hero.rect.y)
                if key[pygame.K_LEFT]:
                    self.hero.update(self.hero.rect.x - 50, self.hero.rect.y)

            self.screen.blit(fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)
            self.tiles_group.draw(self.screen)
            self.player_group.draw(self.screen)
            self.items.draw(self.screen)
            self.items.update()
            self.time += 1
            pygame.display.flip()
            self.clock.tick(self.fps)


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


class Coin(AnimatedSprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(pygame.transform.scale(app.load_image('coin.png'), (app.tile_width * 8, app.tile_height)), 8,
                         1, app.tile_width * pos_x, app.tile_height * (pos_y + 1), 2, (app.all_sprites, app.items))

    def get(self):
        app.score += 100
        pygame.mixer.Sound('data/coin.mp3').play()
        self.kill()


if __name__ == '__main__':
    app = App()
    app.start_wind()
