# Tkinter Othello

This repository contains a GUI based Othello (Reversi) game built with Python.
It relies on the Tkinter GUI toolkit and the module set published by
[magu1436](https://github.com/magu1436/TkinterBoardGame.git).

## Requirements

- **Python**: developed with Python **3.13**.
 - **Libraries**: `pyyaml` is required to load configuration. The game also uses
  `Pillow` for image handling. To save match history in a database, install
  `mysql-connector-python`.

Install the dependencies with `pip`:

```bash
pip install pyyaml pillow mysql-connector-python
```

## Running the Game

Execute `othello.py` with Python 3.13:

```bash
python othello.py
```

A window will open showing the home screen from which you can start playing.

## Customising Images

Game graphics are stored in the `images/` directory. `config.yaml` defines the
path for each graphic used in the application. Place your own PNG files in this
directory and update the corresponding path inside `config.yaml` to change the
appearance of the board, pieces, or background.

```
BLACK_STONE_IMAGE_PATH: "images/stone_black.png"
WHITE_STONE_IMAGE_PATH: "images/stone_white.png"
...
```

PNG format is expected for all images.

## Match History

Matches can now be recorded in a MySQL database. From the history screen you
can replay any saved game, resume from the middle of a match or watch it play
out to the end.

## Database Setup

To enable the database features:

1. Install the `mysql-connector-python` library.
2. Create a MySQL database where match history will be stored.
3. Enter your connection details in `database_info.yaml`.

## Credits

This project uses modules created by **magu1436**, available at
[https://github.com/magu1436/TkinterBoardGame.git](https://github.com/magu1436/TkinterBoardGame.git).

---
Feel free to fork this repository and modify it to suit your needs.

## 日本語版

このリポジトリはPython製のGUI版オセロ（リバーシ）ゲームです。
Tkinterを使ったGUIと、[magu1436](https://github.com/magu1436/TkinterBoardGame.git) が公開しているモジュール群に依存しています。

## 必要要件

- **Python**: このプログラムは **Python 3.13** で開発されました。
- **ライブラリ**: 設定読み込みに `pyyaml` を使用します。また画像表示に `Pillow`
  が必要です。対戦履歴をデータベースに保存する場合は
  `mysql-connector-python` もインストールしてください。

以下のコマンドで依存パッケージをインストールしてください。

```bash
pip install pyyaml pillow mysql-connector-python
```

## ゲームの起動

`othello.py` を Python 3.13 で実行します。

```bash
python othello.py
```

起動するとホーム画面が表示され、ゲームを始められます。

## 画像のカスタマイズ

ゲームで使用する画像は `images/` フォルダに入っています。
`config.yaml` でそれぞれの画像のパスを指定できます。PNG形式の画像をこのフォルダに配置し、`config.yaml` 内のパスを変更することで、ボードや駒、背景などの見た目を変更できます。

```
BLACK_STONE_IMAGE_PATH: "images/stone_black.png"
WHITE_STONE_IMAGE_PATH: "images/stone_white.png"
...
```

すべての画像は PNG 形式である必要があります。

## 対戦履歴

対局結果を MySQL データベースに保存できます。履歴一覧画面から記録した対局を再生し、途中から再開したり、最後まで進行を確認することが可能です。

## データベース準備

以下を行うことでデータベース機能を利用できます。

1. `mysql-connector-python` ライブラリを導入する。
2. 履歴を保存するための MySQL データベースを作成する。
3. `database_info.yaml` に接続情報を記入する。

## クレジット

このプロジェクトでは **magu1436** が作成したモジュールを利用しています。  
https://github.com/magu1436/TkinterBoardGame.git

---

