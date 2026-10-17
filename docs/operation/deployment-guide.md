# XO-Code Busters デプロイ・運用手順書

- 作成日：2026-10-17
- 対象：`https://sarajevo.jp`
- 運用方式：ローカルUbuntu → GitHub → Debian VPS（手動デプロイ）
- 本書の位置付け：今回の実施結果を反映した運用手順。未確認事項は明記する。

## 1. システム構成

```text
開発用Ubuntu / VSCode
  └─ git push → GitHub（main）
                    └─ VPS上で git pull --ff-only

インターネット
  └─ https://sarajevo.jp（443/TCP）
      └─ Caddy（TLS終端・リバースプロキシ）
          └─ http://127.0.0.1:3000
              └─ Express（Node.js、systemd管理）
                  ├─ Webページ・ゲームの配信
                  └─ API（例：GET /api/health）
```

| 項目 | 現在の設定・確認結果 |
|---|---|
| ドメイン | `sarajevo.jp`（`www`は運用対象外） |
| VPS | KAGOYA VPS、Debian 13.6（trixie） |
| Node.js | v24系。VPSで `/usr/bin/node` を確認 |
| Caddy | Debianパッケージ、v2.6.2（構築時確認） |
| Express | v5系（`src/server/package.json` は `^5.1.0` を指定） |
| GitHub | `https://github.com/Sarajevo001/xo-code-busters` |
| VPS配置先 | `/srv/xo-code-busters` |
| アプリ起動ファイル | `/srv/xo-code-busters/src/server/server.js` |
| アプリ待受 | `127.0.0.1:3000` |
| systemdサービス | `xo-code-busters.service` |
| アプリ実行ユーザー | `xo-code-busters`（ログインシェルなし） |
| デプロイ作業ユーザー | `debian` |

**責務の分離**：`debian`でSSHログインして更新・管理する。Expressは`debian`ではなく、systemdの`User=xo-code-busters`により専用権限で起動する。Caddyは独立したサービスとして稼働する。

## 2. Gitで管理する設定ファイル

```text
deploy/
├── caddy/
│   └── Caddyfile
└── systemd/
    └── xo-code-busters.service
```

### Caddy設定（現在の内容）

`deploy/caddy/Caddyfile`

```caddyfile
sarajevo.jp {
    reverse_proxy 127.0.0.1:3000
}
```

実際にCaddyが参照するファイルは`/etc/caddy/Caddyfile`。Git管理ファイルからコピーして反映する。

### systemd設定（現在の内容）

`deploy/systemd/xo-code-busters.service`

```ini
[Unit]
Description=XO-Code Busters Express Server
After=network.target

[Service]
Type=simple
User=xo-code-busters
Group=xo-code-busters
WorkingDirectory=/srv/xo-code-busters/src/server
ExecStart=/usr/bin/node /srv/xo-code-busters/src/server/server.js
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

実際にsystemdが参照するファイルは`/etc/systemd/system/xo-code-busters.service`。Git管理ファイルからコピーして反映する。

## 3. 初期構築時に実施したこと（再構築用の要約）

1. ムームードメインで` sarajevo.jp `のAレコードをVPSのグローバルIPに設定し、`dig sarajevo.jp A +short`で名前解決を確認した。
2. VPSにNode.jsおよびCaddyを用意した。Caddyをsystemdで有効化した。
3. GitHubのリポジトリを`/srv/xo-code-busters`へ配置した。
4. `deploy/caddy/Caddyfile`を`/etc/caddy/Caddyfile`へ配置し、Caddyをreloadした。
5. CaddyがLet's Encryptの証明書を取得し、HTTPSが利用可能になった。
6. Express専用のシステムユーザーを作成した。
7. `deploy/systemd/xo-code-busters.service`をsystemdへ登録し、サービスを起動・有効化した。
8. ローカルAPI、HTTPS経由のAPI、トップページ、ゲーム画面を確認した。

**専用ユーザー作成（初回のみ）**

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin xo-code-busters
id xo-code-busters
```

**Caddy設定の登録（初回または変更時）**

```bash
sudo caddy validate --config /srv/xo-code-busters/deploy/caddy/Caddyfile --adapter caddyfile
sudo cp /srv/xo-code-busters/deploy/caddy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

**Expressサービス登録（初回のみ）**

```bash
sudo systemd-analyze verify /srv/xo-code-busters/deploy/systemd/xo-code-busters.service
sudo cp /srv/xo-code-busters/deploy/systemd/xo-code-busters.service /etc/systemd/system/xo-code-busters.service
sudo systemctl daemon-reload
sudo systemctl enable --now xo-code-busters
```

> 初期構築でのパッケージ導入手順・DNS管理画面の詳細操作は本書では再現していない。再構築時には各環境の現行設定を確認する。

## 4. 通常のデプロイ手順（アプリケーション更新）

### 4.1 ローカルUbuntu

開発・テストを行い、対象ファイルを確認してコミット・pushする。

```bash
cd ~/develop/xo-code-busters
git status
git add <更新対象のファイル>
git commit -m "<変更内容>"
git push origin main
```

`git add .`による意図しないファイルの登録に注意する。特に依存関係の管理ファイルは登録方針を確認すること。

### 4.2 Debian VPS

```bash
cd /srv/xo-code-busters
git status
git pull --ff-only
```

`--ff-only`はFast-Forwardで更新できる場合だけ反映し、VPS側で履歴が分岐していた場合にはマージせず停止する。

**サーバー側コードや依存関係が変更された場合**は、必要に応じて依存関係を更新し、Expressを再起動する。

```bash
cd /srv/xo-code-busters/src/server
# package-lock.jsonが適切に管理されている場合：
# npm ci --omit=dev
sudo systemctl restart xo-code-busters
systemctl status xo-code-busters --no-pager
```

**注意**：構築時、`src/server/package-lock.json`はGit追跡状態が未確定だった。`npm ci`を標準手順として確定する前に、`package.json`と`package-lock.json`をGitでどう管理するか確認する。ロックファイルのない状態で`npm ci`を実行しない。

HTML・クライアントJavaScriptなど静的ファイルのみの更新で、Expressが毎回ファイルを読み出す構成なら、通常はExpress再起動不要。ただしサーバーコードや起動時に読み込む設定を変更した場合は再起動する。

### 4.3 動作確認

```bash
curl -i http://127.0.0.1:3000/api/health
curl -i https://sarajevo.jp/api/health
```

両方ともHTTP 200と`{"status":"ok"}`を期待する。ブラウザでは以下を確認する。

- `https://sarajevo.jp/`：トップページと`Server status: ok`
- `https://sarajevo.jp/game/`：タイトル画面、ゲーム開始、ゲーム進行

APIのPOSTなど、更新内容に応じた個別機能の動作確認を追加する。

## 5. インフラ設定を変更した場合

### Caddyfile変更時

```bash
cd /srv/xo-code-busters
git pull --ff-only
sudo caddy validate --config deploy/caddy/Caddyfile --adapter caddyfile
sudo cp deploy/caddy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
systemctl status caddy --no-pager
```

### systemdサービス定義変更時

```bash
cd /srv/xo-code-busters
git pull --ff-only
sudo systemd-analyze verify deploy/systemd/xo-code-busters.service
sudo cp deploy/systemd/xo-code-busters.service /etc/systemd/system/xo-code-busters.service
sudo systemctl daemon-reload
sudo systemctl restart xo-code-busters
systemctl status xo-code-busters --no-pager
```

`daemon-reload`はサービス定義の再読込。実行中のExpressに新しい定義を適用するため、ここでは`restart`も行う。

## 6. 状態確認・障害調査

```bash
# Expressの状態
systemctl status xo-code-busters --no-pager

# Expressの直近ログ
sudo journalctl -u xo-code-busters -n 100 --no-pager

# Caddyの状態・ログ
systemctl status caddy --no-pager
sudo journalctl -u caddy -n 100 --no-pager

# 3000番ポートの待受確認
sudo ss -ltnp | grep ':3000'

# ローカルAPIと公開APIを切り分ける
curl -i http://127.0.0.1:3000/api/health
curl -i https://sarajevo.jp/api/health
```

| 現象 | 優先確認箇所 |
|---|---|
| ローカルAPIも失敗 | Expressサービス、Node.jsログ、ポート、ファイル権限 |
| ローカルAPI成功・HTTPS側失敗 | Caddyサービス、Caddyfile、DNS・TLS・リバースプロキシ |
| トップページ成功・一部機能失敗 | ブラウザ開発者ツール、該当API、静的ファイルのパス |
| `git pull --ff-only`失敗 | `git status`とブランチ履歴を確認。安易にmerge/resetしない |

## 7. 2026-10-17時点の検証実績

**確認済み**

- DNS Aレコードの名前解決
- Caddyの設定検証・reload、Let's Encrypt証明書取得
- systemdサービスの`enabled`・`active (running)`
- `GET http://127.0.0.1:3000/api/health`：HTTP 200、`{"status":"ok"}`
- `GET https://sarajevo.jp/api/health`：HTTP/2 200、`{"status":"ok"}`
- 公開トップページ表示、画面上の`Server status: ok`
- 公開ゲームのSTART → GAME → CLEAR遷移（クリア時スコア3000の画面を確認）

**未確認または今回の記録にないもの**

- OS再起動後の実際の自動復旧試験（自動起動設定`enabled`自体は確認済み）
- トップページの名前送信POSTの公開環境での再確認
- ゲームのGAME OVER遷移
- 本番環境での依存関係再インストール手順の確定
- セキュリティ監査、負荷試験、バックアップ・復旧試験

## 8. 今後の運用上の注意

- GitHubを正本とし、VPS上でソースを直接編集しない。
- Caddyfileとsystemdサービス定義はリポジトリ側を編集し、VPSでコピーして反映する。
- VPS上での更新には、静的ファイル変更・サーバー変更・インフラ設定変更の区別を付ける。
- 別サイトを追加する場合は、Caddyのサイト定義、Expressの待受ポート、systemdサービス、必要に応じた専用実行ユーザーを追加する。SSHログインユーザーをサイトごとに切り替える必要はない。
- 今回の手順は手動運用を前提とする。CI/CDや無停止デプロイは現時点の必須要件に含めない。
