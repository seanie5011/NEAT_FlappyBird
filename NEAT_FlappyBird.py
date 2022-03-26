import pygame, neat, time, os, sys, random

#---Initialising---#
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

pygame.init()

GEN = 0

#---Imports---#
BIRD_IMGS = [pygame.transform.scale(pygame.image.load("assets\\yellowbird-upflap.png"), (68, 48)),
             pygame.transform.scale(pygame.image.load("assets\\yellowbird-midflap.png"), (68, 48)),
             pygame.transform.scale(pygame.image.load("assets\\yellowbird-downflap.png"), (68, 48))]

PIPE_IMG = pygame.transform.scale(pygame.image.load("assets\\pipe-green.png"), (100, SCREEN_HEIGHT))
FLOOR_IMG = pygame.transform.scale(pygame.image.load("assets\\base.png"), (SCREEN_WIDTH, 200))
BG_IMG = pygame.transform.scale(pygame.image.load("assets\\background-day.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font
GAME_FONT = pygame.font.Font("assets\\04B_19.ttf", 40)

class Bird():
    IMGS = BIRD_IMGS
    ROT_MAX = 25
    ROT_V = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.tick_count = 0 # when we last jumped
        self.v = 0
        self.height = self.y

        self.tilt = 0

        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        # set velocity and reset time
        self.v = -11
        self.tick_count = 0
        # update height
        self.height = self.y

    def move(self):
        # increase time
        self.tick_count += 1
        # find the displacement using s = ut + 1/2at^2 (with a = 3), remember y-direction is downwards
        d = self.v * self.tick_count + 0.5 * 3 * (self.tick_count)**2

        # set max displacement (limits velocity)
        if d >= 16:
            d = 16
        # fine tune jump height
        if d < 0:
            d -= 2

        self.y = self.y + d

        # tilt bird
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.ROT_MAX:
                self.tilt = self.ROT_MAX # limits how much we rotate when looking up
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_V # nose dive

    def draw(self, screen):
        # every frame increase timer
        self.img_count += 1

        # if current timer matches some multiple of animation frame rate
        if self.img_count < 1 * self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < 2 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < 3 * self.ANIMATION_TIME:
            self.img = self.IMGS[2]
        elif self.img_count < 4 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count > 4 * self.ANIMATION_TIME: # when hits max animation time
            self.img = self.IMGS[0]
            self.img_count = 0

        # when nose diving, set to specific animation
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = 2 * self.ANIMATION_TIME

        # rotate image and get rect
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        rotated_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center) # ensures center of rotated rect is at center of unrotated

        screen.blit(rotated_img, rotated_rect.topleft)

    def get_mask(self): # used in collision detection
        return pygame.mask.from_surface(self.img)

class Pipe():
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.v = 5

        self.height = 0
        self.gap = 200
        self.top = 0
        self.bottom = 0

        self.PIPE_BOTTOM = PIPE_IMG
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # flip the pipe sprite

        self.passed = False
        self.set_height()

    def set_height(self):
        # find random height for pipes to spawn
        self.height = random.randrange(40, 450)
        # set positions
        self.top = self.height - self.PIPE_TOP.get_height() # y-direction is downwards, find the position to start drawing the Top Pipe
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.VEL

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # get vector between both pipes and bird
        top_offset = (self.x - bird.x, self.top - round(bird.y)) # round as we cant have decimal pixel values
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_offset) # need to provide offset to pygame.mask.Mask
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

        # check if there is overlap (if not None)
        if top_point or bottom_point:
            return True
        else:
            return False

class Floor():
    VEL = 5
    WIDTH = FLOOR_IMG.get_width()
    IMG = FLOOR_IMG

    def __init__(self, y):
        self.y = y

        # positions of two instances of floor
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # move both by same amount
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # if they reach end of run, reset
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, score, gen, alive):
    screen.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(screen)

    floor.draw(screen)
    for bird in birds:
        pygame.draw.line(screen, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (pipes[-1].x, pipes[-1].bottom), width = 3)
        pygame.draw.line(screen, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (pipes[-1].x, pipes[-1].bottom - pipes[-1].gap), width = 3)
        bird.draw(screen)

    text_score = GAME_FONT.render("SCORE: " + str(score), 1, (255, 255, 255))
    screen.blit(text_score, (SCREEN_WIDTH - 10 - text_score.get_width(), 10))

    text_gen = GAME_FONT.render("GEN: " + str(gen), 1, (255, 255, 255))
    screen.blit(text_gen, (10, 10))

    text_alive = GAME_FONT.render("ALIVE: " + str(alive), 1, (255, 255, 255))
    screen.blit(text_alive, (10, 10 + text_gen.get_height()))

    pygame.display.update()

def main(genomes, config): # often called eval_genomes or similar
    global GEN
    GEN += 1

    clock = pygame.time.Clock()
    screen_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen_display.fill((0, 0, 0))

    nets = []
    birds = []
    ge = []
    for _, g in genomes: # genomes is a tuple with the index and actual genome object, so need to differentiate
        net = neat.nn.FeedForwardNetwork.create(g, config) # set up NN for genome
        nets.append(net)

        birds.append(Bird(230, 350)) # create bird for it

        g.fitness = 0
        ge.append(g) # store genome with 0 fitness

    base = Floor(730)
    pipes = [Pipe(600)]

    score = 0

    run = True
    while run:
        #---events---#
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        pipe_index = 0 # looking at first pipe
        if len(birds) > 0: # if there are birds
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # if there are pipes and bird is further than first pipe (note due to setup only two pipes can be visible)
                pipe_index = 1 # looking at second pipe
        else:
            run = False
            break

        for index, bird in enumerate(birds):
            bird.move()
            ge[index].fitness += 0.1 # runs 30 times a second, so 3 fitness a second for staying alive

            # returns output of NN through Activation Func given Bird Y, Top Pipe Distance and Bottom Pipe Distance
            output = nets[index].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))
            # if our only (so first in list) output neuron sufficiently activated (NN is certain)
            if output[0] > 0.5:
                bird.jump()

        # move objects
        base.move()

        # pipe logic and movement
        remove_pipes = []
        add_pipe = False

        for pipe in pipes: # check over all pipes
            for index, bird in enumerate(birds): # check collisions and position for each bird
                if pipe.collide(bird): # bird dies
                    ge[index].fitness -= 1 # favours birds that make it through pipe

                    birds.pop(index) # removes the bird from list
                    nets.pop(index)
                    ge.pop(index)

                if not pipe.passed and pipe.x < bird.x: # if we have not yet passed pipe and pipe is behind us
                    pipe.passed = True # now passed
                    add_pipe = True # determines whether we should add a new pipe

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # if pipe is completely off screen
                remove_pipes.append(pipe)

            pipe.move()
            
        # add new pipes
        if add_pipe:
            pipes.append(Pipe(600))
            # increase score and fitness
            score += 1
            for g in ge:
                g.fitness += 3

        # remove pipes
        for pipe in remove_pipes:
            pipes.remove(pipe)

        # bird dies
        for index, bird in enumerate(birds):
            if score == 30:
                print("PASSED----------------------")
                birds.pop(index)
                nets.pop(index)
                ge.pop(index)
            # if hits base or goes too high
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(index)
                nets.pop(index)
                ge.pop(index)

        # draw
        draw_screen(screen_display, birds, pipes, base, score, GEN - 1, len(birds)) # GEN - 1 as its one step ahead from being updated at start

        clock.tick(30)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50) # main is our fitness function, played 50 times, returns best genome when finished

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

# RL as there is clearly more reward for going further then there is dying
# fitness is our sense of reward and NEAT is the method to identify which NN gives most reward
# by running 100 birds at a time we actually find a perfect bird very quickly by chance
# this is not of course computationally favourable so we will lower amount of birds