# 迷路データ

マイクロマウスの迷路データを管理するリポジトリ。  
過去の大会の迷路や練習用の迷路を随時追加していく。

迷路を表示・編集・変換するウェブアプリは[こちら](https://kerikun11.github.io/micromouse-maze-data/)。

--------------------------------------------------------------------------------

## 保存形式

迷路ファイルはテキスト形式とする。  
以下のパーツを用いて迷路情報を表現する。

| パーツ       | 表現形式                        | 注記                              |
| ------------ | ------------------------------- | --------------------------------- |
| 柱           | `+`                             | 隣接壁がないときも記載            |
| 既知壁（横） | `---`                           | ハイフン `-` 3つ                  |
| 既知壁（縦） | <code>&#124;</code>             | 縦棒 <code>&#124;</code> 1つ      |
| 未知壁（横） | <code>&nbsp;.&nbsp;</code>      | 半角スペースでドット `.` をはさむ |
| 未知壁（縦） | `.`                             | ドット `.` 1つ                    |
| スタート区画 | <code>&nbsp;S&nbsp;</code>      | 半角スペースで `S` をはさむ       |
| ゴール区画   | <code>&nbsp;G&nbsp;</code>      | 半角スペースで `G` をはさむ       |
| その他の区画 | <code>&nbsp;&nbsp;&nbsp;</code> | 半角スペース3つ                   |

注意:

- 迷路は正方形にすること。
  - 長方形の迷路を表現したい場合は左下に寄せて残りを壁で埋める。
- ファイルの終端にも改行をつけること。

### 例

```
+---+---+---+---+---+---+---+---+---+
|   |       |       |       | G   G |
+   +   +   +   +   +   +   +   +   +
|       |       |       |   | G   G |
+   +   +---+   +   +---+   +---+   +
|   |           |   .   |           |
+   +---+   +---+ . +---+---+   +---+
|       |       |   .   .   |       |
+---+   +   +   +---+---+   +---+   +
|       |   |       |       |       |
+   +   +---+---+   +   +   +   +   +
|   |   |       |       |       |   |
+   +   +   +   +---+   +---+   +   +
|   |       |       |           |   |
+   +---+   +---+   +---+   +---+   +
|       |   |       |           |   |
+   +   +   +   +---+   +---+   +   +
| S |       |                       |
+---+---+---+---+---+---+---+---+---+
```

--------------------------------------------------------------------------------

## 迷路の編集

迷路を編集したいときはテキストファイルを直接書き換えてもよいが、
クリックするだけで壁を編集できる Python アプリケーションを用意した。

### 依存パッケージ

- `python3`
- `python3-matplotlib`

### 使用方法

以下のコマンドで迷路のウィンドウが表示される

```sh
# clone this repository
git clone https://github.com/kerikun11/micromouse-maze-data.git
# change the directory
cd micromouse-maze-data
# run the application
python3 tools/maze_editor.py data/32MM2019HX.maze
# exit app to save the maze at ./output directory
```

壁をクリックすると、有無を切り替えることができる。

画面を閉じると編集した迷路が `output` ディレクトリに保存される。

--------------------------------------------------------------------------------

## 迷路サイズの推定

ファイルサイズから迷路の1辺の区画数(迷路サイズ)を推定できる。

ファイルサイズを `F` 、
迷路サイズを `M` としたとき、
改行コードを 1 Byte と仮定すると
両者の関係は次式で表せる。

    F = (4*M + 1 + 1) * (2*M + 1)

2次方程式の解の公式を用いると、次式のように表せる。

    M = (sqrt(2*F) - 2) / 4

もしも改行コードが 2 Bytes だとしても、
切り捨てを考慮すると上式で計算が可能である。

--------------------------------------------------------------------------------

## 参考資料

- [micromouseonline/mazefiles - GitHub](https://github.com/micromouseonline/mazefiles)
