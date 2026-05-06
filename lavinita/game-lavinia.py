import arcade
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Thrift Store Rack"

STARTING_MONEY = 100
RACK_SIZE = 12
SPACING = 120


class ThriftItem:
    def __init__(self):
        textures = [
            "assets/shirt.png",
            "assets/dress.png",
            "assets/pants.png"
        ]

        texture_path = random.choice(textures)

        self.sprite = arcade.Sprite(texture_path, scale=0.4)

        self.price = random.randint(5, 30)
        self.value = random.randint(0, 60)

        # Subtle rarity tint (less harsh)
        if self.value > 45:
            self.sprite.color = (255, 220, 120)
        elif self.value > 25:
            self.sprite.color = (220, 220, 220)
        else:
            self.sprite.color = (255, 255, 255)


class ThriftGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color((245, 240, 230))  # warm store color

        self.rack = []
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

    def setup(self):
        self.rack.clear()
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

        for _ in range(RACK_SIZE):
            item = ThriftItem()
            self.rack.append(item)
            self.sprite_list.append(item.sprite)

        self.update_positions()

    def update_positions(self):
        center_x = SCREEN_WIDTH // 2

        for i, item in enumerate(self.rack):
            offset = (i * SPACING) - self.current_offset
            x = center_x + offset

            # Distance from center
            dist = abs(i - self.current_index)

            # Depth effect
            scale = max(0.25, 0.5 - dist * 0.05)
            alpha = max(120, 255 - dist * 40)

            item.sprite.scale = scale
            item.sprite.alpha = alpha

            # Slight vertical curve (like rack arc)
            y = SCREEN_HEIGHT // 2 + 50 - dist * 10

            item.sprite.center_x = x
            item.sprite.center_y = y

    def on_draw(self):
        self.clear()

        # --- BACKGROUND WALL ---
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (245, 240, 230)
        )

        # --- FLOOR ---
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, 100,
            SCREEN_WIDTH, 200,
            (220, 210, 190)
        )

        # --- RACK BAR ---
        rack_y = SCREEN_HEIGHT // 2 + 120
        arcade.draw_line(100, rack_y, 800, rack_y, (120, 80, 40), 6)

        # --- HANGERS (little lines above clothes) ---
        for item in self.rack:
            arcade.draw_line(
                item.sprite.center_x,
                rack_y,
                item.sprite.center_x,
                item.sprite.center_y + 30,
                arcade.color.DARK_GRAY,
                2
            )

        # --- CLOTHES ---
        self.sprite_list.draw()

        # --- CENTER ITEM INFO PANEL ---
        if self.rack:
            item = self.rack[self.current_index]

            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, 140,
                260, 90,
                (255, 255, 255)
            )

            arcade.draw_text(
                f"Price: ${item.price}",
                SCREEN_WIDTH // 2 - 60,
                150,
                arcade.color.BLACK,
                16
            )

        # --- UI PANEL ---
        arcade.draw_rectangle_filled(150, 50, 260, 80, (255, 255, 255))

        arcade.draw_text(f"Money: ${self.money}", 40, 60, arcade.color.BLACK, 16)
        arcade.draw_text(f"Profit: {self.score}", 40, 30, arcade.color.BLACK, 16)

        arcade.draw_text(
            "← → browse   SPACE buy",
            300, 30,
            arcade.color.DARK_GRAY,
            14
        )

        arcade.draw_text(self.message, 300, 60, arcade.color.RED, 16)

    def on_update(self, delta_time):
        # Smooth animation
        speed = 8
        self.current_offset += (self.target_offset - self.current_offset) / speed
        self.update_positions()

    def on_key_press(self, key, modifiers):
        if not self.rack:
            return

        if key == arcade.key.RIGHT:
            self.current_index = (self.current_index + 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        elif key == arcade.key.LEFT:
            self.current_index = (self.current_index - 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        elif key == arcade.key.SPACE:
            item = self.rack[self.current_index]

            if item.price > self.money:
                self.message = "Not enough money!"
                return

            self.money -= item.price
            profit = item.value - item.price
            self.score += profit

            self.message = f"Profit: {profit}"

            # Remove item
            self.sprite_list.remove(item.sprite)
            self.rack.pop(self.current_index)

            # Add new item
            new_item = ThriftItem()
            self.rack.append(new_item)
            self.sprite_list.append(new_item.sprite)

            if self.current_index >= len(self.rack):
                self.current_index = 0

            self.target_offset = self.current_index * SPACING


def main():
    game = ThriftGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
