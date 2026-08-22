# XO-Code Busters 開発ロードマップ

最終更新：2026-08-22

## 1. この資料の目的

この資料は、XO-Code Busters Webアプリケーションについて、

- 今何を作ろうとしているのか
- 何が決まっているのか
- どこまで進んでいるのか
- 次に何をするのか

を短時間で確認するための資料です。

詳細な設計仕様そのものを記載することは目的としません。

---

## 2. 現在のフェーズ

**開発環境・サーバー環境の初期構築**

現在はアプリケーション本体の本格実装前です。

まず、開発PC → GitHub → VPS という基本的な開発・デプロイ経路を構築します。

---

## 3. 基本構成

### 開発環境

Ubuntu PC

`~/develop/xo-code-busters`

ここでソースコードおよびドキュメントを編集します。

基本フロー：

Ubuntu  
↓  
Git Commit / Push  
↓  
GitHub  
↓  
VPSでGit Pull  
↓  
実行

GitHubをソースコードおよびドキュメントの正本とします。

VPS上では原則としてソースコードを直接編集しません。

---

## 4. 現在想定している技術

### クライアント

- HTML
- CSS
- Vanilla JavaScript
- PixiJS（ゲーム部分）

### サーバー

- Debian
- Node.js
- PostgreSQL（予定）

### 認証・認可

以下を候補として検討中。

- OAuth 2.0
- OpenID Connect

### 開発・管理

- Ubuntu
- Visual Studio Code
- Git
- GitHub
- KAGOYA VPS

---

## 5. 技術選定方針

このプロジェクトでは、最初から多数のフレームワークやライブラリを導入することを目的としません。

まず可能な限りシンプルな構成で実装します。

特にJavaScriptについては、Vanilla JavaScriptおよびNode.jsの標準機能を利用して実装し、その過程で生じた課題を確認します。

そのうえで、

「なぜその機能・ライブラリ・フレームワークが必要なのか」

を理解してから採用を判断します。

これはオブジェクト指向についても同様です。

言語やフレームワークが自動的に提供する仕組みに最初から依存するのではなく、まず自分で設計・実装し、必要性や効果を確認することを重視します。

---

## 6. 現在までの実績

### GitHub

`xo-code-busters` リポジトリを作成済み。

Ubuntu開発環境へClone済み。

配置場所：

`~/develop/xo-code-busters`

### 開発環境

Ubuntuを開発環境として使用。

Visual Studio Codeでリポジトリを開き、開発できる状態まで準備済み。

### KAGOYA VPS

VPS契約済み。

OS：

Debian

実施済み：

- `apt update`
- `apt upgrade`

Node.js確認済み：

- Node.js v24.18.0
- npm 11.16.0

VPS上に仮ディレクトリとして、

`~/XO-Code-Busters`

を作成済み。

正式な配置先候補：

`/srv/xo-code-busters`

VPSへのGitHubリポジトリ配置は未実施。

---

## 7. 現在のリポジトリ構成

```text
xo-code-busters/
├── README.md
├── .gitignore
└── docs/
    ├── overview/
    │   └── roadmap.md
    └── operation/
        └── project-operation-guide.md
```

必要になった時点で、

- client
- server
- test
- specification
- decisions
- research
- presentations
- scripts

等を追加します。

空のディレクトリを先に大量に作るのではなく、必要になった時点で追加します。

---

## 8. 次にやること

### 直近

1. 初期ドキュメントをGit Commit
2. GitHubへPush
3. GitHub上で初回Commitを確認
4. VPSの正式な配置方法を確定
5. VPSへリポジトリをClone

### その後

6. クライアント側の最小構成を作成
7. HTML / Vanilla JavaScriptによる最小画面を実装
8. Node.jsによる最小Web APIを実装
9. ブラウザからWeb APIを呼び出す
10. クライアント → サーバー間の通信を確認

その後、設定画面・メンテナンス画面の実装へ進みます。

PostgreSQL、認証・認可、PixiJS等については、必要となる段階で導入します。

---

## 9. 将来的に作成する資料

### 概略資料

現在地やロードマップを確認するための資料。

### 詳細設計資料

画面、DB、API、処理仕様、クラス構成、シーケンス等を記録する設計書。

### 判断ログ

設計・技術選定において、

- 何を問題としたか
- どのような選択肢があったか
- なぜその判断をしたか
- 後に判断を変更したか

を記録します。

### プレゼン資料

実際に構築したシステムについて、技術構成、設計判断、特徴、得られた知見等を説明する資料。

システムがある程度完成してから作成します。

