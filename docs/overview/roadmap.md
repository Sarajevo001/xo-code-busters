# XO-Code Busters 開発ロードマップ

最終更新：2026-08-23

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

**アプリケーション実装開始**

開発PC → GitHub → VPS という基本的な開発・デプロイ経路の構築が完了しました。

クライアントおよびサーバーの最小構成を作成し、
HTML / Vanilla JavaScriptによるクライアントと、
Node.js標準機能によるWeb APIとの基本通信まで実装しました。

ローカル開発環境では、

- クライアントからWeb APIを呼び出す
- Web APIからJSONを返す
- クライアントからJSONをPOSTする
- Node.jsでリクエストを受け取る
- 処理結果をJSONで返す
- 受け取った結果をブラウザへ表示する

という基本的な往復通信を確認済みです。

次はGitHubへPushしたアプリケーションをVPSへ反映し、
VPS上でNode.jsアプリケーションを起動して動作を確認します。

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

### VPS

KAGOYA VPS

配置場所：

`/srv/xo-code-busters`

GitHubからClone済みです。

今後はGitHubへPushされた内容をVPS側でGit Pullして反映します。

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

### Web公開

- nginx（導入予定）

nginxからリポジトリ全体を公開するのではなく、クライアントの静的公開領域のみを公開対象とする方針です。

Node.jsによるWeb APIは、nginxからリバースプロキシする構成を候補とします。

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

TypeScript等のOOPや型安全性を支援する技術についても、最初から導入するのではなく、Vanilla JavaScriptで実装する過程で課題や必要性を確認したうえで採用を判断します。

---

## 6. 現在までの実績

### GitHub

`xo-code-busters` リポジトリを作成済み。

Ubuntu開発環境へClone済み。

配置場所：

`~/develop/xo-code-busters`

初期ドキュメントおよびGit管理用ファイルを作成済み。

- `README.md`
- `.gitignore`
- `docs/overview/roadmap.md`
- `docs/operation/project-operation-guide.md`

初回Commit：

`Initial project setup`

GitHubへの初回PushおよびGitHub上での反映確認まで完了しています。

アプリケーションの最小構成および基本通信処理についてもCommit / Push済みです。

Commit：

`クライアント・サーバー間の基本通信を実装`

### 開発環境

Ubuntuを開発環境として使用。

Visual Studio Codeでリポジトリを開き、開発できる状態まで準備済み。

Visual Studio CodeからGitのCommit / Pushを行えることを確認済み。

### クライアント

`src/client` にクライアント側の最小構成を作成しました。

実施済み：

- `index.html` を作成
- Vanilla JavaScriptを外部ファイル `js/app.js` として分離
- JavaScriptからDOMを取得し、画面を書き換えられることを確認
- Visual Studio CodeのLive Serverを利用してHTTP経由で表示
- Node.js Web APIを `fetch` で呼び出す処理を実装
- Web APIから取得したJSONを画面へ表示
- 入力値をJSONとしてWeb APIへPOST
- Web APIから返された結果を画面へ表示

### Node.js Web API

`src/server/server.js` にNode.js標準の `http` モジュールを利用した最小Web APIを実装しました。

外部Webフレームワークは現時点では導入していません。

実装済みAPI：

#### GET `/api/health`

サーバーの動作確認用API。

レスポンス例：

```json
{
  "status": "ok"
}### Web公開・セキュリティ方針

Web公開時に `/srv/xo-code-busters` 全体を公開対象にはしない方針としました。

将来的にnginxを導入し、クライアントの静的公開領域のみを公開対象とします。

以下についてはWebから直接参照できない構成とします。

- `server/`
- `docs/`
- `.git/`
- 秘密情報
- その他、公開を意図していないファイル

また、ディレクトリトラバーサル対策をセキュリティ設計項目として扱います。

基本方針：

- APIのURLと実ファイルパスを直接対応させない
- ユーザー入力をそのままファイルパスとして使用しない
- ファイルアクセスが必要な場合は許可された領域内に制限する
- パスの正規化等を行い、公開・アクセス可能な範囲からの逸脱を防止する

詳細については、セキュリティ設計を作成する段階で定義します。

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

1. クライアント・サーバーの最小ディレクトリ構成を決定
2. クライアント側の最小構成を作成
3. HTML / Vanilla JavaScriptによる最小画面を実装
4. Node.js標準機能による最小Web APIを実装
5. ローカル開発環境でWeb APIの動作を確認
6. ブラウザからWeb APIを呼び出す
7. クライアント → サーバー間の通信を確認
8. GitHubへPush
9. VPSでGit Pull
10. VPS上でNode.jsアプリケーションを起動し、動作を確認

### その後

- nginxによるWeb公開構成を構築
- 静的公開領域と非公開領域を分離
- Node.js Web APIへのリバースプロキシを構築
- HTTPS化を検討・実施
- PostgreSQLを導入
- 設定画面・メンテナンス画面の実装
- 認証・認可方式を検討
- ゲーム部分の実装段階でPixiJSを導入

PostgreSQL、nginx、認証・認可、PixiJS、追加ライブラリ等については、必要となる段階で導入します。

---

## 9. 将来的に作成する資料

### 概略資料

現在地やロードマップを確認するための資料。

### 詳細設計資料

画面、DB、API、処理仕様、クラス構成、シーケンス等を記録する設計書。

セキュリティ設計についても詳細設計資料として管理します。

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

### 一点だけ補足

今回、元のロードマップにあった「技術選定方針」はそのまま残しています。ここは今回の実装方法とも綺麗に一致しています。もともと「Vanilla JavaScriptとNode.js標準機能でまず実装し、課題を確認してから追加技術を判断する」としていました。:contentReference[oaicite:1]{index=1}

実際今日、

**素のNode.js → CORSに遭遇 → Originを限定して許可 → OPTIONSを処理 → GET/POST通信成立**

と、まさにその方針どおりに一個問題を踏めました。

なので、これは単なる進捗ではなく、**ロードマップに書いていた開発方針が実際の開発として動き始めた最初の日**と見てよいと思います。