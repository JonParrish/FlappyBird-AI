import pygame
import neat 
import time
import os 
import random 
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird: 
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #Tilts bird avatar up and down
    ROT_VEL = 20 #How much we rotate the bird on each frame
    ANIMATION_TIME = 5 #How slow or fast the bird "flaps"

    def __init__(self, x, y): 
        self.x = x #starting x position of bird
        self.y = y #starting y position of bird
        self.tilt = 0 #starting tilt  of bird; 0 looks forward with no tilt either way
        self.tick_count = 0 #used in physics of bird
        self.vel = 0 #velocity, starts at 0 'cause you don't start moving
        self.height = self.y 
        self.img_count = 0 #Used to tell which image is being used for animation purposes
        self.img = self.IMGS[0] #starting iamge

     #When we jump, we reset tick_count to 0 
    def jump(self): 
        self.vel = -10.5 #starting velocity. 
        self.tick_count = 0 #keeps track of when bird last jumped
        self.height = self.y #keeps track of where bird jumped from
        
    def move(self): 
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2 #Tells us based off our current velocity how much we are moving up or down. 
        #self.tick_count is used in place of seconds as out variable for time

        if d >= 16: #terminal velocity/failsafe for velocity equation
            d = 16
            
        if d < 0: 
            d -= 2
            
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50: 
            if self.tilt < self.MAX_ROTATION: 
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90: 
                self.tilt -= self.ROT_VEL

    def draw(self, win): 
        self.img_count += 1

        #Checks which image should be displayed
        if self.img_count < self.ANIMATION_TIME: 
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80: 
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #rotate bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)
        

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe: 
    GAP = 200 #space between horizantal pipes
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False

        self.set_height()
    
    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False


class Base:
    VEL = 5 #same as pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        #checks to see if one of the 2 img's are off teh screen and moves it back to the right side to start again.
        if self.x1 + self.WIDTH < 0:
            self.x1 + self.x2 + self.WIDTH
 
        if self.x2 + self.WIDTH < 0:
            self.x2 + self.x1 + self.WIDTH
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
               

#rotate image function, stolen from 
def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)
        
def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0)) #blit just means draw
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pygame.display.update()

def main(genomes, config):

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
        

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock() #Creates a clock for ensuring program runs at same speed regardless of OS, system, or RAM, etc. 
    
    score = 0

    run = True
    while run: 
        clock.tick(30) #Tick's a maximum of 30 times a second 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
        
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        #bird.move()
        rem = []
        add_pipe = False
        for pipe in pipes: 

            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)                 
                
                if not pipe.passed and pipe.x < bird.x: 
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            #Attempts at difficulty increasing    
            if score > 5:
                if score > 10:
                    pipes.append(Pipe(400))
                else:
                    pipes.append(Pipe(500))
            else:
                pipes.append(Pipe(600))
        
        for r in rem:
            pipes.remove(r)
        #death check
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move() 
        draw_window(win, birds, pipes, base, score)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'breedingbird.txt')
    run(config_path)