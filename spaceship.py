"""Заготовка игры с космическим кораблем"""


import random
import arcade


width, height, score = 1000, 1000, 0


class GameView(arcade.View):
    def __init__(self):
        super(GameView, self).__init__()
        self.player = None
        self.score = score
        self.background = None
        self.meteors = arcade.SpriteList()
        self.stars = arcade.SpriteList()
        self.shoots = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.setup()

    def setup(self):
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.background = arcade.Sprite("data/fon.jpeg", 1.5)
        self.player = arcade.Sprite(":resources:images/space_shooter/playerShip1_orange.png", scale=0.5,
                                    flipped_diagonally=True, flipped_horizontally=True, hit_box_algorithm="Detailed")
        global height
        self.player.center_y = height / 2
        self.player.left = 10
        self.score = 0
        self.all_sprites.append(self.player)

        arcade.schedule(self.add_meteor, 0.25)
        arcade.schedule(self.add_star, 1)

    def add_meteor(self, delta_time):
        meteor = Meteor()
        self.meteors.append(meteor)
        self.all_sprites.append(meteor)

    def add_star(self, delta_time):
        star = Star()
        self.stars.append(star)
        self.all_sprites.append(star)

    def on_draw(self):
        arcade.start_render()
        self.background.draw()
        self.all_sprites.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.player.change_y = 5
        if symbol == arcade.key.DOWN:
            self.player.change_y = -5
        if symbol == arcade.key.RIGHT:
            self.player.change_x = 5
        if symbol == arcade.key.LEFT:
            self.player.change_x = -5
        if symbol == arcade.key.SPACE:
            shoot = Shoot(self.player.right, self.player.top - 0.5 * self.player.height)
            self.shoots.append(shoot)
            self.all_sprites.append(shoot)

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol in {arcade.key.UP, arcade.key.DOWN}:
            self.player.change_y = 0
        if _symbol in {arcade.key.LEFT, arcade.key.RIGHT}:
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        self.all_sprites.update()

        global width, height
        if self.player.top > height:
            self.player.top = height
        if self.player.right > width:
            self.player.right = width
        if self.player.bottom < 0:
            self.player.bottom = 0
        if self.player.left < 0:
            self.player.left = 0

        for star in self.player.collides_with_list(self.stars):
            self.score += 100
            star.destroy()

        for shoot in self.shoots:
            if res := shoot.collides_with_list(self.meteors):
                shoot.destroy()
                for meteor in res:
                    meteor.destroy()

        if self.player.collides_with_list(self.meteors):
            global score
            score += self.score
            arcade.close_window()


class MovingSprite(arcade.Sprite):
    def update(self):
        super(MovingSprite, self).update()
        global width
        if self.right < 0 or self.right > width + 200:
            self.remove_from_sprite_lists()

    def destroy(self):
        self.remove_from_sprite_lists()


class Meteor(MovingSprite):
    meteor_sprites_images = ["meteorGrey_big1.png",
                             "meteorGrey_big2.png",
                             "meteorGrey_big3.png",
                             "meteorGrey_big4.png",
                             "meteorGrey_med1.png",
                             "meteorGrey_med2.png",
                             "meteorGrey_small1.png",
                             "meteorGrey_small2.png",
                             "meteorGrey_tiny1.png",
                             "meteorGrey_tiny2.png"]

    def __init__(self):
        super(Meteor, self).__init__(f':resources:/images/space_shooter/{random.choice(self.meteor_sprites_images)}',
                                     0.5, hit_box_algorithm='Detailed')
        global width, height
        self.left = random.randint(width, width + 80)
        self.top = random.randint(0, height + 80)
        self.velocity = (random.randint(-20, -5), 0)


class Star(MovingSprite):
    def __init__(self):
        super().__init__(':resources:/images/items/star.png', 0.5)
        global width, height
        self.left = random.randint(width, width + 80)
        self.top = random.randint(0, height + 80)
        self.velocity = (random.randint(-5, -2), 0)


class Shoot(MovingSprite):
    def __init__(self, x, y):
        super(Shoot, self).__init__(':resources:/images/space_shooter/laserBlue01.png')
        self.left = x
        self.top = y
        self.velocity = (30, 0)


def spaceship(w, h):
    global width, height
    width, height = w, h,
    window = arcade.Window(width, height)
    view = GameView()
    window.show_view(view)
    arcade.run()


def get_score():
    return score


if __name__ == '__main__':
    pass
