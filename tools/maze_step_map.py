#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# author: Ryotaro Onuki (kerikun11+github@gmail.com)
# description: a step map of a maze
# usage: $ python maze_step_map.py mazefile.maze
# python version >= 3.8
# ============================================================================ #
import sys
import numpy as np

from maze import Maze  # calls ./maze.py


class StepMap:
    """
    a cell based step map of a maze
    """

    def __init__(self, maze):
        """
        construct a cell based step map of the maze
        """
        self.maze = maze
        self.step_map = [np.inf] * maze.cell_index_size

    def update(self, roots=None):
        """
        calculate cost map of cells using breadth first search
        """
        # prepare
        maze = self.maze
        step_map = self.step_map
        roots = roots if roots else maze.goals
        # initialize
        for c in step_map:
            c = np.inf
        open_list = []
        for x, y in roots:
            step_map[maze.get_cell_index(x, y)] = 0
            open_list.append([x, y])
        # breadth first search
        while open_list:
            x, y = open_list.pop(0)
            i = maze.get_cell_index(x, y)
            c = step_map[i]
            # update neighbors
            for nx, ny, nd in [
                [x+1, y, Maze.East],
                [x, y+1, Maze.North],
                [x-1, y, Maze.West],
                [x, y-1, Maze.South],
            ]:
                # see if the next cell can be visited
                if not maze.is_inside_of_field(nx, ny) or maze.wall(x, y, nd):
                    continue
                ni = maze.get_cell_index(nx, ny)
                nc = step_map[ni]
                if nc < c + 1:
                    continue
                step_map[ni] = c + 1
                open_list.append([nx, ny])
        return step_map

    def __str__(self):
        maze = self.maze
        res = ''
        for y in reversed(range(maze.size)):
            for x in range(maze.size):
                c = self.step_map[maze.get_cell_index(x, y)]
                res += f'{c:>4}'
            res += '\n'
        return res

    def __getitem__(self, key):
        return self.step_map[key]


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

    # show cost map
    step_map = StepMap(maze)
    step_map.update()
    print(step_map)
