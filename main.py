# work with world instance (probably it is copied to Agent class)

import tkinter as tk
import random


class Agent:
    def __init__(self, world):
        self.x = 3
        self.y = 0
        self.world = world
        self.logic_map = {(x, y): [False, False, False] for x in range(4) for y in range(4)}
        self.route_queue = []
        self.was_here = {(3, 0)}

    def get_locations(self):
        locations = []
        if self.x > 0:
            locations.append((self.x - 1, self.y))
        if self.x < 3:
            locations.append((self.x + 1, self.y))
        if self.y > 0:
            locations.append((self.x, self.y - 1))
        if self.y < 3:
            locations.append((self.x, self.y + 1))
        return {location: [False, False, False] for location in locations}

    def perceive(self):
        locations = self.get_locations()
        hole, gold, vampus = False, False, False
        for location in locations:
            if location not in self.was_here:
                curr = self.logic_map[location]
                feel = self.world[location[0]][location[1]]
                new = [curr[num] or feel[num] for num in range(3)]
                if new[0]:
                    print(f'There is probably a hole in {location}')
                if new[2]:
                    print(f'There is probably a vampus in {location}')
                self.logic_map[location] = new
                # hole = True if feel[0] else False
                # gold = True if feel[1] else False
                # vampus = True if feel[2] else False

        # for location in locations:
        #     self.logic_map[location][0] = hole
        #     self.logic_map[location][0] = gold
        #     self.logic_map[location][0] = vampus


    def move(self):
        locations = self.get_locations()
        for location in locations:
            if location not in self.was_here:
                self.route_queue.append(location)

        self.perceive()

        self.route_queue.sort(key=lambda x: (-self.logic_map[(x[0], x[1])][1],
                                             self.logic_map[(x[0], x[1])][0],
                                             self.logic_map[(x[0], x[1])][2]), reverse=True)

        step = self.route_queue.pop()
        self.world[self.x][self.y][3] = False
        self.x, self.y = step
        self.world[self.x][self.y][3] = True
        self.was_here.add((self.x, self.y))


class App(tk.Tk):  # build the grid
    def __init__(self, world, agent, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.canvas = tk.Canvas(self, width=600, height=600, borderwidth=0, highlightthickness=0)
        self.world = world
        self.agent = agent
        self.canvas.pack(side="top", fill="both", expand="true")
        self.rows = 4
        self.columns = 4
        self.cellwidth = 150
        self.cellheight = 150
        self.rect = {}
        self.oval = {}

        self.redraw(1000)

    def redraw(self, delay):
        fall, killed, won = False, False, False
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column * self.cellwidth
                y1 = row * self.cellwidth
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row, column] = self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", tags="rect")
                if self.world[row][column][0]:
                    self.rect[row, column] = self.canvas.create_oval(x1, y1, x2, y2, fill="black")
                if self.world[row][column][1]:
                    self.rect[row, column] = self.canvas.create_oval(x1 + 25, y1 + 25, x2 - 25, y2 - 25, fill='yellow')
                if self.world[row][column][2]:
                    self.rect[row, column] = self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill='green')
                if self.world[row][column][3]:
                    self.rect[row, column] = self.canvas.create_oval(x1 + 20, y1 + 20, x2 - 20, y2 - 20, fill='red')

        for column in range(self.columns):
            for row in range(self.rows):
                if self.world[row][column][0] and self.world[row][column][3]:
                    fall = True
                if self.world[row][column][2] and self.world[row][column][3]:
                    killed = True
                if self.world[row][column][1] and self.world[row][column][3]:
                    won = True

        if fall:
            print('agent fell in hole!')
        elif killed:
            print('agent killed by vampus!')
        elif won:
            print('agent found gold!')
        else:
            self.agent.move()
            self.after(delay, lambda: self.redraw(delay))


def generate_world():
    # [hole, gold, vampus, agent]
    world = []
    for row in range(4):
        r = []
        for column in range(4):
            if random.random() < 0.2:
                r.append([True, False, False, False])
            else:
                r.append([False, False, False, False])
        world.append(r)

    gold_x, gold_y = 3, 0
    while gold_x == 3 and gold_y == 0:
        gold_x, gold_y = random.randint(0, 3), random.randint(0, 3)

    vamp_x, vamp_y = 3, 0
    while vamp_x == 3 and vamp_y == 0 or (vamp_x, vamp_y) == (gold_x, gold_y):
        vamp_x, vamp_y = random.randint(0, 3), random.randint(0, 3)

    world[gold_x][gold_y][1] = True
    world[vamp_x][vamp_y][2] = True
    world[3][0][0] = False
    world[3][0][3] = True

    return world


if __name__ == '__main__':
    WORLD = generate_world()
    AGENT = Agent(WORLD)
    app = App(WORLD, AGENT)
    app.mainloop()
