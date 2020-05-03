#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python version >= 3.8
# usage: $ python maze.py mazefile.maze
# ============================================================================ #
import sys
import numpy as np


class Maze:
    """
    a maze class includes wall data, start indexes, goal indexes
    """
    # constants
    East, North, West, South = range(4)

    def __init__(self, size=32):
        """
        construct a maze object with a maze size
        """
        self.size = size  # number of cells on one side of the maze
        # the number of cells in the maze
        self.cell_index_size = size * size
        # the number of walls to save: x * y * z
        self.wall_index_size = size * size * 2
        # wall data
        self.walls = np.zeros(self.wall_index_size, dtype=bool)  # wall flags
        self.knowns = np.zeros(self.wall_index_size, dtype=bool)  # wall flags
        # start and goal cells
        self.start = []
        self.goals = []

    @staticmethod
    def parse(file):
        """
        parse maze string and construct a maze object
        """
        lines = file.readlines()
        maze = Maze(len(lines)//2)  # get maze size
        for i, line in enumerate(reversed(lines)):
            # skip if comment line
            if line.startswith('#'):
                continue
            line = line.rstrip()  # remove \n
            # +---+---+
            if i % 2 == 0:
                for j, c in enumerate(line[2:: 4]):
                    if c == '-':
                        maze.wall(j, i//2, Maze.South, True, new_known=True)
                    elif c == ' ':
                        maze.wall(j, i//2, Maze.South, False, new_known=True)
            # |   |   |
            else:
                for j, c in enumerate(line[0:: 4]):
                    if c == '|':
                        maze.wall(j, i//2, Maze.West, True, new_known=True)
                    elif c == ' ':
                        maze.wall(j, i//2, Maze.West, False, new_known=True)
                for j, c in enumerate(line[2:: 4]):
                    if c == 'S':
                        maze.start.append([j, i//2])
                    if c == 'G':
                        maze.goals.append([j, i//2])
        return maze

    @classmethod
    def uniquify(cls, x, y, d):
        """
        returns a unique coordinates of a wall without redundancy on both sides of the wall
        """
        if d == cls.East:
            x, y, z, d = x, y, 0, cls.East
        elif d == cls.North:
            x, y, z, d = x, y, 1, cls.North
        elif d == cls.West:
            x, y, z, d = x-1, y, 0, cls.East
        elif d == cls.South:
            x, y, z, d = x, y-1, 1, cls.North
        return x, y, z, d

    def get_index(self, x, y, z=None):
        """
        get a unique id of a wall or cell inside of the maze
        """
        if z == None:
            # cell
            if not self.is_inside_of_field(x, y):
                raise ValueError("out of field!")
            return y * self.size + x
        else:
            # wall
            if not self.is_inside_of_field(x, y, z):
                raise ValueError("out of field!")
            return z * self.size * self.size + y * self.size + x

    def is_inside_of_field(self, x, y, z=None):
        """
        determine if the wall or cell is inside of the field
        """
        s = self.size
        if z == None:
            # cell
            return x >= 0 and y >= 0 and x < s and y < s
        else:
            # wall
            return x >= 0 and y >= 0 and x < s+z-1 and y < s-z

    def wall(self, x, y, d, new_state=None, new_known=None):
        """
        get wall or update wall, and optionally update known flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        if not self.is_inside_of_field(x, y, z):
            return True
        i = self.get_index(x, y, z)
        if new_state != None:
            self.walls[i] = new_state
        if new_known != None:
            self.knowns[i] = new_known
        return self.walls[i]

    def known(self, x, y, d, update=None):
        """
        get or update if the wall is known
        """
        x, y, z, d = self.uniquify(x, y, d)
        if not self.is_inside_of_field(x, y, z):
            return True
        i = self.get_index(x, y, z)
        if update != None:
            self.knowns[i] = update
        return self.knowns[i]

    def __str__(self):
        """
        show information of the maze
        """
        return f'size: {self.size}x{self.size}' + '\n' + \
            'start: ' + ', '.join([f'({x}, {y})' for x, y in self.start]) + '\n' + \
            'goals: ' + ', '.join([f'({x}, {y})' for x, y in self.goals])

    def generate_maze_string(self):
        """
        generate a string to be saved in text format
        """
        res = ''
        for y in reversed(range(-1, self.size)):
            # +---+---+
            res += '+'
            for x in range(self.size):
                d = Maze.North
                if not self.known(x, y, d):
                    res += ' . '
                elif self.wall(x, y, d):
                    res += '---'
                else:
                    res += '   '
                res += '+'
            res += '\n'
            # |   |   |
            if y == -1:
                break
            res += '|'
            for x in range(self.size):
                if [x, y] in self.start:
                    res += ' S '
                elif [x, y] in self.goals:
                    res += ' G '
                else:
                    res += '   '
                d = Maze.East
                if not self.known(x, y, d):
                    res += '.'
                elif self.wall(x, y, d):
                    res += '|'
                else:
                    res += ' '
            res += '\n'
        return res

    def get_cost_map(self, roots=None):
        """
        calculate cost map of cells using breadth first search
        """
        roots = roots if roots else self.goals
        # initialize
        cost_map = [np.inf] * self.cell_index_size
        open_list = []
        for x, y in roots:
            cost_map[self.get_index(x, y)] = 0
            open_list.append([x, y])
        # breadth first search
        while open_list:
            x, y = open_list.pop(0)
            i = self.get_index(x, y)
            c = cost_map[i]
            # update neighbors
            for nx, ny, nd in [
                [x+1, y, Maze.East],
                [x, y+1, Maze.North],
                [x-1, y, Maze.West],
                [x, y-1, Maze.South],
            ]:
                # see if the next cell can be visited
                if not self.is_inside_of_field(nx, ny) or self.wall(x, y, nd):
                    continue
                ni = self.get_index(nx, ny)
                nc = cost_map[ni]
                if nc < c + 1:
                    continue
                cost_map[ni] = c + 1
                open_list.append([nx, ny])
        return cost_map

    def print_cost_map(self, cost_map, file=sys.stdout):
        for y in reversed(range(self.size)):
            for x in range(self.size):
                c = cost_map[self.get_index(x, y)]
                print(f'{c:>4}', end="", file=file)
            print(file=file)


# ============================================================================ #
# example
if __name__ == "__main__":
    # count argument
    if len(sys.argv) < 2:
        print('please specify a maze file.')
        sys.exit(1)

    # set filepath
    filepath = sys.argv[1]

    # read maze file
    with open(filepath, 'r') as file:
        maze = Maze.parse(file)

    # show info
    print(maze)
    print(maze.generate_maze_string())

    # show cost map
    maze.print_cost_map(maze.get_cost_map())
