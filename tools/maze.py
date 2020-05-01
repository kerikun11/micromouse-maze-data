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
        self.index_size = size * size * 2  # the number of walls to save: x * y * z
        self.walls = np.zeros(self.index_size, dtype=bool)  # wall flags
        self.knowns = np.zeros(self.index_size, dtype=bool)  # wall flags
        self.start = []
        self.goals = []

    @staticmethod
    def parse(file):
        """
        parse maze string and construct maze object
        """
        lines = file.readlines()
        maze = Maze(len(lines)//2)  # get maze size
        for i, line in enumerate(reversed(lines)):
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

    def index(self, x, y, z):
        """
        get a unique id of a wall inside of the maze
        """
        if not self.is_inside_of_field(x, y, z):
            raise ValueError("out of field!")
        return z * self.size * self.size + y * self.size + x

    def is_inside_of_field(self, x, y, z):
        """
        determine if the wall is inside of the field
        """
        s = self.size
        return x >= 0 and y >= 0 and x < s+z-1 and y < s-z

    def wall(self, x, y, d, new_state=None, new_known=None):
        """
        get wall or update wall, and optionally update known flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        if not self.is_inside_of_field(x, y, z):
            return True
        i = self.index(x, y, z)
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
        i = self.index(x, y, z)
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
    print(maze)
    print(maze.generate_maze_string())
