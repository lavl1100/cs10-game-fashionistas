import arcade
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Thrift & Fashion Game (Fixed)"

STARTING_MONEY = 100
RACK_SIZE = 12
SPACING = 120

FAST_FASHION = ["polyester", "nylon", "rayon", "acrylic"]
ECO = ["cotton", "linen", "wool", "hemp"]


class Item:
    def __init__(self):
        textures = ["assets/shirt.png", "assets/dress.png", "assets/pants.png"]

        self.sprite = arcade.Sprite(random.choice(textures), scale=0.4)

        if random.random() < 0.5:
            self.fabric = random.choice(FAST_FASHION)
            self.eco = False
        else:
            self.fabric = random.choice(ECO)
            self.eco = True

        if self.eco:
            self.price = random.randint(15, 35)
            self.value = random.randint(30, 70)
            self.sprite.color = (180, 255, 200)
        else:
            self.price = random.randint(5, 20)
            self.value = random.randint(10, 40)
            self.sprite.color = (255, 220, 220)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((245, 240, 230))

        self.rack = []
        self.sprites = arcade.SpriteList()
        self.inventory = []

        self.index = 0
        self.offset = 0
        self.target = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.msg = ""

        self.end = False

    def setup(self):
        self.rack.clear()
        self.sprites = arcade.SpriteList()
        self.inventory.clear()

        self.index = 0
        self.offset = 0
        self.target = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.msg = ""
        self.end = False

        for _ in range(RACK_SIZE):
            item = Item()
            self.rack.append(item)
            self.sprites.append(item.sprite)

        self.update()

    def update(self):
        center = SCREEN_WIDTH // 2

        for i, item in enumerate(self.rack):
            x = center + (i * SPACING) - self.offset
            dist = abs(i - self.index)

            item.sprite.center_x = x
            item.sprite.center_y = SCREEN_HEIGHT // 2 + 50 - dist * 10

            item.sprite.scale = max(0.25, 0.5 - dist * 0.05)
            item.sprite.alpha = max(120, 255 - dist * 40)

    def on_draw(self):
        self.clear()

        if self.end:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (30, 30, 30))

            arcade.draw_text("SUMMARY", 350, 520, arcade.color.WHITE, 30)
            arcade.draw_text(f"Score: {self.score}", 350, 450, arcade.color.GREEN, 20)

            eco = sum(1 for i in self.inventory if i.eco)
            fast = len(self.inventory) - eco

            arcade.draw_text(f"Eco items: {eco}", 350, 400, arcade.color.GREEN, 16)
            arcade.draw_text(f"Fast fashion: {fast}", 350, 370, arcade.color.RED, 16)

            arcade.draw_text("CLICK TO RESTART", 320, 250, arcade.color.WHITE, 20)
            return

        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (245, 240, 230))
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, 200, (220, 210, 190))

        arcade.draw_line(100, SCREEN_HEIGHT // 2 + 120, 800, SCREEN_HEIGHT // 2 + 120, (120, 80, 40), 6)

        self.sprites.draw()

        if self.rack:
            item = self.rack[self.index]

            arcade.draw_text(item.fabric, 400, 150, arcade.color.BLACK, 16)
            arcade.draw_text(
                "ECO 🌱" if item.eco else "FAST ❌",
                400, 120,
                arcade.color.GREEN if item.eco else arcade.color.RED,
                14
            )

        arcade.draw_lbwh_rectangle_filled(20, 20, 340, 90, (255, 255, 255))
        arcade.draw_text(f"Money: {self.money}", 40, 70, arcade.color.BLACK, 16)
        arcade.draw_text(f"Score: {self.score}", 40, 45, arcade.color.BLACK, 16)

        arcade.draw_lbwh_rectangle_filled(720, 30, 160, 50, (200, 200, 200))
        arcade.draw_text("END", 780, 50, arcade.color.BLACK, 14)

        arcade.draw_text(self.msg, 400, 60, arcade.color.RED, 16)

    def on_update(self, dt):
        self.offset += (self.target - self.offset) * 0.1
        self.update()

    def on_key_press(self, key, modifiers):
        if self.end:
            self.setup()
            return

        if not self.rack:
            return

        if key == arcade.key.RIGHT:
            self.index = (self.index + 1) % len(self.rack)
            self.target = self.index * SPACING

        elif key == arcade.key.LEFT:
            self.index = (self.index - 1) % len(self.rack)
            self.target = self.index * SPACING

    def on_mouse_press(self, x, y, button, modifiers):
        if self.end:
            self.setup()
            return

        # END BUTTON FIRST (important fix)
        if 720 <= x <= 880 and 30 <= y <= 80:
            self.end = True
            return

        if not self.rack:
            return

        # SAFE INDEX CHECK (fixes “can’t buy” bug)
        if self.index >= len(self.rack):
            self.index = 0

        item = self.rack[self.index]

        if item.price > self.money:
            self.msg = "Not enough money!"
            return

        self.money -= item.price

        if item.eco:
            gain = (item.value - item.price) * 2
        else:
            gain = -(item.price + 10)

        self.score += gain
        self.inventory.append(item)

        self.sprites.remove(item.sprite)
        self.rack.pop(self.index)

        if self.rack:
            self.index %= len(self.rack)

        new_item = Item()
        self.rack.append(new_item)
        self.sprites.append(new_item.sprite)

        self.target = self.index * SPACING


def main():
    game = Game()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
