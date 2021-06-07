import pygame
import os
import random

class Settings():
    breite = 576
    höhe = 576
    title = "Minesweeper"
    file_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(file_path, "images")
    fps = 60
    

    @staticmethod
    def get_dim():
        return (Settings.breite, Settings.höhe)


class Mine(pygame.sprite.Sprite):
    def __init__(self, pygame, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, "Miene.png")).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (64, 64))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

class Fahne(pygame.sprite.Sprite):
    def __init__(self, pygame, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, "Fahne.png")).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (64, 64))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


class Zahl(pygame.sprite.Sprite):
    def __init__(self, pygame, bild, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, bild)).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (64, 64))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


class Voll(pygame.sprite.Sprite):
    def __init__(self, pygame, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, "Voll.png")).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (64, 64))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


class Leer(pygame.sprite.Sprite):
    def __init__(self, pygame, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, "Leer.png")).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (64, 64))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


class Game(object):
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()
        self.Ende = False

        self.all_voll = pygame.sprite.Group()      #erstellung der gruppe
        self.all_leer = pygame.sprite.Group()      #erstellung der gruppe
        self.all_mine = pygame.sprite.Group() 
        self.all_zahl = pygame.sprite.Group()
        self.start = True

    def run(self):
        while not self.Ende:             # Hauptprogrammschleife mit Abbruchkriterium   
            self.clock.tick(Settings.fps)          # Setzt die Taktrate auf max 60fps   
            for event in pygame.event.get():    # Durchwandere alle aufgetretenen  Ereignisse
                if event.type == pygame.QUIT:   # Wenn das rechts obere X im Fenster geklickt
                    self.Ende = True                 # Flag wird auf Ende gesetzt
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.Ende = True
            if self.start == True:
                self.start = False
                for x in range(0, 576, 64):
                    for y in range(0, 576, 64):
                        self.leer = Leer(pygame, x, y)
                        self.all_leer.add(self.leer)
                for mine in range(0, 10):
                    self.minex = random.randrange(0, 576, 64)
                    self.miney = random.randrange(0, 576, 64)
                    self.mine = Mine(pygame, self.minex, self.miney)
                    self.all_mine.add(self.mine)
                    print(self.all_mine)


            self.all_leer.draw(self.screen)
            self.all_zahl.draw(self.screen)
            self.all_mine.draw(self.screen)
            
            pygame.display.flip()
            
if __name__ == '__main__':                      
    pygame.init()               # Bereitet die Module zur Verwendung vor  
    game = Game()
    game.run()
    pygame.quit()               #beendet pygame