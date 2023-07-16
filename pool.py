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
        self.display.fill(BLACK)
        self.table.draw(self.display)
        for ball in self.balls:
            ball.draw(self.display)
        pygame.display.flip()

    def rack_balls(self):
        self.balls: list[Ball] = []
        colours = [RED]*7 + [YELLOW]*7 + [BLACK]
        for i in range(15):
            self.balls.append(Ball((SCREEN_X//2 + 2*Ball.RADIUS*(i-7), SCREEN_Y//2), colours[i]))


class Table:
    WIDTH = 700
    HEIGHT = 350
    def __init__(self) -> None:
        self.rect = TABLE_IMG.get_rect()
        self.mask = pygame.mask.from_surface(TABLE_IMG.convert_alpha(), threshold=1)

    def draw(self, display: pygame.Surface):
        pygame.draw.rect(display, FELT_GREEN, self.rect)
        display.blit(TABLE_IMG, self.rect)
        for pixel in self.mask.outline():
            pygame.draw.circle(display, WHITE, (pixel[0] + self.rect.x, pixel[1] + self.rect.y), 1)
        


class Ball:
    RADIUS = 9
    def __init__(self, coordinates, colour) -> None:
        self.pos = pygame.math.Vector2(coordinates)
        self.colour = colour
        self.moving = False
        self.velocity = pygame.math.Vector2(5, 0)
        self.moving = True
        self.velocity = self.velocity.rotate(random.randint(0, 360))
        self.collided_last_frame = False


    def update(self, game: Game):
        self.pos += self.velocity
        if self.velocity.length() > 0.1:
            self.moving = True
            self.velocity *= 1
        else:
            self.velocity = pygame.math.Vector2(0, 0)
            self.moving = False

        self.check_collisions(game)

    def check_collisions(self, game):
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
            self.velocity.x *= -1
        if self.pos.y < 50 + self.RADIUS or self.pos.y > 400 - self.RADIUS:
            if self.pos.y < 50 + self.RADIUS:
                self.pos.y = 50 + self.RADIUS
            else:
                self.pos.y = 400 - self.RADIUS
            self.velocity.y *= -1
        
    
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
        pygame.draw.circle(display, self.colour, (self.pos.x, self.pos.y), self.RADIUS)




if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
