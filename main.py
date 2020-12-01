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
        self.know_vampus_position, self.know_gold_position = False, False

    def get_locations(self):
        """Get all neighbour cells."""
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
        """Perceive from nearby cells (feel vampus Stench, Breeze from hole or see Glitter from gold)."""
        locations = self.get_locations()
        hole, gold, vampus = False, False, False

        # Get info from nearby cells
        for location in locations:
            if location not in self.was_here:
                feel = self.world[location[0]][location[1]]

                if feel[0]: hole = True
                if feel[1] and not self.know_gold_position: gold = True
                if feel[2] and not self.know_vampus_position: vampus = True

        # Compare new info with knowledge base (KB) and print out thoughts
        for location in locations:
            if location not in self.was_here:
                if hole:
                    self.logic_map[location][0] = True
                    print(f'There is probably a hole in {location}')
                if gold:
                    if self.logic_map[location][1]:
                        self.know_gold_position = True
                        print(f'There is definitely gold in {location}')
                        self.clear_map(location, 1)
                    else:
                        self.logic_map[location][1] = True
                        print(f'There is probably a gold in {location}')
                if vampus:
                    if self.logic_map[location][2]:
                        self.know_vampus_position = True
                        print(f'Vampus is definately at {location}')
                        self.clear_map(location, 2)
                    else:
                        self.logic_map[location][2] = True
                        print(f'There is probably a vampus in {location}')

    def clear_map(self, location, item):
        """Clear logic map if vampus or gold found."""
        for i in range(4):
            for j in range(4):
                if (i, j) == location:
                    continue
                else:
                    self.logic_map[(i, j)][item] = 0

    def move(self):
        """Make step."""
        # Check if agent didn't fall in hole in cell he thought hole is
        if self.logic_map[(self.x, self.y)][0]:
            self.logic_map[(self.x, self.y)][0] = False
            print(f'There is no hole in {(self.x, self.y)}')

        locations = self.get_locations()
        for location in locations:
            if location not in self.was_here:
                self.route_queue.append(location)

        self.perceive()

        # Sort route queue according to gold, hole and vampus positions in KB
        self.route_queue.sort(key=lambda x: (-self.logic_map[(x[0], x[1])][1],
                                             self.logic_map[(x[0], x[1])][0],
                                             self.logic_map[(x[0], x[1])][2]), reverse=True)

        # Get best step and make it
        step = self.route_queue.pop()
        self.world[self.x][self.y][3] = False
        self.x, self.y = step
        self.world[self.x][self.y][3] = True
        self.was_here.add((self.x, self.y))


# Build gui app
class App(tk.Tk):
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
        # Parameters to check for results
        fall, killed, won = False, False, False
        # Redraw world
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

        # Check if agent in hole, vampus or gold cells
        for column in range(self.columns):
            for row in range(self.rows):
                if self.world[row][column][0] and self.world[row][column][3]:
                    fall = True
                if self.world[row][column][2] and self.world[row][column][3]:
                    killed = True
                if self.world[row][column][1] and self.world[row][column][3]:
                    won = True

        # Get result or keep moving
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
    """Generate world 4x4 with probability 0.2 of hole in cell, 1 vampus and 1 gold.
     Every cell is array in form [hole, gold, vampus, agent], where every value is bool.
     """
    world = []
    for row in range(4):
        r = []
        for column in range(4):
            if random.random() < 0.2:
                r.append([True, False, False, False])
            else:
                r.append([False, False, False, False])
        world.append(r)

    # Place gold in any cell except of agent start position
    gold_x, gold_y = 3, 0
    while gold_x == 3 and gold_y == 0:
        gold_x, gold_y = random.randint(0, 3), random.randint(0, 3)

    # Place vampus in any cell except of agent start position and gold position
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
