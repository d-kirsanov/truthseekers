import os

os.environ["SDL_VIDEO_WINDOW_POS"] = "80,20"


import pgzrun
import random
from datetime import datetime
import math

WIDTH = 1600
HEIGHT = 1200

population = 500
longevity = 200

generation = 0

iq_inheritability = 0.6
iq_to_fertility = -5
iq_bonus = 0

culture_dissemination_rate = 0.005 
culture_dissemination_rate_per_iq = 10  
culture_dissemination_radius = 50  # then suddenly up

avg_breeding_iq_sum = 0
avg_breeding_iq_n = 0

alphabet = ['A', 'B', 'C', 'D']
truth = [random.choice(alphabet) for _ in range(300)]

culture_discovery_rate = 0.001
culture_discovery_rate_per_iq = 10
culture_error_rate = 0.1
culture_error_rate_per_iq = -10

filename = datetime.now().strftime("%Y-%m-%d=%H=%M=%S.csv")
fo = open(filename, "a")
fo.write(f"gen,pop,iq,iq_b,truth,error\n")
fo.close()

class human:
    def __init__(self):
        self.pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.longevity = longevity
        self.age = 0
        self.parents = None
        self.iq = random.gauss(1, 0.15)
        self.culture = ""
        self.speaking = 0

    def fertility(self):
        return 0.02 * (1 + (self.iq - 1) * iq_to_fertility)

    def inherit(self, f, m):
        global avg_breeding_iq_sum, avg_breeding_iq_n
        self.parents = (f, m)
        parents_iq = (f.iq + m.iq) / 2
        self.iq = random.gauss(
            1 - iq_inheritability + iq_inheritability * parents_iq + iq_bonus, 0.15
        )
        #print(f"parents are {parents_iq}, me {self.iq}")
        avg_breeding_iq_sum += parents_iq
        avg_breeding_iq_n += 1

    def discover_truth(self):
        p = culture_discovery_rate * (1 + (self.iq - 1) * culture_discovery_rate_per_iq)
        if random.random() < p:
            new = truth[len(self.culture)]
            self.hear_truth(self.culture + new)

    def hear_truth(self, new):
        if len(new) <= len(self.culture):
            return
        error_p = culture_error_rate * (1 + (self.iq - 1) * culture_error_rate_per_iq)
        if random.random() < error_p:
            self.culture += random.choice(alphabet)
        else:
            self.culture += new[len(self.culture)]

    def spread_culture(self):
        p = culture_dissemination_rate * (1 + (self.iq - 1) * culture_dissemination_rate_per_iq)
        if self.culture != "" and random.random() < p:
            self.speaking = 10
            for h in all:
                if self.dist(h) < culture_dissemination_radius:
                    h.hear_truth(self.culture)

    def step(self):
        self.age += 1
        if self.age >= self.longevity:
            self.die()
        self.discover_truth()
        self.spread_culture()

    def die(self):
        all.remove(self)

    def r(self):
        return 4

    def color(self):
        g = int(255 * (1 - (self.longevity - self.age) / self.longevity))
        return (g, g, g)

    def draw(self):
        screen.draw.filled_circle(self.pos, self.r(), self.color())

        if self.speaking > 0:
            screen.draw.circle(self.pos, culture_dissemination_radius, color="green")
            self.speaking -= 1

        if self.age < 5 and self.parents != None:
            screen.draw.line(self.pos, self.parents[0].pos, (0, 0, 255))
            screen.draw.line(self.pos, self.parents[1].pos, (0, 0, 255))

        for i, c in enumerate(self.culture):  # comment this out if it runs too slow
            screen.draw.text(
            c,
            (self.pos[0] + i * 7, self.pos[1]),
            fontsize=12,
            color="black" if c == truth[i] else "red",
            )


    def dist(self, other):
        return math.sqrt(
            (self.pos[0] - other.pos[0]) ** 2 + (self.pos[1] - other.pos[1]) ** 2
        )


all = [human() for i in range(int(population / 2))]


def find_closest(child):
    hs = sorted(all, key=lambda x: x.dist(child))
    return hs[0], hs[1]


def try_birth():
    h = human()
    f, m = find_closest(h)
    if random.random() < f.fertility() + m.fertility():
        h.inherit(f, m)
        return h
    else:
        return None


def draw():
    global generation
    generation += 1

    screen.fill((255, 255, 255))
    
    for h in all:
        h.draw()

    screen.draw.text(
        f"{generation}",
        (20, HEIGHT - 50),
        fontsize=25,
        color="blue",
    )
    screen.draw.text(
        f"n {len(all)}",
        (100, HEIGHT - 50),
        fontsize=25,
        color="blue",
    )
    iq_avg = 100*sum([h.iq for h in all])/len(all)
    screen.draw.text(
        f"iq {iq_avg:.1f}",
        (200, HEIGHT - 50),
        fontsize=25,
        color="blue",
    )
    iq_breeding_avg = 100*avg_breeding_iq_sum/avg_breeding_iq_n
    screen.draw.text(
        f"breeding iq {iq_breeding_avg:.1f}",
        (300, HEIGHT - 50),
        fontsize=25,
        color="blue",
    )

    total_culture = sum([len(x.culture) for x in all])
    total_errors = sum([sum([1 if c != truth[i] else 0 for i, c in enumerate(x.culture)]) for x in all])
    if total_culture != 0:

        screen.draw.text(
            f"culture {total_culture} errors {total_errors / total_culture:.2f}",
            (450, HEIGHT - 50),
            fontsize=25,
            color="blue",
        )

        with open(filename, "a") as fo:
            fo.write(f"{generation},{len(all)},{iq_avg:.1f},{iq_breeding_avg:.1f},{total_culture},{total_errors / total_culture:.3f}\n")


def update():

    for h in all:
        h.step()

    for i in range(population - len(all)):
        h = try_birth()
        if h != None:
            all.append(h)

    global culture_dissemination_radius, iq_bonus, longevity
    
    if generation == 10000:
        culture_dissemination_radius += 200

    if generation == 20000:
        iq_bonus += 0.1

    if generation == 30000:
        longevity += 100



pgzrun.go()
