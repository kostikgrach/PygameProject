import os
import sys
import pygame


class App:
    def __init__(self):
        pygame.init()
        self.width, self.height = 2000, 1000
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.key.set_repeat(200, 70)
        self.fps = 50
        self.all_sprites = pygame.sprite.Group()

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
    def msg(self, col):
        pygame.time.delay(1000)
        font = pygame.font.Font(None, 80)
        string_rendered = font.render('НАЖМИТЕ ПРОБЛЕЛ, ЧТОБЫ ПРОДОЛЖИТЬ', True, pygame.Color(col))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 440
        intro_rect.y = 800
        self.screen.blit(string_rendered, intro_rect)


    def run_game(self):
        intro_text = ['<НАЗВАНИЕ ИГРЫ>']
        self.sound = pygame.mixer.Sound('data/start.mp3')
        self.sound.play()
        self.fon = pygame.transform.scale(self.load_image('start_fon.jpg'), (self.width, self.height))
        self.screen.blit(self.fon, (0, 0))
        font = pygame.font.Font(None, 120)
        text_coord = 400
        for line in intro_text:
            string_rendered = font.render(line, True, pygame.Color(255, 240, 240))
            intro_rect = string_rendered.get_rect()
            text_coord += 30
            intro_rect.top = text_coord
            intro_rect.x = 600
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
                        pass
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()

            count += 1

            self.msg(colors[count % 2])
            pygame.display.update()
            pygame.display.flip()
            self.clock.tick(self.fps)



if __name__ == '__main__':
    app = App()
    app.run_game()
