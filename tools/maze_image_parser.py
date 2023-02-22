#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# author: Ryotaro Onuki (kerikun11+github@gmail.com)
# description: a tool to parse maze image and generate maze object
# usage: $ python maze_image_parser.py maze_image.png
# python version >= 3.8
# ============================================================================ #
import os
import sys
import datetime
import cv2
import numpy as np
from matplotlib import pyplot as plt

from maze import Maze  # calls ./maze.py
from maze_step_map import StepMap  # calls ./maze_step_map.py


def show(img):
    """
    for debug
    """
    plt.figure()
    plt.imshow(img, cmap='gray', interpolation='bicubic')
    plt.xticks([]), plt.yticks([]), plt.tight_layout()


def get_maze_from_img(filepath, maze_size=None):
    """
    parse maze image and generate maze object
    """
    # get src image
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    # print('shape: ', img.shape)
    # show(img)

    # resize
    width = 1000
    scale = width / img.shape[1]
    img = cv2.resize(img, dsize=None, fx=scale, fy=scale)

    # inversion
    img = cv2.bitwise_not(img)
    # show(img)

    # binarization
    retval, img = cv2.threshold(
        img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # show(img)

    # ノイズ除去
    w = 5
    kernel = np.ones((w, w), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
    w = 6
    kernel = np.ones((w, w), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    # show(img), plt.show(), exit()

    # 輪郭抽出
    # 行の和、列の和をとる
    sum_col = np.sum(img, axis=0)
    sum_row = np.sum(img, axis=1)
    # plt.figure()
    # plt.plot(sum_col)
    # plt.figure()
    # plt.plot(sum_row)
    # plt.show()
    # 和を半分に分割する
    sl, sr = np.array_split(np.sum(img, axis=0), 2)
    st, sb = np.array_split(np.sum(img, axis=1), 2)
    # l = np.argmax(sl)
    # r = np.argmax(sr) + len(sl)
    # t = np.argmax(st)
    # b = np.argmax(sb) + len(st)
    ratio = 0.97
    lm = np.where(sl > np.max(sl) * ratio)[0]
    l = lm[len(lm)//2]
    rm = np.where(sr > np.max(sr) * ratio)[0]
    r = rm[len(rm)//2] + len(sl)
    tm = np.where(st > np.max(st) * ratio)[0]
    t = tm[len(tm)//2]
    bm = np.where(sb > np.max(sb) * ratio)[0]
    b = bm[len(bm)//2] + len(st)
    # print(f'l:{l}, r:{r}, t:{t}, b:{b}')
    img = img[t:b, l:r]
    show(img)

    # 迷路サイズの推定
    if maze_size == None:
        sum_col = np.sum(img, axis=1)
        sum_col = sum_col < np.average(sum_col)
        diff_col = np.append(sum_col, 0) - np.append(0, sum_col)
        maze_size = sum(diff_col > 0)
    maze_size = int(maze_size)
    print('maze size:', maze_size)

    # 迷路オブジェクトの作成
    maze = Maze(maze_size)
    x_indexes = np.linspace(0, img.shape[1], maze_size+1, dtype='int32')
    y_indexes = np.linspace(img.shape[0], 0, maze_size+1, dtype='int32')
    x_width = img.shape[1] // maze_size
    y_width = img.shape[0] // maze_size
    for y in range(maze_size):
        for x in range(maze_size-1):
            w = img[y_indexes[y]-y_width//2, x_indexes[x+1]]
            maze.wall(x, y, Maze.East, new_state=w, new_known=True)
    for x in range(maze_size):
        for y in range(maze_size-1):
            w = img[y_indexes[y+1], x_indexes[x]+x_width//2]
            maze.wall(x, y, Maze.North, new_state=w, new_known=True)
    # スタート区画を設定
    maze.start.append([0, 0])
    # ゴール区画を設定; ここでは幅優先探索で壁のない柱のあるマスをゴールとする
    step_map = StepMap(maze)
    step_map.update(maze.start)
    for x in range(maze.size):
        for y in range(maze.size):
            if not maze.is_inside_of_field(x, y) \
                    or not np.isfinite(step_map[maze.get_cell_index(x, y)]):
                continue
            # 柱のまわりの4マスを列挙
            around_pillar = [
                [x, y, Maze.East],
                [x+1, y, Maze.North],
                [x+1, y+1, Maze.West],
                [x, y+1, Maze.South],
            ]
            if all(not maze.wall(x, y, d) for x, y, d in around_pillar):
                for x, y, d in around_pillar:
                    maze.goals.append([x, y])
    maze.goals = list(map(list, set(map(tuple, maze.goals))))  # 重複を除く

    # 図を表示
    plt.show()

    # 終了
    return maze


if __name__ == "__main__":
    # check arguments
    if len(sys.argv) < 2:
        print('please specify a maze image file.')
        sys.exit(1)

    # set filepath
    filepath = sys.argv[1]
    maze_size = sys.argv[2] if len(sys.argv)>=2 else None # option

    # parse
    maze = get_maze_from_img(filepath, maze_size)

    # 表示
    print(maze.get_maze_string())
    print(maze)

    # save maze
    os.makedirs('output', exist_ok=True)
    datetime_string = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    output_filepath = f'./output/{basename_without_ext}-{datetime_string}.maze'
    with open(output_filepath, 'w') as file:
        file.write(maze.get_maze_string())
        print('maze data saved: ' + output_filepath)
