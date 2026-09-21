# XO-Code Busters 開発ロードマップ

最終更新：2026-09-21

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

**Node.js標準httpによる基本通信確認完了・Express移行準備**

HTML / Vanilla JavaScriptによるクライアントと、Node.js標準 `http` モジュールによるWeb APIを実装しました。

ローカル環境での基本通信に加え、ローカルのクライアントからKAGOYA VPS上のNode.js Web APIへの実通信まで確認済みです。

確認済み：

- GET `/api/health`
- POST `/api/hello`
- JSONによるリクエスト／レスポンス
- CORS preflight
- Ubuntu → GitHub → VPS の反映経路
- ローカルClient → VPS Web APIの通信

Node.js標準機能で実装した結果、リクエストBodyの受信・JSON解析、ルーティング、レスポンス生成等について、API増加時には共通化が必要になることを確認しました。

これらを独自に共通化するのではなく、Webアプリケーションとして必要な抽象化を提供するExpressを採用することを決定しました。

次は既存APIの仕様を維持したままExpressへ移行します。

---

## 3. XO-Code Bustersが目指すシステム

XO-Code Bustersでは、Webアプリケーションとして設定画面、メンテナンス画面、認証・認可、データ永続化等を段階的に実装します。

さらに、実際に操作して遊べるゲームをシステムの一部として実装します。

ゲーム開発技術そのものの習得を主目的とはせず、XO-Code Bustersというシステムを実際に触れる形で示し、システム全体に説得力と見栄えを持たせるためのショーケースとして位置付けます。

将来的には、

```text
ゲームを遊ぶ
    ↓
ゲーム内で欲しいものが生まれる
    ↓
購入・決済
    ↓
ユーザーへ権利を付与
    ↓
ゲームへ反映
```

という一連のユースケースを成立させることを想定しています。

これにより、

- 認証
- ユーザー管理
- 商品管理
- 購入
- 決済
- 権利管理
- ゲーム

といった複数の機能を、一つのWebシステムとして連携させます。

実際の課金を必須とはせず、必要に応じて仮想的な決済による実装も検討します。

ゲーム部分の描画にはPixiJSを使用する予定ですが、具体的な実装方式についてはゲーム実装段階で決定します。

---

## 4. 基本構成

### 開発環境

Ubuntu PC

`~/develop/xo-code-busters`

ここでソースコードおよびドキュメントを編集します。

基本フロー：

```text
Ubuntu
  ↓
Git Commit / Push
  ↓
GitHub
  ↓
VPSでGit Pull
  ↓
実行
```

GitHubをソースコードおよびドキュメントの正本とします。

VPS上では原則としてソースコードを直接編集しません。

### VPS

KAGOYA VPS

配置場所：

`/srv/xo-code-busters`

GitHubからClone済みです。

GitHubへPushされた内容をVPS側でGit Pullして反映します。

### 現在の開発時構成

```text
Browser
  ├─ Client → Live Server :5500
  └─ API    → Node.js :3000
```

ClientとAPIが別Originであるため、現在は開発用のCORS対応を行っています。

### Express移行後の開発時構成

```text
Browser
   ↓ http://localhost:3000
Express
   ├─ Client静的ファイル
   └─ /api/*
```

ExpressからClientとAPIの両方を配信し、同一Originとします。

ClientからAPIを呼び出す際は、

```javascript
fetch("/api/...");
```

のような相対URLを使用します。

これにより、Client側が環境ごとのAPIサーバーのホスト名やポート番号を直接意識しない構成とします。

---

## 5. 現在想定している技術

### クライアント

- HTML
- CSS
- Vanilla JavaScript
- PixiJS（ゲーム部分・予定）

### サーバー

- Debian
- Node.js
- Express（採用決定）
- PostgreSQL（予定）

### Web公開

- HTTPS（採用決定）
- Caddy（第一候補・未検証）

公開時は、Caddyをインターネット側の公開基盤とし、ExpressをWebアプリケーションとして動作させる構成を第一候補とします。

想定構成：

```text
Internet
   ↓ HTTPS :443
Caddy
   ├─ TLS終端
   ├─ 証明書取得
   ├─ 証明書自動更新
   └─ Reverse Proxy
          ↓ HTTP :3000
       Express
        ├─ Client
        └─ /api/*
```

Caddyについてはまだ導入・検証前であり、現時点では最終確定ではありません。

### 認証・認可

以下を候補として検討します。

- OAuth 2.0
- OpenID Connect

具体的な方式については、認証・認可要件が明確になった段階で決定します。

### 開発・管理

- Ubuntu
- Visual Studio Code
- Git
- GitHub
- KAGOYA VPS

---

## 6. 技術選定方針

このプロジェクトでは、最初から多数のフレームワークやライブラリを導入することを目的としません。

まず可能な限りシンプルな構成で実装します。

特にJavaScriptについては、Vanilla JavaScriptおよびNode.jsの標準機能を利用して実装し、その過程で生じた課題を確認します。

そのうえで、

**「なぜその機能・ライブラリ・フレームワークが必要なのか」**

を理解してから採用を判断します。

便利なものを最初から全部使うのではなく、「なぜそれが必要なのか」を自分で踏んで確かめます。

**作って、困って、考えて、設計する。**

これはオブジェクト指向についても同様です。

言語やフレームワークが自動的に提供する仕組みに最初から依存するのではなく、まず自分で設計・実装し、必要性や効果を確認することを重視します。

TypeScript等のOOPや型安全性を支援する技術についても、最初から導入するのではなく、Vanilla JavaScriptで実装する過程で課題や必要性を確認したうえで採用を判断します。

### Express採用までの確認

Node.js標準 `http` によるWeb API実装では、リクエストBodyの受信・JSON解析などを直接実装しました。

例えばPOSTリクエストでは、

```javascript
let body = "";

req.on("data", chunk => {
    body += chunk;
});

req.on("end", () => {
    const data = JSON.parse(body);
});
```

という処理が必要になりました。

APIが増えることを考えると、同種の処理について共通化が必要になります。

独自の共通処理を構築するのではなく、

- `express.json()`
- `app.get()`
- `app.post()`
- `res.json()`
- 静的ファイル配信

等のWebアプリケーション向けの抽象化を利用することが適切と判断し、Expressを採用することとしました。

これは、標準機能による実装を経験したうえで必要性を確認してから追加技術を採用するという、本プロジェクトの技術選定方針に基づく判断です。

---

## 7. 現在までの実績

### GitHub

`xo-code-busters` リポジトリを作成済み。

Ubuntu開発環境へClone済み。

配置場所：

`~/develop/xo-code-busters`

GitHubへのCommit / Pushおよび、VPSでのGit Pullによる反映を確認済みです。

GitHubをソースコードおよびドキュメントの正本として運用します。

### 開発環境

Ubuntuを開発環境として使用。

Visual Studio Codeでリポジトリを開き、開発できる状態まで準備済みです。

Visual Studio CodeからGitのCommit / Pushを行えることを確認済みです。

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

`src/server/server.js` に、Node.js標準の `http` モジュールを利用した最小Web APIを実装しました。

実装済みAPI：

#### GET `/api/health`

サーバーの動作確認用API。

レスポンス例：

```json
{
  "status": "ok"
}
```

#### POST `/api/hello`

ClientからJSONを受信し、処理結果をJSONとして返すAPI。

レスポンス例：

```json
{
  "message": "Hello, xxx"
}
```

Node.js標準機能による実装では、

- HTTPサーバー生成
- CORSヘッダー
- OPTIONSリクエスト処理
- URL / HTTP Methodによるルーティング
- Request Bodyの受信
- JSON解析
- JSONレスポンス生成
- 404レスポンス

を直接実装しました。

これにより、Webフレームワークがどの責務を抽象化しているのかを確認しました。

### 現行Web APIの責務確認

Expressへの移行に先立ち、現在の `src/server/server.js` が担っている責務を整理しました。

確認した主な責務：

- HTTPサーバー生成
- CORSヘッダー設定
- OPTIONSリクエスト処理
- URL / HTTP Methodによるルーティング
- Request Bodyの受信
- JSON解析
- JSONレスポンス生成
- 404レスポンス

これらのうち、Express導入によってどの責務がフレームワーク側へ移るのかを確認済みです。

### VPSとの通信確認

GitHubへPushしたアプリケーションをKAGOYA VPSへ反映し、VPS上でNode.js Web APIを起動しました。

ローカルPC上のClientからインターネット経由でVPS上のWeb APIを呼び出し、以下を確認しました。

- GET `/api/health` → HTTP 200
- POST `/api/hello` → HTTP 200
- CORS preflight → HTTP 204

これにより、

```text
Ubuntu Browser / Live Server
        ↓
     Internet
        ↓
KAGOYA VPS / Node.js :3000
```

という経路でClientとWeb APIの実通信が成立することを確認しました。

### API接続先に関する課題

ClientとAPIを別Originで動作させる現在の構成では、ClientがAPIサーバーのホスト名やポート番号を認識する必要があります。

ローカル環境とVPS環境で接続先が異なるため、環境ごとにAPI接続先を変更する必要性が生じました。

この課題については、ExpressからClientとAPIを同一Originで配信し、

```javascript
fetch("/api/...");
```

という相対URLでAPIを呼び出す構成へ変更することで解消する方針としました。

---

## 8. 現在のリポジトリ構成

```text
xo-code-busters/
├── README.md
├── .gitignore
├── docs/
│   ├── overview/
│   │   └── roadmap.md
│   ├── operation/
│   │   └── project-operation-guide.md
│   ├── specification/
│   ├── decisions/
│   ├── research/
│   └── presentations/
└── src/
    ├── client/
    │   ├── index.html
    │   └── js/
    │       └── app.js
    └── server/
        └── server.js
```

`src/client` と `src/server` の責務分離は維持します。

現時点でこの構成を変更する予定はありません。

今後、実際に必要性が生じた場合に、

- routes
- services
- tests
- scripts

等の追加や構成変更を検討します。

空のディレクトリを先に大量に作るのではなく、必要になった時点で追加します。

---

## 9. Web公開・セキュリティ方針

Web公開時に `/srv/xo-code-busters` 全体を公開対象にはしません。

Expressによる静的ファイル配信では、公開対象を `src/client` に限定します。

以下についてはWebから直接参照できない構成とします。

- `src/server/`
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

## 10. 次にやること

### 直近

1. Expressをプロジェクトへ導入
2. GET `/api/health` をExpressへ移行
3. POST `/api/hello` をExpressへ移行
4. 既存APIと同じ動作になることをローカル環境で確認
5. Expressから `src/client` を静的配信
6. ClientのAPI呼び出しを `/api/...` の相対URLへ変更
7. 同一OriginでClient → API通信を確認
8. 現在の開発用CORS処理を削除
9. GitHubへCommit / Push
10. VPSへ反映して動作確認

### その後

- CaddyをVPSへ導入して適合性を検証
- Caddy → ExpressのReverse Proxyを構築
- HTTPSによる公開
- 証明書取得・自動更新を確認
- 設定画面・メンテナンス画面を実装
- PostgreSQLによるデータ永続化
- 認証・認可方式を検討・実装
- PixiJSを利用したゲームを実装
- 商品・購入機能を実装
- 決済処理を実装
- ユーザーへの権利付与を実装
- 付与された権利をゲームへ反映

これらの実装順序は現時点で固定しません。

実装を進めながら依存関係や必要性を確認し、適切な順序を判断します。

---

## 11. 将来的に作成・拡充する資料

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

Express採用や、今後のCaddy採否等についても、必要に応じて判断ログへ記録します。

### プレゼン資料

実際に構築したシステムについて、技術構成、設計判断、特徴、得られた知見等を説明する資料。

システムがある程度完成してから作成します。
