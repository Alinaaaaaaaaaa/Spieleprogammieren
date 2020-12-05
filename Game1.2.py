import pygame       # Stellt Objekte und Konstanten zur Spielprogrammierung zur Verfügung
import os
import random

class Settings(object):
    width = 700                 #Posizionierung des Fensters
    height = 400
    title = "Game1.2"           #Name des Spiels
    fps = 60                    #Begrenzung der Frames pro Sekunde
    file_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(file_path, "images2")        #Auswahl des Ortners wo alles drin ist

    @staticmethod
    def get_dim():
        return (Settings.width, Settings.height)

class Character(pygame.sprite.Sprite):
    def __init__(self, pygame):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.images_path, "Spieler1_Stehend.png")).convert_alpha()  #auwahl des bildes
        self.image = pygame.transform.scale(self.image, (50, 80))               #skalliert das bild
        self.rect = self.image.get_rect()
        self.space = False
        self.rect.left = (Settings.width - self.rect.width) // 2                #Posizionierung des characters
        self.rect.top = (Settings.height - self.rect.height) // 2
        self.direction = 0
        self.speed = 5

    def update(self):
       # Steuerung mit Pfeiltasten
        if pygame.key.get_pressed()[pygame.K_LEFT] == True:
           self.rect.left -= self.speed

        if pygame.key.get_pressed()[pygame.K_RIGHT] == True:
            self.rect.left += self.speed

        if pygame.key.get_pressed()[pygame.K_UP] == True:
           self.rect.top -= self.speed

        if pygame.key.get_pressed()[pygame.K_DOWN] == True:
            self.rect.top += self.speed

        # Kollision mit dem Rand
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= Settings.width:
            self.rect.right = Settings.width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= Settings.height:
            self.rect.bottom = Settings.height

        # Teleportation beim loslassen der Leertaste
        if pygame.key.get_pressed()[pygame.K_SPACE] == True:
            self.space = True
        if pygame.key.get_pressed()[pygame.K_SPACE] == False and self.space == True:
            self.rect.top = random.randrange(0, Settings.height - self.rect.height)
            self.rect.left = random.randrange(0, Settings.width - self.rect.width)
            self.space = False


class Game(object):
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        pygame.display.set_caption(Settings.title)

        self.background = pygame.image.load(os.path.join(Settings.images_path, "background.png")).convert()
        self.background = pygame.transform.scale(self.background, (Settings.width, Settings.height))
        self.background_rect = self.background.get_rect()

        self.all_character = pygame.sprite.Group()      #erstellung der gruppe
        self.character = Character(pygame)              #erstellung des character
        self.all_character.add(self.character)  	    #packt den character in die gruppe

        self.clock = pygame.time.Clock()
        self.done = False

    def run(self):
        while not self.done:             # Hauptprogrammschleife mit Abbruchkriterium   
            self.clock.tick(Settings.fps)          # Setzt die Taktrate auf max 60fps   
            for event in pygame.event.get():    # Durchwandere alle aufgetretenen  Ereignisse
                if event.type == pygame.QUIT:   # Wenn das rechts obere X im Fenster geklickt
                    self.done = True                 # Flag wird auf Ende gesetzt


            self.screen.blit(self.background, self.background_rect)
            self.all_character.draw(self.screen)
            self.all_character.update()
            pygame.display.flip()   # Aktualisiert das Fenster


if __name__ == '__main__':      #                      
    pygame.init()               # Bereitet die Module zur Verwendung vor  
    game = Game()
    game.run()
    pygame.quit()               #beendet pygame