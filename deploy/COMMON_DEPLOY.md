# 講座共通デプロイ準備（静的公開 v1）

## 範囲
`deploy/deploy_projects.py` はXO側の `projects.json` と各講座の `deploy.json` を検証し、公開計画をJSONで出力する。オプションで既存Gitチェックアウトのmainをfast-forward更新し、Caddy設定の**プレビュー**を出力する。

## 実行
```bash
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --update
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --caddy-preview /tmp/xo-projects.preview.caddy
python3 -m unittest discover -s deploy -p 'test_deploy_projects.py' -v
```

- 初期状態の `deploy/projects.json` は空。これを公開成功とみなさない。
- `--update` は**明示指定時のみ**既存のcleanなmainブランチをfast-forwardする。新規cloneはしない。Gitリモートは指定したGitHubリポジトリと一致する必要がある。
- `--update` で複数のリポジトリを更新する場合、全体の原子的なロールバックは保証しない。更新失敗時は手動で状況を確認する。
- Caddy設定はプレビューのみ。稼働中の `/etc/caddy/Caddyfile` は上書きしない。Caddyの再起動・reloadもしない。
- URLのルート `/` はプレビュー生成対象外。既存XOサイトとの衝突を避けるため第4工程で統合設計する。
- 現状の `handle_path` はURLプレフィックスを取り除く。絶対URLに依存するコンテンツやCaddyの既存ルーティングとの整合は第4工程で確認する。
- `node` と `php` は将来案であり未対応。
- 実際の公開先・既存Caddy設定・RPG移行は第4工程の対象。

## 判定条件
- 単体テスト成功：ローカルの正常系と異常系の期待結果が一致。
- 失敗：不正な入力が通る、または正常な入力が拒否される。
- 判定不能：テスト実行環境・結果が確認できない。
- VPSでの公開成功：この単体テストでは判定しない。

## demo.sarajevo.jp の玄関ページ（2026-11-26）
現行の共通デプロイは `bash deploy/deploy.sh`。この手順は自分自身をmainに同期し、登録講座を更新し、`apply_caddy.py` で構文検証・バックアップ・適用・reloadを行う。上記のプレビューは登録講座の経路のみを出力し、玄関ページは実適用用の生成処理が担当する。
RPG講座が demo.sarajevo.jp の /oop-rpg-workshop/ に登録されている場合に、完全一致の / のみをXO側の src/public/demo-portal/index.html に割り当てる。登録講座の接頭辞、sarajevo.jp のリバースプロキシ、その他ホストを変更しない。登録されていないパスを玄関の静的ルートとして公開しない。公開後は /、RPG講座への遷移、旧経路、非公開パスの拒否、XO本体の /api/health を確認し、不一致時は追加作業を停止して既存バックアップでの復旧を判断する。
