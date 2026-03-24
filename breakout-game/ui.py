# ui.py
import turtle
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class UI:
    """
    Manages the head-up display (HUD) including score and lives.
    Communicates with the BreakoutGame class to update numbers or show messages.
    """
    def __init__(self, screen):
        """
        Creates hidden turtles to act as text pens for score and lives.
        Positions them at the top corners of the provided screen.
        """
        self.screen = screen
        self.score = 0
        self.lives = 3

        # ---------------------------- SCORE LABEL ------------------------------- #
        self.score_t = turtle.Turtle()
        self.score_t.hideturtle()
        self.score_t.penup()
        self.score_t.color("white")
        self.score_t.goto(-SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 - 40)

        # ---------------------------- LIVES LABEL  ------------------------------- #
        self.lives_t = turtle.Turtle()
        self.lives_t.hideturtle()
        self.lives_t.penup()
        self.lives_t.color("white")
        self.lives_t.goto(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 40)

        # ---------------------------- UPDATING STARTING METHODS ------------------------------- #
        self._update_score()
        self._update_lives()



    # ---------------------------- Private/internal helpers ------------------------------- #
    def _update_score(self):
        """Internal helper to clear and redraw the score text."""
        self.score_t.clear()
        self.score_t.write(f"Score: {self.score}", align="left", font=("Consolas", 16, "bold"))

    def _update_lives(self):
        """Internal helper to clear and redraw the lives text."""
        self.lives_t.clear()
        self.lives_t.write(f"Lives: {self.lives}", align="left", font=("Consolas", 16, "bold"))




    # ---------------------------- Public methods ------------------------------- #
    def add_points(self, points):
        """Increments score and triggers a UI redraw. Called by Game class on brick collision."""
        self.score += points
        self._update_score()

    def lose_life(self):
        """Decrements lives. Returns False if game over, True if still alive."""
        self.lives -= 1
        self._update_lives()
        return self.lives > 0

    def show_message(self, text, color="white"):
        """Creates a temporary turtle to write a large message in the center of the screen."""
        msg = turtle.Turtle()
        msg.hideturtle()
        msg.penup()
        msg.color(color)
        msg.goto(0, 0)
        msg.write(text, align="center", font=("Consolas", 40, "bold"))