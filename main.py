import time
from random import randint, uniform
import pygame
from math import sin, cos, atan2, sqrt

pygame.init()

WIDTH, HEIGHT = 900, 900
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("coca cola pepsi amogh anna seksi ")
WHITE=(255,255,255)
SPACE=(15,15,15)
YELLOW = (255, 255, 0)
BLUE = (0,0,255)


spectrum = [['M', 0.45, (255, 204,111)],
            ['K', 0.8, (254, 210, 160)], 
            ['G', 1.04, (254, 245, 234)], 
            ['F', 1.4, (248, 247, 255)], 
            ['A', 2.1, (202, 215, 255)], 
            ['B', 16, (170, 191, 255)],
            ['O', 100, (155, 177, 254)]] # MKGFABO - [[solar masses Mo, rgb()]....]

Mo = 1.98892*10**30 # Solar mass
Mr = 6.9634*10**8 # Solar radius


massmultiplier = 0.1
dm = massmultiplier
radiusmultiplier = 0.1
dr = radiusmultiplier
wallcollisions = False

zoom = 250
timescale = 10
panx, pany = 0,0

HEADINGFONT = pygame.font.SysFont("monospace", 18)
SUBTEXTFONT = pygame.font.SysFont("monospace", int(14*zoom/250))
class Planet:
    UNIT = 1.496e9
    G = 6.67e-11
    SCALE = zoom/UNIT
    TIME = 10
    def __init__(self, x, y, radius, mass, color, sun = False, orbit = True):
        self.x = x
        self.y = y
        self.sun = sun
        self.mass = mass
        self.color = color
        self.sclass = None
        self.radius = radius*self.SCALE
        self.velx = 0
        self.vely = 0
        self.name = ''
        self.orbit = []
        self.orbitbool = orbit
        if self.sun:
            for sequence in range(len(spectrum)):
                solar_mass_range = spectrum[sequence][1]
                if round(self.mass/Mo, 3) <= solar_mass_range:
                    self.color = spectrum[sequence][2]
                    self.sclass = spectrum[sequence][0]
                    break
                else:
                    continue

    @classmethod
    def change_scale(cls,zoom):
        cls.SCALE = zoom/cls.UNIT
    @classmethod
    def change_time(cls, time):
        cls.TIME = time
    def draw(self, window):
        x = self.x * self.SCALE + WIDTH/2
        y = self.y * self.SCALE + HEIGHT/2
        if self.name != 'blackhole':
            pygame.draw.circle(window, WHITE, (x, y), self.radius+1)
            pygame.draw.circle(window, self.color, (x, y), self.radius)



        if self.sun:
            typeinfo = []
            class_ = str(self.sclass)
            match class_:
                case 'M':
                    typeinfo = ["Red dwarf", "Tk: 2000-5200K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'K':
                    typeinfo = ["Orange dwarf", "Tk: 3900-5300K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'G':
                    typeinfo = ["Yellow dwarf", "Tk: 5300-6000K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'F':
                    typeinfo = ["Yellow-white dwarf", "Tk: 6000-7600K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'A':
                    typeinfo = ["White dwarf", "Tk: 7600-100000", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'B':
                    typeinfo = ["Blue-white giant", "Tk: 10000-30000K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'O':
                    typeinfo = ["Blue supergiant", "Tk: 30000-50000K", f"Mo: {round(self.mass/Mo, 7)}"]
                case 'U':
                    typeinfo = ["-unidentified-", "-","-"]
            typetext = SUBTEXTFONT.render(f"{typeinfo[0]}", 1, (200,200,200))
            temptext = SUBTEXTFONT.render(f"{typeinfo[1]}", 1, (200,200,200))
            masstext = SUBTEXTFONT.render(f"{typeinfo[2]}", 1, (200,200,200))
            veltext = SUBTEXTFONT.render(f"{round(self.x * self.SCALE + WIDTH/2)},{round(self.y * self.SCALE + HEIGHT/2)}", 1, (200,200,200))
            window.blit(typetext, (x - typetext.get_width()/2, y - typetext.get_height()/2 + (self.radius) + 20))
            window.blit(temptext, (x - typetext.get_width()/2, y - typetext.get_height()/2 + (self.radius) + 35))
            window.blit(masstext, (x - typetext.get_width()/2, y - typetext.get_height()/2 + (self.radius) + 50))
            window.blit(veltext, (x - typetext.get_width()/2, y - typetext.get_height()/2 + (self.radius) + 65))

            if self.name == 'blackhole':
                self.mass = 10e4*Mo
                self.sclass = 'U'
                pygame.draw.circle(window, (255, 204, 111), (x, y), Mr * self.SCALE * 0.5 + 2)
                pygame.draw.circle(window, (254, 147, 22), (x, y), Mr * self.SCALE * 0.5 + 1)
                pygame.draw.circle(window, (0, 0, 0), (x, y), Mr * self.SCALE * 0.5)



        else:
            if self.name != '':
                nametext = SUBTEXTFONT.render(f"{self.name}", 1, (200,200,200))
                window.blit(nametext, (x - nametext.get_width()/2, y - nametext.get_height()/2 + (self.radius) + 5))

        if len(self.orbit) > 2 and not self.sun:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(WINDOW, self.color, False, updated_points, 1)
    def force(self, planet):
        px, py = planet.x, planet.y
        dx = px - self.x
        dy = py - self.y
        d = sqrt(dx**2 + dy**2)
        force = self.G * self.mass * planet.mass / d**2
        theta = atan2(dy,dx)

        fx = cos(theta) * force
        fy = sin(theta) * force
        return fx, fy

    def update(self, planets):
        
        fxt = fyt = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.force(planet)
            fxt += fx
            fyt += fy

        
        self.velx += fxt/self.mass * self.TIME
        self.vely += fyt/self.mass * self.TIME

        self.x += self.velx * self.TIME
        self.y += self.vely * self.TIME
        self.orbit.append((self.x, self.y))
    def collision(self, other):

        collided = int(sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)) <= (self.radius + other.radius)*2e6
        return collided

def create_on_click(mousepos, defrad):
    mx, my = mousepos
    mx = round((((mx/WIDTH)/0.5)-1)*1.75, 3)
    my = round((((my/WIDTH)/0.5)-1)*1.75, 3)
    RANDOM = (randint(0,255),randint(0,255),randint(0,255))
    p = Planet(mx*Planet.UNIT,my*Planet.UNIT,Mr*radiusmultiplier,Mo*massmultiplier,RANDOM)
    return p

def collisions(planets):
    for i in planets:
        for j in planets:
            if i!= j:
                if i.collision(j):
                    if i.mass >= j.mass:
                        planets.remove(j)
                    else:
                        planets.remove(i)
def slingshot(location, mousepos, sun = True):
    x, y = location
    mx1, my1 = mousepos
    mx = (mx1-WIDTH/2)/Planet.SCALE
    my = (my1-HEIGHT/2)/Planet.SCALE

    print(mx1, my1, mx, my)

    vx = (mx1-x)/5*-1*10e3
    vy = (my1-y)/5*-1*10e3

    p = Planet(mx,my,Mr*radiusmultiplier,Mo*massmultiplier,WHITE, sun)
    p.velx = vx
    p.vely = vy
    return p

#TODO-zoom
def solar_system(planets):
    sun = Planet(0*Planet.UNIT,0,Mr*0.5,Mo,YELLOW, True)

    mercury = Planet((0.387 * Planet.UNIT), 0, 0.03*Mr, 3.30 * 10 ** 23, (54, 98, 165))
    mercury.vely = -4.74e5
    mercury.name = 'mercury'

    venus = Planet((0.723 * Planet.UNIT), 0, 0.08*Mr, 4.8685 * 10 ** 24, (202,96,35))
    venus.vely = -3.502e5
    venus.name = 'venus'

    earth = Planet((1*Planet.UNIT),0,0.05*Mr,5.97219*10**26,(35,79,202))
    earth.vely = 2.9783e5
    earth.name = 'earth'

    mars = Planet((1.524 * Planet.UNIT), 0, 0.04*Mr, 6.39 * 10 ** 23, (149,83,59))
    mars.vely = 2.407e5
    mars.name = 'mars'

    jupiter = Planet((5.2 * Planet.UNIT), 0, 0.09*Mr, 1898 * 10 ** 24, (198,153,136))
    jupiter.vely = 1.307e5
    jupiter.name = 'jupiter'

    saturn = Planet((9.5 * Planet.UNIT), 0, 0.08*Mr, 568 * 10 ** 24, (198,179,136))
    saturn.vely = 0.967e5
    saturn.name = 'saturn'

    uranus = Planet((19.22 * Planet.UNIT), 0, 0.035*Mr, 86.8 * 10 ** 24, (34,121,171))
    uranus.vely = 0.679e5
    uranus.name = 'uranus'

    planets.extend([sun, mercury, venus, earth, mars, jupiter, saturn, uranus])
def main():
    run = True
    clock = pygame.time.Clock()


    planets = []


    global dr,dm,massmultiplier, radiusmultiplier, WIDTH, HEIGHT, zoom, panx, pany, wallcollisions, timescale
    label2 = HEADINGFONT.render(f"Scroll to change radius, Drag and click to slingshot", 1, WHITE)
    label3 = HEADINGFONT.render(f"UP/DOWN to increment radius/mass", 1, WHITE)
    label4 = HEADINGFONT.render(f"S to spawn solar system", 1, WHITE)
    label5 = HEADINGFONT.render(f"C to clear space", 1, WHITE)
    label6 = HEADINGFONT.render(f"B to spawn black hole", 1, WHITE)
    label7 = HEADINGFONT.render(f"T to enable wall collisions", 1, WHITE)
    label8 = HEADINGFONT.render(f"Right/Left to change time scale", 1, WHITE)


    temploc = None


    while run:
        clock.tick(60)


        mouse_pos = pygame.mouse.get_pos()
        WIDTH, HEIGHT = WINDOW.get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if temploc:
                        # planets.append(create_on_click(mouse_pos, defaultradius))
                        planets.append(slingshot(temploc, mouse_pos, True))
                        temploc = None
                    else:
                        temploc = mouse_pos

                elif event.button == 2:
                    pan_start = pygame.mouse.get_pos()

                elif event.button == 4: # scroll up
                    massmultiplier = dm if massmultiplier <dm else round(massmultiplier+dm, 4)
                    radiusmultiplier = dr if radiusmultiplier < dm < dr else round(radiusmultiplier+dr, 4)

                elif event.button == 5: # scroll down
                    massmultiplier = dm if massmultiplier <dm else round(massmultiplier-dm, len(str(dm)))
                    radiusmultiplier = dr if radiusmultiplier < dm else round(radiusmultiplier-dr, len(str(dm)))




            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    dm /=10
                    dr /=10
                elif event.key == pygame.K_UP:
                    dm =dm*10
                    dr =dr*10
                    print(dm)
                elif event.key == pygame.K_s:
                    solar_system(planets)
                elif event.key == pygame.K_c:
                    planets.clear()
                elif event.key == pygame.K_EQUALS:
                    zoom += 50
                    Planet.change_scale(zoom)
                elif event.key == pygame.K_MINUS:
                    zoom -= 50
                    Planet.change_scale(zoom)
                elif event.key == pygame.K_b:
                    bh = Planet(0, 0, Mr, Mo, WHITE, True)
                    bh.name = 'blackhole'
                    WINDOW.fill((150,150,150))
                    pygame.display.flip()
                    time.sleep(0.01)
                    planets.append(bh)

                elif event.key == pygame.K_t:
                    wallcollisions = not wallcollisions

                elif event.key == pygame.K_RIGHT:
                    timescale += 10
                    Planet.change_time(timescale)

                elif event.key == pygame.K_LEFT:
                    timescale -= 10
                    Planet.change_time(timescale)
        # WINDOW.fill((0,0,0))
        WINDOW.fill(SPACE)



        massmultiplier = dm if massmultiplier == 0 else massmultiplier
        radiusmultiplier = dr if radiusmultiplier == 0 else radiusmultiplier


        label = HEADINGFONT.render(f"Solar Mass:{round(massmultiplier, 5)}, Radius:{radiusmultiplier}, Increment:{dm}, Wall collisions: {wallcollisions}, zoom: {zoom}, time: {timescale}", 1, WHITE)
        WINDOW.blit(label, (WIDTH // 2 - label.get_width() / 2, 0))
        WINDOW.blit(label2, (WIDTH // 2 - label2.get_width() / 2, 20))
        WINDOW.blit(label3, (WIDTH // 2 - label3.get_width() / 2, 40))
        WINDOW.blit(label4, (WIDTH // 2 - label4.get_width() / 2, 60))
        WINDOW.blit(label5, (WIDTH // 2 - label5.get_width() / 2, 80))
        WINDOW.blit(label6, (WIDTH // 2 - label6.get_width() / 2, 100))
        WINDOW.blit(label7, (WIDTH // 2 - label7.get_width() / 2, 120))
        WINDOW.blit(label8, (WIDTH // 2 - label8.get_width() / 2, 140))

        if temploc:
            pygame.draw.line(WINDOW, WHITE, temploc, mouse_pos, 2)

        collisions(planets)

        for planet in planets[:]:
            planet.update(planets)

            planet.draw(WINDOW)
            off_screen = planet.x*planet.SCALE < -WIDTH/2 or planet.y*planet.SCALE < -HEIGHT/2 or planet.x*planet.SCALE > WIDTH/2 or planet.y*planet.SCALE > HEIGHT/2
            if off_screen:
                if wallcollisions:
                    planet.velx *= -1
                    planet.vely *= -1
                    off_screen = False
                else:
                    planets.remove(planet)
                    print('removed')




        pygame.display.flip()
    pygame.quit()

main()
