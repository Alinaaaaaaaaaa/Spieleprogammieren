import random, pygame, sys
from pygame.locals import *

# Settings
FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 900
BOXSIZE = 30
GAPSIZE = 5
FIELDWIDTH = 20
FIELDHEIGHT = 20
XMARGIN = int((WINDOWWIDTH-(FIELDWIDTH*(BOXSIZE+GAPSIZE)))/2)
YMARGIN = XMARGIN
MINESTOTAL = 60

assert MINESTOTAL < FIELDHEIGHT*FIELDWIDTH, 'More mines than boxes'
assert BOXSIZE^2 * (FIELDHEIGHT*FIELDWIDTH) < WINDOWHEIGHT*WINDOWWIDTH, 'Boxes will not fit on screen'
assert BOXSIZE/2 > 5, 'Bounding errors when drawing rectangle, cannot use half-5 in drawMinesNumbers'

# Farben zuweisen
LIGHTGRAY = (225, 225, 225)
DARKGRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)

# Hauptfarben einrichten
BGCOLOR = WHITE
FIELDCOLOR = BLACK
BOXCOLOR_COV = DARKGRAY 
BOXCOLOR_REV = LIGHTGRAY 
MINECOLOR = BLACK
TEXTCOLOR_1 = BLUE
TEXTCOLOR_2 = RED
TEXTCOLOR_3 = BLACK
HILITECOLOR = GREEN
RESETBGCOLOR = LIGHTGRAY
MINEMARK_COV = RED

# Schriftart einrichten 
FONTTYPE = 'Courier New'
FONTSIZE = 20

def main():

    # globale Variablen & pygame-Modul initialisieren
    global FPSCLOCK, DISPLAYSURFACE, BASICFONT, RESET_SURF, RESET_RECT, SHOW_SURF, SHOW_RECT
    pygame.init()
    pygame.display.set_caption('Minesweeper')
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.SysFont(FONTTYPE, FONTSIZE)

    # Objekte und Rechtecke zurücksetzen und anzeigen
    RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
    SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)

    # speichert XY von der Maus
    mouse_x = 0
    mouse_y = 0

    # Datenstrukturen und Listen einrichten
    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

    # setzt Hintergrundfarbe
    DISPLAYSURFACE.fill(BGCOLOR)

    # main Spiele Schleife
    while True:

        # Prüfung auf Beenden Funktion
        checkForKeyPress()

        # initialize input booleans
        mouseClicked = False
        spacePressed = False

        # felder Zeichnen
        DISPLAYSURFACE.fill(BGCOLOR)
        pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
        drawField()
        drawMinesNumbers(mineField)        

        # event handling loop
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouseClicked = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    spacePressed = True
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    spacePressed = False

        # draw covers
        drawCovers(revealedBoxes, markedMines)

        tipFont = pygame.font.SysFont(FONTTYPE, 16) 
        drawText('Tip: Highlight a box and press space (rather than click the mouse)', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
        drawText('to mark areas that you think contain mines.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)
            
        # Boxen an angeklickten Stellen bestimmen
        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)

        if (box_x, box_y) == (None, None):

            # Prüft, ob Reset-Box angeklickt ist
            if RESET_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(RESET_RECT)
                if mouseClicked: 
                    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

            # Prüft, ob Showbox angeklickt ist
            if SHOW_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(SHOW_RECT)
                if mouseClicked:
                    revealedBoxes = blankRevealedBoxData(True)

        else:

            # nicht angezeigtes Feld markieren
            if not revealedBoxes[box_x][box_y]: 
                highlightBox(box_x, box_y)

                # Minen markieren
                if spacePressed:
                    markedMines.append([box_x, box_y])
                    
                # angeklickte Boxen aufdecken
                if mouseClicked:
                    revealedBoxes[box_x][box_y] = True

                    # Wenn 0 aufgedeckt wird, relevante Felder werden angezeigt
                    if mineField[box_x][box_y] == '[0]':
                        showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY)

                    # wenn Mine aufgedeckt wird, Minen anzeigen
                    if mineField[box_x][box_y] == '[X]':
                        showMines(revealedBoxes, mineField, box_x, box_y)
                        gameOverAnimation(mineField, revealedBoxes, markedMines, 'LOSS')
                        mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

        # prüfen, ob der Spieler gewonnen hat 
        if gameWon(revealedBoxes, mineField):
            gameOverAnimation(mineField, revealedBoxes, markedMines, 'WIN')
            mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()
            
        # Bildschirm neu zeichnen
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
def blankField():

   # erzeugt leere FIELDWIDTH x FIELDHEIGHT Datenstruktur

    field = []
    for x in range(FIELDWIDTH):
        field.append([]) 
        for y in range(FIELDHEIGHT):
            field[x].append('[ ]')
    return field

def placeMines(field): 

    # setzt Minen in die Datenstruktur FIELDWIDTH x FIELDHEIGHT
    # benötigt leeres Feld als Eingabe

    mineCount = 0
    xy = [] 
    while mineCount < MINESTOTAL: 
        x = random.randint(0,FIELDWIDTH-1)
        y = random.randint(0,FIELDHEIGHT-1)
        xy.append([x,y]) 
        if xy.count([x,y]) > 1: 
            xy.remove([x,y]) 
        else: 
            field[x][y] = '[X]' 
            mineCount += 1

def isThereMine(field, x, y): 

    # Überprüft, ob sich die Mine an einem bestimmten Feld befindet

    return field[x][y] == '[X]'  

def placeNumbers(field): 

    # setzt Zahlen in die Datenstruktur FIELDWIDTH x FIELDHEIGHT
    # benötigt Feld mit Minen als Eingabe

    for x in range(FIELDWIDTH):
        for y in range(FIELDHEIGHT):
            if not isThereMine(field, x, y):
                count = 0
                if x != 0: 
                    if isThereMine(field, x-1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x-1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x-1, y+1):
                            count += 1
                if x != FIELDWIDTH-1: 
                    if isThereMine(field, x+1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x+1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x+1, y+1):
                            count += 1
                if y != 0: 
                    if isThereMine(field, x, y-1):
                        count += 1
                if y != FIELDHEIGHT-1: 
                    if isThereMine(field, x, y+1):
                        count += 1
                field[x][y] = '[%s]' %(count)

def blankRevealedBoxData(val):

    # liefert FIELDWIDTH x FIELDHEIGHT Datenstruktur abweichend von der Felddatenstruktur

    revealedBoxes = []
    for i in range(FIELDWIDTH):
        revealedBoxes.append([val] * FIELDHEIGHT)
    return revealedBoxes

def gameSetup():

    # Minenfeld-Datenstruktur, Liste aller Nullen für Rekursion und aufgedeckte boolesche Datenstruktur einrichten

    mineField = blankField()
    placeMines(mineField)
    placeNumbers(mineField)
    zeroListXY = []
    markedMines = []
    revealedBoxes = blankRevealedBoxData(False)

    return mineField, zeroListXY, revealedBoxes, markedMines

def drawField():

    # zeichnet Feld und Reset-Taste

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_REV, (left, top, BOXSIZE, BOXSIZE))

    DISPLAYSURFACE.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURFACE.blit(SHOW_SURF, SHOW_RECT)

def drawMinesNumbers(field):
    
    # Feld sollte Minen und Zahlen haben

    half = int(BOXSIZE*0.5) 
    quarter = int(BOXSIZE*0.25)
    eighth = int(BOXSIZE*0.125)
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            center_x, center_y = getCenterXY(box_x, box_y)
            if field[box_x][box_y] == '[X]':
                pygame.draw.circle(DISPLAYSURFACE, MINECOLOR, (left+half, top+half), quarter)
                pygame.draw.circle(DISPLAYSURFACE, WHITE, (left+half, top+half), eighth)
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+eighth, top+half), (left+half+quarter+eighth, top+half))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+half, top+eighth), (left+half, top+half+quarter+eighth))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+quarter), (left+half+quarter, top+half+quarter))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+half+quarter), (left+half+quarter, top+quarter))
            else: 
                for i in range(1,9):
                    if field[box_x][box_y] == '[' + str(i) + ']':
                        if i in range(1,3):
                            textColor = TEXTCOLOR_1
                        else:
                            textColor = TEXTCOLOR_2
                        drawText(str(i), BASICFONT, textColor, DISPLAYSURFACE, center_x, center_y)

def showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY):

    # Ändert die Struktur der aufgedeckten Boxen, wenn box_x und box_y gleich [0] sind 
    # alle Boxen mit Rekursion anzeigen
    
    revealedBoxes[box_x][box_y] = True
    revealAdjacentBoxes(revealedBoxes, box_x, box_y)
    for i,j in getAdjacentBoxesXY(mineField, box_x, box_y):
        if mineField[i][j] == '[0]' and [i,j] not in zeroListXY:
            zeroListXY.append([i,j])
            showNumbers(revealedBoxes, mineField, i, j, zeroListXY)

def showMines(revealedBoxes, mineField, box_x, box_y): 

    # Ändert die Struktur der aufgedecktenBox-Daten, wenn die gewählte box_x & box_y gleich [X] ist 

    for i in range(FIELDWIDTH):
        for j in range(FIELDHEIGHT):
            if mineField[i][j] == '[X]':
                revealedBoxes[i][j] = True
    
def revealAdjacentBoxes(revealedBoxes, box_x, box_y):

    # ändert die Datenstruktur revealedBoxes so, dass alle benachbarten Boxen zu (box_x, box_y) auf True gesetzt werden

    if box_x != 0: 
        revealedBoxes[box_x-1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x-1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x-1][box_y+1] = True
    if box_x != FIELDWIDTH-1:
        revealedBoxes[box_x+1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x+1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x+1][box_y+1] = True
    if box_y != 0: 
        revealedBoxes[box_x][box_y-1] = True
    if box_y != FIELDHEIGHT-1: 
        revealedBoxes[box_x][box_y+1] = True

def getAdjacentBoxesXY(mineField, box_x, box_y):

    # Box-XY-Koordinaten für alle benachbarten Boxen zu (box_x, box_y) holen

    adjacentBoxesXY = []

    if box_x != 0:
        adjacentBoxesXY.append([box_x-1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x-1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x-1,box_y+1])
    if box_x != FIELDWIDTH-1: 
        adjacentBoxesXY.append([box_x+1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x+1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x+1,box_y+1])
    if box_y != 0:
        adjacentBoxesXY.append([box_x,box_y-1])
    if box_y != FIELDHEIGHT-1:
        adjacentBoxesXY.append([box_x,box_y+1])

    return adjacentBoxesXY
    
def drawCovers(revealedBoxes, markedMines):

    # verwendet die aufgedeckte Datenstruktur FIELDWIDTH x FIELDHEIGHT, um zu bestimmen, ob ein Kasten gezeichnet werden soll, der die Mine/Nummer bedeckt
    # rote Abdeckung statt grauer Abdeckung über markierte Minen zeichnen

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if not revealedBoxes[box_x][box_y]:
                left, top = getLeftTopXY(box_x, box_y)
                if [box_x, box_y] in markedMines:
                    pygame.draw.rect(DISPLAYSURFACE, MINEMARK_COV, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_COV, (left, top, BOXSIZE, BOXSIZE))

def drawText(text, font, color, surface, x, y):  

    # Funktion zum einfachen Zeichnen von Text und zur Rückgabe von Objekt & Rect-Paar

    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)

def drawButton(text, color, bgcolor, center_x, center_y):

    # ähnlich wie drawText, aber Text hat bg-Farbe und liefert obj & rect

    butSurf = BASICFONT.render(text, True, color, bgcolor)
    butRect = butSurf.get_rect()
    butRect.centerx = center_x
    butRect.centery = center_y

    return (butSurf, butRect)

def getLeftTopXY(box_x, box_y):

    # linke & obere Koordinaten für das Zeichnen von Minenboxen ermitteln

    left = XMARGIN + box_x*(BOXSIZE+GAPSIZE)
    top = YMARGIN + box_y*(BOXSIZE+GAPSIZE)
    return left, top

def getCenterXY(box_x, box_y):

    # Zentralkoordinaten für das Zeichnen von Minenkästen ermitteln

    center_x = XMARGIN + BOXSIZE/2 + box_x*(BOXSIZE+GAPSIZE)
    center_y = YMARGIN + BOXSIZE/2 + box_y*(BOXSIZE+GAPSIZE)
    return center_x, center_y

def getBoxAtPixel(x, y):

    # liefert die Koordinaten der Box an den Mauskoordinaten
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)

def highlightBox(box_x, box_y):

    # Box hervorheben, wenn die Maus über sie fährt
    
    left, top = getLeftTopXY(box_x, box_y)
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (left, top, BOXSIZE, BOXSIZE), 4)

def highlightButton(butRect):

    # Schaltfläche hervorheben, wenn die Maus über sie fährt

    linewidth = 4
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (butRect.left-linewidth, butRect.top-linewidth, butRect.width+2*linewidth, butRect.height+2*linewidth), linewidth)

def gameWon(revealedBoxes, mineField):

    # prüft, ob der Spieler alle Kästchen aufgedeckt hat

    notMineCount = 0

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if revealedBoxes[box_x][box_y] == True:
                if mineField[box_x][box_y] != '[X]':
                    notMineCount += 1

    if notMineCount >= (FIELDWIDTH*FIELDHEIGHT)-MINESTOTAL:
        return True
    else:
        return False

def gameOverAnimation(mineField, revealedBoxes, markedMines, result):

    # mlässt den Hintergrund rot (Verloren) oder blau (Sieg) blinken

    origSurf = DISPLAYSURFACE.copy()
    flashSurf = pygame.Surface(DISPLAYSURFACE.get_size())
    flashSurf = flashSurf.convert_alpha()
    animationSpeed = 20

    if result == 'WIN':
        r, g, b = BLUE
    else:
        r, g, b = RED

    for i in range(5):
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, animationSpeed*step): # animation loop
                checkForKeyPress()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURFACE.blit(origSurf, (0, 0))
                DISPLAYSURFACE.blit(flashSurf, (0, 0))
                pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
                drawField()
                drawMinesNumbers(mineField)
                tipFont = pygame.font.SysFont(FONTTYPE, 16) 
                drawText('Tip: Highlight a box and press space (rather than click the mouse)', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
                drawText('to mark areas that you think contain mines.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)
                RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
                SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)
                drawCovers(revealedBoxes, markedMines)
                pygame.display.update()
                FPSCLOCK.tick(FPS)
  
def terminate():

    # einfache Funktion zum Beenden des Spiels
    
    pygame.quit()
    sys.exit()

def checkForKeyPress():

    # prüfen, ob beenden oder eine andere Taste gedrückt wird
    
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
        
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

# Code ausführen
if __name__ == '__main__':
    main()