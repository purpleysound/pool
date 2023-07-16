import pygame
import random
import math


SCREEN_X, SCREEN_Y = 804, 456

RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FELT_GREEN = (44, 130, 87)

TABLE_IMG = pygame.image.load('table.png')

FRICTION = 1  # 1 is smooth, 0<fr<1 is rough
E = 1
I = pygame.math.Vector2(1, 0)
J = pygame.math.Vector2(0, 1)

class Game:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
        self.clock = pygame.time.Clock()
        self.running = True
        self.table = Table()
        self.rack_balls()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(pygame.mouse.get_pos())

    def update(self):
        for ball in self.balls:
            ball.update(self)

    def draw(self):
        self.display.fill(FELT_GREEN)
        for hole in self.table.holes:
            hole.draw(self.display)
        self.table.draw(self.display)
        for ball in self.balls:
            ball.draw(self.display)
        pygame.display.flip()

    def rack_balls(self):
        self.balls: list[Ball] = []
        colours = [RED, YELLOW, RED, RED, BLACK, YELLOW, YELLOW, RED, YELLOW, RED, RED, YELLOW, RED, YELLOW, YELLOW]
        x = 600
        y = 225 + 2*Ball.RADIUS
        first_in_column_y = 225
        for i in range(15):
            if i in [1, 3, 6, 10]:
                x += 3**0.5 * Ball.RADIUS  # 2rcos(30)
                first_in_column_y += 0.5 * Ball.RADIUS  # 2rsin(30)
                y = first_in_column_y
            else:
                y -= 2*Ball.RADIUS
            self.balls.append(Ball((x, y), colours[i]))


class Table:
    WIDTH = 700
    HEIGHT = 350
    def __init__(self) -> None:
        self.rect = TABLE_IMG.get_rect()
        self.holes = [Hole(hole) for hole in Hole.HOLES]

    def draw(self, display: pygame.Surface):
        display.blit(TABLE_IMG, self.rect)


class Hole:
    RADIUS = 25
    HOLES = [(50, 50), (402, 40), (755, 50), (50, 407), (402, 417), (755, 407)]
    def __init__(self, coordinates) -> None:
        self.pos = pygame.math.Vector2(coordinates)

    def draw(self, display):
        pygame.draw.circle(display, BLACK, (self.pos.x, self.pos.y), self.RADIUS)        


class Ball:
    RADIUS = 9
    def __init__(self, coordinates, colour) -> None:
        self.pos = pygame.math.Vector2(coordinates)
        self.colour = colour
        self.moving = False
        self.velocity = pygame.math.Vector2(0, 0)
        self.velocity = self.velocity.rotate(random.randint(0, 360))
        self.collided_last_frame = False

    def update(self, game: Game):
        self.pos += self.velocity
        if self.velocity.length() > 0.1:
            self.moving = True
            self.velocity *= FRICTION
        else:
            self.velocity = pygame.math.Vector2(5, 0)
            self.moving = False
        
        self.check_pocketed(game)
        self.check_collisions(game)

    def check_pocketed(self, game: Game):
        for hole in game.table.holes:
            if self.distance_to_ball(hole) < hole.RADIUS + 0.5*self.RADIUS:
                game.balls.remove(self)
                break

    def check_collisions(self, game: Game):
        if self.collided_last_frame:
            self.collided_last_frame = False
            return
        
        for ball in game.balls:
            if ball is not self:
                if self.distance_to_ball(ball) < 2*self.RADIUS:
                    self.ball_collision(ball)
                    self.collided_last_frame = True
        
        # check for collisions with table
        if self.pos.x < 50 + self.RADIUS or self.pos.x > 750 - self.RADIUS:
            if self.pos.x < 50 + self.RADIUS:
                self.pos.x = 50 + self.RADIUS
            else:
                self.pos.x = 750 - self.RADIUS
            self.velocity.x *= -E
        if self.pos.y < 50 + self.RADIUS or self.pos.y > 400 - self.RADIUS:
            if self.pos.y < 50 + self.RADIUS:
                self.pos.y = 50 + self.RADIUS
            else:
                self.pos.y = 400 - self.RADIUS
            self.velocity.y *= -E
        
    def distance_to_ball(self, other):
        return (self.pos - other.pos).length()
    
    def get_angle(self):
        """Returns angle subtended by i vector and velocity in radians"""
        if self.velocity.length() == 0:
            return 0
        if self.velocity.y < 0:
            angle = self.velocity.angle_to(I)
        else:
            angle = -self.velocity.angle_to(I)
        return math.radians(angle)
    
    def ball_collision(self, other):
        collision = other.pos - self.pos
        collision = collision.normalize()
        self_dot = self.velocity.dot(collision)
        other_dot = other.velocity.dot(collision)
        # some other guy did this and it worked
        self.velocity += (other_dot - self_dot) * collision * 0.5*(1+E)
        other.velocity += (self_dot - other_dot) * collision * 0.5*(1+E)

    def draw(self, display):
        pygame.draw.circle(display, self.colour, (int(self.pos.x), int(self.pos.y)), self.RADIUS)


if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
