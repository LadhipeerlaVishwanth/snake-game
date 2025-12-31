from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
import random

# ================= CONFIG =================
GRID_MIN = 20
GRID_MAX = 28

START_SPEED = 0.30
SPEED_STEP = 0.02
MIN_SPEED = 0.08
POINTS_PER_SPEED = 4
# =========================================


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (1, 1)
        self.pos_hint = {"x": 0, "y": 0}

        self.ready = False
        self.game_over = False
        self.GRID = None

        self.snake = []
        self.food = None
        self.direction = "RIGHT"

        self.speed = START_SPEED
        self.move_timer = 0.0
        self.score = 0

        # ---- Animation states ----
        self.food_scale = 1.0
        self.food_pulse_dir = 1
        self.head_pop = 1.0
        self.death_flash = 0

        self.score_label = Label(
            text="Score: 0",
            size_hint=(None, None),
            size=(120, 30),
            pos_hint={"x": 0.01, "y": 0.95}
        )
        self.add_widget(self.score_label)

        self.game_over_label = Label(
            text="",
            font_size=32,
            center=self.center,
            opacity=0
        )
        self.add_widget(self.game_over_label)

        Clock.schedule_interval(self.update, 1 / 60)

    # ---------- INIT ----------
    def on_size(self, *args):
        if self.ready or self.width == 0 or self.height == 0:
            return

        self.GRID = min(max(int(self.width / 30), GRID_MIN), GRID_MAX)
        self.reset_game()
        self.ready = True

    # ---------- RESET ----------
    def reset_game(self):
        cx = (self.width // 2) // self.GRID * self.GRID
        cy = (self.height // 2) // self.GRID * self.GRID

        self.snake = [
            (cx, cy),
            (cx - self.GRID, cy),
            (cx - 2 * self.GRID, cy)
        ]

        self.food = self.spawn_food()
        self.direction = "RIGHT"

        self.speed = START_SPEED
        self.move_timer = 0.0
        self.score = 0
        self.game_over = False

        self.food_scale = 1.0
        self.food_pulse_dir = 1
        self.head_pop = 1.0
        self.death_flash = 0

        self.score_label.text = "Score: 0"
        self.game_over_label.opacity = 0

    # ---------- FOOD ----------
    def spawn_food(self):
        cols = int(self.width // self.GRID)
        rows = int(self.height // self.GRID)
        return (
            random.randrange(cols) * self.GRID,
            random.randrange(rows) * self.GRID
        )

    # ---------- UPDATE ----------
    def update(self, dt):
        if not self.ready or self.game_over:
            return

        # Snake movement timing
        self.move_timer += dt
        if self.move_timer >= self.speed:
            self.move_timer = 0.0
            self.move_snake()

        # Food pulse animation
        self.food_scale += 0.01 * self.food_pulse_dir
        if self.food_scale > 1.15:
            self.food_pulse_dir = -1
        elif self.food_scale < 0.85:
            self.food_pulse_dir = 1

        # Head pop animation decay
        self.head_pop += (1.0 - self.head_pop) * 0.25

        self.draw()

    # ---------- MOVE ----------
    def move_snake(self):
        hx, hy = self.snake[0]

        if self.direction == "UP":
            hy += self.GRID
        elif self.direction == "DOWN":
            hy -= self.GRID
        elif self.direction == "LEFT":
            hx -= self.GRID
        elif self.direction == "RIGHT":
            hx += self.GRID

        new_head = (hx, hy)

        if (
            hx < 0 or hx + self.GRID > self.width or
            hy < 0 or hy + self.GRID > self.height or
            new_head in self.snake
        ):
            self.game_over = True
            self.game_over_label.text = f"GAME OVER\nScore: {self.score}"
            self.game_over_label.opacity = 1
            self.death_flash = 10
            App.get_running_app().show_restart()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.score_label.text = f"Score: {self.score}"
            self.head_pop = 1.25

            if self.score % POINTS_PER_SPEED == 0 and self.speed > MIN_SPEED:
                self.speed -= SPEED_STEP

            self.food = self.spawn_food()
        else:
            self.snake.pop()

    # ---------- DRAW HEAD ----------
    def draw_snake_head(self, x, y):
        size = self.GRID * self.head_pop
        off = (self.GRID - size) / 2

        Color(0.2, 1, 0.2)
        Rectangle(pos=(x + off, y + off), size=(size, size))

        eye = self.GRID * 0.15
        eoff = self.GRID * 0.2

        if self.direction == "RIGHT":
            eyes = [(x + self.GRID - eoff, y + self.GRID * 0.65),
                    (x + self.GRID - eoff, y + self.GRID * 0.35)]
        elif self.direction == "LEFT":
            eyes = [(x + eoff - eye, y + self.GRID * 0.65),
                    (x + eoff - eye, y + self.GRID * 0.35)]
        elif self.direction == "UP":
            eyes = [(x + self.GRID * 0.35, y + self.GRID - eoff),
                    (x + self.GRID * 0.65, y + self.GRID - eoff)]
        else:
            eyes = [(x + self.GRID * 0.35, y + eoff - eye),
                    (x + self.GRID * 0.65, y + eoff - eye)]

        Color(0, 0, 0)
        for ex, ey in eyes:
            Rectangle(pos=(ex, ey), size=(eye, eye))

    # ---------- DRAW ----------
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            if self.death_flash > 0:
                Color(0.3, 0, 0)
                self.death_flash -= 1
            else:
                Color(0, 0, 0)

            Rectangle(pos=(0, 0), size=self.size)

            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.width, self.height), width=2)

            Color(0, 0.8, 0)
            for x, y in self.snake[1:]:
                Rectangle(pos=(x, y), size=(self.GRID, self.GRID))

            hx, hy = self.snake[0]
            self.draw_snake_head(hx, hy)

            fs = self.GRID * self.food_scale
            fx = self.food[0] + (self.GRID - fs) / 2
            fy = self.food[1] + (self.GRID - fs) / 2

            Color(1, 0, 0)
            Rectangle(pos=(fx, fy), size=(fs, fs))

    # ---------- KEYBOARD ----------
    def on_key_down(self, window, key, *args):
        if key == 273:
            self.direction = "UP"
        elif key == 274:
            self.direction = "DOWN"
        elif key == 276:
            self.direction = "LEFT"
        elif key == 275:
            self.direction = "RIGHT"


class SnakeApp(App):
    def build(self):
        root = FloatLayout()
        self.game = SnakeGame()
        root.add_widget(self.game)

        Window.bind(on_key_down=self.game.on_key_down)

        # Controls overlay
        def ctrl(txt, x, y, d):
            btn = Button(
                text=txt,
                size_hint=(0.18, 0.08),
                pos_hint={"x": x, "y": y},
                background_normal="",
                background_down="",
                background_color=(1, 1, 1, 0.15),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda i: setattr(self.game, "direction", d))
            root.add_widget(btn)

        ctrl("↑", 0.41, 0.10, "UP")
        ctrl("←", 0.23, 0.01, "LEFT")
        ctrl("↓", 0.41, 0.01, "DOWN")
        ctrl("→", 0.59, 0.01, "RIGHT")

        self.restart_btn = Button(
            text="RESTART",
            size_hint=(0.4, 0.08),
            pos_hint={"x": 0.3, "y": 0.45},
            opacity=0,
            disabled=True
        )
        self.restart_btn.bind(on_press=self.restart_game)
        root.add_widget(self.restart_btn)

        return root

    def show_restart(self):
        self.restart_btn.opacity = 1
        self.restart_btn.disabled = False

    def restart_game(self, instance):
        self.restart_btn.opacity = 0
        self.restart_btn.disabled = True
        self.game.reset_game()


if __name__ == "__main__":
    SnakeApp().run()
