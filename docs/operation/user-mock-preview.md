# ユーザー管理モック確認手順

認証・DB・管理APIを実装しない画面レビュー専用環境。既存の公開Express、Caddy、systemdは変更しない。確認サーバーはループバック限定、配信対象は明示したモックファイルのみ。実際の認証情報を入力しない。

## VPSへの反映

deploy/README.md のXO本体専用手順でmainを同期する。その後、開発PCから次を実行する（VPS_HOSTは実際のSSH接続先に置換）。

```bash
ssh -L 3100:127.0.0.1:3100 debian@VPS_HOST 'cd /srv/GitHub/Sarajevo001/xo-code-busters && node src/mock-preview/server.js'
```

SSH接続中に開発PCのブラウザで http://127.0.0.1:3100/client/mock.html と http://127.0.0.1:3100/admin/ を開く。終了はCtrl+C。ポート3100を外部公開しない。既存アプリへのリンクは公開サイト https://sarajevo.jp/apps/ 以下で別途確認する。モック確認サーバーではアプリを配信しない。

## 判定

HTTP経由の主要操作、入力検証、ログアウト、非対象ファイルの拒否をCIで確認する。VPS実機でのSSH接続、画面レビューは別途確認し、未実施を合格扱いしない。
