import sys
import pygame
import pygame.freetype
import math

pygame.init()
pygame.mixer.init()
pygame.freetype.init()
myfont=pygame.freetype.SysFont(None,20)

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ludo se crack")

niveau = 1
font = pygame.font.Font("casse-brique/verdana.ttf", 30)
clock = pygame.time.Clock()
BLANC = (255,255,255)
NOIR = (0,0,0)
ROUGE = (255,0,0)
ORANGE = (255,127,0)
JAUNE = (255,255,0)
RAYON_BALLE = 10
XMIN, YMIN = 0, 0
XMAX, YMAX = width, height

class Balle:
    def vitesse_par_angle(self, angle):
        self.vx = self.vitesse * math.cos(math.radians(angle))
        self.vy = -self.vitesse * math.sin(math.radians(angle))

    def print_score(self):
        ascore = font.render(str(f"score: {self.score}"), 1, BLANC)
        avie = font.render(str(f"vie: {self.vie}"),1,BLANC)
        screen.blit(ascore, (2,4))
        screen.blit(avie,(width - 100,4))

    def __init__(self):
        self.x, self.y = (400,400)
        self.vitesse = 8
        self.vitesse_par_angle(60)
        self.score = 0
        self.sur_raquette = True
        self.vie = 3
        self.game_over = False

    def afficher(self):
        pygame.draw.rect(screen, BLANC,(int(self.x-RAYON_BALLE), int(self.y-RAYON_BALLE),2*RAYON_BALLE, 2*RAYON_BALLE), 0)

    def rebond_raquette(self, raquette):
        diff = raquette.x - self.x
        longueur_totale = raquette.longueur/2 + RAYON_BALLE
        angle = 90 + 80 * diff/longueur_totale
        self.vitesse_par_angle(angle)

    def deplacer(self, raquette):
        if self.sur_raquette:
            self.y = raquette.y - 2*RAYON_BALLE
            self.x = raquette.x
        else:
            self.x += self.vx
            self.y += self.vy
        if raquette.collision_balle(self) and self.vy > 0:
            self.rebond_raquette(raquette)
        if self.x + RAYON_BALLE > XMAX:
            self.vx = -self.vx
        if self.x - RAYON_BALLE < XMIN:
            self.vx = -self.vx
        if self.y + RAYON_BALLE > YMAX:
            self.vie -= 1
            self.sur_raquette = True                                                       #fin du jeu
        if self.y - RAYON_BALLE < YMIN:
            self.vy = -self.vy

class Raquette:
    def __init__(self):
        self.x = (XMIN+XMAX)/2
        self.y = YMAX - RAYON_BALLE
        self.longueur = 10*RAYON_BALLE

    def collision_balle(self, balle):
        vertical = abs(self.y - balle.y) < 2*RAYON_BALLE
        horizontal = abs(self.x - balle.x) < self.longueur/2 + RAYON_BALLE
        return vertical and horizontal

    def afficher(self):
        pygame.draw.rect(screen, BLANC,(int(self.x-self.longueur/2),int(self.y-RAYON_BALLE),self.longueur, 2*RAYON_BALLE), 0)

    def deplacer(self, x):
        if x - self.longueur/2 < XMIN:
            self.x = XMIN + self.longueur/2
        elif x + self.longueur/2 > XMAX:
            self.x = XMAX - self.longueur/2
        else:
            self.x = x

class Brique:
    def __init__(self, x, y,vie):
        self.x = x
        self.y = y
        self.vie = vie
        self.longueur = 5 * RAYON_BALLE
        self.largeur = 3 * RAYON_BALLE

    def en_vie (self):
        return self.vie > 0

    def afficher(self):
        if self.vie == 1:
            pygame.draw.rect(screen,BLANC, (int(self.x-self.longueur/2), int(self.y-self.largeur/2), self.longueur, self.largeur), 0)
        elif self.vie == 2:
            pygame.draw.rect(screen,JAUNE, (int(self.x-self.longueur/2), int(self.y-self.largeur/2), self.longueur, self.largeur), 0)
        elif self.vie == 3:
            pygame.draw.rect(screen,ORANGE, (int(self.x-self.longueur/2), int(self.y-self.largeur/2), self.longueur, self.largeur), 0)
        elif self.vie == 4:
            pygame.draw.rect(screen,ROUGE, (int(self.x-self.longueur/2), int(self.y-self.largeur/2), self.longueur, self.largeur), 0)

    def collision_balle(self, balle):
        marge = self.largeur/2 + RAYON_BALLE
        dy = balle.y - self.y
        touche = False
        if balle.x >= self.x:
            dx = balle.x - (self.x + self.longueur/2 - self.largeur/2)
            if abs(dy) <= marge and dx <= marge:
                touche = True
                if dx <= abs(dy):
                    balle.vy = -balle.vy
                else :
                    balle.vx = -balle.vx
        else:
            dx = balle.x - (self.x - self.longueur/2 + self.largeur/2)
            if abs(dy) <= marge and -dx <= marge:
                touche = True
                if -dx <= abs(dy):
                    balle.vy = -balle.vy
                else:
                    balle.vx = -balle.vx
        if touche:
            self.vie -= 1
            if self.vie == 0:
                balle.score += 1
                casse = pygame.mixer.Sound('casse-brique/brique.wav')
                casse.play()
        return touche

class Jeu:
    def __init__(self):
        self.balle = Balle()
        self.raquette = Raquette()
        self.brique = []
        if niveau == 2:
            for y in range(13):
                self.brique.extend([Brique(((y*50)+100),250,4)])
            for  y in range(11):
                self.brique.extend([Brique(((y*50)+150),220,3),Brique(((y*50)+150),280,3)])
            for  y in range(9):
                self.brique.extend([Brique(((y*50)+200),190,2),Brique(((y*50)+200),310,2)])
            for  y in range(7):
                self.brique.extend([Brique(((y*50)+250),160,1),Brique(((y*50)+250),340,1)])
            self.brique.extend([Brique(700,130,4),Brique(700,100,4),Brique(700,70,4),Brique(650,100,4),Brique(750,100,4),Brique(400,100,4)])
            self.brique.extend([Brique(100,130,4),Brique(100,100,4),Brique(100,70,4),Brique(50,100,4),Brique(150,100,4)])
        else:
            for y in range(13):
                self.brique.extend([Brique(((y*50)+100),70,3)])
                self.brique.extend([Brique(((y*50)+100),100,3)])
                self.brique.extend([Brique(((y*50)+100),130,2)])
                self.brique.extend([Brique(((y*50)+100),160,2)])
                self.brique.extend([Brique(((y*50)+100),190,1)])
                self.brique.extend([Brique(((y*50)+100),220,1)])
        
    def gestion_evenements (self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.balle.sur_raquette:
                            self.balle.sur_raquette = False
                            self.balle.vitesse_par_angle(60)

    def mise_a_jour(self):
        x,y = pygame.mouse.get_pos()
        self.balle.deplacer(self.raquette)
        for i in self.brique:
            if i.en_vie():
                i.collision_balle(self.balle)
        self.raquette.deplacer(x)

    def affichage(self):
        screen.fill(NOIR)
        self.balle.afficher()
        self.raquette.afficher()
        for i in self.brique:
            if i.en_vie():
                i.afficher()
        self.balle.print_score()

jeu = Jeu()
menu = True
while menu:
    screen.fill(NOIR)
    bvn = font.render(str("bienvenu sur le jeux de casse brique"), 1, BLANC)
    clicker = font.render(str("clicker pour jouer"), 1, BLANC)
    screen.blit(bvn, (70,height/2 - 50))
    screen.blit(clicker, (250,height/2 + 50))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                menu = False
    pygame.display.flip()
    clock.tick(60)
while True:
    
    if jeu.balle.vie == 0:
    # game over 
        screen.fill(NOIR)
        fin = font.render(str("Gamme over !!"), 1, BLANC)
        screen.blit(fin, (250,height/2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    jeu = Jeu()
    elif jeu.balle.score == 78:
        screen.fill(NOIR)
        fin = font.render(str("et c'est ganniez"), 1, BLANC)
        clicker = font.render(str("clicker pour jouer"), 1, BLANC)
        screen.blit(clicker, (250,height/2 + 50))
        screen.blit(fin, (250,height/2 - 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    niveau += 1
                    jeu = Jeu()
    else:
    # le jeu
        jeu.gestion_evenements()
        jeu.mise_a_jour()
        jeu.affichage()
    pygame.display.flip()
    clock.tick(60)