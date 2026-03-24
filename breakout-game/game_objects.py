import turtle
from constants import *



# ---------------------------- Parent Classes  ------------------------------- #
class GameObject:
    """
    Base class for all visual elements in the game.
    Provides a turtle instance, positioning, and basic hit-box calculation.
    """
    def __init__(self, x=0, y=0, shape="square", color="white", stretch_w=1.0, stretch_h=1.0):
        """
        Initializes the turtle component and moves it to the starting (x, y).
        The stretch parameters convert the default 20x20 turtle square into
        the specific dimensions needed for paddles or bricks.
        """
        self.t = turtle.Turtle()
        self.t.shape(shape)
        self.t.color(color)
        self.t.penup()
        self.t.shapesize(stretch_wid=stretch_h, stretch_len=stretch_w) # returns a tuple (stretch_wid, stretch_len, outline) when called
        self.t.goto(x, y)
        self.x = x
        self.y = y

    def hide(self):
        """Hides the turtle from the screen. Used when a brick is destroyed."""
        self.t.hideturtle()

    def get_rect(self):
        """
        Calculates the AABB (Axis-Aligned Bounding Box) for the object.
        Multiplies the turtle's stretch factor (shapesize tuple) by the base size (20px).
        Returns a dictionary used by the collision detection in BreakoutGame.
        """
        w = self.t.shapesize()[1] * 20 # Horizontal stretch * 20 = width in px
        h = self.t.shapesize()[0] * 20 # Vertical stretch * 20 = width in px
        return {
            "left": self.x - w/2,
            "right": self.x + w/2,
            "top": self.y + h/2,
            "bottom": self.y - h/2
        }




class MovableObject(GameObject):
    """
    Extension of GameObject for items that change position over time (Ball, Paddle).
    Introduces delta-x (dx) and delta-y (dy) for velocity control.
    """
    def __init__(self, *args, **kwargs):
        """Sets up velocity components to 0 by default."""
        super().__init__(*args, **kwargs)
        self.dx = 0
        self.dy = 0

    def move(self):
        """Updates x and y based on velocity and teleports the turtle to new coordinates."""
        self.x += self.dx
        self.y += self.dy
        self.t.goto(self.x, self.y)



# ---------------------------- Child Classes  ------------------------------- #



class Paddle(MovableObject):
    """
    The player-controlled paddle.
    Inherits move() logic but is restricted to the horizontal axis by the Game class.
    """
    def __init__(self):
        """Sizes the paddle using PADDLE_WIDTH and PADDLE_HEIGHT from constants."""
        super().__init__(0, PADDLE_Y, stretch_w=PADDLE_WIDTH/20, stretch_h=PADDLE_HEIGHT/20)

class Ball(MovableObject):
    """
    The game ball.
    Interacts with walls, the paddle, and bricks via the Game class's collision logic.
    """
    def __init__(self):
        """Uses circular shape and BALL_RADIUS for initialization."""
        super().__init__(0, 0, "circle", stretch_w=BALL_RADIUS/10, stretch_h=BALL_RADIUS/10)

class Brick(GameObject):
    """
    Static targets for the ball.
    Each brick holds a point value used by the UI class when destroyed.
    """
    def __init__(self, x, y, color, points):
        """Sets color and score value; uses static positioning."""
        super().__init__(x, y, color=color, stretch_w=BRICK_WIDTH/20, stretch_h=BRICK_HEIGHT/20)
        self.points = points