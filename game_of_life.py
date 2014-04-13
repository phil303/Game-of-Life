import time
import random
import sys

LIVE = "@"
DEAD = " "

CURSOR_UP_ONE = '\x1b[1A'
CR = '\x1b[2K'
ERASE_LINE = CURSOR_UP_ONE + CR + CURSOR_UP_ONE

class Cell(object):
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state
        self.next_state = None

    def neighbors(self, grid):
        # from top to bottom, left to right
        neighbors = []
        for y in (1, 0, -1):
            for x in (-1, 0, 1):
                if x == 0 and y == 0:
                    continue
                neighbors.append(grid.find_cell(self.x + x, self.y + y))
        return neighbors

    def set_next_state(self, grid):
        live_count = len([c for c in self.neighbors(grid) if c.state != DEAD])

        # a dead cell w/ 3 live neighbors becomes a live cell
        if self.state == DEAD and live_count == 3:
            self.next_state = LIVE

        elif self.state == LIVE:
            # live cell with less than 2 or more than 3 neighbors dies
            if live_count < 2 or live_count > 3:
                self.next_state = DEAD
            # live cell with 2-3 neighbors lives
            else:
                self.next_state = LIVE

        else:
            self.next_state = DEAD

    def __repr__(self):
        return self.state

class Grid(object):
    def __init__(self, length, height, life_ratio):
        self.length = length
        self.height = height

        self.board = []
        self.running_live_count = []

        self.randomize_state(life_ratio)

    def find_cell(self, x, y):
        x = x % self.length
        y = y % self.height
        return self.board[x][y]

    def randomize_state(self, starting_life_ratio):
        for x in range(self.length):
            self.board.append([None] * self.height)
            for y in range(self.height):
                if random.random() < starting_life_ratio:
                    self.board[x][y] = Cell(x, y, LIVE)
                else:
                    self.board[x][y] = Cell(x, y, DEAD)

    def render_state(self, generation):
        live_count = 0
        board = ""
        for row in self.board:
            string = ""
            for c in row:
                string += " %s " % c.state
                if c.state == LIVE:
                    live_count += 1
            board += "%s\n" % string

        # keep track of last 10 live counts
        if len(self.running_live_count) >= 10:
            self.running_live_count = self.running_live_count[1:]
        self.running_live_count.append(live_count)

        self.erase_previous_state()
        sys.stdout.write(board)
        if len(set(self.running_live_count)) == 1:
            print "live cells: %s / STATIC" % live_count
        else:
            print "Live cells: %s" % live_count
        print "Generation: %s" % generation
        sys.stdout.flush()

    def erase_previous_state(self):
        for i in range(self.height):
            print ERASE_LINE
        # for the live cell count and the generation lines
        print ERASE_LINE * 2

    def define_next_state(self):
        for x in range(self.length):
            for y in range(self.height):
                # set next state on cell, must be done after entire grid is
                # created
                self.board[x][y].set_next_state(self)
        for x in range(self.length):
            for y in range(self.height):
                self.board[x][y].state = self.board[x][y].next_state


class Game(object):
    def __init__(self, length, height, life_ratio):
        self.grid = Grid(length, height, life_ratio)
        self.run()

    def run(self):
        generation = 1
        try:
            while True:
                self.grid.render_state(generation)
                self.grid.define_next_state()
                generation += 1
                time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == '__main__':
    Game(30, 30, 0.4).run()
