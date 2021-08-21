/**
 * @description maze viewer
 * @author Ryotaro Onuki <kerikun11+github@gmail.com>
 * @date 2021.01.11
 */
"use strict";

import Maze from "./maze.js";

/**
  * @brief 迷路ファイル名をC言語の変数名に変換する関数
  */
function maze_name_escape(src) {
    let maze_name = src.replaceAll(/[^\w_$]/ig, "_");
    if (maze_name.match(/^[0-9]/)) maze_name = "_" + maze_name;
    return maze_name;
}

/**
 * @brief C言語の配列フィールドの内容を更新する関数
 */
function update_c_array(maze, maze_name) {
    let bit_order = [0, 1, 2, 3];
    if (document.getElementById("bit-order-1").checked) bit_order = [0, 1, 2, 3];
    if (document.getElementById("bit-order-2").checked) bit_order = [1, 0, 3, 2];
    let y_origin_is_top = document.getElementById("y-origin-is-top").checked;
    let maze_c_array_string = maze.get_c_array_string({
        name: maze_name_escape(maze_name), bit_order: bit_order, y_origin_is_top: y_origin_is_top
    });
    document.getElementById("maze-c-array-field").innerText = maze_c_array_string;
}

/**
 * @brief 迷路テキストフィールドを更新する関数
 */
function update_maze_text(maze) {
    let maze_text_field = document.getElementById("maze-text-field");
    let maze_string = maze.get_maze_string();
    maze_text_field.innerText = "";
    for (let char of maze_string) {
        let span = document.createElement('span');
        span.innerText = char;
        /* クリックで壁の有無を切り替えるイベントを追加する */
        span.addEventListener('click', function () {
            let position = 0;
            let el = this;
            while (el.previousSibling !== null) {
                position++;
                el = el.previousSibling;
            }
            let [x, y, d] = maze.get_wall_index_from_maze_string_index(position);
            maze.update_wall(x, y, d, !maze.is_wall(x, y, d));
            update_maze_text(maze);
            update_c_array(maze, maze_name);
        });
        maze_text_field.appendChild(span);
    }
}

/**
 * @brief GitHub から過去の迷路データを取得する関数
 */
function get_maze_from_github() {
    let url = "https://api.github.com/repos/kerikun11/micromouse-maze-data/contents/data?ref=master";
    $.getJSON(url, function (data) {
        for (let item of data) {
            let option = document.createElement("option");
            option.text = item["name"];
            option.value = item["download_url"];
            $("#maze-file-select-github").append(option);
        }
    });
}

/* global variables */
let maze_name = "default.maze";
let maze_string = document.getElementById("maze-text-field").innerText;
let maze = Maze.parse_maze_string(maze_string);

/* 各フィールドの初期化 */
get_maze_from_github();
update_maze_text(maze);
update_c_array(maze, maze_name);

/* 迷路ファイルが更新されたとき */
$("#maze-file-select-upload").on("change", function (evt) {
    // ラベルにファイル名を表示する
    $(this).next(".custom-file-label").html($(this)[0].files[0].name);
    maze_name = $(this)[0].files[0].name
    //FileReaderの作成
    let reader = new FileReader();
    //テキスト形式で読み込む
    let file = evt.target.files;
    reader.readAsText(file[0]);
    //読込終了後の処理
    reader.onload = function (ev) {
        //テキストエリアに表示する
        maze = Maze.parse_maze_string(reader.result);
        update_maze_text(maze);
        update_c_array(maze, maze_name);
    }
});

/* 迷路ファイルが更新されたとき */
$("#maze-file-select-github").on("change", function (evt) {
    // ラベルにファイル名を表示する
    let url = $(this).val();
    maze_name = url.split('/').reverse()[0]
    fetch(url).then(function (response) {
        response.text().then(function (text) {
            maze = Maze.parse_maze_string(text);
            update_maze_text(maze);
            update_c_array(maze, maze_name);
        });
    });
});

/* ビット順のラジオボタンが更新されたとき */
$(".bit-order-input").on("change", function (evt) {
    update_c_array(maze, maze_name);
});
$("#y-origin-is-top").on("change", function (evt) {
    update_c_array(maze, maze_name);
});

/* コピーボタン */
function copy_text(id) {
    let text = document.getElementById(id).innerText;
    let area = document.createElement("textarea");
    area.textContent = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    document.body.removeChild(area);
}
$("#maze-text-copy-button").on("click", function (evt) {
    copy_text("maze-text-field");
});
$("#maze-c-array-copy-button").on("click", function (evt) {
    copy_text("maze-c-array-field");
});

/* 保存ボタン */
function download(data, filename, type) {
    var file = new Blob([data], { type: type });
    var a = document.createElement("a"),
        url = URL.createObjectURL(file);
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 0);
}
$("#maze-text-save-button").on("click", function (evt) {
    let maze_string = maze.get_maze_string();
    download(maze_string, maze_name, "text/plain");
});
