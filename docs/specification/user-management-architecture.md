# ユーザー管理 システム構成設計（段階的実装）

最終更新：2026-10-21

## 1. 論理構成

一般ユーザー向けWeb/API、管理者向けWeb/API、PostgreSQL DBを論理的に分離する。初期は同一KAGOYA VPS上で構成し、将来は三つの独立サーバーへ物理分離できるようにする。

| 系統 | URL・待受 | 実装状態 |
|---|---|---|
| 一般ユーザー向け | `sarajevo.jp` → Express `127.0.0.1:3000` | 既存公開運用中 |
| 管理者向け | `admin.sarajevo.jp` → Express `127.0.0.1:3001` | URLは決定。Express骨組みのみ。公開・DNS・Caddy反映なし |
| DB | PostgreSQL | 未導入・未接続 |

## 2. ディレクトリ

```text
src/
  client/         # 一般ユーザー画面（mock.htmlは試作）
  apps/           # 個別アプリ
  server/         # 既存一般ユーザーExpress/API
  admin-client/   # 管理者画面モック
  admin-server/   # 独立Express骨組み
  shared/         # 両サーバーの共通ライブラリ
    db/ logging/ errors/ config/ utils/
deploy/
  caddy/          # 稼働設定と管理者向け未適用ドラフト
  systemd/        # 既存サービスと管理者用未適用定義
```

## 3. 共通ライブラリ

`src/shared` はサーバー側のDB接続・トランザクション基盤、ログ出力、例外定義、設定読込、汎用処理の共通配置先。各APIはソース／パッケージを共有するが、互いのプロセスを実行時依存先にしない。将来の別サーバー配備では各サービスへ独立して組み込む。DB接続設定と権限はサービス別に持つ。

現時点ではパッケージ骨組みとREADMEのみ。DB接続やログ機能が完成したという意味ではない。

## 4. 現在の管理者サーバー骨組み

`src/admin-server/server.js` はデフォルトでループバックのポート3001を待ち受ける設計。GET `/api/health` 以外はHTTP 503を返し、`src/admin-client` を配信しない。認証・認可・セッション・管理APIは未実装。起動検証は未実施。

`deploy/systemd/xo-code-busters-admin.service` と `deploy/caddy/admin.Caddyfile.draft` は未適用の設定案。稼働中のCaddy設定、systemd、DNSを変更したものではない。

## 5. セキュリティ・公開方針

管理者向け機能は、認証・認可のサーバー側実装が完了するまでインターネットに公開しない。フロントエンドの画面非表示だけで保護したものとはみなさない。認証方式やDB設計はモック段階で先行確定しない。

GitHubを正本とし、コミットとVPSデプロイは別操作。明示的な承認なしにデプロイしない。
