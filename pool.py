import pygame
import random
import math
import time


SCREEN_X, SCREEN_Y = 804, 456

RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FELT_GREEN = (44, 130, 87)
CUE_WOOD_COLOUR = (139, 69, 19)

pygame.init()
TABLE_IMG = pygame.image.load('table.png')

FRICTION = 0.99  # 1 is smooth, 0<fr<1 is rough
COLLISION_DELAY = 0  # number of frames between ball collisions, prevents balls from getting stuck together but makes break less realistic
E = 1
I = pygame.math.Vector2(1, 0)
J = pygame.math.Vector2(0, 1)
OUT_OF_BOUNDS = pygame.math.Vector2(-100, -100)

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.rack_balls()

            if not any(ball.moving for ball in self.balls):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.cue_start_time = time.time()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.cue_end_time = time.time()
                    velocity = min(10*(self.cue_end_time - self.cue_start_time), 20)
                    self.balls[-1].project(velocity, pygame.mouse.get_pos())

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
        # Creates an equilateral triangle of balls starting at (600, 225)
        for i in range(5):
            for j in range(i+1):
                self.balls.append(Ball((600 + 2*i*Ball.RADIUS, 225 + (2*j-i)*Ball.RADIUS), colours.pop(0)))
        self.balls.append(CueBall((200, 225)))


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
        self.velocity = pygame.math.Vector2(0, 0)
        self.moving = False
        self.velocity = self.velocity.rotate(random.randint(0, 360))
        self.frames_since_last_ball_collision = 0

    def update(self, game: Game):
        self.pos += self.velocity
        if self.velocity.length() > 0.1:
            self.velocity *= FRICTION
            self.moving = True
        else:
            self.velocity = pygame.math.Vector2(0, 0)
            self.moving = False
        
        self.check_pocketed(game)
        self.frames_since_last_ball_collision += 1
        self.check_collisions(game)

    def check_pocketed(self, game: Game):
        for hole in game.table.holes:
            if self.distance_to_ball(hole) < hole.RADIUS + 0.5*self.RADIUS:
                self.get_pocketed(game)
                break

    def check_collisions(self, game: Game):
        # check for collisions with table
        if self.pos == OUT_OF_BOUNDS:
            return  # If this gets triggered accidentally i will personally throw a hissy fit

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

        if self.frames_since_last_ball_collision < COLLISION_DELAY:
            return
        
        for ball in game.balls:
            if ball is not self:
                if self.distance_to_ball(ball) < 2*self.RADIUS:
                    self.ball_collision(ball)
                    self.frames_since_last_ball_collision = 0  
        
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

        overlap = 2*self.RADIUS - (other.pos - self.pos).length()
        assert overlap > 0
        self.pos -= collision * overlap
        other.pos += collision * overlap

    def get_pocketed(self, game: Game):
        game.balls.remove(self)

    def draw(self, display):
        pygame.draw.circle(display, self.colour, (int(self.pos.x), int(self.pos.y)), self.RADIUS)


class CueBall(Ball):
    def __init__(self, coordinates) -> None:
        super().__init__(coordinates, WHITE)
        self.can_be_shot = True

    def update(self, game: Game):
        if any(ball.moving for ball in game.balls):
            self.can_be_shot = False
        else:
            self.can_be_shot = True
        if self.can_be_shot and self.pos == OUT_OF_BOUNDS:
            self.pos = pygame.math.Vector2(200, 225)
        super().update(game)
        
    def project(self, speed, target_coord):
        target = pygame.math.Vector2(target_coord)
        target = target - self.pos
        target = target.normalize()
        target = target * speed
        self.velocity = target

    def get_pocketed(self, game: Game):
        self.pos = OUT_OF_BOUNDS
        self.velocity = pygame.math.Vector2(0, 0)

    def draw(self, display):
        super().draw(display)
        if self.can_be_shot:  # Cue
            mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
            delta = self.pos - mouse_pos  # rotated 180 because cue is behind ball
            delta = delta.normalize()
            delta = delta * 2*self.RADIUS
            start_pos = self.pos + delta
            end_pos = self.pos + 100*delta
            pygame.draw.line(display, CUE_WOOD_COLOUR, (start_pos.x, start_pos.y), (end_pos.x, end_pos.y), 5)


if __name__ == '__main__':
    pygame.init()
    Game().run()
    pygame.quit()
