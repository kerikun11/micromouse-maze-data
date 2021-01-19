/**
 * @description maze class
 * @author Ryotaro Onuki <kerikun11+github@gmail.com>
 * @date 2021.01.17
 */
"use strict";

export default class Maze {
    static East = 0;
    static North = 1;
    static West = 2;
    static South = 3;
    constructor(size = 32, start = [0, 0], goals = []) {
        this.size = size;
        this.cell_index_size = size * size;
        this.wall_index_size = size * size * 2;
        this.walls = Array(this.wall_index_size).fill(false);
        this.knowns = Array(this.wall_index_size).fill(false);
        this.start = start;
        this.goals = goals;
    }
    static uniquify(x, y, d) {
        switch (d) {
            case Maze.East: return [x, y, 0, d];
            case Maze.North: return [x, y, 1, d];
            case Maze.West: return [x - 1, y, 0, Maze.East];
            case Maze.South: return [x, y - 1, 1, Maze.North];
        }
    }
    get_wall_index(x, y, z) {
        if (!this.is_inside_of_field(x, y, z))
            throw "out of field!";
        return x + y * this.size + z * this.size * this.size;
    }
    get_cell_index(x, y) {
        if (!this.is_inside_of_field(x, y))
            throw "out of field!";
        return x + y * this.size;
    }
    is_inside_of_field(x, y, z = void 0) {
        let s = this.size;
        if (z === void 0)
            return x >= 0 && y >= 0 && x < s && y < s;
        else
            return x >= 0 && y >= 0 && x < s + z - 1 && y < s - z;
    }
    is_wall(x, y, d) {
        var [x, y, z, d] = Maze.uniquify(x, y, d)
        if (!this.is_inside_of_field(x, y, z))
            return true;
        return this.walls[this.get_wall_index(x, y, z)];
    }
    is_known(x, y, d) {
        var [x, y, z, d] = Maze.uniquify(x, y, d)
        if (!this.is_inside_of_field(x, y, z))
            return true;
        return this.knowns[this.get_wall_index(x, y, z)];
    }
    update_wall(x, y, d, new_wall_state) {
        this.set_wall(x, y, d, new_wall_state);
        this.set_known(x, y, d, true);
    }
    set_wall(x, y, d, new_state) {
        var [x, y, z, d] = Maze.uniquify(x, y, d)
        if (!this.is_inside_of_field(x, y, z))
            return true;
        return this.walls[this.get_wall_index(x, y, z)] = new_state;
    }
    set_known(x, y, d, new_state) {
        var [x, y, z, d] = Maze.uniquify(x, y, d)
        if (!this.is_inside_of_field(x, y, z))
            return true;
        return this.knowns[this.get_wall_index(x, y, z)] = new_state;
    }
    get_maze_string() {
        let res = "";
        let s = this.size;
        for (let y = s - 1; y >= -1; --y) {
            // horizontal walls
            res += "+";
            for (let x = 0; x < s; ++x) {
                if (!this.is_known(x, y, Maze.North))
                    res += " . ";
                else if (this.is_wall(x, y, Maze.North))
                    res += "---";
                else
                    res += "   ";
                res += "+";
            }
            res += "\n";
            // vertical walls
            if (y === -1) break;
            res += "|";
            for (let x = 0; x < s; ++x) {
                // cell space
                if (JSON.stringify(this.start) === JSON.stringify([x, y]))
                    res += " S ";
                else if (this.goals.map(p => JSON.stringify(p)).includes(JSON.stringify([x, y])))
                    res += " G ";
                else
                    res += "   ";
                // vertical wall
                if (!this.is_known(x, y, Maze.East))
                    res += ".";
                else if (this.is_wall(x, y, Maze.East))
                    res += "|";
                else
                    res += " ";
            }
            res += "\n";
        }
        return res;
    }
    get_c_array_string({
        name = "maze_data",
        type = "const uint8_t",
        bit_order = [0, 1, 2, 3],
        y_origin_is_top = false,
    } = {}) {
        let s = this.size;
        let y_comment = y_origin_is_top ? "N-1-y" : "y";
        let res = `${type} ${name}[ /* ${y_comment} */ ${s}][ /* x */ ${s}] = {\n`;
        let y_array = [...Array(s).keys()]; // 0, 1, ... , s-1
        if (y_origin_is_top) y_array = y_array.reverse();
        for (let y of y_array) {
            res += "    {";
            for (let x = 0; x < s; ++x) {
                let hex = 0;
                if (this.is_wall(x, y, Maze.East)) hex += 1 << bit_order[0];
                if (this.is_wall(x, y, Maze.North)) hex += 1 << bit_order[1];
                if (this.is_wall(x, y, Maze.West)) hex += 1 << bit_order[2];
                if (this.is_wall(x, y, Maze.South)) hex += 1 << bit_order[3];
                res += `0x${hex.toString(16)}`;
                if (x < s - 1) res += ", ";
            }
            res += "},\n";
        }
        res += "};\n";
        return res;
    }
    static parse_maze_string(maze_string) {
        maze_string = maze_string.trim();
        let lines = maze_string.split(/\r?\n/);
        let s_x = Math.floor(lines[0].length / 4);
        let s_y = Math.floor(lines.length / 2);
        let s = Math.max(s_y, s_x);
        let maze = new Maze(s);
        lines = lines.reverse();
        for (let y = 0; y < s_y; y++) {
            // horizontal walls
            var line = lines[y * 2 + 0].trim();
            for (let x = 0; x < s_x; x++) {
                if (line[x * 4 + 2] === '-')
                    maze.update_wall(x, y, Maze.South, true);
                else if (line[x * 4 + 2] === ' ')
                    maze.update_wall(x, y, Maze.South, false);
            }
            // vertical walls
            var line = lines[y * 2 + 1].trim();
            for (let x = 0; x < s_x; x++) {
                if (line[x * 4 + 0] === '|')
                    maze.update_wall(x, y, Maze.West, true);
                else if (line[x * 4 + 0] === ' ')
                    maze.update_wall(x, y, Maze.West, false);
                if (line[x * 4 + 2] === 'S')
                    maze.start = [x, y];
                else if (line[x * 4 + 2] === 'G')
                    maze.goals.push([x, y]);
            }
        }
        return maze;
    }
    get_wall_index_from_maze_string_index(index) {
        let s = this.size;
        let y_span = (4 * s + 2) * 2;
        let y = Math.floor(s - index / y_span);
        let x = Math.floor(((index - 1 - 1) % (y_span / 2)) / 4);
        let z = Math.floor(index / (y_span / 2) + 1) % 2;
        // console.log(x, y, z);
        if (z === 0 && Math.floor((index) % (y_span / 2)) % 4 !== 2)
            return [x, y, Maze.East];
        else if (z === 1 && Math.floor(index % (y_span / 2)) % 4 !== 0)
            return [x, y, Maze.North];
        return [-1, -1, Maze.East];
    }
    toString() {
        let res = "";
        res += "size: " + this.size + "\n";
        res += "start: " + [this.start].map(p => "(" + p[0] + "," + p[1] + ")").join(",") + "\n";
        res += "goals: " + this.goals.map(p => "(" + p[0] + "," + p[1] + ")").join(",") + "\n";
        return res;
    }
}
