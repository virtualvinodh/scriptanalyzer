# GUI for the Trajectory reconstruction module
import pygame
from pygame.locals import *

def DispTrajectory(path,colr):

    # Initialization
    pygame.init()
    
    screen = pygame.display.set_mode((500, 330))
    pygame.display.set_caption("Visualizing Pen Trajectory")
    x,y= 200,200
    done = False
    clock = pygame.time.Clock()
    
    while done == False:
        clock.tick(10)
        screen.fill((255, 255, 255))
        pen = pygame.image.load("../resources/pen.gif").convert()
        
        X, Y = [], []
        
        for x,y in path:
            x,y = int(x), int(y)
            X.append(x)
            Y.append(y)
            screen.blit(pen,(x,y-50))
            pygame.draw.circle(screen,colr,(x,y),3,0)
            pygame.time.wait(5)
            pygame.display.flip()
            
            screen.fill((255, 255, 255))
            for xn, yn in zip(X,Y):
                pygame.draw.circle(screen,colr,(xn,yn),3,0)
            
        pygame.time.wait(4000)
        done = True
        
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                done = True
                
        pygame.display.flip()
        
    pygame.quit()
