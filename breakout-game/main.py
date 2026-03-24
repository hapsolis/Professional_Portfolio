import turtle
import time
from constants import *
from game_objects import Paddle, Ball, Brick
from ui import UI



class BreakoutGame:
    """
    The core Game Engine.
    Orchestrates movement, handles input, checks collisions, and manages the game loop.
    """
    def __init__(self):
        """
        Initializes the Screen, UI, Paddle, Ball, and Bricks.
        Sets the tracer to 0 for manual screen updates (prevents flickering).
        """
        # ---------------------------- SCREEN SETUP ------------------------------- #
        self.screen = turtle.Screen()
        self.screen.title("Breakout – Day 87")
        self.screen.bgcolor("black")
        self.screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen.tracer(0)

        # ---------------------------- UI/Paddle/Ball CLASSES INSTANTIATE ------------------------------- #
        self.ui = UI(self.screen)
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = self._create_bricks()     # <===== Private Method / Internal helper function

        self.ball_on_paddle = True
        self.launch_time = time.time()
        self.game_is_on = True

        self.launch_requested = False # Manual launch flag
        self._setup_controls()          # <===== Private Method / Internal helper function

    def _create_bricks(self):
        """
        Uses a Nested Loop (a loop inside a loop) to build a grid of bricks
        -The Outer Loop (row): Moves vertically from top to bottom.
        -The Inner Loop (col): Moves horizontally from left to right for every row.
        """
        bricks = []
        y = BRICK_START_Y
        for row in range(BRICK_ROWS):
            color, points = COLORS_AND_POINTS[row // 2] # Creates the "double-row" color pattern , based on the constant's tuples
            for col in range(BRICK_COLS):
                #       Start    +  Center of the object +      gap
                x = -SCREEN_WIDTH//2 + BRICK_WIDTH//2 + col * (BRICK_WIDTH + 5)  # col 1: x = Start + 52 + 5, col 2: x = Start + 104 + 10
                bricks.append(Brick(x, y, color, points))
            y -= BRICK_HEIGHT + 5
        return bricks

    def _setup_controls(self):
        """
        Binds keyboard keys to paddle velocity.
        Uses lambda to directly set the 'dx' attribute of the paddle object.
        """
        self.screen.listen()
        self.screen.onkeypress(lambda: setattr(self.paddle, 'dx', -PADDLE_SPEED), "Left")
        self.screen.onkeypress(lambda: setattr(self.paddle, 'dx',  PADDLE_SPEED), "Right")
        self.screen.onkeyrelease(lambda: setattr(self.paddle, 'dx', 0), "Left")
        self.screen.onkeyrelease(lambda: setattr(self.paddle, 'dx', 0), "Right")

        self.screen.onkeypress(lambda: setattr(self, 'launch_requested', True) if self.ball_on_paddle else None,
                               "space")

    def run(self):                      # <===== Public method
        """
        Main Game Loop.
        1. Updates positions.
        2. Clamps paddle to walls.
        3. Handles ball-launch timer.
        4. Triggers collision checks.
        """
        while self.game_is_on:
            self.screen.update()
            time.sleep(FPS_DELAY)

            self.paddle.move()

            # Boundary checking for paddle
            half_w = PADDLE_WIDTH / 2
            if self.paddle.x < -SCREEN_WIDTH//2 + half_w:
                self.paddle.x = -SCREEN_WIDTH//2 + half_w
            elif self.paddle.x > SCREEN_WIDTH//2 - half_w:
                self.paddle.x = SCREEN_WIDTH//2 - half_w

            if self.ball_on_paddle:
                # Ball follows paddle until auto/manual-launch
                self.ball.x = self.paddle.x
                self.ball.y = self.paddle.y + 25
                self.ball.t.goto(self.ball.x, self.ball.y)

                if time.time() - self.launch_time > AUTO_LAUNCH_SEC or self.launch_requested:
                    self.ball.dx = 4
                    self.ball.dy = 6
                    self.ball_on_paddle = False
                    self.launch_requested = False  # Reset the flag for the next life
            else:
                self.ball.move()
                self._handle_collisions()           # <===== Private Method / Internal helper function

            if len(self.bricks) == 0:
                self.ui.show_message(text="YOU WIN!", color="lime")
                self.game_is_on = False

        self.screen.exitonclick()



    # ---------------------------- internal/prived "Loop" Helpers ------------------------------- #

    def _handle_collisions(self):
        """
        Check interaction between the Ball and all other entities.
        Includes wall bouncing, paddle deflection, and brick destruction.
        """
        # Wall bounces (Left/Right/Top)
        if abs(self.ball.x) > SCREEN_WIDTH//2 - BALL_RADIUS:
            self.ball.dx *= -1
        if self.ball.y > SCREEN_HEIGHT//2 - BALL_RADIUS:
            self.ball.dy *= -1

        # Paddle collision
        if self._check_collision(self.ball, self.paddle):
            self.ball.dy = abs(self.ball.dy) # Ensure it moves upward
            # Calculate bounce angle based on where ball hits the paddle
            hit_pos = (self.ball.x - self.paddle.x) / (PADDLE_WIDTH / 2) #/ (PADDLE_WIDTH / 2) "Normalizes" the number
            self.ball.dx = hit_pos * 7

        # Floor collision (Loss of life)
        if self.ball.y < -SCREEN_HEIGHT//2:
            if not self.ui.lose_life():
                self.ui.show_message("GAME OVER", "red")
                self.game_is_on = False
            else:
                # Reset ball to paddle
                self.ball_on_paddle = True
                self.launch_time = time.time()

        # Brick collisions
        for brick in self.bricks[:]: # Copy list to safely remove during iteration, equivalent to "temp_list = bricks[:]"
            if self._check_collision(self.ball, brick):
                brick.hide()
                self.bricks.remove(brick)
                self.ball.dy *= -1
                self.ui.add_points(brick.points)
                break

    def _check_collision(self, a, b):
        """
        Uses AABB (Axis-Aligned Bounding Box) logic to see if two GameObject rectangles overlap.
        Relies on the get_rect() method provided by the GameObject class.
        """
        ar = a.get_rect()
        br = b.get_rect()

        # If any of these are True, the objects are not touching.
        return not (ar["right"] < br["left"] or
                    ar["left"] > br["right"] or
                    ar["top"] < br["bottom"] or
                    ar["bottom"] > br["top"]
                    )

if __name__ == "__main__":
    game = BreakoutGame()
    game.run()