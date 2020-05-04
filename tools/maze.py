#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# author: Ryotaro Onuki (kerikun11+github@gmail.com)
# description: a maze module includes Maze class
# usage: $ python maze.py mazefile.maze
# python version >= 3.8
# ============================================================================ #
import sys
import numpy as np


class Maze:
    """
    a maze class includes wall data, start indexes, goal indexes
    """
    # constants
    East, North, West, South = range(4)

    def __init__(self, size=32, start=[], goals=[]):
        """
        construct a maze object with a maze size

        Returns
        -------
        None
        """
        self.size = size  # number of cells on one side of the maze
        # the number of cells in the maze: x * y
        self.cell_index_size = size * size
        # the number of walls to save: x * y * z
        self.wall_index_size = size * size * 2
        # wall data; wall states and known flags
        self.walls = np.zeros(self.wall_index_size, dtype=bool)
        self.knowns = np.zeros(self.wall_index_size, dtype=bool)
        # start and goal cells
        self.start = start
        self.goals = goals

    @classmethod
    def uniquify(cls, x, y, d):
        """
        returns a unique coordinates of a wall without redundancy on both sides of the wall

        Returns
        -------
        int x, int y, int z, int d
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

    def get_wall_index(self, x, y, z):
        """
        get a unique and sequential index of a wall inside of the maze

        Returns
        -------
        int index
        """
        if not self.is_inside_of_field(x, y, z):
            raise ValueError("out of field!")
        return x + y * self.size + z * self.size * self.size

    def get_cell_index(self, x, y):
        """
        get a unique and sequential index of a cell inside of the maze

        Returns
        -------
        int index
        """
        if not self.is_inside_of_field(x, y):
            raise ValueError("out of field!")
        return y * self.size + x

    def is_inside_of_field(self, x, y, z=None):
        """
        determine if the wall or cell is inside of the field

        Returns
        -------
        bool result
        """
        s = self.size  # maze size
        if z == None:
            return x >= 0 and y >= 0 and x < s and y < s  # cell
        else:
            return x >= 0 and y >= 0 and x < s+z-1 and y < s-z  # wall

    def wall(self, x, y, d, new_state=None, new_known=None):
        """
        get or update a wall flag, and optionally update a known flag

        Returns
        -------
        bool flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        # If it is out of the field, the wall is assumed to exist.
        if not self.is_inside_of_field(x, y, z):
            return True
        i = self.get_wall_index(x, y, z)
        if new_state != None:
            self.walls[i] = new_state
        if new_known != None:
            self.knowns[i] = new_known
        return self.walls[i]

    def known(self, x, y, d, new_known=None):
        """
        get or update a known flag of a wall

        Returns
        -------
        bool flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        # If it is out of the field, the wall is assumed to be known.
        if not self.is_inside_of_field(x, y, z):
            return True
        i = self.get_wall_index(x, y, z)
        if new_known != None:
            self.knowns[i] = new_known
        return self.knowns[i]

    def __str__(self):
        """
        show information of the maze

        Returns
        -------
        string
        """
        return f'size: {self.size}x{self.size}' + '\n' + \
            'start: ' + ', '.join([f'({x}, {y})' for x, y in self.start]) + '\n' + \
            'goals: ' + ', '.join([f'({x}, {y})' for x, y in self.goals])

    @staticmethod
    def parse_maze_string(file):
        """
        parse a maze string from file and construct a maze object

        Returns
        -------
        Maze object
        """
        lines = file.readlines()
        maze_size = max(len(lines)//2, len(lines[0])//4)
        maze = Maze(maze_size)  # construct a maze object
        for i, line in enumerate(reversed(lines)):
            line = line.rstrip()  # remove \n
            # +---+---+---+---+
            if i % 2 == 0:
                for j, c in enumerate(line[2:: 4]):
                    if c == '-':
                        maze.wall(j, i//2, Maze.South, True, new_known=True)
                    elif c == ' ':
                        maze.wall(j, i//2, Maze.South, False, new_known=True)
            # |   |   | G |   |
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

    def get_maze_string(self):
        """
        generate a maze string to be saved in text format

        Returns
        -------
        string
        """
        res = ''  # result string
        for y in reversed(range(-1, self.size)):
            # +---+---+---+---+
            res += '+'  # first pillar
            for x in range(self.size):
                # horizontal wall
                if not self.known(x, y, Maze.North):
                    res += ' . '
                elif self.wall(x, y, Maze.North):
                    res += '---'
                else:
                    res += '   '
                res += '+'  # pillar
            res += '\n'
            # |   |   | G |   |
            if y == -1:
                break
            res += '|'  # first wall
            for x in range(self.size):
                # cell space
                if [x, y] in self.start:
                    res += ' S '
                elif [x, y] in self.goals:
                    res += ' G '
                else:
                    res += '   '
                # vertical wall
                if not self.known(x, y, Maze.East):
                    res += '.'
                elif self.wall(x, y, Maze.East):
                    res += '|'
                else:
                    res += ' '
            res += '\n'
        return res


# ============================================================================ #
# example
if __name__ == "__main__":
    # check arguments
    if len(sys.argv) < 2:
        print('please specify a maze file.')
        sys.exit(1)

    # set filepath
    filepath = sys.argv[1]

    # read maze file
    with open(filepath, 'r') as file:
        maze = Maze.parse_maze_string(file)

    # show info
    print(maze)
    print(maze.get_maze_string())
