#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# author: Ryotaro Onuki (kerikun11+github@gmail.com)
# description: a tool to edit maze file
# usage: $ python maze_editor.py mazefile.maze
# python version >= 3.8
# ============================================================================ #
import os
import sys
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
from maze import Maze  # calls ./maze.py


class MazeEditor:
    """
    A tool to draw a maze so that you can edit the wall by clicking on it.
    """

    def __init__(self, maze):
        """
        construct a maze editor object with a maze object
        """
        self.maze = maze  # maze object

    def draw_maze(self):
        maze = self.maze
        # print walls
        for i in range(maze.size+1):
            for j in range(maze.size):
                # +---+---+
                if maze.wall(i, j, Maze.South):
                    self.draw_wall(maze, i, j, Maze.South)
                else:
                    self.draw_wall(maze, i, j, Maze.South, ':', color='gray')
                # |   |   |
                if maze.wall(j, i, Maze.West):
                    self.draw_wall(maze, j, i, Maze.West)
                else:
                    self.draw_wall(maze, j, i, Maze.West, ':', color='gray')
        # print start and goal character
        for ps, t in [[maze.start, 'S'], [maze.goals, 'G']]:
            for p in ps:
                plt.text(p[0], p[1], t, ha='center', va='center')
        plt.gca().set_aspect('equal')  # set the x and y axes to the same scale
        plt.xticks(range(0, maze.size+1, 1))
        plt.yticks(range(0, maze.size+1, 1))
        plt.xlim([-1/2, maze.size-1/2])
        plt.ylim([-1/2, maze.size-1/2])
        plt.tight_layout()

    @staticmethod
    def draw_wall(maze, x, y, d, fmt='k', **kwargs):
        x, y, z, d = Maze.uniquify(x, y, d)
        if z == 0:
            x, y = [x+1/2, x+1/2], [y-1/2, y+1/2]
        else:
            x, y = [x-1/2, x+1/2], [y+1/2, y+1/2]
        plt.plot(x, y, 'w', lw=2)  # erase wall
        plt.plot(x, y, fmt, **kwargs)  # draw new wall
        plt.plot(x, y, 'k.')  # draw pillars

    def attach_wall_toggle(self):
        plt.connect('button_press_event', self.button_press_event)

    def button_press_event(self, event):
        maze = self.maze
        x, y = event.xdata, event.ydata
        xf, xi = math.modf(x)
        yf, yi = math.modf(y)
        z, d = [0, Maze.East] if abs(xf-1/2) < abs(yf-1/2) else [1, Maze.North]
        if z == 0:
            x, y = int(round(x-1/2)), int(round(y))
        else:
            x, y = int(round(x)), int(round(y-1/2))
        w = not maze.wall(x, y, d)
        c = 'r' if w else 'r:'
        maze.wall(x, y, d, w, new_known=True)
        MazeEditor.draw_wall(maze, x, y, d, c)
        plt.draw()
        print(maze.get_maze_string())


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
    print(maze)
    print(maze.get_maze_string())

    # prepare figure
    figsize = maze.size / 2
    fig = plt.figure(figsize=(figsize, figsize))

    # setup maze editor
    mp = MazeEditor(maze)
    mp.draw_maze()
    mp.attach_wall_toggle()

    # start
    plt.show()

    # save modified maze
    os.makedirs('output', exist_ok=True)
    datetime_string = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    output_filepath = f'./output/{basename_without_ext}-{datetime_string}.maze'
    with open(output_filepath, 'w') as file:
        file.write(maze.get_maze_string())
        print('modified maze data saved: ' + output_filepath)
