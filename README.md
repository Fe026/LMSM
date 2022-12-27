# LMSM

東京都市大学WebClassを一覧表示するアプリケーションです。

**ベータ版です。コンパイルから自分でできる方のみ使用可能です。**
## コンパイル方法

1. [Rust](https://www.rust-lang.org/ja/)をインストールする 
2. [Go](https://go.dev)をインストールする
3. ~/LMSM で cargo build --release　を実行
4. target/release/LMSM を ~/LMSM に移動させる
5. ~/LMSM/src で go build を実行
6. 下記のインストール手順に従う

**自己証明書を用いている関係上初回起動時にChromeに警告されます**


## インストール (Python3をインストールします)

**事前にGoogle Chromeをインストールしてください。**

1. Installer.exeを実行し、指示に従い導入を進める **(Add python 3.* to PAHTにチェックを入れる)**
2. パソコンを再起動する
3. Installer.exeを実行する (必須モジュールのインストールを実行します)

## 動作環境

- Windows >= 10
- [Python](https://www.python.org/downloads/) >= 3.8
- [Google Chrome](https://www.google.com/intl/ja_jp/chrome/)

## 動作検証環境

### PC 1

- Windows 11
- Python 3.11.0
- Google Chrome 106

### PC 2

- Windows 10
- Python 3.10.5
- Google Chrome 103
