/**
 * @description maze viewer
 * @author Ryotaro Onuki <kerikun11+github@gmail.com>
 * @date 2021.01.11
 */
"use strict";

class Maze {
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
  get_c_array_string({ name = "maze_data", type = "const uint8_t", bit_order = [0, 1, 2, 3] } = {}) {
    let s = this.size;
    let res = `${type} ${name}[${s}][${s}] = {\n`;
    for (let y = s - 1; y >= 0; --y) {
      res += "    {";
      for (let x = 0; x < s; ++x) {
        let hex = 0;
        if (this.is_wall(x, y, Maze.East)) hex += 1 << bit_order[0];
        if (this.is_wall(x, y, Maze.North)) hex += 1 << bit_order[1];
        if (this.is_wall(x, y, Maze.West)) hex += 1 << bit_order[2];
        if (this.is_wall(x, y, Maze.South)) hex += 1 << bit_order[3];
        res += `0x${hex.toString(16)}, `;
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
  toString() {
    let res = "";
    res += "size: " + this.size + "\n";
    res += "start: " + [this.start].map(p => "(" + p[0] + "," + p[1] + ")").join(",") + "\n";
    res += "goals: " + this.goals.map(p => "(" + p[0] + "," + p[1] + ")").join(",") + "\n";
    return res;
  }
}

function update_c_array() {
  let maze_string = document.getElementById("maze-field").innerText;
  let maze = Maze.parse_maze_string(maze_string);
  let bit_order = [0, 1, 2, 3];
  if (document.getElementById("bit-order-1").checked) bit_order = [0, 1, 2, 3];
  if (document.getElementById("bit-order-2").checked) bit_order = [1, 0, 3, 2];
  let maze_c_array_string = maze.get_c_array_string({ name: maze_name, bit_order: bit_order });
  document.getElementById("maze-c-array-field").innerText = maze_c_array_string;
}

let maze_name = "maze_data";
update_c_array();

$(".custom-file-input").on("change", function (evt) {
  // ラベルにファイル名を表示する
  $(this).next(".custom-file-label").html($(this)[0].files[0].name);
  maze_name = $(this)[0].files[0].name.replaceAll(/[^\w_$]/ig, "_");
  if (maze_name.match(/^[0-9]/)) maze_name = "_" + maze_name;
  //FileReaderの作成
  var reader = new FileReader();
  //テキスト形式で読み込む
  var file = evt.target.files;
  reader.readAsText(file[0]);
  //読込終了後の処理
  reader.onload = function (ev) {
    //テキストエリアに表示する
    document.getElementById("maze-field").innerText = reader.result;
    update_c_array();
  }
});

$(".form-check-input").on("change", function (evt) {
  update_c_array();
});

// var maze = new Maze(4);
// var maze = new Maze(4, [0, 0], [[2, 3], [1, 2]]);
// maze.update_wall(0, 0, Maze.East, true);
// maze.update_wall(0, 0, Maze.North, false);
// maze.update_wall(0, 1, Maze.East, true);
// maze.update_wall(0, 1, Maze.North, false);
// maze.update_wall(0, 2, Maze.East, true);
// maze.update_wall(0, 2, Maze.North, false);
// maze.update_wall(0, 3, Maze.East, false);
// maze.update_wall(1, 3, Maze.East, true);
// maze.update_wall(1, 2, Maze.North, false);
// var maze_string = maze.get_maze_string();
// console.log(maze_string);
// maze = Maze.parse_maze_string(maze_string)
// console.log(maze.toString())
// console.log(maze.get_maze_string())
// console.log(maze.get_c_array_string())
